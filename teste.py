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


DOW = UserFileSystem().userDownloads
OUT = DOW.concat('output', create=True)
#dest = OUT.concat('MOVIDOS', create=True)
#src_dir = Directory('/mnt/dados/Teste')


def test():
    output_sheet = OUT.join_file('cartas.xlsx')
    #extract_name = ExtractNameInnerText(OUT, lib_digitalized=LibDigitalized.CARTA_CALCULO)
    #files = InputFiles(src_dir).get_files(file_type=LibraryDocs.PDF)[1:3]

    file_pdf = File('/mnt/hd_dados/2025-11-03 CARTAS TOI WHATSAPP/OcrCartas/EXTREMA/107 Ago 2024 - 10 Set 2025/Origin/Digitalizado_20250807-2021.pdf')
    bytes_pdf = file_pdf.path.read_bytes()
    name = NameFileInnerTable(lib_digitalized=LibDigitalized.CARTA_CALCULO)

    name.rename_document(bytes_pdf, OUT)


def main():
    test()


main()









