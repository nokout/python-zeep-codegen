"""
Unit tests for custom exception classes.

Tests exception hierarchy and behavior.
"""
import pytest

from exceptions import (
    WSDLSchemaError,
    DownloadError,
    ValidationError,
    XSDGenerationError,
    ConversionError,
    SchemaGenerationError
)


@pytest.mark.unit
def test_base_exception() -> None:
    """Test base WSDLSchemaError exception."""
    error = WSDLSchemaError("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)


@pytest.mark.unit
def test_download_error_inherits_base() -> None:
    """Test DownloadError inherits from WSDLSchemaError."""
    error = DownloadError("Download failed")
    assert isinstance(error, WSDLSchemaError)
    assert isinstance(error, Exception)


@pytest.mark.unit
def test_validation_error_inherits_base() -> None:
    """Test ValidationError inherits from WSDLSchemaError."""
    error = ValidationError("Validation failed")
    assert isinstance(error, WSDLSchemaError)


@pytest.mark.unit
def test_xsd_generation_error_inherits_base() -> None:
    """Test XSDGenerationError inherits from WSDLSchemaError."""
    error = XSDGenerationError("Generation failed")
    assert isinstance(error, WSDLSchemaError)


@pytest.mark.unit
def test_conversion_error_inherits_base() -> None:
    """Test ConversionError inherits from WSDLSchemaError."""
    error = ConversionError("Conversion failed")
    assert isinstance(error, WSDLSchemaError)


@pytest.mark.unit
def test_schema_generation_error_inherits_base() -> None:
    """Test SchemaGenerationError inherits from WSDLSchemaError."""
    error = SchemaGenerationError("Schema generation failed")
    assert isinstance(error, WSDLSchemaError)


@pytest.mark.unit
def test_exceptions_can_be_caught_by_base() -> None:
    """Test that all exceptions can be caught using base exception."""
    errors = [
        DownloadError("test"),
        ValidationError("test"),
        XSDGenerationError("test"),
        ConversionError("test"),
        SchemaGenerationError("test")
    ]
    
    for error in errors:
        try:
            raise error
        except WSDLSchemaError:
            pass  # Should catch all
        else:
            pytest.fail(f"Failed to catch {type(error).__name__} as WSDLSchemaError")


@pytest.mark.unit
def test_exception_messages() -> None:
    """Test that exception messages are preserved."""
    message = "Detailed error message"
    error = ConversionError(message)
    assert str(error) == message
