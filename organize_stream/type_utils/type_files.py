from __future__ import annotations
from enum import StrEnum
from typing import TypeAlias
from io import BytesIO
from organize_stream.utils import sp, sheet, ListString, ListColumnBody
from organize_stream.erros import InvalidSrcFile


class LibDigitalized(StrEnum):

    GENERIC = 'generic'
    CARTA_CALCULO = 'carta_calculo'
    EPI = 'epi'


class DynamicFile(object):

    def __init__(self, file: str | sp.File | bytes | BytesIO):
        if isinstance(file, sp.File):
            pass
        elif isinstance(file, bytes):
            pass
        elif isinstance(file, BytesIO):
            pass
        elif isinstance(file, str):
            pass
        else:
            raise InvalidSrcFile(
                f'{__class__.__name__} Arquivo inválido ... {file}, use ... bytes|BytesIO|File|str'
            )
        self.file = file

    @property
    def is_bytes(self) -> bool:
        return isinstance(self.file, bytes)

    @property
    def is_bytes_io(self) -> bool:
        return isinstance(self.file, BytesIO)

    @property
    def is_file(self) -> bool:
        return isinstance(self.file, str)

    @property
    def is_file_path(self) -> bool:
        return isinstance(self.file, sp.File)


class KeyFiles(StrEnum):

    FILE_PATH = 'FILE_PATH'
    FILE_NAME = 'FILE_NAME'
    DIRECTORY = 'DIRECTORY'
    FILE_TYPE = 'FILE_TYPE'
    ORIGIN_DISK_TYPE = 'ORIGIN_DISK_TYPE'
    NEW_FILE_NAME = 'NEW_FILE_NAME'
    UNIQUE_KEY = 'UNIQUE_KEY'


class KeyWordsFileNames(dict):

    def __init__(self):
        super().__init__({})
        self[KeyFiles.FILE_PATH.value] = None
        self[KeyFiles.FILE_NAME.value] = None
        self[KeyFiles.DIRECTORY.value] = None
        self[KeyFiles.FILE_TYPE.value] = None
        self[KeyFiles.ORIGIN_DISK_TYPE.value] = None
        self[KeyFiles.NEW_FILE_NAME.value] = None
        self[KeyFiles.UNIQUE_KEY.value] = None

    def __repr__(self):
        return f'KeyWordsFileNames: {super().__repr__()}'

    def keys(self) -> list[str]:
        return list(super().keys())


class OriginFileName(sp.File):

    def __init__(self, filename: str):
        super().__init__(filename)


class DestFileName(sp.File):

    def __init__(self, filename: str):
        super().__init__(filename)
