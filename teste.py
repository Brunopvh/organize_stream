"""
    Correções em sheet_stream
- TableTextKeyWord().set_colum() -> Falha: pois pode adicionar colunas repetidas
- concat_table_documents()       -> Falha: pois precisa corrigir a coluna KEY

    Correções em convert_stream
- DocumentPdf().to_dict()       -> Falha: pois está gerando a coluna KEY de forma incorreta.
"""
import organize_stream as org
from soup_files import *
import pandas as pd
import convert_stream as cs
from sheet_stream import save_data

DOW = UserFileSystem().userDownloads
OUT = DOW.concat('output', create=True)
dest = OUT.concat('MOVIDOS', create=True)


def test():

    output_sheet = OUT.join_file('teste-ext.xlsx')
    src_dir = Directory('/mnt/hd_dados/2025-11-03 CARTAS TOI WHATSAPP/OcrCartas/EXTREMA/107 Ago 2024 - 10 Set 2025/Origin')

    fil = org.FilterText('TOI', dest)
    fd = org.OrganizeInnerText(fil)
    fd.add_dir_pdf(src_dir)


def main():
    test()


main()









