#!/usr/bin/env python3

__version__ = '2.4'
from .read import (
    read_image, read_images, read_document_pdf, create_table_from_dict,
    read_directory_pdf, read_directory_image, read_file_pdf, create_tb_from_names
)
from .find import (
    SearchableText, NameFinderInnerText, NameFinderInnerData, NameFinder,
    FilterText, FilterData, OriginFileName, DestFileName, fmt_str_file,
)
from .document import (
    OrganizeInnerData, DocumentTextExtract, OrganizeInnerText,
)
from .cartas import CartaCalculo


