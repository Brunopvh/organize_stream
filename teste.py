"""

"""

from soup_files import *
import pandas as pd
import convert_stream as cs
from sheet_stream import save_data, ReadFileSheet, fmt_col_to_date, LibDate
from organize_stream.type_utils import (
    TextProgress, IterTable, Table, TableRow, KeyFiles, KeyWordsFileNames, DynamicFile, DiskFile
)
from organize_stream import (
    ExtractNameInnerData, DocumentTextExtract, ExtractNameInnerText, LibDigitalized
)
from organize_stream.document.organize_files import NameFileInnerTable, LibDigitalized


DOW = UserFileSystem().userDownloads
OUT = DOW.concat('output', create=True)
#dest = OUT.concat('MOVIDOS', create=True)

src_dir = Directory('/mnt/dados/Teste')


def test():
    output_sheet = OUT.join_file('cartas.xlsx')
    #extract_name = ExtractNameInnerText(OUT, lib_digitalized=LibDigitalized.CARTA_CALCULO)

    files = InputFiles(src_dir).get_files(file_type=LibraryDocs.PDF)[1:3]
    file_pdf = File('/mnt/dados/Teste/1939174 175102179-WS12623S902-EXTREMA.pdf')
    bytes_pdf = file_pdf.path.read_bytes()

    name = NameFileInnerTable(lib_digitalized=LibDigitalized.CARTA_CALCULO)
    __kw = name.get_new_document_name(bytes_pdf)
    if __kw.src_dynamic_file.is_bytes:
        output_name = __kw.new_file_name
        if __kw.file_type is not None:
            output_name = f'{output_name}.{__kw.file_type}'
            
        if output_name is not None:
            out = OUT.join_file(output_name)
            with open(out.absolute(), 'wb') as fp:
                fp.write(__kw.src_dynamic_file.file)



def main():
    test()


main()









