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
    src_dir = Directory('/mnt/dados/2025-11-02 Cartas Toi WhatsApp/OriginLocalidades/JACY E UNIAO/WP TOI JACI E UNIAO DE 22 09 2025 ATE 31 10 2025')
    input_files = InputFiles(src_dir)
    _images = input_files.get_files(file_type=LibraryDocs.IMAGE)
    _pdfs = input_files.get_files(file_type=LibraryDocs.PDF)
    df = ReadFileSheet(src_sheet).get_dataframe()
    df = fmt_col_to_date(df, 'POSTAGEM', date_fmt=LibDate.Y_M_D)

    #ft = org.FilterText('TOI|TOL', key_words=['UC'])
    #fil = org.OrganizeInnerText(dest, lib_digitalized=org.LibDigitalized.CARTA_CALCULO, filters=ft)
    ft = org.FilterData(
        df, col_find='TOI', col_new_name='UC', cols_in_name=['TOI', 'POSTAGEM', 'ESTADO']
    )
    fil = org.OrganizeInnerData(dest, filters=ft)
    
    fil.add_images(_images)
    fil.add_dir_pdf(src_dir)



def main():
    test()


main()









