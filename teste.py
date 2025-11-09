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
from sheet_stream import save_data, ReadFileSheet, fmt_col_to_date, LibDate

DOW = UserFileSystem().userDownloads
OUT = DOW.concat('output', create=True)
dest = OUT.concat('MOVIDOS', create=True)


def test():

    output_sheet = OUT.join_file('teste-ext.xlsx')
    src_sheet = File('/home/brunoc/Documentos/BASE/base-gm.xlsx')
    src_dir = Directory('/mnt/dados/Teste')
    input_files = InputFiles(src_dir)
    files = input_files.get_files(file_type=LibraryDocs.PDF)[0:3]

    for f in files:
        tb = org.read_document(cs.DocumentPdf(f))
        if tb.length == 0:
            continue
            
        carta = org.CartaCalculo(tb)
        org.cartas.move_cartas([carta], dest)




def main():
    test()


main()









