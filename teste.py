"""

"""

from soup_files import *
import pandas as pd
import convert_stream as cs
from sheet_stream import save_data, ReadFileSheet, fmt_col_to_date, LibDate
from organize_stream.type_utils import (
    TextProgress, IterTable, Table, TableRow, KeyFiles, KeyWordsFileName, DynamicFile, DiskFile
)
from organize_stream import (
    ExtractNameInnerData, DocumentTextExtract, ExtractNameInnerText, LibDigitalized
)
from organize_stream.document.name_files import NameFileInnerTable, LibDigitalized
from io import BytesIO

DOW = UserFileSystem().userDownloads
OUT = DOW.concat('output', create=True)
dest = OUT.concat('MOVIDOS', create=True)
src_dir = Directory('/home/brunoc/Downloads/input')


def test():
    output_sheet = OUT.join_file('cartas.xlsx')
    output_zip = OUT.join_file('cartas.zip')

    images = InputFiles(src_dir).get_files(file_type=LibraryDocs.PDF)
    name = NameFileInnerTable(lib_digitalized=LibDigitalized.CARTA_CALCULO)
    _bt_zip: BytesIO = name.documents_to_zip(images)
    with open(output_zip.absolute(), 'wb') as zipf:
        zipf.write(_bt_zip.getvalue())


def main():
    test()


main()









