from __future__ import annotations
import shutil
import soup_files as sp
from organize_stream.type_utils import Carta
from organize_stream.find import fmt_str_file, remove_bad_chars
from sheet_stream import (
    ArrayString, ListColumnBody, TableDocuments,
)


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
    def medidor(self) -> str | None:
        _medidor = self.lines.find_text('MEDI')

        if _medidor is None:
            return None
        arr = ArrayString(_medidor.split(' '))
        arr = arr.get_next_all('MEDI')
        if arr.is_empty:
            return None
        final_medidor = ' '.join(arr)
        if len(final_medidor) > 12:
            final_medidor = final_medidor[:12]
        return remove_bad_chars(final_medidor)

    def get_line_key(self) -> str | None:
        _check = ['UC', 'TOI', 'TOL']
        _key_word = 'CAR'
        lines = self.lines
        filter_list = ArrayString([])
        elements = ArrayString([])
        list_index: list[int] = []

        # Filtrar os indices desejados.
        for txt in _check:
            idx = lines.find_index(txt)
            if idx is not None:
                if not idx in list_index:
                    list_index.append(idx)

        # Gerar nova lista com os valores filtrados.
        for num in list_index:
            if ' ' in lines[num]:
                filter_list.extend(lines[num].split(' '))
            else:
                filter_list.append(lines[num])

        # Gerar a linha final
        for item in _check:
            i = filter_list.get_next_string(item)
            if i is not None:
                elements.append(i)

        if elements.length == 0:
            final_line: str = ''
        else:
            final_line: str = ' '.join(elements)

        # Incluir a cidade
        cidade = self.cidade
        medidor = self.medidor
        if medidor is not None:
            final_line = f'{final_line}-{medidor}'
        if cidade is not None:
            final_line = f'{final_line}-{cidade}'
        return remove_bad_chars(final_line)

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
            output_file_name = fmt_str_file(carta.get_line_key())

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


