"""

"""

from soup_files import *
import pandas as pd
import convert_stream as cs
from sheet_stream import save_data, ReadFileSheet, fmt_col_to_date, LibDate
from organize_stream.type_utils import (
    TextProgress, KeyFiles, KeyWordsFileName, DynamicFile, DiskFile
)
from organize_stream import (
    ExtractNameInnerData, DocumentTextExtract, ExtractNameInnerText, LibDigitalized
)
from organize_stream.document.name_files import NameFileInnerTable, LibDigitalized
from io import BytesIO

DOW = UserFileSystem().userDownloads
OUT = DOW.concat('output', create=True)
dest = OUT.concat('MOVIDOS', create=True)


def test():
    pass


def main():
    test()


main()









