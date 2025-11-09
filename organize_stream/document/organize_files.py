#!/usr/bin/env python3
from __future__ import annotations
from typing import Union
from organize_stream.find import (
    NameFinderInnerText, NameFinderInnerData, NameFinder, FilterText,
    FilterData, OriginFileName, DestFileName
)
from organize_stream.read import create_tb_from_names
from organize_stream.document.observer import Observer
from organize_stream.document.text_extract import DocumentTextExtract
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

    def __init__(self, filter_text: FilterText):
        super().__init__()
        self._count: int = 0
        self.filter_text: FilterText = filter_text
        self.extractor: DocumentTextExtract = DocumentTextExtract()
        self.extractor.add_observer(self)
        self.extractor.threshold = False
        self.pbar: sp.ProgressBarAdapter = sp.ProgressBarAdapter()
        self.max_char: int = 90
        self.upper_case: bool = True

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
            self.add_image(image)

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

    def add_dir_image(self, path: sp.Directory):
        self.extractor.add_directory_image(path)

    def receive_notify(self, notify: cs.TextTable) -> None:
        pass


class OrganizeInnerText(Organize):
    """
    Mover/Renomear arquivos de acordo com padrões de texto presentes
    nos documentos/imagens.

    O padrão de texto a ser filtrado deve ser criado no objeto FilterText(). Se desejar
    filtrar mais de uma ocorrência nos documentos/imagens, separe as ocorrências com um '|'

    """

    def __init__(self, filter_text: FilterText):
        super().__init__(filter_text)
        self.name_finder: NameFinderInnerText = NameFinderInnerText(self.filter_text)

    def receive_notify(self, notify: cs.DictTextTable) -> None:
        self._count += 1
        self.move_where_contains_text(notify)

    def move_where_contains_text(self, tb: cs.DictTextTable) -> None:
        """
        Mover/Renomear arquivos de acordo com padrões de texto presentes
        nos documentos/imagens.
        """
        new_names: dict[OriginFileName, DestFileName] = self.name_finder.get_new_name(
            tb, max_char=self.max_char, upper_case=self.upper_case
        )
        move_path_files(new_names, replace=False)


class OrganizeInnerData(Organize):
    """
        Organizar os arquivos com base nos dados de uma tabela/DataFrame
    """

    def __init__(self, filter_data: FilterData):
        """
        :param df: DataFrame com os dados de uma tabela/DataFrame, onde cada linha de determinada
        coluna será comparada com os textos presentes nos documentos.

        :param filter_data: FilterData com os nomes das colunas onde será buscado os textos a serem
        filtrados linha a linha.
        """
        super().__init__(filter_data)
        self.filter_data: FilterData = filter_data
        self.name_inner_data: NameFinderInnerData = NameFinderInnerData(self.filter_data)

    def receive_notify(self, notify: cs.DictTextTable) -> None:
        self._count += 1
        self.move_where_math_column(notify)

    def move_where_math_column(self, tb: cs.DictTextTable) -> None:
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
        mv_items = self.name_inner_data.get_new_name(
            tb, max_char=self.max_char, upper_case=self.upper_case
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
        values: list[cs.DictTextTable] = create_tb_from_names(files)
        for current_tb in values:
            mv_items = self.name_inner_data.get_new_name(
                current_tb, max_char=self.max_char, upper_case=self.upper_case
            )
            move_path_files(mv_items, replace=False)
