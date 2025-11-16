from __future__ import annotations
from enum import StrEnum
from typing import TypeAlias, Union
from io import BytesIO
from organize_stream.utils import sp, sheet, ListString, ListColumnBody
from organize_stream.erros import InvalidSrcFile
from sheet_stream.type_utils import get_hash_from_bytes
import shutil

DiskFile: TypeAlias = Union[str, sp.File, bytes, BytesIO]


class LibDigitalized(StrEnum):

    GENERIC = 'generic'
    CARTA_CALCULO = 'carta_calculo'
    EPI = 'epi'


class KeyFiles(StrEnum):

    SRC_FILE_PATH = 'SRC_FILE_PATH'
    SRC_FILENAME = 'FILE_NAME'
    DIRECTORY = 'DIRECTORY'
    FILE_TYPE = 'FILE_TYPE'
    NEW_FILE_NAME = 'NEW_FILE_NAME'
    UNIQUE_KEY = 'UNIQUE_KEY'


class DynamicFile(object):

    def __init__(self, file: DiskFile):
        if isinstance(file, sp.File):
            self.__src_obj = 'FILE'
        elif isinstance(file, bytes):
            self.__src_obj = 'BYTES'
        elif isinstance(file, BytesIO):
            self.__src_obj = 'BYTES_IO'
        elif isinstance(file, str):
            self.__src_obj = 'STR'
        else:
            raise InvalidSrcFile(
                f'{__class__.__name__} Arquivo inválido ... {file}, use ... bytes|BytesIO|File|str'
            )
        self.file: DiskFile = file

    @property
    def id_file(self) -> str | None:
        if (self.__src_obj == 'BYTES') or (self.__src_obj == 'BYTES_IO'):
            _id_file = get_hash_from_bytes(self.file)
        elif self.__src_obj == 'STR':
            _id_file = self.file
        elif self.__src_obj == 'FILE':
            _id_file = self.file.absolute()
        else:
            _id_file = None
        return _id_file

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

    def __hash__(self):
        return hash(self.file)

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
        return None


class OriginFileName(sp.File):

    def __init__(self, filename: str):
        super().__init__(filename)


class DestFilePath(sp.File):

    def __init__(self, filename: str):
        super().__init__(filename)


class KeyWordsFileName(dict):
    """
        Dicionário que contém informações de um arquivo no disco, bytes|BytesIO|File|str.
    A chave KeyFiles.NEW_FILE_NAME.value - pode ser definida futuramente para guardar o
    novo nome do arquivo (bastando concatenar com o diretório de saída para obter o caminho
    absoluto do novo arquivo).

    """

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
    def input_dynamic_file(self, value: DynamicFile) -> None:
        if not isinstance(value, DynamicFile):
            raise TypeError(f'{__class__.__name__} Use: DynamicFile()')
        self[KeyFiles.SRC_FILE_PATH.value] = value

    @property
    def output_name_str(self) -> str | None:
        return self[KeyFiles.NEW_FILE_NAME.value]

    @output_name_str.setter
    def output_name_str(self, value: Union[str, None] | None) -> None:
        self[KeyFiles.NEW_FILE_NAME.value] = value

    @property
    def extension_file(self) -> str | None:
        return self[KeyFiles.FILE_TYPE]

    @extension_file.setter
    def extension_file(self, new: str):
        self[KeyFiles.FILE_TYPE] = new

    def __repr__(self):
        return f'KeyWordsFileNames: {super().__repr__()}'

    def __hash__(self):
        return hash(self.input_dynamic_file.file)

    def __eq__(self, other):
        if self.input_dynamic_file is not None and other.input_dynamic_file is not None:
            return self.input_dynamic_file.file == other.input_dynamic_file.file
        return self.__hash__() == other.__hash__()

    def keys(self) -> ListString:
        return ListString(list(super().keys()))

    def save(self, output_dir: sp.Directory) -> tuple[DynamicFile, DestFilePath | None, bool]:
        """
            Salva os bytes do arquivo original no novo caminho absoluto gerado.

        :param output_dir: Diretório para concatenar com o nome do novo arquivo
        (chave: KeyFiles.NEW_FILE_NAME.value).

        :return: Tuple (DynamicFile, DestFileName | None, bool).
        Se a operação falhar o terceiro elemento da tuple será False, se não, será True.
        tuple[0] -> DynamicFile arquivo original
        tuple[1] -> DestFileName caminho absoluto do arquivo salvo no disco ou None se a operação falhar.
        tuple[2] -> bool sucesso ou erro.

        """
        if self.extension_file is None:
            return self.input_dynamic_file, None, False
        if self.output_name_str is None:
            return self.input_dynamic_file, None, False

        try:
            output_file: sp.File = output_dir.join_file(f'{self.output_name_str}{self.extension_file}')
            output_dir.mkdir()
            with open(output_file.absolute(), 'wb') as f:
                f.write(self.input_dynamic_file.get_bytes())
        except Exception as e:
            print(f'{__class__.__name__} Error: {e}')
            return self.input_dynamic_file, None, False
        else:
            return self.input_dynamic_file, DestFilePath(output_file.absolute()), False

    def move(self, output_dir: sp.Directory) -> tuple[DynamicFile, DestFilePath | None, bool]:
        if (not self.input_dynamic_file.is_file) and (not self.input_dynamic_file.is_file_path):
            return self.input_dynamic_file, None, False
        if self.extension_file is None:
            return self.input_dynamic_file, None, False
        if self.output_name_str is None:
            return self.input_dynamic_file, None, False

        output_file: sp.File = output_dir.join_file(f'{self.output_name_str}{self.extension_file}')
        try:
            if self.input_dynamic_file.is_file:
                shutil.move(self.input_dynamic_file.file, output_file.absolute())
            elif self.input_dynamic_file.is_file_path:
                shutil.move(self.input_dynamic_file.file.absolute(), output_file.absolute())
        except Exception as e:
            print(f'{__class__.__name__} Error: {e}')
            return self.input_dynamic_file, None, False
        else:
            return self.input_dynamic_file, DestFilePath(output_file.absolute()), True

