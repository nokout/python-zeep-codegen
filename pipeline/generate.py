"""
Pipeline module for generating Python dataclasses from XSD/WSDL files using xsdata.
"""
import logging
import subprocess
import shutil
from pathlib import Path

from exceptions import XSDGenerationError

logger = logging.getLogger(__name__)


def generate_dataclasses(xsd_file: str, temp_dir: Path = None, keep_temp: bool = False) -> tuple[str, Path]:
    """
    Generate Python dataclasses from XSD file using xsdata in a temporary directory.
    
    Args:
        xsd_file: Path to XSD or WSDL file
        temp_dir: Temporary directory for generation (will be created if None)
        keep_temp: If True, don't delete temp directory after processing
    
    Returns:
        Tuple of (module_name, temp_dir_path)
    
    Raises:
        XSDGenerationError: If xsdata generation fails
    """
    logger.info(f"Generating dataclasses from XSD/WSDL: {xsd_file}")
    
    # Create temporary directory if not provided
    if temp_dir is None:
        temp_dir = Path(".temp")
    
    # Clean generated_models subdirectory only (preserve downloads)
    temp_dir.mkdir(parents=True, exist_ok=True)
    dataclasses_dir = temp_dir / "generated_dataclasses"
    if dataclasses_dir.exists():
        shutil.rmtree(dataclasses_dir, ignore_errors=True)
    
    output_package = "generated_dataclasses"
    
    logger.info(f"Temp directory: {temp_dir}")
    logger.info(f"Output package: {output_package}")
    
    # Run xsdata generate command - it will create files in current dir, so we need to chdir
    cmd = ["xsdata", "generate", "-p", output_package, str(Path(xsd_file).absolute())]
    logger.debug(f"Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(temp_dir))
    
    if result.returncode != 0:
        error_msg = f"xsdata generation failed: {result.stderr}"
        logger.error(error_msg)
        if not keep_temp and temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise XSDGenerationError(error_msg)
    
    # Derive module name from XSD filename
    xsd_path = Path(xsd_file)
    module_name = xsd_path.stem.replace('-', '_').replace('.', '_')
    full_module = f"{output_package}.{module_name}"
    
    logger.info(f"Generated dataclasses in temp directory")
    logger.info(f"Module: {full_module}")
    if keep_temp:
        logger.info(f"Temp directory preserved: {temp_dir}")
    
    return full_module, temp_dir
