"""
Pipeline module for JSON Schema generation from Pydantic models.

This module handles Step 3 of the conversion pipeline: taking Pydantic models
and generating a unified JSON Schema document with all type definitions in $defs.
"""
import logging
import json
from pathlib import Path
from typing import Dict, Type, Any, Optional, List

from exceptions import SchemaGenerationError

logger: logging.Logger = logging.getLogger(__name__)


def generate_json_schema(
    pydantic_models: Dict[str, Type[Any]],
    main_model_name: str,
    output_dir: Optional[Path] = None
) -> Path:
    """
    Generate unified JSON Schema from Pydantic models.
    
    Creates a single JSON Schema document with the main model as the root and all
    other types defined in the $defs section. This approach avoids duplication and
    provides a self-contained schema document.
    
    Args:
        pydantic_models: Dictionary mapping model names to Pydantic model classes
        main_model_name: Name of the main/root model to use as schema root
        output_dir: Directory to save schema file (default: 'schemas')
    
    Returns:
        Path to generated schema file
    
    Raises:
        SchemaGenerationError: If main model not found or schema generation fails
    
    Example:
        >>> models = {'Order': OrderModel, 'Customer': CustomerModel}
        >>> path = generate_json_schema(models, 'Order')
        >>> print(path)
        schemas/unified_schema.json
    """
    logger.info(f"Generating JSON Schema with main model: {main_model_name}")
    
    if main_model_name not in pydantic_models:
        available: str = ', '.join(pydantic_models.keys())
        error_msg: str = f"Model '{main_model_name}' not found. Available models: {available}"
        logger.error(error_msg)
        raise SchemaGenerationError(error_msg)
    
    main_model: Type[Any] = pydantic_models[main_model_name]
    
    # Generate unified schema
    schema: Dict[str, Any] = main_model.model_json_schema()
    
    # Ensure output directory exists and clean old schemas
    if output_dir:
        output_path: Path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        schema_path: Path = output_path / "schema.json"
    else:
        schema_path = Path("schemas") / "unified_schema.json"
        schema_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Remove old schema files in this directory
    if schema_path.parent.exists():
        for old_file in schema_path.parent.glob("*.json"):
            old_file.unlink()
            logger.debug(f"Removed old file: {old_file.name}")
    
    # Save schema
    with open(schema_path, 'w') as f:
        json.dump(schema, f, indent=2, default=str)
    
    logger.info(f"Generated unified schema: {schema_path}")
    
    if '$defs' in schema:
        logger.info(f"Main model: {main_model_name}")
        logger.info(f"Nested definitions: {len(schema['$defs'])} types")
        defs_list: List[str] = list(schema['$defs'].keys())
        types_summary: str = ', '.join(defs_list[:8])
        if len(defs_list) > 8:
            types_summary += f"... (+{len(defs_list) - 8} more)"
        logger.info(f"Types: {types_summary}")
    
    # Create summary file in same directory
    summary_file: Path = schema_path.parent / "summary.json"
    summary: Dict[str, Any] = {
        "main_model": main_model_name,
        "total_models": len(pydantic_models),
        "schema_file": str(schema_path),
        "nested_types": len(schema.get('$defs', {})),
        "models": list(pydantic_models.keys())
    }
    
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Created summary: {summary_file}")
    
    return schema_path
