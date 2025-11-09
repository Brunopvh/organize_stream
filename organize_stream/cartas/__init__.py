from __future__ import annotations
from abc import ABC, abstractmethod
import convert_stream as cs
import pandas as pd
import shutil
import soup_files as sp
from organize_stream.erros import TableFileEmptyError
from organize_stream.find import list_bad_chars, remove_bad_chars


class Carta(ABC):

    def __init__(self, tb: cs.DictTextTable):
        self.tb: cs.DictTextTable = tb
        if self.tb.length == 0:
            raise TableFileEmptyError('A tabela de arquivos não pode estar vazia!')
        self._uniq_key_words = cs.ArrayString([])

    @property
    def uniq_key_words(self) -> cs.ArrayString:
        return self._uniq_key_words

    @property
    def file(self) -> sp.File:
        return sp.File(self.tb[cs.ColumnsTable.FILE_PATH.value][0])

    @property
    def dir_path(self) -> sp.Directory:
        return sp.Directory(self.tb[cs.ColumnsTable.DIR.value][0])

    @property
    def extension_file(self) -> str:
        return self.tb[cs.ColumnsTable.FILETYPE.value][0]

    @property
    def lines(self) -> cs.ColumnBody:
        return self.tb[cs.ColumnsTable.TEXT.value]

    def __repr__(self):
        return f'Carta: {self.get_lines_keys()}'

    @abstractmethod
    def get_line_key(self) -> str:
        pass

    @abstractmethod
    def get_lines_keys(self) -> cs.ArrayString:
        pass

    def to_excel(self, file: sp.File):
        self.tb.to_data().to_excel(file.absolute(), index=False)

    def to_file_text(self, file: sp.File):
        lines = self.lines
        print(f'Exportando: {file.absolute()}')
        with open(file.absolute(), 'w', encoding='utf-8') as f:
            f.writelines(lines)


class CartaCalculo(Carta):

    def __init__(self, tb: cs.DictTextTable):
        super().__init__(tb)
        self._uniq_key_words = cs.ArrayString(
            ['UC', 'TOI', 'POSTAGEM', 'DESTINA', 'LIVRO']
        )

        self.localidades: dict[str, str] = {
            'NOVA': 'NOVA MAMORE',
            'MAMORE': 'NOVA MAMORE',
            'GUAJARA': 'GUAJARA MIRIM',
            'GUAJ': 'GUAJARA MIRIM',
            'VISTA': 'VISTA ALEGRE',
        }

    @property
    def cidade(self) -> str:
        lines = self.lines
        _loc = 'nan'
        for k in self.localidades.keys():
            out = lines.find_text(k)
            if out is not None:
                _loc = self.localidades[k]
                break
        return remove_bad_chars(_loc).upper()

    @property
    def medidor(self) -> str:
        lines = self.lines
        out: str | None = lines.find_text('MEDI')
        if out is None:
            return 'nan'
        if not ' ' in out:
            return remove_bad_chars(out)
        arr = cs.ArrayString(out.split(' '))
        return remove_bad_chars(' '.join(arr.get_next_all('MEDI'))).upper()

    def get_line_key(self) -> str:
        _check = ['UC', 'TOI', 'TOL']
        _key_word = 'CAR'
        lines = self.lines
        content: cs.ArrayString = cs.ArrayString([])
        content.append(self.cidade)
        for k in _check:
            values: str | None = lines.find_text(k)
            if values is not None:
                elements = cs.ArrayString(values.split(' '))
                if not elements.contains(_key_word, case=False, iqual=False):
                    continue
                uniq_value = elements.get_next_string(k)
                if uniq_value is not None:
                    content.append(f'{remove_bad_chars(uniq_value)}')
        content.append(self.medidor)
        _carta_name = ' '.join(content)
        if len(_carta_name) > 100:
            _carta_name = _carta_name[:100]
        return _carta_name.upper()

    def get_lines_keys(self) -> cs.ArrayString:
        lines = self.lines
        content: cs.ArrayString = cs.ArrayString([])
        for k in self.uniq_key_words:
            values = lines.find_text(k)
            if values is not None:
                elements = cs.ArrayString(values.split(' '))
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
            src_file: sp.File = carta.file
            dest = carta.get_line_key()
            dest = f'{dest}{carta.extension_file}'
        except Exception as err:
            print(err)
        else:
            dest_file = output_dir.join_file(dest)
            if not src_file.exists():
                continue
            if dest_file.exists():
                continue
            try:
                print(f'Movendo: {dest_file.absolute()}')
                shutil.move(src_file.absolute(), dest_file.absolute())
            except Exception as e:
                print(e)


