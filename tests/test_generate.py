"""
Unit tests for the generate module.

Tests the generate_dataclasses function with mocked subprocess calls.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import subprocess

from pipeline.generate import generate_dataclasses
from exceptions import XSDGenerationError


@pytest.mark.unit
def test_generate_dataclasses_success(simple_xsd_file: Path, temp_test_dir: Path) -> None:
    """Test successful dataclass generation."""
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stderr = ''
    
    with patch('subprocess.run', return_value=mock_result):
        module_name, temp_path = generate_dataclasses(
            str(simple_xsd_file),
            temp_dir=temp_test_dir,
            keep_temp=True
        )
        
        assert module_name == 'generated_dataclasses.simple'
        assert temp_path == temp_test_dir


@pytest.mark.unit
def test_generate_dataclasses_xsdata_error(simple_xsd_file: Path, temp_test_dir: Path) -> None:
    """Test handling of xsdata generation errors."""
    mock_result = Mock()
    mock_result.returncode = 1
    mock_result.stderr = 'xsdata error: invalid schema'
    
    with patch('subprocess.run', return_value=mock_result):
        with pytest.raises(XSDGenerationError, match="xsdata generation failed"):
            generate_dataclasses(
                str(simple_xsd_file),
                temp_dir=temp_test_dir
            )


@pytest.mark.unit
def test_generate_dataclasses_module_name_normalization() -> None:
    """Test that module names are properly normalized."""
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stderr = ''
    
    with patch('subprocess.run', return_value=mock_result):
        with patch('pathlib.Path.mkdir'):
            # Test with dashes in filename
            module_name, _ = generate_dataclasses(
                'my-service-v2.xsd',
                keep_temp=True
            )
            assert module_name == 'generated_dataclasses.my_service_v2'
            
            # Test with dots in filename
            module_name, _ = generate_dataclasses(
                'service.1.0.xsd',
                keep_temp=True
            )
            assert module_name == 'generated_dataclasses.service_1_0'


@pytest.mark.unit
def test_generate_dataclasses_temp_dir_creation(simple_xsd_file: Path) -> None:
    """Test that temp directory is created if not provided."""
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stderr = ''
    
    with patch('subprocess.run', return_value=mock_result):
        module_name, temp_path = generate_dataclasses(
            str(simple_xsd_file),
            keep_temp=True
        )
        
        # Should use default .temp directory
        assert temp_path == Path('.temp')
