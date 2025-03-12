"""DD converter exceptions module."""

class DDError(Exception):
    """Base exception for DD converter errors."""
    pass

class DDFileError(DDError):
    """Exception raised for file-related errors."""
    pass

class DDParserError(DDError):
    """Exception raised for parsing errors."""
    pass

class DDValidationError(DDError):
    """Exception raised for validation errors."""
    pass

class DDConversionError(DDError):
    """Exception raised for conversion errors."""
    pass 