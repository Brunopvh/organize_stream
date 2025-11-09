from __future__ import annotations
from abc import ABC, abstractmethod
from organize_stream.erros import TableFileEmptyError
from sheet_stream import (
    TableDocuments, ArrayString, ColumnsTable,
    ListColumnBody
)
import soup_files as sp


class Carta(ABC):

    def __init__(self, tb: TableDocuments):
        self.tb: TableDocuments = tb
        if self.tb.length == 0:
            raise TableFileEmptyError('A tabela de arquivos não pode estar vazia!')
        self._uniq_key_words = ArrayString([])

    @property
    def uniq_key_words(self) -> ArrayString:
        return self._uniq_key_words

    @property
    def file_path_origin(self) -> sp.File | None:
        value: ListColumnBody = self.tb.get_column(ColumnsTable.FILE_PATH)
        if value.is_empty:
            return None
        if (value[0] == '') or (value[0] == 'nan') or (value[0] == 'None') \
                or (value[0] == '-') or (value[0] == 'NaT'):
            return None
        try:
            file_path = sp.File(value[0])
        except Exception as e:
            print(e)
            return None
        else:
            if file_path.path.exists():
                return file_path
            return None

    @property
    def dir_path_origin(self) -> sp.Directory | None:
        value: ListColumnBody = self.tb.get_column(ColumnsTable.DIR)
        if value.is_empty:
            return None
        if (value[0] == '') or (value[0] == 'nan') or (value[0] == 'None') \
                or (value[0] == '-') or (value[0] == 'NaT'):
            return None
        try:
            _dir_path = sp.Directory(value[0])
        except Exception as e:
            print(e)
            return None
        else:
            if _dir_path.path.exists():
                return _dir_path
            return None

    @property
    def extension_file(self) -> str | None:
        value: ListColumnBody = self.tb.get_column(ColumnsTable.FILETYPE)
        if value.is_empty:
            return None
        if (value[0] == '') or (value[0] == 'nan') or (value[0] == 'None') \
                or (value[0] == '-') or (value[0] == 'NaT'):
            return None
        return value[0]

    @property
    def lines(self) -> ListColumnBody:
        return self.tb.get_column(ColumnsTable.TEXT)

    def __repr__(self):
        return f'Carta: {self.get_lines_keys()}'

    @abstractmethod
    def get_line_key(self) -> str:
        pass

    @abstractmethod
    def get_lines_keys(self) -> ArrayString:
        pass

    def to_excel(self, file: sp.File):
        self.tb.to_data().to_excel(file.absolute())

    def to_file_text(self, file: sp.File):
        lines = self.lines
        print(f'Exportando: {file.absolute()}')
        with open(file.absolute(), 'w', encoding='utf-8') as f:
            f.writelines(lines)
