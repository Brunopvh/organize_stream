from __future__ import annotations
from collections.abc import Iterable, Iterator
from sheet_stream import TableDocuments, TableRow, ListColumnBody


class IterTable(Iterator):

    def __init__(self, col: Table, iter_table: bool = False):
        self.__idx: int = 0
        self._col: Table = col
        self._iter_table = iter_table

        if self._iter_table:
            self.__max_iter: int = self._col.columns.length
        else:
            self.__max_iter: int = self._col.length

    def __iter__(self) -> IterTable:
        return self

    def __next__(self) -> TableRow | ListColumnBody:
        if self.__idx >= self.__max_iter:
            self.__idx = 0
            raise StopIteration()
        self.__idx += 1
        if self._iter_table:
            _name: str = self._col.columns[self.__idx - 1]
            return self._col.get_column(_name)
        else:
            return self._col.get_row(self.__idx - 1)


class Table(TableDocuments):

    def __init__(self, body_list: list[ListColumnBody]):
        super().__init__(body_list)

    def iter_rows(self) -> Iterable[TableRow]:
        return IterTable(self)

    def iter_tables(self) -> Iterable[ListColumnBody]:
        return IterTable(self, True)

