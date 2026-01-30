"""
Utility module for managing temporary directories with context managers.

This module provides context managers and utilities for safe creation and cleanup
of temporary directories used during the conversion pipeline.
"""
import logging
import shutil
from pathlib import Path
from typing import Generator, Optional
from contextlib import contextmanager

logger: logging.Logger = logging.getLogger(__name__)


@contextmanager
def temp_directory(
    base_path: Optional[Path] = None,
    cleanup: bool = True
) -> Generator[Path, None, None]:
    """
    Context manager for creating and cleaning up temporary directories.
    
    Creates a temporary directory at the specified path and ensures it's cleaned up
    when the context exits, unless cleanup=False is specified. This is useful for
    managing intermediate files during the conversion pipeline.
    
    Args:
        base_path: Path where temp directory should be created. If None, uses '.temp'
        cleanup: If True, delete the directory on exit; if False, preserve it
    
    Yields:
        Path object pointing to the temporary directory
    
    Example:
        >>> with temp_directory() as temp_dir:
        ...     # Work with temp_dir
        ...     (temp_dir / 'file.txt').write_text('data')
        ...     # Directory is automatically cleaned up on exit
        
        >>> with temp_directory(cleanup=False) as temp_dir:
        ...     # Directory preserved for debugging
        ...     pass
    """
    temp_path: Path = base_path if base_path else Path('.temp')
    temp_path.mkdir(parents=True, exist_ok=True)
    
    logger.debug(f"Created temp directory: {temp_path}")
    
    try:
        yield temp_path
    finally:
        if cleanup:
            try:
                shutil.rmtree(temp_path, ignore_errors=True)
                logger.debug(f"Cleaned up temp directory: {temp_path}")
            except Exception as e:
                logger.warning(f"Could not clean up temp directory {temp_path}: {e}")
        else:
            logger.debug(f"Preserved temp directory: {temp_path}")


@contextmanager
def preserve_sys_path() -> Generator[None, None, None]:
    """
    Context manager to preserve and restore sys.path.
    
    Temporarily modifies sys.path during module imports and restores it afterwards.
    This ensures that dynamic imports don't permanently pollute the module search path.
    
    Yields:
        None
        
    Example:
        >>> import sys
        >>> original_len = len(sys.path)
        >>> with preserve_sys_path():
        ...     sys.path.insert(0, '/tmp/some/path')
        ...     # sys.path is modified here
        >>> assert len(sys.path) == original_len  # Restored
    """
    import sys
    original_path = sys.path.copy()
    logger.debug("Saved sys.path")
    
    try:
        yield
    finally:
        sys.path[:] = original_path
        logger.debug("Restored sys.path")
