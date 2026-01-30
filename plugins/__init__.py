"""
Built-in output format plugins.

Provides standard output formats including JSON Schema and Pydantic code.
"""
import logging
import json
from pathlib import Path
from typing import Dict, Type, Any

from utils.plugins import OutputPlugin

logger: logging.Logger = logging.getLogger(__name__)


class JSONSchemaPlugin(OutputPlugin):
    """
    JSON Schema output plugin.
    
    Generates standard JSON Schema format from Pydantic models.
    This is the default output format.
    """
    
    name = "json_schema"
    description = "JSON Schema (default format)"
    
    def generate(
        self,
        pydantic_models: Dict[str, Type[Any]],
        main_model: str,
        output_path: Path,
        **options: Any
    ) -> Path:
        """
        Generate JSON Schema output.
        
        Args:
            pydantic_models: Dictionary of Pydantic model classes
            main_model: Name of the main/root model
            output_path: Path where schema should be written
            **options: Additional options (indent, ensure_ascii, etc.)
        
        Returns:
            Path to generated schema file
        """
        if main_model not in pydantic_models:
            available = ', '.join(pydantic_models.keys())
            raise ValueError(f"Model '{main_model}' not found. Available: {available}")
        
        model = pydantic_models[main_model]
        schema = model.model_json_schema()
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write schema
        indent = options.get('indent', 2)
        ensure_ascii = options.get('ensure_ascii', False)
        
        with open(output_path, 'w') as f:
            json.dump(schema, f, indent=indent, ensure_ascii=ensure_ascii, default=str)
        
        logger.info(f"Generated JSON Schema: {output_path}")
        return output_path


class PydanticCodePlugin(OutputPlugin):
    """
    Pydantic Python code output plugin.
    
    Generates Python source code with Pydantic model definitions.
    """
    
    name = "pydantic_code"
    description = "Pydantic Python source code"
    
    def generate(
        self,
        pydantic_models: Dict[str, Type[Any]],
        main_model: str,
        output_path: Path,
        **options: Any
    ) -> Path:
        """
        Generate Pydantic Python code output.
        
        Args:
            pydantic_models: Dictionary of Pydantic model classes
            main_model: Name of the main/root model
            output_path: Path where Python code should be written
            **options: Additional options
        
        Returns:
            Path to generated Python file
        """
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write('"""\nGenerated Pydantic Models\n\n')
            f.write('Auto-generated - do not edit manually.\n"""\n\n')
            f.write('from pydantic import BaseModel\n')
            f.write('from typing import Optional, List\n')
            f.write('from decimal import Decimal\n')
            f.write('from datetime import datetime, date\n\n')
            
            for name, model in pydantic_models.items():
                f.write(f"class {name}(BaseModel):\n")
                if model.model_fields:
                    for field_name, field_info in model.model_fields.items():
                        field_type = str(field_info.annotation).replace('typing.', '')
                        if field_info.is_required():
                            f.write(f"    {field_name}: {field_type}\n")
                        else:
                            default = field_info.default
                            if default is None:
                                f.write(f"    {field_name}: {field_type} = None\n")
                            else:
                                f.write(f"    {field_name}: {field_type} = {repr(default)}\n")
                else:
                    f.write("    pass\n")
                f.write("\n")
        
        logger.info(f"Generated Pydantic code: {output_path}")
        return output_path
