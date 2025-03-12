"""DD converter package."""

__version__ = '0.1.0'

from dd_converter.converter import convert_dd_to_csv, convert_folder_to_csvs
from dd_converter.parser import DDParser
from dd_converter.exceptions import (
    DDError,
    DDFileError,
    DDParserError,
    DDValidationError,
    DDConversionError
)

__all__ = [
    "convert_dd_to_csv",
    "convert_folder_to_csvs",
    "DDParser",
    "DDError",
    "DDFileError",
    "DDParserError",
    "DDValidationError",
    "DDConversionError"
] 