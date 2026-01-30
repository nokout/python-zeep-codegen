"""
Pipeline module for generating Python dataclasses from XSD/WSDL files using xsdata.

This module handles Step 1 of the conversion pipeline: converting XSD/WSDL schemas
to Python dataclasses using xsdata's CLI tool. The generated dataclasses preserve
the structure and types from the original schema.
"""
import logging
import subprocess
import shutil
from pathlib import Path
from typing import Tuple, Optional, Final

from exceptions import XSDGenerationError

logger: logging.Logger = logging.getLogger(__name__)

# Constants
DEFAULT_OUTPUT_PACKAGE: Final[str] = "generated_dataclasses"


def generate_dataclasses(
    xsd_file: str,
    temp_dir: Optional[Path] = None,
    keep_temp: bool = False
) -> Tuple[str, Path]:
    """
    Generate Python dataclasses from XSD file using xsdata in a temporary directory.
    
    Runs xsdata's code generation tool to create Python dataclasses that match the
    structure defined in the XSD/WSDL schema. The generated code includes proper
    type annotations and preserves relationships between types.
    
    Args:
        xsd_file: Path to XSD or WSDL file (local path or absolute path)
        temp_dir: Temporary directory for generation (will be created if None)
        keep_temp: If True, don't delete temp directory after processing
    
    Returns:
        Tuple of (module_name, temp_dir_path):
            - module_name: Fully qualified Python module name for generated code
            - temp_dir_path: Path to temporary directory containing generated files
    
    Raises:
        XSDGenerationError: If xsdata generation fails or encounters errors
    
    Example:
        >>> module_name, temp_path = generate_dataclasses('order.xsd')
        >>> print(module_name)
        generated_dataclasses.order
    """
    logger.info(f"Generating dataclasses from XSD/WSDL: {xsd_file}")
    
    # Create temporary directory if not provided
    if temp_dir is None:
        temp_dir = Path(".temp")
    
    # Clean generated_models subdirectory only (preserve downloads)
    temp_dir.mkdir(parents=True, exist_ok=True)
    dataclasses_dir: Path = temp_dir / DEFAULT_OUTPUT_PACKAGE
    if dataclasses_dir.exists():
        shutil.rmtree(dataclasses_dir, ignore_errors=True)
    
    output_package: str = DEFAULT_OUTPUT_PACKAGE
    
    logger.info(f"Temp directory: {temp_dir}")
    logger.info(f"Output package: {output_package}")
    
    # Run xsdata generate command - it will create files in current dir, so we need to chdir
    cmd: list[str] = ["xsdata", "generate", "-p", output_package, str(Path(xsd_file).absolute())]
    logger.debug(f"Running: {' '.join(cmd)}")
    
    result: subprocess.CompletedProcess[str] = subprocess.run(
        cmd, capture_output=True, text=True, cwd=str(temp_dir)
    )
    
    if result.returncode != 0:
        error_msg: str = f"xsdata generation failed: {result.stderr}"
        logger.error(error_msg)
        if not keep_temp and temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise XSDGenerationError(error_msg)
    
    # Derive module name from XSD filename
    xsd_path: Path = Path(xsd_file)
    module_name: str = xsd_path.stem.replace('-', '_').replace('.', '_')
    full_module: str = f"{output_package}.{module_name}"
    
    logger.info(f"Generated dataclasses in temp directory")
    logger.info(f"Module: {full_module}")
    if keep_temp:
        logger.info(f"Temp directory preserved: {temp_dir}")
    
    return full_module, temp_dir
