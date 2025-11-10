#!/usr/bin/env python3

from sheet_stream import TableDocuments, concat_table_documents
from organize_stream.read import read_image, read_document, Ocr
from organize_stream.type_utils.observer import NotifyProvider
import soup_files as sp
import convert_stream as cs
import ocr_stream as ocr
import pandas as pd


class DocumentTextExtract(NotifyProvider):
    """
        Extrair texto de arquivos, e converter em Excel/DataFrame
    """

    def __init__(self, recognize_image: ocr.RecognizeImage = Ocr()):
        super().__init__()
        self.tb_list: list[TableDocuments] = []
        self.recognize: ocr.RecognizeImage = recognize_image
        self.threshold: bool = False
        self._count: int = 0
        self._pbar = sp.ProgressBarAdapter()

    @property
    def pbar(self) -> sp.ProgressBarAdapter:
        return self._pbar

    @pbar.setter
    def pbar(self, pbar: sp.ProgressBarAdapter) -> None:
        self._pbar = pbar

    @property
    def is_empty(self) -> bool:
        return len(self.tb_list) == 0

    def add_table(self, tb: TableDocuments) -> None:
        if tb.length == 0:
            return
        self.tb_list.append(tb)
        self._count += 1
        self.pbar.update_text(f'{__class__.__name__} Tabela adicionada: {self._count}')
        self.send_notify(tb)

    def add_directory_pdf(
                self,
                dir_pdf: sp.Directory, *,
                apply_ocr: bool = False,
                dpi: int = 200
            ):
        files = sp.InputFiles(dir_pdf).get_files(file_type=sp.LibraryDocs.PDF)
        total = len(files)
        for n, f in enumerate(files):
            self.pbar.update(
                ((n + 1) / total) * 100,
                f'{n + 1}/{total} {f.basename()}',
            )
            print()
            if apply_ocr:
                tb = read_document(cs.DocumentPdf(f), self.recognize, pbar=self.pbar, dpi=dpi)
            else:
                tb = cs.DocumentPdf(f).to_dict()
            self.add_table(tb)

    def add_directory_image(self, dir_image: sp.Directory):
        files_images = sp.InputFiles(dir_image).get_files(file_type=sp.LibraryDocs.IMAGE)
        total = len(files_images)
        for idx, f in enumerate(files_images):
            self.pbar.update(
                ((idx + 1) / total) * 100,
                f'{idx + 1}/{total} {f.basename()}',
            )
            img = cs.ImageObject(f)
            if self.threshold:
                img.set_threshold_gray()
            self.add_table(read_image(img, recognize=self.recognize))

    def add_file_pdf(self, file_pdf: sp.File, *, apply_ocr: bool = False, dpi: int = 200):
        if apply_ocr:
            tb = read_document(cs.DocumentPdf(file_pdf), self.recognize, pbar=self.pbar, dpi=dpi)
        else:
            tb = cs.DocumentPdf(file_pdf).to_dict()
        self.add_table(tb)

    def add_file_image(self, file_image: sp.File):
        tb: TableDocuments = read_image(cs.ImageObject(file_image), recognize=self.recognize)
        self.add_table(tb)

    def add_image(self, image: cs.ImageObject):
        if not isinstance(image, cs.ImageObject):
            raise TypeError('Image must be an cs.ImageObject')
        self.add_table(read_image(image, recognize=self.recognize))

    def add_document(self, document: cs.DocumentPdf, *, apply_ocr: bool = False, dpi: int = 200,):

        if apply_ocr:
            tb = read_document(document, self.recognize, pbar=self.pbar, dpi=dpi)
        else:
            tb = document.to_dict()
        self.add_table(tb)

    def to_data(self) -> pd.DataFrame:
        if len(self.tb_list) == 0:
            return TableDocuments.create_void_df()
        final_tb = concat_table_documents(self.tb_list)
        return final_tb.to_data().astype('str')

    def to_excel(self, file: sp.File) -> None:
        try:
            self.to_data().to_excel(file.absolute(), index=False)
        except Exception as e:
            print(f'Error: {e}')
