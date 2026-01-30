"""
Pipeline module for generating JSON Schema from Pydantic models.
"""
import logging
import json
from pathlib import Path

from exceptions import SchemaGenerationError

logger = logging.getLogger(__name__)


def generate_json_schema(pydantic_models: dict, main_model_name: str, output_dir: Path = None) -> Path:
    """
    Generate unified JSON Schema from Pydantic models.
    
    Args:
        pydantic_models: Dictionary of Pydantic models
        main_model_name: Name of the main/root model
        output_dir: Directory to save schema file (default: 'schemas')
    
    Returns:
        Path to generated schema file
    
    Raises:
        SchemaGenerationError: If schema generation fails
    """
    logger.info(f"Generating JSON Schema with main model: {main_model_name}")
    
    if main_model_name not in pydantic_models:
        available = ', '.join(pydantic_models.keys())
        error_msg = f"Model '{main_model_name}' not found. Available models: {available}"
        logger.error(error_msg)
        raise SchemaGenerationError(error_msg)
    
    main_model = pydantic_models[main_model_name]
    
    # Generate unified schema
    schema = main_model.model_json_schema()
    
    # Ensure output directory exists and clean old schemas
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        schema_path = output_path / "schema.json"
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
        defs_list = list(schema['$defs'].keys())
        types_summary = ', '.join(defs_list[:8])
        if len(defs_list) > 8:
            types_summary += f"... (+{len(defs_list) - 8} more)"
        logger.info(f"Types: {types_summary}")
    
    # Create summary file in same directory
    summary_file = schema_path.parent / "summary.json"
    summary = {
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
