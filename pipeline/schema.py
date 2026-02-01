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


def generate_individual_schemas(
    pydantic_models: Dict[str, Type[Any]],
    output_dir: Optional[Path] = None
) -> Path:
    """
    Generate individual JSON Schema files for each Pydantic model.
    
    Creates separate JSON Schema files for each type, enabling VS Code users
    to edit JSON documents of any type (not just the root). Each schema file
    is self-contained with its own $defs for referenced types.
    
    This approach is better for VS Code authoring as it allows users to:
    - Create and edit JSON documents for any type
    - Get IntelliSense/validation for all types
    - Use $schema reference to any type-specific schema
    
    Args:
        pydantic_models: Dictionary mapping model names to Pydantic model classes
        output_dir: Directory to save schema files (default: 'schemas')
    
    Returns:
        Path to output directory containing all schema files
    
    Raises:
        SchemaGenerationError: If schema generation fails
    
    Example:
        >>> models = {'Order': OrderModel, 'Customer': CustomerModel}
        >>> path = generate_individual_schemas(models)
        >>> # Creates: schemas/Order.schema.json, schemas/Customer.schema.json
    """
    logger.info(f"Generating individual JSON Schemas for {len(pydantic_models)} models")
    
    # Determine output directory
    if output_dir:
        schema_dir: Path = Path(output_dir)
    else:
        schema_dir = Path("schemas")
    
    schema_dir.mkdir(parents=True, exist_ok=True)
    
    # Remove old schema files in this directory
    if schema_dir.exists():
        for old_file in schema_dir.glob("*.json"):
            old_file.unlink()
            logger.debug(f"Removed old file: {old_file.name}")
    
    # Generate a schema file for each model
    generated_files: List[Path] = []
    for model_name, model_class in pydantic_models.items():
        try:
            # Generate schema for this model
            schema: Dict[str, Any] = model_class.model_json_schema()
            
            # Save to individual file
            schema_file: Path = schema_dir / f"{model_name}.schema.json"
            with open(schema_file, 'w') as f:
                json.dump(schema, f, indent=2, default=str)
            
            generated_files.append(schema_file)
            logger.debug(f"Generated schema: {schema_file.name}")
            
        except Exception as e:
            error_msg: str = f"Failed to generate schema for '{model_name}': {e}"
            logger.error(error_msg)
            raise SchemaGenerationError(error_msg) from e
    
    logger.info(f"Generated {len(generated_files)} individual schema files")
    
    # Create index/summary file
    index_file: Path = schema_dir / "index.json"
    index_data: Dict[str, Any] = {
        "description": "Individual JSON Schemas for VS Code authoring",
        "generated_schemas": [f.name for f in generated_files],
        "total_schemas": len(generated_files),
        "usage": {
            "vscode": "Reference any schema with: {\"$schema\": \"./SchemaName.schema.json\"}",
            "example": f"To edit a {generated_files[0].stem.replace('.schema', '')} document, add: {{\"$schema\": \"./{generated_files[0].name}\"}}"
        }
    }
    
    with open(index_file, 'w') as f:
        json.dump(index_data, f, indent=2)
    
    logger.info(f"Created index: {index_file}")
    
    # Log summary
    schema_names: List[str] = [f.stem.replace('.schema', '') for f in generated_files]
    types_summary: str = ', '.join(schema_names[:8])
    if len(schema_names) > 8:
        types_summary += f"... (+{len(schema_names) - 8} more)"
    logger.info(f"Schemas: {types_summary}")
    
    return schema_dir
