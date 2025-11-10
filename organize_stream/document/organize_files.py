#!/usr/bin/env python3
from __future__ import annotations
from typing import Union
from organize_stream.type_utils import (
    FilterText, FilterData, DigitalizedDocument, LibDigitalized, Observer
)
from organize_stream.find import (
    NameFinderInnerText, NameFinderInnerData, OriginFileName, DestFileName
)
from organize_stream.read import create_tb_from_names
from organize_stream.text_extract import DocumentTextExtract
from organize_stream.cartas import CartaCalculo, GenericDocument, FichaEpi
from organize_stream.erros import InvalidTDigitalizedDocument
from sheet_stream import TableDocuments, ColumnsTable
import soup_files as sp
import convert_stream as cs
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


class Organize(Observer):

    def __init__(self, output_dir: sp.Directory, *, filters: FilterText = None):
        super().__init__()
        self._count: int = 0
        self.output_dir: sp.Directory = output_dir
        self.extractor: DocumentTextExtract = DocumentTextExtract()
        self.extractor.add_observer(self)
        self.extractor.threshold = False
        self.pbar: sp.ProgressBarAdapter = sp.ProgressBarAdapter()
        self.max_char: int = 90
        self.upper_case: bool = True
        self.save_tables: bool = True
        self.filters: FilterText = filters

    @property
    def output_dir_tables(self) -> sp.Directory:
        return self.output_dir.concat('Tabelas', create=True)

    def _show_error(self, txt: str):
        print()
        self.pbar.update_text(f'{__class__.__name__} {txt}')

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


class OrganizeInnerText(Organize):
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


class OrganizeInnerData(Organize):
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
