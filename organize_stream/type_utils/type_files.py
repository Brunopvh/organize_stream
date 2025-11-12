from __future__ import annotations
from enum import StrEnum
from typing import TypeAlias, Union
from io import BytesIO
from organize_stream.utils import sp, sheet, ListString, ListColumnBody
from organize_stream.erros import InvalidSrcFile

DiskFile: TypeAlias = Union[str, sp.File, bytes, BytesIO]


class LibDigitalized(StrEnum):

    GENERIC = 'generic'
    CARTA_CALCULO = 'carta_calculo'
    EPI = 'epi'


class DynamicFile(object):

    def __init__(self, file: DiskFile):
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

    SRC_FILE_PATH = 'FILE_PATH'
    SRC_FILENAME = 'FILE_NAME'
    DIRECTORY = 'DIRECTORY'
    FILE_TYPE = 'FILE_TYPE'
    ORIGIN_DISK_TYPE = 'ORIGIN_DISK_TYPE'
    NEW_FILE_NAME = 'NEW_FILE_NAME'
    UNIQUE_KEY = 'UNIQUE_KEY'


class KeyWordsFileNames(dict):

    def __init__(self):
        super().__init__({})
        self[KeyFiles.SRC_FILE_PATH.value] = None
        self[KeyFiles.SRC_FILENAME.value] = None
        self[KeyFiles.DIRECTORY.value] = None
        self[KeyFiles.FILE_TYPE.value] = None
        self[KeyFiles.ORIGIN_DISK_TYPE.value] = None
        self[KeyFiles.NEW_FILE_NAME.value] = None
        self[KeyFiles.UNIQUE_KEY.value] = None

    @property
    def origin_disk_type(self) -> str | None:
        return self[KeyFiles.ORIGIN_DISK_TYPE]

    @property
    def src_dynamic_file(self) -> DynamicFile | None:
        return self[KeyFiles.SRC_FILE_PATH.value]

    @property
    def new_file_name(self) -> str | None:
        return self[KeyFiles.NEW_FILE_NAME.value]

    @property
    def file_type(self) -> str | None:
        return self[KeyFiles.FILE_TYPE]

    @file_type.setter
    def file_type(self, new: str):
        self[KeyFiles.FILE_TYPE] = new

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
