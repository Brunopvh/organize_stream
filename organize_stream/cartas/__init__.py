from __future__ import annotations
from abc import ABC, abstractmethod
import convert_stream as cs
import pandas as pd
import shutil
import soup_files as sp
from organize_stream.erros import TableFileEmptyError
from organize_stream.find import list_bad_chars, remove_bad_chars
from sheet_stream.type_utils import concat_table_documents
from sheet_stream import (
    ListItems, ListString, ArrayString, ListColumnBody, TableDocuments, 
    ColumnsTable, clean_string
)


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


class CartaCalculo(Carta):

    def __init__(self, tb: TableDocuments):
        super().__init__(tb)
        self._uniq_key_words = ArrayString(
            ['UC', 'TOI', 'POSTAGEM', 'DESTINA', 'LIVRO']
        )

        self.localidades: dict[str, str] = {
            'NOVA MA': 'NOVA MAMORE',
            'MAMORE': 'NOVA MAMORE',
            'GUAJAR': 'GUAJARA MIRIM',
            'GUAJ': 'GUAJARA MIRIM',
            'VISTA': 'VISTA ALEGRE',
            'EXTREM': 'EXTREMA',
        }

    @property
    def cidade(self) -> str | None:
        lines: ListColumnBody = self.lines
        _loc = None
        for k in self.localidades.keys():
            out = lines.find_text(k)
            if out is not None:
                _loc = self.localidades[k]
                break
        if _loc is None:
            if lines.contains('LOCA'):
                arr = ArrayString([])
                for line in lines:
                    if ' ' in line:
                        arr.extend(line.split(' '))
                    else:
                        arr.add_item(line)
                _loc = arr.get_next_all('LOCA')
                _loc = ' '.join(_loc)
                if len(_loc) > 10:
                    _loc = _loc[:10]

        if _loc is None:
            return None
        return remove_bad_chars(_loc).upper()

    @property
    def medidor(self) -> str:
        lines = self.lines
        out: str | None = lines.find_text('MEDI')
        if out is None:
            return 'nan'
        if not ' ' in out:
            return remove_bad_chars(out)
        arr = ArrayString(out.split(' '))
        return remove_bad_chars(' '.join(arr.get_next_all('MEDI'))).upper()

    def get_line_key(self) -> str | None:
        _check = ['UC', 'TOI', 'TOL']
        _key_word = 'CAR'
        lines = self.lines
        elements = ArrayString([])
        list_idx: list[int] = []
        for item in _check:
            i = lines.find_index(item, case=False, iqual=False)
            if i is not None:
                if not i in list_idx:
                    list_idx.append(i)
        for idx in list_idx:
            elements.append(lines[idx])

        if elements.length == 0:
            return None
        return ' '.join(elements)

    def get_lines_keys(self) -> ArrayString:
        lines = self.lines
        content: ArrayString = ArrayString([])
        for k in self.uniq_key_words:
            values = lines.find_text(k)
            if values is not None:
                elements = ArrayString(values.split(' '))
                uniq_value = elements.get_next_string(k)
                if uniq_value is not None:
                    content.append(f'{remove_bad_chars(uniq_value)}')
        content.append(self.cidade)
        content.append(self.medidor)
        return content


def move_cartas(cartas: list[Carta], output_dir: sp.Directory):
    output_dir.mkdir()
    for carta in cartas:
        try:
            src_file: sp.File = carta.file_path_origin
            if src_file is None:
                continue
            if not src_file.exists():
                continue
            output_file_name = carta.get_line_key()
            if output_file_name is None:
                continue
            if carta.extension_file is None:
                continue
            output_file_name = f'{output_file_name}{carta.extension_file}'
        except Exception as err:
            print(err)
        else:
            dest_file = output_dir.join_file(output_file_name)
            if not isinstance(dest_file, sp.File):
                continue
            if dest_file.exists():
                continue
            try:
                print(f'Movendo: {dest_file.absolute()}')
                shutil.move(src_file.absolute(), dest_file.absolute())
            except Exception as e:
                print(e)


