#!/usr/bin/env python3
#from __future__ import annotations
from organize_stream.read import read_file_pdf, read_image
from organize_stream.document.observer import NotifyProvider
import soup_files as sp
import convert_stream as cs
import ocr_stream as ocr
import pandas as pd


class DocumentTextExtract(NotifyProvider):
    """
        Extrair texto de arquivos, e converter em Excel/DataFrame
    """

    def __init__(self, recoginze: ocr.RecognizePdf = ocr.RecognizePdf()):
        super().__init__()
        self.tb_list: list[cs.DictTextTable] = []
        self.recognize: ocr.RecognizePdf = recoginze
        self.threshold: bool = True
        self._count: int = 0

    @property
    def pbar(self) -> sp.ProgressBarAdapter:
        return self.recognize.pbar

    @pbar.setter
    def pbar(self, pbar: sp.ProgressBarAdapter) -> None:
        self.recognize.set_pbar(pbar)

    @property
    def is_empty(self) -> bool:
        return len(self.tb_list) == 0

    def add_table(self, tb: cs.DictTextTable) -> None:
        self.tb_list.append(tb)
        self._count += 1
        self.pbar.update_text(f'{__class__.__name__} Tabela adicionada: {self._count}')
        self.send_notify(tb)

    def add_directory_pdf(
            self,
            dir_pdf: sp.Directory, *,
            apply_ocr: bool = False,
            dpi: int = 200
    ):
        files = sp.InputFiles(dir_pdf).get_files(file_type=sp.LibraryDocs.PDF)
        total = len(files)
        for n, f in enumerate(files):
            self.pbar.update(
                ((n + 1) / total) * 100,
                f'{n + 1}/{total} {f.basename()}',
            )
            tb = read_file_pdf(f, apply_ocr=apply_ocr, pbar=self.pbar, dpi=dpi)
            self.add_table(tb)

    def add_directory_image(self, dir_image: sp.Directory):
        files_images = sp.InputFiles(dir_image).get_files(file_type=sp.LibraryDocs.IMAGE)
        total = len(files_images)
        for idx, f in enumerate(files_images):
            self.pbar.update(
                ((idx + 1) / total) * 100,
                f'{idx + 1}/{total} {f.basename()}',
            )
            # self.add_table(read_image(f))
            img = cs.ImageObject(f)
            if self.threshold:
                img.set_threshold_gray()
            self.add_table(read_image(img))

    def add_file_pdf(self, file_pdf: sp.File, apply_ocr: bool = False):
        tb = read_file_pdf(file_pdf, pbar=self.pbar, apply_ocr=apply_ocr)
        self.add_table(tb)

    def add_file_image(self, file_image: sp.File):
        tb: cs.DictTextTable = read_image(file_image)
        self.add_table(tb)

    def add_image(self, image: cs.ImageObject):
        if not isinstance(image, cs.ImageObject):
            raise TypeError('Image must be an cs.ImageObject')
        self.add_table(read_image(image))

    def add_document(
            self, document:
            cs.DocumentPdf, *,
            apply_ocr: bool = False,
            dpi: int = 200,
    ):

        if apply_ocr:
            pages: list[cs.PageDocumentPdf] = []
            _metadata = document.metadata
            converter = cs.ConvertPdfToImages(document)
            converter.set_pbar(self.pbar)
            imgs = converter.to_images(dpi=dpi)
            total = len(imgs)
            for n, im in enumerate(imgs):
                self.pbar.update(
                    ((n + 1) / total) * 100,
                    f'[OCR PDF] página {n + 1}/{total}'
                )

                if self.threshold:
                    im.set_threshold_gray()
                txt = self.recognize.recognize_image.image_recognize(im)
                pages.append(txt.to_page_pdf())
            print()
            document = cs.DocumentPdf.create_from_pages(pages)
            document.metadata = _metadata
        tb = document.to_dict()
        self.add_table(tb)

    def to_data(self) -> pd.DataFrame:
        if len(self.tb_list) == 0:
            return cs.DictTextTable.create_void_df()
        _data: list[pd.DataFrame] = []
        for m in self.tb_list:
            _data.append(pd.DataFrame.from_dict(m))
        return pd.concat(_data).astype('str')

    def to_excel(self, file: sp.File) -> None:
        self.to_data().to_excel(file.absolute(), index=False)

