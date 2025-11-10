from .observer import Observer, NotifyProvider
from .digital_doc import DigitalizedDocument, FilterText, FilterData
from enum import StrEnum


class LibDigitalized(StrEnum):

    GENERIC = 'generic'
    CARTA_CALCULO = 'carta_calculo'
    EPI = 'epi'


__all__ = [
    'DigitalizedDocument', 'FilterText', 'Observer',
    'NotifyProvider', 'LibDigitalized', 'FilterData',
]

