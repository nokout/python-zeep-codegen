#!/usr/bin/env python3
"""
WSDL/XSD to JSON Schema Converter

Main entry point for converting WSDL/XSD files to JSON Schemas with Pydantic models.
Orchestrates a three-step pipeline:
  1. Generate Python dataclasses from XSD using xsdata (in temp directory)
  2. Convert dataclasses to Pydantic models with validation
  3. Generate unified JSON Schema with all type definitions

The tool supports local files and HTTP/HTTPS URLs, with comprehensive error handling
and optional debug modes for investigating conversion issues.

Configuration can be provided via YAML/TOML files (.zeep-codegen.yaml or .zeep-codegen.toml)
in the current directory or parent directories.

Usage:
    python wsdl_to_schema.py input.xsd --main-model Order
    python wsdl_to_schema.py https://example.com/service.wsdl --main-model Request
    python wsdl_to_schema.py input.xsd --main-model Order --keep-temp --verbose
"""
import click
import logging
import shutil
from pathlib import Path
from typing import Optional

from pipeline import (
    download_from_url,
    generate_dataclasses,
    convert_to_pydantic,
    generate_json_schema,
    generate_individual_schemas
)
from exceptions import WSDLSchemaError
from utils.config import Config

logger: logging.Logger = logging.getLogger(__name__)


@click.command()
@click.argument('input_file', type=click.Path())
@click.option(
    '--main-model',
    required=True,
    help='Name of the main/root model for the unified schema (e.g., Order, Customer)'
)
@click.option(
    '--output-dir',
    type=click.Path(),
    help='Output directory for all generated files (default: output/[INPUT_NAME] or from config)'
)
@click.option(
    '--keep-temp',
    is_flag=True,
    help='Keep temporary directory with generated dataclasses (for debugging)'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Enable verbose debug output'
)
@click.option(
    '--config',
    type=click.Path(exists=True),
    help='Path to configuration file (YAML or TOML). If not specified, searches for .zeep-codegen.yaml/.toml'
)
@click.option(
    '--individual-schemas',
    is_flag=True,
    help='Generate individual schema files for each type (better for VS Code editing)'
)
def main(
    input_file: str,
    main_model: str,
    output_dir: Optional[str],
    keep_temp: bool,
    verbose: bool,
    config: Optional[str],
    individual_schemas: bool
) -> None:
    """Convert XSD/WSDL files to JSON Schema.

    INPUT_FILE can be:
      - Path to a local XSD file
      - Path to a local WSDL file  
      - HTTP/HTTPS URL to a remote WSDL/XSD

    Configuration files (.zeep-codegen.yaml or .zeep-codegen.toml) can provide
    default values for options. CLI arguments override config file values.

    Examples:

      Process local XSD file:
      
        python wsdl_to_schema.py tests/sample.xsd --main-model Order

      Process local WSDL file:
      
        python wsdl_to_schema.py service.wsdl --main-model OrderRequestType

      Process WSDL from HTTP URL:
      
        python wsdl_to_schema.py https://example.com/service?wsdl --main-model Order

      Generate individual schemas for VS Code editing:
      
        python wsdl_to_schema.py input.xsd --main-model Order --individual-schemas

      Keep temporary files for debugging:
      
        python wsdl_to_schema.py input.xsd --main-model Order --keep-temp

      With custom output directory:
      
        python wsdl_to_schema.py input.wsdl --main-model Request --output-dir custom_output
        
      With config file:
      
        python wsdl_to_schema.py input.xsd --main-model Order --config my-config.yaml
      
      Enable verbose logging:
      
        python wsdl_to_schema.py input.xsd --main-model Order --verbose
    """
    
    # Load configuration
    cfg: Optional[Config] = None
    if config:
        # Load specified config file
        try:
            cfg = Config.load_from_file(Path(config))
            click.echo(f"✓ Loaded config from {config}")
        except Exception as e:
            click.echo(f"⚠ Warning: Could not load config file: {e}")
    else:
        # Try to discover config file
        cfg = Config.discover()
        if cfg:
            click.echo("✓ Using discovered config file")
    
    # Apply config defaults (CLI args take precedence)
    if cfg:
        if output_dir is None and cfg.get('output_dir'):
            output_dir = cfg.get('output_dir')
        if not keep_temp:
            keep_temp = bool(cfg.get('keep_temp', False))
        if not verbose:
            verbose = bool(cfg.get('verbose', False))
    
    # Configure logging
    log_level: int = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s: %(message)s'
    )
    
    # Check if input is URL or local file
    is_url: bool = input_file.startswith(('http://', 'https://'))
    
    if is_url:
        # Download from URL
        try:
            downloaded_path: Path = download_from_url(input_file)
            input_file = str(downloaded_path)
        except WSDLSchemaError as e:
            click.echo(f"❌ Error: {e}")
            raise click.Abort()
    else:
        # Validate local file exists
        input_path: Path = Path(input_file)
        if not input_path.exists():
            click.echo(f"❌ Error: File not found: {input_file}")
            raise click.Abort()
        
        # Validate file type
        if input_path.suffix.lower() not in ['.xsd', '.wsdl']:
            logger.warning(f"File extension '{input_path.suffix}' is not .xsd or .wsdl")
            logger.warning("Proceeding anyway, but xsdata may not recognize the file format.")
    
    click.echo("\n" + "╔" + "═" * 68 + "╗")
    click.echo("║" + " " * 18 + "XSD/WSDL TO JSON SCHEMA" + " " * 27 + "║")
    click.echo("╚" + "═" * 68 + "╝")
    
    # Determine output directory
    final_output_dir: Path
    if output_dir:
        final_output_dir = Path(output_dir)
    else:
        # Use input filename as output directory name (preserve original name)
        final_output_dir = Path("output") / Path(input_file).stem
    
    temp_dir: Optional[Path] = None
    try:
        # Step 1: Generate dataclasses from XSD/WSDL to temp directory
        click.echo(f"\n{'='*70}")
        click.echo("Step 1: Generating Dataclasses from XSD/WSDL")
        click.echo(f"{'='*70}")
        module_name: str
        module_name, temp_dir = generate_dataclasses(
            str(input_file), 
            keep_temp=keep_temp
        )
        
        # Step 2: Convert to Pydantic models
        click.echo(f"\n{'='*70}")
        click.echo("Step 2: Converting Dataclasses to Pydantic Models")
        click.echo(f"{'='*70}")
        pydantic_models, models_file = convert_to_pydantic(
            module_name, temp_dir, final_output_dir
        )
        
        # Step 3: Generate JSON Schema
        click.echo(f"\n{'='*70}")
        click.echo("Step 3: Generating JSON Schema")
        click.echo(f"{'='*70}")
        
        schema_file: Path
        schema_dir: Path
        
        if individual_schemas:
            # Generate individual schema files for each type
            schema_dir = generate_individual_schemas(
                pydantic_models, final_output_dir
            )
            schema_file = schema_dir / "index.json"
        else:
            # Generate unified schema with main model as root
            schema_file = generate_json_schema(
                pydantic_models, main_model, final_output_dir
            )
            schema_dir = schema_file.parent
        
        # Final summary
        click.echo(f"\n{'='*70}")
        click.echo("✓ Conversion Complete!")
        click.echo(f"{'='*70}")
        click.echo(f"\nGenerated files:")
        click.echo(f"  • Pydantic models: {models_file}")
        if individual_schemas:
            click.echo(f"  • JSON Schemas (individual): {schema_dir}")
            click.echo(f"    - Generated {len(pydantic_models)} schema files")
            click.echo(f"    - Each type can be edited in VS Code with IntelliSense")
        else:
            click.echo(f"  • JSON Schema (unified): {schema_file}")
        if temp_dir and keep_temp:
            click.echo(f"  • Temp directory: {temp_dir} (preserved)")
        file_type: str = Path(input_file).suffix.upper().lstrip('.')
        source: str = 'URL' if is_url else 'File'
        mode_desc: str = "Individual Schemas" if individual_schemas else "Unified Schema"
        click.echo(f"\nWorkflow: {source} ({file_type}) → Dataclass (xsdata) → Pydantic → {mode_desc}")
        click.echo()
    
    except WSDLSchemaError as e:
        click.echo(f"\n❌ Error: {e}")
        logger.debug("Exception details:", exc_info=True)
        raise click.Abort()
    
    finally:
        # Clean up temporary directory unless --keep-temp is specified
        if temp_dir and not keep_temp:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
                logger.info("Cleaned up temporary directory")
            except Exception as e:
                logger.warning(f"Could not clean up temp directory: {e}")


if __name__ == "__main__":
    main()
