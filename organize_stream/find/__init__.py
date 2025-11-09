#!/usr/bin/env python3
from __future__ import annotations
import pandas as pd
import soup_files as sp
import convert_stream as cs


list_bad_chars: list[str] = [
    '.', '!', ':', '?', '(', ')', '{', '}',
    '+', '#', '@', '<', '>', '/', '¢', ':',
    ',', '®', '“', "“", ';', '‘', '|', '\\',
    '¥', '&', '"', '£'
]
_remove_end_name: list[str] = ['-']
_remove_start_name: list[str] = ['-']


def remove_bad_chars(text: str) -> str:
    for c in list_bad_chars:
        text = text.replace(c, '')
    return text


def fmt_str_file(
            filename: str, *,
            max_char: int = 80,
            upper_case: bool = True
        ) -> str:
    for c in list_bad_chars:
        filename = filename.replace(c, '')
    for c in _remove_end_name:
        if filename[-1] == c:
            filename = filename[:-1]
    for c in _remove_start_name:
        while c in filename[0]:
            filename = filename[1:]
    while '--' in filename:
        filename = filename.replace('--', '-')
    if upper_case:
        filename = filename.upper()
    if len(filename) <= max_char:
        return filename
    return filename[0:max_char]


class OriginFileName(sp.File):

    def __init__(self, filename: str):
        super().__init__(filename)


class DestFileName(sp.File):

    def __init__(self, filename: str):
        super().__init__(filename)


class FilterText(object):
    """
        Padrão de informações a serem filtradas em um documento.
    """
    def __init__(
                self,
                find_txt: str,
                out_dir: sp.Directory, *,
                separator: str = ' ',
                case: bool = False,
                iqual: bool = False,
                key_filter: str = None,
            ):
        self.find_txt: str = find_txt
        self.out_dir: sp.Directory = out_dir
        self.case: bool = case
        self.iqual: bool = iqual
        self.separator: str = separator
        self.key_filter: str = key_filter


class FilterData(FilterText):

    def __init__(
                self,
                src_df: pd.DataFrame, *,
                out_dir: sp.Directory,
                col_find: str,
                col_new_name: str,
                cols_in_name: list[str],
                find_txt: str = 'nan',
                separator: str = ' ',
                case: bool = False,
                iqual: bool = False,
                key_filter: str = None
            ):
        super().__init__(
                find_txt,
                out_dir,
                separator=separator,
                case=case,
                iqual=iqual,
                key_filter=key_filter
            )
        self.col_find: str = col_find
        self.col_new_name: str = col_new_name
        self.cols_in_name: list[str] = cols_in_name
        self.src_df: pd.DataFrame = src_df.astype('str')


class SearchableText(object):

    default_elements: cs.DictTextTable = cs.DictTextTable.create_void_dict()
    default_columns: cs.HeadValues = cs.HeadValues([cs.HeadCell(x) for x in list(default_elements.keys())])

    def __init__(self):
        self.elements: cs.DictTextTable = cs.DictTextTable.create_void_dict()

    def __repr__(self):
        return f'SearchableText\nHead: {self.head}\nBody: {self.body}'

    def is_empty(self) -> bool:
        return len(self.elements[cs.HeadCell(cs.ColumnsTable.TEXT.value)]) == 0

    @property
    def head(self) -> cs.HeadValues:
        return cs.HeadValues([cs.HeadCell(x) for x in list(self.elements.keys())])

    @property
    def body(self) -> list[cs.ColumnBody]:
        return [cs.ColumnBody(cs.HeadCell(_k), self.elements[_k]) for _k in self.elements.keys()]

    @property
    def first(self) -> dict[str, str]:
        if self.is_empty():
            return {}
        cols: cs.HeadValues = self.head
        _first = {}
        for col in cols:
            _first[col] = self.elements[col][0]
        return _first

    @property
    def last(self) -> dict[str, str]:
        if self.is_empty():
            return {}
        cols = self.head
        _last = {}
        for col in cols:
            _last[col] = self.elements[col][-1]
        return _last

    @property
    def length(self) -> int:
        return len(self.elements[cs.HeadCell(cs.ColumnsTable.TEXT.value)])

    @property
    def files(self) -> cs.ColumnBody:
        return self.elements[cs.HeadCell(cs.ColumnsTable.FILE_PATH.value)]

    def get_item(self, idx: int) -> dict[str, str]:
        cols: cs.HeadValues = self.head
        try:
            _item = {}
            for col in cols:
                _item[col] = self.elements[col][idx]
            return _item
        except Exception as err:
            print(err)
            return {}

    def get_column(self, name: str) -> cs.ColumnBody:
        return self.elements[cs.HeadCell(name)]

    def add_line(self, line: dict[str, str]) -> None:
        cols_in_line: cs.HeadValues = cs.HeadValues([cs.HeadCell(x) for x in list(line.keys())])
        cols_in_searchable: cs.HeadValues = self.head
        for col in cols_in_searchable:
            if cols_in_line.contains(col, case=True, iqual=True):
                self.elements[col].append(line[col])

    def clear(self) -> None:
        for _k in self.elements.keys():
            self.elements[_k].clear()

    def to_string(self) -> str:
        """
            Retorna o texto da coluna TEXT em formato de string
        ou 'nas' em caso de erro nas = Not a String
        """
        try:
            return ' '.join(self.elements[cs.HeadCell(cs.ColumnsTable.TEXT.value)])
        except Exception as e:
            print(e)
            return 'nan'

    def to_data_frame(self) -> pd.DataFrame:
        return pd.DataFrame.from_dict(self.elements)

    def to_file_json(self, file: sp.File):
        """Exporta os dados da busca para arquivo .JSON"""
        dt = sp.JsonConvert.from_dict(self.elements).to_json_data()
        dt.to_file(file)

    def to_file_excel(self, file: sp.File):
        """Exporta os dados da busca para arquivo .XLSX"""
        self.to_data_frame().to_excel(file.absolute(), index=False)

    @classmethod
    def create(cls, df: pd.DataFrame) -> SearchableText:
        cols: list[str] = df.columns.tolist()
        _values: list[cs.ColumnBody] = []
        for col in cols:
            _values.append(
                cs.ColumnBody(
                    col, cs.ListString(df[col].astype('str').values.tolist())
                )
            )
        s = cls()
        s.elements = cs.DictTextTable(_values)
        return s


class NameFinder(object):
    """
    Recebe o texto bruto de documentos, e filtra texto baseado em padrões.
    """

    def __init__(self, filter_text: FilterText):
        self.filter_data: FilterText = filter_text
        # Coluna que contem o texto usado como filtro em cada linha da busca
        self._col_name_filter: str = cs.HeadCell('FILTRO')
        # Coluna que contem o texto de filtro adicional
        self._col_include_filter: str = cs.HeadCell('FILTRO ADICIONAL')

    def get_new_name(
                self,
                tb: cs.DictTextTable, *,
                max_char: int = 90,
                upper_case: bool = True,
            ) -> dict[OriginFileName, DestFileName]:
        pass


class NameFinderInnerText(NameFinder):

    def __init__(self, filter_text: FilterText):
        super().__init__(filter_text)

    def get_new_name(
                self,
                tb: cs.DictTextTable, *,
                max_char: int = 90,
                upper_case: bool = True,
            ) -> dict[OriginFileName, DestFileName]:
        new_dest_names: list[str] = []
        tb_txt_file: pd.DataFrame = pd.DataFrame.from_dict(tb)
        df = tb_txt_file[[cs.ColumnsTable.TEXT.value, cs.ColumnsTable.FILE_PATH.value]].astype('str')

        # Divide padrões múltiplos separados por "|"
        patterns = [p.strip() for p in self.filter_data.find_txt.split('|') if p.strip()]
        if not patterns:
            print(f'{__class__.__name__}: Nenhum padrão de busca válido informado.')
            return {}

        # Define padrão regex dependendo de "iqual"
        if self.filter_data.iqual:
            regex_pattern = '^(' + '|'.join(patterns) + ')$'
        else:
            regex_pattern = '(' + '|'.join(patterns) + ')'

        # Filtra linhas no DataFrame
        mask: pd.Series = df[cs.ColumnsTable.TEXT.value].str.contains(
            regex_pattern,
            case=self.filter_data.case,
            regex=True,
            na=False
        )
        matched_df = df[mask]
        total_matches = len(matched_df)

        if total_matches == 0:
            return {}

        # Para cada linha encontrada, gera nome limpo e adiciona à lista de movimentação
        src_file: sp.File = sp.File(tb[cs.ColumnsTable.FILE_PATH.value][0])
        src_extension: str = tb[cs.ColumnsTable.FILETYPE.value][0]
        for _, row in matched_df.iterrows():
            current_line: str = row[cs.ColumnsTable.TEXT.value]
            if self.filter_data.key_filter is not None:
                if not self.filter_data.key_filter.upper() in current_line.upper():
                    continue
            # Usa o texto da linha como base do novo nome
            new_file_name: str = fmt_str_file(current_line.strip())
            # Garante que o nome não fique vazio
            if not new_file_name:
                new_file_name = src_file.name()
            new_dest_names.append(f"{new_file_name}{src_extension}")

        if len(new_dest_names) == 0:
            return {}
        output_name: str = ' '.join(new_dest_names)
        if len(output_name) > max_char:
            output_name = output_name[:max_char]
        _origin = OriginFileName(src_file.absolute())
        _dest = DestFileName(self.filter_data.out_dir.join_file(output_name).absolute())
        return {_origin: _dest}


class NameFinderInnerData(NameFinder):
    def __init__(self, filter_text: FilterData):
        super().__init__(filter_text)
        self.filter_data: FilterData = filter_text

    def get_new_name(
                self,
                tb: cs.DictTextTable, *,
                max_char: int = 90,
                upper_case: bool = True,
            ) -> dict[OriginFileName, DestFileName]:
        # Lista de valores da coluna texto.
        list_values_find: list[str] = self.filter_data.src_df[self.filter_data.col_find].astype('str').values.tolist()
        # Lista de valores da coluna com novos nomes de arquivo.
        new_names: list[str] = self.filter_data.src_df[self.filter_data.col_new_name].astype('str').values.tolist()
        # Lista de valores com as linhas de texto do arquivo em formato list[str].
        lines_doc: cs.ArrayString = cs.ArrayString(tb[cs.ColumnsTable.TEXT.value])
        # Lista das colunas/texto a serem acrescentados no nome do novo arquivo.
        cols_include_names: list[list[str]] = []

        if len(self.filter_data.cols_in_name) > 0:
            for c in self.filter_data.cols_in_name:
                values_include: list[str] = self.filter_data.src_df[c].astype('str').values.tolist()
                cols_include_names.append(values_include)

        line_df: str
        idx_df: int
        output_name: str = None
        for idx_df, line_df in enumerate(list_values_find):
            if not lines_doc.contains(line_df, case=False):
                continue

            output_name = new_names[idx_df]
            if len(self.filter_data.cols_in_name) > 0:
                include_strings = ''
                element: list[str]
                for element in cols_include_names:
                    include_strings = f'{include_strings}-{element[idx_df]}'
                output_name = f'{output_name}-{include_strings}'
            output_name: str = fmt_str_file(output_name, max_char=max_char, upper_case=upper_case)
            break

        if output_name is None:
            return {}
        if len(output_name) > max_char:
            output_name = output_name[:max_char]
        output_name = f'{output_name}{tb[cs.ColumnsTable.FILETYPE.value][0]}'
        _dest = DestFileName(self.filter_data.out_dir.join_file(output_name).absolute())
        _origin = OriginFileName(tb[cs.ColumnsTable.FILE_PATH.value][0])
        print(f'{__class__.__name__} ocorrência encontrada: {output_name}')
        return {_origin: _dest}
