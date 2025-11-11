"""

"""

from soup_files import *
import pandas as pd
import convert_stream as cs
from sheet_stream import save_data, ReadFileSheet, fmt_col_to_date, LibDate
from organize_stream.type_utils import TextProgress, IterTable, Table, TableRow
from organize_stream import (
    ExtractNameInnerData, DocumentTextExtract, ExtractNameInnerText, LibDigitalized
)


DOW = UserFileSystem().userDownloads
OUT = DOW.concat('output', create=True)
#dest = OUT.concat('MOVIDOS', create=True)

src_dir = Directory('/mnt/dados/Teste')


def test():
    output_sheet = OUT.join_file('cartas.xlsx')
    #extract_name = ExtractNameInnerText(OUT, lib_digitalized=LibDigitalized.CARTA_CALCULO)
    extract_txt = DocumentTextExtract()
    files = InputFiles(src_dir).get_files(file_type=LibraryDocs.PDF)[0:2]

    for f in files:
        extract_txt.add_file_pdf(f)
        break

    tb1 = extract_txt.values[0]
    _items = list(tb1.values())

    tb = Table(_items)
    for row in tb.iter_tables():
        print('---------------------------------------------------------')
        print(row.length)
        print(row)



def main():
    test()


main()









