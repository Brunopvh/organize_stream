#!/usr/bin/env python3
from __future__ import annotations
import os.path
from io import BytesIO
import convert_stream as cs
import ocr_stream as ocr
import soup_files as sp


class Ocr(ocr.RecognizeImage):
    """
    Singleton para reconhecimento de texto em imagens
    """
    _instance = None  # armazena a instância única

    def __new__(
                cls, bin_tess: ocr.BinTesseract = ocr.BinTesseract(), *,
                lib_ocr: ocr.LibOcr = ocr.DEFAULT_LIB_OCR
            ):
        if cls._instance is None:
            # Cria a instância uma única vez
            cls._instance = super(Ocr, cls).__new__(cls)
        return cls._instance

    def __init__(
                self, bin_tess: ocr.BinTesseract = ocr.BinTesseract(), *,
                lib_ocr: ocr.LibOcr = ocr.DEFAULT_LIB_OCR,
            ):
        # Evita reexecutar __init__ em chamadas subsequentes
        if not hasattr(self, "_initialized"):
            super().__init__(bin_tess, lib_ocr=lib_ocr)
            self._initialized = True


def create_table_from_dict(data: dict[str, cs.ColumnBody]) -> cs.TextTable:
    _values: list[cs.ColumnBody] = []
    for _k in data.keys():
        _values.append(data[_k])
    return cs.TextTable(_values)


def create_tb_from_names(files: list[sp.File]) -> list[cs.DictTextTable]:
    values: list[cs.DictTextTable] = []
    for f in files:
        tb = cs.DictTextTable.create_void_dict()
        tb[cs.ColumnsTable.TEXT.value].append(f.name())
        tb[cs.ColumnsTable.FILETYPE.value].append(f.extension())
        tb[cs.ColumnsTable.FILE_PATH.value].append(f.absolute())
        tb[cs.ColumnsTable.FILE_NAME.value].append(f.basename())
        tb[cs.ColumnsTable.KEY.value].append('0')
        tb[cs.ColumnsTable.NUM_PAGE.value].append('nan')
        tb[cs.ColumnsTable.NUM_LINE.value].append('1')
        tb[cs.ColumnsTable.DIR.value].append(f.dirname())
        values.append(tb)
    return values


def recognize_images(
            images: list[cs.ImageObject] | list[sp.File], *,
            recognize: Ocr = Ocr(),
            pbar: sp.ProgressBarAdapter = sp.ProgressBarAdapter(),
        ) -> cs.DocumentPdf:
    """
        Aplicar OCR em lista de imagens, e retornar um documento DocumentPdf() com as imagens embutidas.
    """
    pages_pdf: list[cs.PageDocumentPdf] = []
    max_num: int = len(images)
    print()
    pbar.start()
    for _num, im in enumerate(images):
        if isinstance(im, sp.File):
            im = cs.ImageObject(im)
        pbar.update(
            ((_num + 1) / max_num) * 100,
            f'[OCR IMAGEM]: {_num + 1}/{max_num} {im.metadata.name}',
        )
        tmp_doc = recognize.image_recognize(im).to_document()
        pages_pdf.extend(tmp_doc.to_pages())
        del tmp_doc
    pbar.stop()
    print()
    return cs.DocumentPdf.create_from_pages(pages_pdf)


def read_image(
            image: sp.File | cs.ImageObject | bytes | BytesIO, *,
            recognize: Ocr = Ocr(),
        ) -> cs.DictTextTable:
    """
        Extrair o texto de uma imagem e retornar o texto em no formato cs.DictTextTable().
    """
    if isinstance(image, sp.File):
        image: cs.ImageObject = cs.ImageObject(image)
    elif isinstance(image, cs.ImageObject):
        pass
    elif isinstance(image, bytes):
        image: cs.ImageObject = cs.ImageObject.create_from_bytes(image)
    elif isinstance(image, BytesIO):
        image: cs.ImageObject = cs.ImageObject(image)
    else:
        raise ValueError('Use: File|DocumentPdf|bytes|ByesIO')

    txt = recognize.image_to_string(image)
    try:
        _values = txt.split('\n')
    except Exception as e:
        print(f'Error: {e}')
        _values = ['nan']

    if image.metadata.file_path.is_empty:
        return cs.DictTextTable.create_from_values(_values, file_type=image.metadata.extension)
    else:
        return cs.DictTextTable.create_from_values(
            _values,
            file_path=image.metadata.file_path,
            file_type=image.metadata.extension,
        )


def read_images(
            images_files: list[cs.ImageObject] | list[sp.File], *,
            recognize: Ocr = Ocr(),
            pbar: sp.ProgressBarAdapter = sp.ProgressBarAdapter(),
        ) -> cs.DictTextTable:
    """
        Lista de imagens e retorna dict[str, ColumnBody]
    """
    list_table: list[cs.DictTextTable] = []
    max_num: int = len(images_files)
    print()
    pbar.start()
    for _num, img in enumerate(images_files):
        if isinstance(img, sp.File):
            img: cs.ImageObject = cs.ImageObject(img)
        pbar.update(
            ((_num + 1) / max_num) * 100,
            f'[OCR IMAGEM]: {_num + 1}/{max_num} {img.metadata.name}',
        )
        list_table.append(read_image(img, recognize=recognize))
    return cs.mod_types.table_types.concat_maps(list_table)


def read_directory_image(
            directory: sp.Directory, *,
            recognize: Ocr = Ocr(),
            pbar: sp.ProgressBarAdapter = sp.ProgressBarAdapter(),
        ) -> list[cs.TextTable]:
    """
        Ler as imagens de um diretório e retorna list[TextMap]
    """
    _files: list[sp.File] = sp.InputFiles(directory).get_files(file_type=sp.LibraryDocs.IMAGE)
    _data: list[cs.TextTable] = []
    max_num: int = len(_files)
    print()
    pbar.start()
    img: sp.File
    for _num, img in enumerate(_files):
        pbar.update(
            ((_num + 1) / max_num) * 100,
            f'[OCR Imagens]: {_num + 1}/{max_num} {img.basename()}',
        )
        _data.append(
            create_table_from_dict(read_image(img, recognize=recognize))
        )
    return _data


def read_document_pdf(
            document: cs.DocumentPdf,
            file_path: str,
            apply_ocr: bool = False,
            recognize: Ocr = Ocr(),
            pbar: sp.ProgressBarAdapter = sp.ProgressBarAdapter(),
            dpi: int = 200
        ) -> cs.DictTextTable:
    """
    Extrair os textos de páginas PDF e retornar um objeto dict[str, ColumnBody]
    """
    if not isinstance(document, cs.DocumentPdf):
        raise TypeError(f'file_pdf dev ser DocumentPdf() não {type(document)}')
    if apply_ocr:
        conv = cs.ConvertPdfToImages.create(document)
        conv.set_pbar(pbar)
        images: list[cs.ImageObject] = conv.to_images(dpi=dpi)
        document: cs.DocumentPdf = recognize_images(images, recognize=recognize, pbar=pbar)
    return document.to_dict()


def read_file_pdf(
            file_pdf: sp.File,
            apply_ocr: bool = False,
            recognize: Ocr = Ocr(),
            pbar: sp.ProgressBarAdapter = sp.ProgressBarAdapter(),
            dpi: int = 200
        ) -> cs.DictTextTable:
    """
    Extrair os textos de páginas PDF e retornar um objeto cs.TextTable()
    """
    if not isinstance(file_pdf, sp.File):
        raise TypeError(f'file_pdf dev ser File() não {type(file_pdf)}')
    tb = read_document_pdf(
        cs.DocumentPdf(file_pdf),
        file_pdf.absolute(),
        recognize=recognize,
        pbar=pbar,
        apply_ocr=apply_ocr,
        dpi=dpi,
    )
    return tb


def read_directory_pdf(
            directory: sp.Directory, *,
            apply_ocr: bool = False,
            recognize: Ocr = Ocr(),
            pbar: sp.ProgressBarAdapter = sp.ProgressBarAdapter(),
        ) -> list[cs.DictTextTable]:
    #
    files: list[sp.File] = sp.InputFiles(directory).get_files(file_type=sp.LibraryDocs.PDF)
    _text_maps: list[cs.DictTextTable] = []
    for f_pdf in files:
        _current_maps: cs.DictTextTable = read_file_pdf(
            f_pdf, apply_ocr=apply_ocr, recognize=recognize, pbar=pbar
        )
        _text_maps.append(_current_maps)
    return _text_maps


__all__ = [
    'Ocr', 'read_image', 'read_images', 'read_directory_image',
    'read_document_pdf', 'read_file_pdf', 'read_directory_pdf',
    'create_table_from_dict', 'create_tb_from_names'
]
