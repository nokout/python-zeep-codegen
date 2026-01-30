#!/usr/bin/env python3
"""
WSDL/XSD to JSON Schema Converter

This is the main entry point for converting WSDL/XSD files to JSON Schemas.
It orchestrates the complete pipeline:
  1. Generate Python dataclasses from XSD using xsdata (in temp directory)
  2. Convert dataclasses to Pydantic models
  3. Generate unified JSON Schema with all type definitions

Usage:
    python wsdl_to_schema.py input.xsd --main-model Order
    python wsdl_to_schema.py input.xsd --main-model Order --keep-temp
"""
import click
import logging
import shutil
from pathlib import Path

from pipeline import (
    download_from_url,
    generate_dataclasses,
    convert_to_pydantic,
    generate_json_schema
)
from exceptions import WSDLSchemaError

logger = logging.getLogger(__name__)


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
    help='Output directory for all generated files (default: output/[INPUT_NAME])'
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
def main(input_file, main_model, output_dir, keep_temp, verbose):
    """Convert XSD/WSDL files to JSON Schema.

    INPUT_FILE can be:
      - Path to a local XSD file
      - Path to a local WSDL file  
      - HTTP/HTTPS URL to a remote WSDL/XSD

    Examples:

      Process local XSD file:
      
        python wsdl_to_schema.py sample-complex.xsd --main-model Order

      Process local WSDL file:
      
        python wsdl_to_schema.py service.wsdl --main-model OrderRequestType

      Process WSDL from HTTP URL:
      
        python wsdl_to_schema.py https://example.com/service?wsdl --main-model Order

      Keep temporary files for debugging:
      
        python wsdl_to_schema.py input.xsd --main-model Order --keep-temp

      With custom output directory:
      
        python wsdl_to_schema.py input.wsdl --main-model Request --output-dir custom_output
      
      Enable verbose logging:
      
        python wsdl_to_schema.py input.xsd --main-model Order --verbose
    """
    
    # Configure logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s: %(message)s'
    )
    
    # Check if input is URL or local file
    is_url = input_file.startswith(('http://', 'https://'))
    
    if is_url:
        # Download from URL
        try:
            input_file = download_from_url(input_file)
        except WSDLSchemaError as e:
            click.echo(f"❌ Error: {e}")
            raise click.Abort()
    else:
        # Validate local file exists
        input_file = Path(input_file)
        if not input_file.exists():
            click.echo(f"❌ Error: File not found: {input_file}")
            raise click.Abort()
        
        # Validate file type
        if input_file.suffix.lower() not in ['.xsd', '.wsdl']:
            logger.warning(f"File extension '{input_file.suffix}' is not .xsd or .wsdl")
            logger.warning("Proceeding anyway, but xsdata may not recognize the file format.")
    
    click.echo("\n" + "╔" + "═" * 68 + "╗")
    click.echo("║" + " " * 18 + "XSD/WSDL TO JSON SCHEMA" + " " * 27 + "║")
    click.echo("╚" + "═" * 68 + "╝")
    
    # Determine output directory
    if output_dir:
        output_dir = Path(output_dir)
    else:
        # Use input filename as output directory name (preserve original name)
        output_dir = Path("output") / input_file.stem
    
    temp_dir = None
    try:
        # Step 1: Generate dataclasses from XSD/WSDL to temp directory
        click.echo(f"\n{'='*70}")
        click.echo("Step 1: Generating Dataclasses from XSD/WSDL")
        click.echo(f"{'='*70}")
        module_name, temp_dir = generate_dataclasses(
            str(input_file), 
            keep_temp=keep_temp
        )
        
        # Step 2: Convert to Pydantic models
        click.echo(f"\n{'='*70}")
        click.echo("Step 2: Converting Dataclasses to Pydantic Models")
        click.echo(f"{'='*70}")
        pydantic_models, models_file = convert_to_pydantic(module_name, temp_dir, output_dir)
        
        # Step 3: Generate JSON Schema
        click.echo(f"\n{'='*70}")
        click.echo("Step 3: Generating JSON Schema")
        click.echo(f"{'='*70}")
        schema_file = generate_json_schema(pydantic_models, main_model, output_dir)
        
        # Final summary
        click.echo(f"\n{'='*70}")
        click.echo("✓ Conversion Complete!")
        click.echo(f"{'='*70}")
        click.echo(f"\nGenerated files:")
        click.echo(f"  • Pydantic models: {models_file}")
        click.echo(f"  • JSON Schema: {schema_file}")
        if temp_dir and keep_temp:
            click.echo(f"  • Temp directory: {temp_dir} (preserved)")
        file_type = input_file.suffix.upper().lstrip('.')
        source = 'URL' if is_url else 'File'
        click.echo(f"\nWorkflow: {source} ({file_type}) → Dataclass (xsdata) → Pydantic → JSON Schema")
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
