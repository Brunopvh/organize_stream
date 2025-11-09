
import organize_stream as org
from soup_files import *
import pandas as pd
import convert_stream as cs

from organize_stream.cartas import move_cartas

DOW = UserFileSystem().userDownloads
OUT = DOW.concat('output', create=True)
dest = OUT.concat('MOVIDOS', create=True)


def main():
    dest = Directory('/mnt/dados/2025-11-02 Cartas Toi WhatsApp/Output/GM E NM')
    in_dir = Directory('/mnt/dados/2025-11-02 Cartas Toi WhatsApp/OriginLocalidades/GM e NM/WP TOI NM E GM DE 26 09 2025 ATE 31 10 2025')
    files = InputFiles(in_dir).get_files(file_type=LibraryDocs.IMAGE)

    total = len(files)
    for n, f in enumerate(files):
        print(f'{n+1}/{total}')
        tb = org.read_image(f)
        carta = org.CartaCalculo(tb)
        move_cartas([carta], dest)

main()









