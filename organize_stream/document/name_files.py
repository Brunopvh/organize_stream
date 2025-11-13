#!/usr/bin/env python3
from __future__ import annotations
import tempfile
from typing import Callable, Union
from io import BytesIO
from typing import Union
from organize_stream.type_utils import (
    FilterText, FilterData, DigitalizedDocument, LibDigitalized, Observer,
    NotifyProvider, KeyFiles, KeyWordsFileName, DiskFile, DynamicFile,
    Table as TableDocuments
)
from organize_stream.find import (
    NameFinderInnerText, NameFinderInnerData, OriginFileName, DestFileName
)
from organize_stream.utils import (sp, cs)
from organize_stream.read import create_tb_from_names
from organize_stream.text_extract import DocumentTextExtract
from organize_stream.cartas import CartaCalculo, GenericDocument, FichaEpi
from organize_stream.erros import InvalidTDigitalizedDocument, InvalidSrcFile
from sheet_stream import ColumnsTable
from sheet_stream.type_utils import get_hash_from_bytes
import shutil

FindItem = Union[str, list[str]]


def move_list_files(
        mv_items: dict[str, list[sp.File]], *,
        replace: bool = False
) -> None:
    total_file = len(mv_items['src'])
    for idx, file in enumerate(mv_items['src']):
        output_path: sp.File = mv_items['dest'][idx]
        if not file.exists():
            print(f'[PULANDO]: {idx + 1} Arquivo não encontrado {file.absolute()}')
        if output_path.exists():
            if not replace:
                _count = 0
                origin_name = output_path.name_absolute()
                origin_ext = output_path.extension()
                while output_path.exists():
                    _count += 1
                    new_name = f'{origin_name}-{_count}{origin_ext}'
                    output_path = sp.File(new_name)
                del origin_name
                del origin_ext
        print(f'Movendo: {idx + 1}/{total_file} {file.absolute()}')
        try:
            shutil.move(file.absolute(), output_path.absolute())
        except Exception as e:
            print(f'{e}')
        del output_path


def move_path_files(
        mv_items: dict[OriginFileName, DestFileName], *,
        replace: bool = False
) -> None:
    for _k in mv_items:
        output_path = mv_items[_k]
        if not _k.exists():
            print(f'[PULANDO O ARQUIVO NÃO EXISTE]: {_k.basename()}')
        if not replace:
            _count = 0
            origin_name: str = output_path.name_absolute()
            origin_ext = output_path.extension()
            while output_path.exists():
                _count += 1
                new_output_name: str = f'{origin_name}-{_count}{origin_ext}'
                output_path = sp.File(new_output_name)
            del origin_name
            del origin_ext
        try:
            shutil.move(_k.absolute(), output_path.absolute())
        except Exception as e:
            print(e)


def save_key_word_filename(key_word_file: KeyWordsFileName, out_dir: sp.Directory) -> tuple[str, bool]:
    if key_word_file.input_dynamic_file is None:
        raise InvalidSrcFile()

    _id_file: str = None
    if key_word_file.input_dynamic_file.is_bytes_io or key_word_file.input_dynamic_file.is_bytes:
        _id_file = get_hash_from_bytes(key_word_file.input_dynamic_file.file)
    elif key_word_file.input_dynamic_file.is_file:
        _id_file = key_word_file.input_dynamic_file.file
    elif key_word_file.input_dynamic_file.is_file_path:
        _id_file = key_word_file.input_dynamic_file.file.absolute()
    else:
        raise InvalidSrcFile()

    if key_word_file.output_filename is None:
        return (_id_file, False)
    if key_word_file.extension_file is None:
        return (_id_file, False)

    out_dir.mkdir()
    output_path: sp.File = out_dir.join_file(f'{key_word_file.output_filename}{key_word_file.extension_file}')
    print(f'Exportando: {output_path.basename()}')

    if key_word_file.input_dynamic_file.is_bytes:
        # Salvar os bytes no disco.
        with open(output_path.absolute(), 'wb') as fp:
            fp.write(key_word_file.input_dynamic_file.file)
    elif key_word_file.input_dynamic_file.is_bytes_io:
        # Salvar BytesIO() no disco
        key_word_file.input_dynamic_file.file.seek(0)
        with open(output_path.absolute(), 'wb') as fp:
            fp.write(key_word_file.input_dynamic_file.file.getvalue())
    elif key_word_file.input_dynamic_file.is_file:
        # Mover o arquivo no disco.
        try:
            shutil.move(key_word_file.input_dynamic_file.file, output_path.absolute())
        except Exception as e:
            print(e)
            return (_id_file, False)
    elif key_word_file.input_dynamic_file.is_file_path:
        # Mover o arquivo no disco.
        try:
            shutil.move(key_word_file.input_dynamic_file.file.absolute(), output_path.absolute())
        except Exception as e:
            print(e)
            return (_id_file, False)
    return (_id_file, True)


class NameFileInnerTable(object):

    def __init__(
                self,
                extractor: DocumentTextExtract = DocumentTextExtract(), *,
                lib_digitalized: LibDigitalized = LibDigitalized.GENERIC,
                filters: FilterText = None,
                func_save_file: Callable[[KeyWordsFileName, sp.Directory], tuple[str, bool]] = None,
            ):
        super().__init__()
        if func_save_file is None:
            self.func_save_file = save_key_word_filename
        else:
            self.func_save_file = func_save_file
        self.lib_digitalized: LibDigitalized = lib_digitalized
        self.extractor: DocumentTextExtract = extractor
        self.filters = filters
        self.__exported_files: dict[str, bool] = {}
        self.__temp_dir: sp.Directory = sp.Directory(tempfile.mkdtemp())

    def clear(self):
        self.__exported_files.clear()

    def get_exported_files(self) -> dict[str, bool]:
        return self.__exported_files

    def read_image(self, file: DiskFile | cs.ImageObject) -> KeyWordsFileName:
        __dynamic = DynamicFile(file)
        __kw = self.__get_new_name(self.extractor.read_image(file))
        if __kw.extension_file is None:
            __kw.extension_file = '.png'
        __kw.input_dynamic_file = __dynamic
        return __kw

    def read_document(self, file: DiskFile | cs.DocumentPdf, *, dpi: int = 200) -> KeyWordsFileName:
        __dynamic = DynamicFile(file)
        __tb = self.extractor.read_document(file, dpi=dpi)
        __kw = self.__get_new_name(__tb)
        __kw.input_dynamic_file = __dynamic
        if __kw.extension_file is None:
            __kw.extension_file = '.pdf'
        return __kw

    def __get_new_name(self, tb: TableDocuments) -> KeyWordsFileName:
        key_words = KeyWordsFileName()
        _doc: DigitalizedDocument
        if self.lib_digitalized == LibDigitalized.GENERIC:
            _doc = GenericDocument(tb, filters=self.filters)
        elif self.lib_digitalized == LibDigitalized.CARTA_CALCULO:
            _doc = CartaCalculo.create(tb)
        elif self.lib_digitalized == LibDigitalized.EPI:
            _doc = FichaEpi.create(tb)
        else:
            raise InvalidTDigitalizedDocument(f'{__class__.__name__} Documento inválido: {self.lib_digitalized}')

        filename = _doc.get_output_filename()
        if (filename == 'nan') or (filename == ''):
            key_words.output_filename = None
        else:
            key_words.output_filename = filename

        if (key_words.extension_file == 'nan') or (key_words.extension_file == ''):
            key_words.extension_file = None
        else:
            key_words.extension_file = _doc.extension_file
        return key_words

    def __save_file(self, key_word_file: KeyWordsFileName, out_dir: sp.Directory) -> tuple[str, bool]:
        _status: tuple[str, bool] = self.func_save_file(key_word_file, out_dir)
        self.__exported_files[_status[0]] = _status[1]
        return _status

    def rename_image(self, image: DiskFile | cs.ImageObject, output_dir: sp.Directory):
        """
        Extrai o texto de uma imagem e renomeia conforme o padrão do documento informado nesse objeto.
        """
        __kw_im = self.read_image(image)
        self.__save_file(__kw_im, output_dir)

    def rename_document(
                self,
                document: DiskFile | cs.DocumentPdf,
                output_dir: sp.Directory, *,
                dpi: int = 200
            ) -> None:
        """
        Extrai o texto de um PDF e renomeia conforme o padrão do documento informado nesse objeto.
        """
        __kw_pdf = self.read_document(document, dpi=dpi)
        self.__save_file(__kw_pdf, output_dir)

    def documents_to_zip(
                self,
                documents: list[DiskFile] | list[cs.DocumentPdf],
                output_dir: sp.Directory, *,
                dpi: int = 200
            ) -> BytesIO:
        pass

    def images_to_zip(
                self,
                images: list[cs.ImageObject] | list[DiskFile],
                output_dir: sp.Directory
            ) -> BytesIO:
        try:
            shutil.rmtree(self.__temp_dir.absolute())
        except Exception as e:
            print(e)
        self.__temp_dir.mkdir()
        for img in images:
            key_file = self.read_image(img)


class ExtractName(Observer):

    def __init__(self, output_dir: sp.Directory, *, filters: FilterText = None):
        super().__init__()
        self._count: int = 0
        self.output_dir: sp.Directory = output_dir
        self.pbar: sp.ProgressBarAdapter = sp.ProgressBarAdapter()
        self.max_char: int = 90
        self.upper_case: bool = True
        self.save_tables: bool = True
        self.filters: FilterText = filters
        self.extractor: DocumentTextExtract = DocumentTextExtract()
        self.extractor.add_observer(self)
        self.extractor.threshold = False

    @property
    def output_dir_tables(self) -> sp.Directory:
        return self.output_dir.concat('Tabelas', create=True)

    def _show_error(self, txt: str):
        print()
        self.pbar.update_text(f'{__class__.__name__} {txt}')

    def add_table(self, tb: TableDocuments):
        pass

    def add_image(self, image: cs.ImageObject | sp.File):
        if isinstance(image, sp.File):
            self.extractor.add_file_image(image)
        elif isinstance(image, cs.ImageObject):
            self.extractor.add_image(image)
        else:
            self._show_error(f'Image must be an cs.ImageObject | sp.File')

    def add_images(self, images: list[cs.ImageObject] | list[sp.File]):
        total = len(images)
        for n, image in enumerate(images):
            if isinstance(image, sp.File):
                image = cs.ImageObject(image)
            self.pbar.update(
                ((n + 1) / total) * 100,
                f'[ADICIONANDO IMAGEM] {n + 1}/{total} {image.metadata.name}'
            )
            print()
            self.add_image(image)
        self.export_final_table()

    def add_document(
                self,
                document: cs.DocumentPdf, *,
                apply_ocr: bool = True,
                dpi: int = 200
            ):
        self.extractor.add_document(document, apply_ocr=apply_ocr, dpi=dpi)

    def add_dir_pdf(
                self,
                path: sp.Directory, *,
                apply_ocr: bool = True,
                dpi: int = 200
            ):
        self.extractor.add_directory_pdf(path, apply_ocr=apply_ocr, dpi=dpi)
        self.export_final_table()

    def add_dir_image(self, path: sp.Directory):
        self.extractor.add_directory_image(path)
        self.export_final_table()

    def export_tables(self, tb: TableDocuments) -> None:
        if not self.save_tables:
            return
        origin_name = tb.get_column(ColumnsTable.FILE_NAME)[0]
        output_path = self.output_dir_tables.join_file(f'{origin_name}.xlsx')
        if isinstance(output_path, sp.File):
            #print(f'DEBUG: Exportando ... {output_path.basename()}')
            tb.to_data().to_excel(output_path.absolute(), index=False)

    def export_final_table(self):
        if not self.save_tables:
            return
        self.extractor.to_excel(self.output_dir_tables.join_file('data.xlsx'))

    def receive_notify(self, notify: TableDocuments) -> None:
        pass

    def move_digitalized_doc(self, tb: TableDocuments) -> None:
        pass


class ExtractNameInnerText(ExtractName):
    """
    Mover/Renomear arquivos de acordo com padrões de texto presentes
    nos documentos/imagens.

    O padrão de texto a ser filtrado deve ser criado no objeto FilterText(). Se desejar
    filtrar mais de uma ocorrência nos documentos/imagens, separe as ocorrências com um '|'

    """

    def __init__(
                self,
                output_dir: sp.Directory, *,
                lib_digitalized: LibDigitalized = LibDigitalized.GENERIC,
                filters: FilterText = None,
            ):
        super().__init__(output_dir, filters=filters)
        self.lib_digitalized: LibDigitalized = lib_digitalized
        self.name_finder: NameFinderInnerText = NameFinderInnerText(self.output_dir)

    def receive_notify(self, notify: TableDocuments) -> None:
        self._count += 1
        self.move_digitalized_doc(notify)
        self.export_tables(notify)

    def add_table(self, tb: TableDocuments):
        self.move_digitalized_doc(tb)
        self.export_tables(tb)

    def move_digitalized_doc(self, tb: TableDocuments) -> None:
        """
        Mover/Renomear arquivos de acordo com padrões de texto presentes
        nos documentos/imagens.
        """
        dg: DigitalizedDocument
        if self.lib_digitalized == LibDigitalized.GENERIC:
            if self.filters is None:
                print(f'DEBUG: {__class__.__name__} Falha ... o filtro está vazio.')
                return
            dg = GenericDocument(tb, filters=self.filters)
        elif self.lib_digitalized == LibDigitalized.CARTA_CALCULO:
            dg = CartaCalculo.create(tb)
        elif self.lib_digitalized == LibDigitalized.EPI:
            dg = FichaEpi.create(tb)
        else:
            raise InvalidTDigitalizedDocument()
        new_names: dict[OriginFileName, DestFileName] = self.name_finder.get_new_name(dg)
        move_path_files(new_names, replace=False)


class ExtractNameInnerData(ExtractName):
    """
        Organizar os arquivos com base nos dados de uma tabela/DataFrame
    """

    def __init__(self, output_dir: sp.Directory, *, filters: FilterData = None):
        super().__init__(output_dir, filters=None)
        self.filter_data: FilterData = filters
        self.name_inner_data: NameFinderInnerData = NameFinderInnerData(self.output_dir, filters=self.filter_data)

    def receive_notify(self, notify: TableDocuments) -> None:
        self._count += 1
        self.move_digitalized_doc(notify)
        self.export_tables(notify)

    def add_table(self, tb: TableDocuments):
        self.move_digitalized_doc(tb)
        self.export_tables(tb)

    def move_digitalized_doc(self, tb: TableDocuments) -> None:
        mv_items = self.name_inner_data.get_new_name(
            GenericDocument(tb, filters=None)
        )
        move_path_files(mv_items, replace=False)

    def move_where_math_filename(self, files: list[sp.File]) -> None:
        """
            Mover arquivos conforme as ocorrências de texto encontradas na tabela/DataFrame df.
        o nome do novo arquivo será igual à ocorrência de texto da coluna 'col_find', podendo
        estender o nome com elementos de outras colunas, tais colunas podem ser informadas (opcionalmente)
        no parâmetro cols_in_name.
            Ex:
        Suponha que a tabela para renomear aquivos tenha a seguinte estrutura:

        A      B        C
        maça   Cidade 1 xxyyy
        banana Cidade 2 yyxxx
        mamão  Cidade 3 xyxyx

        Se passarmos os parâmetros col_find='A' e col_new_name='A' e o texto banana for
        encontrado no(s) documento, o novo nome do arquivo será banana. Caso incluir o parâmetro
        cols_in_name=['B'] o novo nome do arquivo será banana-Cidade 2 ou
        banana-Cidade 2-yyxxx (se incluir cols_in_name=['B', 'C']).

        """
        values: list[TableDocuments] = create_tb_from_names(files)
        for current_tb in values:
            mv_items = self.name_inner_data.get_new_name(
                GenericDocument(current_tb, filters=None)
            )
            move_path_files(mv_items, replace=False)

