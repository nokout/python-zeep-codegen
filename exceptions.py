"""
Custom exception classes for WSDL/XSD to JSON Schema conversion.

This module defines a hierarchy of exceptions used throughout the conversion pipeline.
All exceptions inherit from WSDLSchemaError, which is the base exception for all
WSDL/XSD processing errors.
"""


class WSDLSchemaError(Exception):
    """Base exception for WSDL/XSD to schema conversion errors."""
    pass


class DownloadError(WSDLSchemaError):
    """Raised when downloading from URL fails."""
    pass


class ValidationError(WSDLSchemaError):
    """Raised when input validation fails."""
    pass


class XSDGenerationError(WSDLSchemaError):
    """Raised when xsdata generation fails."""
    pass


class ConversionError(WSDLSchemaError):
    """Raised when dataclass to Pydantic conversion fails."""
    pass


class SchemaGenerationError(WSDLSchemaError):
    """Raised when JSON schema generation fails."""
    pass


class UIGenerationError(WSDLSchemaError):
    """Raised when UI generation fails."""
    pass
