"""
Pipeline module for converting dataclasses to Pydantic models.
"""
import logging
import sys
import importlib
import inspect
from pathlib import Path
from dataclasses import is_dataclass
from decimal import Decimal
from datetime import datetime, date
from enum import Enum

from xsdata.models.datatype import XmlDate, XmlDateTime

from exceptions import ConversionError
from utils.conversion import dataclass_to_pydantic_model

logger = logging.getLogger(__name__)


def convert_to_pydantic(module_name: str, temp_dir: Path, output_dir: Path = None) -> tuple[dict, Path]:
    """
    Convert dataclasses from module to Pydantic models.
    
    Args:
        module_name: Fully qualified module name (e.g., 'generated_dataclasses.sample_complex')
        temp_dir: Temporary directory containing generated modules
        output_dir: Directory where Pydantic models file should be saved
    
    Returns:
        Tuple of (pydantic_models dict, models_output_path)
    
    Raises:
        ConversionError: If conversion fails
    """
    logger.info(f"Converting dataclasses to Pydantic models from module: {module_name}")
    
    # Add temp directory to sys.path for import
    sys.path.insert(0, str(temp_dir))
    
    try:
        # Import the module
        try:
            module = importlib.import_module(module_name)
        except ImportError as e:
            error_msg = f"Error importing module '{module_name}': {e}"
            logger.error(error_msg)
            raise ConversionError(error_msg)
        
        # Find all dataclasses
        dataclass_types = []
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and is_dataclass(obj):
                dataclass_types.append((name, obj))
        
        logger.info(f"Found {len(dataclass_types)} dataclasses")
        
        # Create namespace for all types (needed for forward references)
        model_namespace = {
            'Decimal': Decimal,
            'XmlDate': XmlDate,
            'XmlDateTime': XmlDateTime,
            'datetime': datetime,
            'date': date,
            'Enum': Enum
        }
        
        # Add all classes from module to namespace
        for name in dir(module):
            if not name.startswith('_'):
                obj = getattr(module, name)
                if inspect.isclass(obj):
                    model_namespace[name] = obj
        
        # First pass: Create all Pydantic models
        pydantic_models = {}
        for name, dataclass_type in dataclass_types:
            try:
                pydantic_model = dataclass_to_pydantic_model(dataclass_type, name)
                pydantic_models[name] = pydantic_model
                model_namespace[name] = pydantic_model
                logger.debug(f"Converted: {name}")
            except Exception as e:
                logger.warning(f"Failed to convert {name}: {e}")
        
        # Second pass: Rebuild models to resolve forward references
        logger.info("Rebuilding models to resolve forward references...")
        for name, model in pydantic_models.items():
            try:
                model.model_rebuild(_types_namespace=model_namespace)
            except Exception as e:
                logger.warning(f"Could not rebuild {name}: {e}")
        
        # Save Pydantic models to Python file
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            models_file = output_path / "pydantic_models.py"
        else:
            models_file = Path("generated") / "pydantic_models.py"
            models_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(models_file, 'w') as f:
            f.write('"""\nGenerated Pydantic Models\n\n')
            f.write(f'Auto-generated from module: {module_name}\n')
            f.write('Do not edit manually.\n"""\n\n')
            f.write('from pydantic import BaseModel\n')
            f.write('from typing import Optional, List\n')
            f.write('from decimal import Decimal\n')
            f.write('from datetime import datetime, date\n')
            f.write('from enum import Enum\n')
            f.write(f'from {module_name} import *\n\n')
            
            for name, model in pydantic_models.items():
                # Get field definitions
                fields_str = []
                for field_name, field_info in model.model_fields.items():
                    field_type = str(field_info.annotation).replace('typing.', '')
                    if field_info.is_required():
                        fields_str.append(f"    {field_name}: {field_type}")
                    else:
                        default = field_info.default
                        if default is None:
                            fields_str.append(f"    {field_name}: {field_type} = None")
                        else:
                            fields_str.append(f"    {field_name}: {field_type} = {repr(default)}")
                
                f.write(f"class {name}(BaseModel):\n")
                if fields_str:
                    f.write('\n'.join(fields_str))
                    f.write('\n\n')
                else:
                    f.write("    pass\n\n")
        
        logger.info(f"Converted {len(pydantic_models)} models")
        logger.info(f"Saved to {models_file}")
        
        return pydantic_models, models_file
    
    finally:
        # Remove temp dir from sys.path
        if str(temp_dir) in sys.path:
            sys.path.remove(str(temp_dir))
