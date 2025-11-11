from .observer import Observer, NotifyProvider
from .digital_doc import DigitalizedDocument, FilterText, FilterData
from enum import StrEnum
from soup_files import File, ProgressBarAdapter


class LibDigitalized(StrEnum):

    GENERIC = 'generic'
    CARTA_CALCULO = 'carta_calculo'
    EPI = 'epi'


class OriginFileName(File):

    def __init__(self, filename: str):
        super().__init__(filename)


class DestFileName(File):

    def __init__(self, filename: str):
        super().__init__(filename)


class TextProgress(object):

    def __init__(self, total: int, start_value: int = 0):
        self.start_value = start_value
        self.total = total
        if total < start_value:
            raise ValueError(f'Total {total} is less than start value {start_value}')
        if total == 0:
            raise ValueError(f'Total {total} is zero')
        self._default_text: str = 'Progresso'
        self.__pbar: ProgressBarAdapter = ProgressBarAdapter()

    def set_update(self):
        self.__pbar.update(
            ((self.start_value+1) / self.total) * 100,
            self._default_text,
        )
        self.start_value += 1


class IterRowsTb(object):
    pass

__all__ = [
    'DigitalizedDocument', 'FilterText', 'Observer',
    'NotifyProvider', 'LibDigitalized', 'FilterData',
    'OriginFileName', 'DestFileName', 'TextProgress',
]

