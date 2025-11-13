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

    def get_bytes(self) -> bytes:
        if self.is_bytes:
            return self.file
        elif self.is_bytes_io:
            self.file.seek(0)
            return self.file.getvalue()
        elif self.is_file:
            bt: bytes
            with open(self.file, 'rb') as f:
                bt = f.read()
            return bt
        elif self.is_file_path:
            bt: bytes
            with open(self.file.absolute(), 'rb') as f:
                bt = f.read()
            return bt


class KeyFiles(StrEnum):

    SRC_FILE_PATH = 'SRC_FILE_PATH'
    SRC_FILENAME = 'FILE_NAME'
    DIRECTORY = 'DIRECTORY'
    FILE_TYPE = 'FILE_TYPE'
    NEW_FILE_NAME = 'NEW_FILE_NAME'
    UNIQUE_KEY = 'UNIQUE_KEY'


class KeyWordsFileName(dict):

    def __init__(self):
        super().__init__({})
        self[KeyFiles.SRC_FILE_PATH.value] = None
        self[KeyFiles.SRC_FILENAME.value] = None
        self[KeyFiles.DIRECTORY.value] = None
        self[KeyFiles.FILE_TYPE.value] = None
        self[KeyFiles.NEW_FILE_NAME.value] = None
        self[KeyFiles.UNIQUE_KEY.value] = None

    @property
    def input_dynamic_file(self) -> DynamicFile | None:
        return self[KeyFiles.SRC_FILE_PATH.value]

    @input_dynamic_file.setter
    def input_dynamic_file(self, value: bytes | None) -> None:
        self[KeyFiles.SRC_FILE_PATH.value] = value

    @property
    def output_filename(self) -> str | None:
        return self[KeyFiles.NEW_FILE_NAME.value]

    @output_filename.setter
    def output_filename(self, value: Union[str, None] | None) -> None:
        self[KeyFiles.NEW_FILE_NAME.value] = value

    @property
    def extension_file(self) -> str | None:
        return self[KeyFiles.FILE_TYPE]

    @extension_file.setter
    def extension_file(self, new: str):
        self[KeyFiles.FILE_TYPE] = new

    def __repr__(self):
        return f'KeyWordsFileNames: {super().__repr__()}'

    def keys(self) -> list[str]:
        return list(super().keys())

    def save(self, output_dir: sp.Directory) -> bool:
        if self.extension_file is None:
            return False
        if self.output_filename is None:
            return False
        output_file = output_dir.join_file(f'{self.output_filename}{self.extension_file}')
        try:
            output_dir.mkdir()
            with open(output_file.absolute(), 'wb') as f:
                f.write(self.input_dynamic_file.get_bytes())
        except Exception as e:
            print(f'{__class__.__name__} Error: {e}')
            return False
        else:
            return True


class OriginFileName(sp.File):

    def __init__(self, filename: str):
        super().__init__(filename)


class DestFileName(sp.File):

    def __init__(self, filename: str):
        super().__init__(filename)
