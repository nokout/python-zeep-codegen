"""
Unit tests for temp directory management utilities.

Tests context managers and resource cleanup.
"""
import pytest
from pathlib import Path
import sys

from utils.temp_manager import temp_directory, preserve_sys_path


@pytest.mark.unit
def test_temp_directory_creates_and_cleans() -> None:
    """Test that temp directory is created and cleaned up."""
    test_path = Path('.test_temp_dir')
    
    with temp_directory(test_path, cleanup=True) as temp_dir:
        assert temp_dir.exists()
        assert temp_dir == test_path
        
        # Create a file in it
        (temp_dir / 'test.txt').write_text('test')
        assert (temp_dir / 'test.txt').exists()
    
    # Should be cleaned up after context exit
    assert not test_path.exists()


@pytest.mark.unit
def test_temp_directory_preserves_when_no_cleanup() -> None:
    """Test that temp directory is preserved when cleanup=False."""
    test_path = Path('.test_temp_preserve')
    
    try:
        with temp_directory(test_path, cleanup=False) as temp_dir:
            (temp_dir / 'test.txt').write_text('test')
        
        # Should still exist
        assert test_path.exists()
        assert (test_path / 'test.txt').exists()
    finally:
        # Clean up manually
        if test_path.exists():
            import shutil
            shutil.rmtree(test_path, ignore_errors=True)


@pytest.mark.unit
def test_temp_directory_default_path() -> None:
    """Test temp directory with default path."""
    with temp_directory(cleanup=True) as temp_dir:
        assert temp_dir.exists()
        assert temp_dir == Path('.temp')


@pytest.mark.unit
def test_preserve_sys_path() -> None:
    """Test that sys.path is preserved and restored."""
    original_path = sys.path.copy()
    original_len = len(sys.path)
    
    with preserve_sys_path():
        # Modify sys.path
        sys.path.insert(0, '/some/test/path')
        assert len(sys.path) == original_len + 1
        assert sys.path[0] == '/some/test/path'
    
    # Should be restored
    assert sys.path == original_path
    assert len(sys.path) == original_len


@pytest.mark.unit
def test_preserve_sys_path_with_exception() -> None:
    """Test that sys.path is restored even when exception occurs."""
    original_path = sys.path.copy()
    
    with pytest.raises(ValueError):
        with preserve_sys_path():
            sys.path.insert(0, '/test/path')
            raise ValueError("Test exception")
    
    # Should still be restored
    assert sys.path == original_path


@pytest.mark.unit
def test_temp_directory_handles_existing_dir() -> None:
    """Test behavior when directory already exists."""
    test_path = Path('.test_existing')
    test_path.mkdir(exist_ok=True)
    
    try:
        # Should not fail if directory exists
        with temp_directory(test_path, cleanup=True) as temp_dir:
            assert temp_dir.exists()
            (temp_dir / 'newfile.txt').write_text('new')
        
        # Should be cleaned up
        assert not test_path.exists()
    finally:
        if test_path.exists():
            import shutil
            shutil.rmtree(test_path, ignore_errors=True)
