#!/usr/bin/env python3
from __future__ import annotations
from typing import Callable, Optional
from io import BytesIO
from organize_stream.utils import (
    sheet, ocr, cs, sp
)
from organize_stream.type_utils import (
    Table as TableDocuments, IterTable, TableRow, NotifyProvider, TextProgress,
    DiskFile, KeyFiles, KeyWordsFileNames,
)
from organize_stream.read import read_image, read_document, Ocr, concat_tables
import pandas as pd


class DocumentTextExtract(NotifyProvider):
    """
        Extrair texto de arquivos, e converter em Excel/DataFrame
    """

    def __init__(
                self,
                recognize_image: ocr.RecognizeImage = Ocr(),
                func_rd_img: Callable[[cs.ImageObject, Optional[ocr.RecognizeImage]], TableDocuments] = None
            ):
        super().__init__()
        if func_rd_img is None:
            self._func_read_image = read_image
        else:
            self._func_read_image = func_rd_img
        self.collection_tables: list[TableDocuments] = []
        self.recognize: ocr.RecognizeImage = recognize_image

        self.threshold: bool = False
        self.__count_idx: int = 0
        self.text_progress: TextProgress = TextProgress()
        self.text_progress.set_pbar(sp.ProgressBarAdapter())
        self._pbar = self.text_progress.get_pbar()

    @property
    def values(self) -> list[TableDocuments]:
        return self.collection_tables

    @property
    def length(self) -> int:
        return self.__count_idx

    @property
    def pbar(self) -> sp.ProgressBarAdapter:
        return self.text_progress.get_pbar()

    @pbar.setter
    def pbar(self, pbar: sp.ProgressBarAdapter) -> None:
        self.text_progress.set_pbar(pbar)

    @property
    def is_empty(self) -> bool:
        return len(self.collection_tables) == 0

    def add_table(self, tb: TableDocuments, send_notify: bool = True) -> None:
        if not isinstance(tb, TableDocuments):
            print(f'DEBUG: Tabela inválida: {tb}')
            return
        if tb.length == 0:
            print(f'DEBUG: Tabela vazia: {tb}')
            return
        self.collection_tables.append(tb)
        self.__count_idx += 1
        if send_notify:
            self.send_notify(tb)

    def add_directory_pdf(
                self,
                dir_pdf: sp.Directory, *,
                apply_ocr: bool = True,
                dpi: int = 200
            ):
        """
        Iterar sobre os arquivos PDF de uma pasta, extrair a tabela/texto de
        cada documento com OCR e adicionar cada tabela a propriedade/lista desse objeto.
        """
        files = sp.InputFiles(dir_pdf).get_files(file_type=sp.LibraryDocs.PDF)
        self.text_progress.total = len(files)
        self.text_progress.start_pbar()
        for n, f in enumerate(files):
            self.text_progress.set_update(f.basename())
            print()
            if apply_ocr:
                tb = read_document(
                    cs.DocumentPdf(f),
                    self.recognize,
                    pbar=self.pbar,
                    dpi=dpi,
                    func_read_image=self._func_read_image
                )
            else:
                _t = cs.DocumentPdf(f).to_dict()
                tb = TableDocuments([_t[k] for k in _t.keys()])
            self.add_table(tb)
        self.text_progress.stop_pbar()

    def add_directory_image(self, dir_image: sp.Directory):
        files_images = sp.InputFiles(dir_image).get_files(file_type=sp.LibraryDocs.IMAGE)
        self.text_progress.total = len(files_images)
        self.text_progress.start_pbar()
        for idx, f in enumerate(files_images):
            self.text_progress.set_update(f.basename())
            img = cs.ImageObject(f)
            if self.threshold:
                img.set_threshold_gray()
            self.add_table(
                self._func_read_image(img, self.recognize)
            )
        self.text_progress.stop_pbar()

    def add_file_pdf(self, file_pdf: sp.File, *, apply_ocr: bool = True, dpi: int = 200):
        tb: TableDocuments
        if apply_ocr:
            tb = read_document(
                cs.DocumentPdf(file_pdf),
                self.recognize,
                pbar=self.pbar, dpi=dpi,
                func_read_image=self._func_read_image # Função Opcional
            )
        else:
            __t = cs.DocumentPdf(file_pdf).to_dict()
            tb = TableDocuments([__t[k] for k in __t.keys()])
        self.add_table(tb)

    def add_file_image(self, file_image: sp.File):
        tb: TableDocuments = self._func_read_image(cs.ImageObject(file_image), self.recognize)
        self.add_table(tb)

    def add_image(self, image: cs.ImageObject):
        if not isinstance(image, cs.ImageObject):
            raise TypeError('Image must be an cs.ImageObject')
        self.add_table(self._func_read_image(image, self.recognize))

    def add_document(self, document: cs.DocumentPdf, *, apply_ocr: bool = False, dpi: int = 200,):
        tb: TableDocuments
        if apply_ocr:
            tb = read_document(
                document,
                self.recognize,
                pbar=self.pbar,
                dpi=dpi,
                func_read_image=self._func_read_image
            )
        else:
            __t = document.to_dict()
            tb = TableDocuments([__t[k] for k in __t.keys()])
        self.add_table(tb)

    def to_table(self) -> TableDocuments:
        if len(self.collection_tables) == 0:
            return TableDocuments.create_void_dict()
        return concat_tables(self.collection_tables)

    def to_data(self) -> pd.DataFrame:
        return self.to_table().to_data().astype('str')

    def to_excel(self, file: sp.File) -> None:
        try:
            self.to_data().to_excel(file.absolute(), index=False)
        except Exception as e:
            print(f'Error: {e}')

    def read_image(self, image: DiskFile) -> TableDocuments:
        img = cs.ImageObject(image)
        return self._func_read_image(img, self.recognize)

    def read_document(self, document: DiskFile, *, dpi: int = 200) -> TableDocuments:
        if isinstance(document, cs.DocumentPdf):
            pass
        elif isinstance(document, bytes):
            document = cs.DocumentPdf.create_from_bytes(BytesIO(document))
        else:
            document = cs.DocumentPdf(document)
        return read_document(
            document,
            self.recognize,
            dpi=dpi,
            func_read_image=self._func_read_image
        )


