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
import argparse
import subprocess
import sys
import importlib
import inspect
import json
import tempfile
import shutil
import requests
from pathlib import Path
from dataclasses import is_dataclass
from decimal import Decimal
from datetime import datetime, date
from enum import Enum
from urllib.parse import urlparse

from pydantic import BaseModel
from xsdata.models.datatype import XmlDate, XmlDateTime

from utils.conversion import dataclass_to_pydantic_model


def download_from_url(url: str, timeout: int = 30) -> Path:
    """
    Download XSD/WSDL file from HTTP/HTTPS URL to temporary location.
    
    Args:
        url: HTTP/HTTPS URL to download from
        timeout: Request timeout in seconds
    
    Returns:
        Path to downloaded file in temp directory
    """
    print(f"\n{'='*70}")
    print("Downloading from URL")
    print(f"{'='*70}")
    print(f"  URL: {url}")
    
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        # Determine filename from URL or Content-Disposition header
        parsed_url = urlparse(url)
        filename = Path(parsed_url.path).name
        
        # If no filename in URL, use generic name based on content type
        if not filename or '.' not in filename:
            content_type = response.headers.get('content-type', '')
            if 'xml' in content_type.lower() or 'wsdl' in url.lower():
                filename = 'downloaded.wsdl' if 'wsdl' in url.lower() else 'downloaded.xsd'
            else:
                filename = 'downloaded.xml'
        
        # Save to temp directory (use downloads subdirectory to avoid conflicts)
        temp_dir = Path(".temp")
        downloads_dir = temp_dir / "downloads"
        downloads_dir.mkdir(parents=True, exist_ok=True)
        file_path = downloads_dir / filename
        
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        print(f"  ✓ Downloaded: {filename} ({len(response.content)} bytes)")
        print(f"  ✓ Saved to: {file_path}")
        
        return file_path
        
    except requests.exceptions.Timeout:
        print(f"\n❌ Error: Request timed out after {timeout} seconds")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Error: Could not connect to {url}")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ Error: HTTP {e.response.status_code} - {e.response.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error downloading file: {e}")
        sys.exit(1)


def generate_dataclasses(xsd_file: str, temp_dir: Path = None, keep_temp: bool = False) -> tuple[str, Path]:
    """
    Generate Python dataclasses from XSD file using xsdata in a temporary directory.
    
    Args:
        xsd_file: Path to XSD or WSDL file
        temp_dir: Temporary directory for generation (will be created if None)
        keep_temp: If True, don't delete temp directory after processing
    
    Returns:
        Tuple of (module_name, temp_dir_path)
    """
    print(f"\n{'='*70}")
    print("Step 1: Generating Dataclasses from XSD/WSDL")
    print(f"{'='*70}")
    print(f"  Input: {xsd_file}")
    
    # Create temporary directory if not provided
    if temp_dir is None:
        temp_dir = Path(".temp")
    
    # Clean generated_models subdirectory only (preserve downloads)
    temp_dir.mkdir(parents=True, exist_ok=True)
    dataclasses_dir = temp_dir / "generated_dataclasses"
    if dataclasses_dir.exists():
        shutil.rmtree(dataclasses_dir, ignore_errors=True)
    
    output_package = "generated_dataclasses"
    
    print(f"  Temp directory: {temp_dir}")
    print(f"  Output package: {output_package}")
    
    # Run xsdata generate command - it will create files in current dir, so we need to chdir
    cmd = ["xsdata", "generate", "-p", output_package, str(Path(xsd_file).absolute())]
    print(f"  Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(temp_dir))
    
    if result.returncode != 0:
        print(f"\n❌ Error running xsdata:")
        print(result.stderr)
        if not keep_temp and temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        sys.exit(1)
    
    # Derive module name from XSD filename
    xsd_path = Path(xsd_file)
    module_name = xsd_path.stem.replace('-', '_').replace('.', '_')
    full_module = f"{output_package}.{module_name}"
    
    print(f"  ✓ Generated dataclasses in temp directory")
    print(f"  ✓ Module: {full_module}")
    if keep_temp:
        print(f"  ℹ️ Temp directory preserved: {temp_dir}")
    
    return full_module, temp_dir


def convert_to_pydantic(module_name: str, temp_dir: Path, output_dir: Path = None) -> tuple[dict, Path]:
    """
    Convert dataclasses from module to Pydantic models.
    
    Args:
        module_name: Fully qualified module name (e.g., 'generated_dataclasses.sample_complex')
        temp_dir: Temporary directory containing generated modules
        output_dir: Directory where Pydantic models file should be saved
    
    Returns:
        Tuple of (pydantic_models dict, models_output_path)
    """
    print(f"\n{'='*70}")
    print("Step 2: Converting Dataclasses to Pydantic Models")
    print(f"{'='*70}")
    print(f"  Module: {module_name}")
    
    # Add temp directory to sys.path for import
    sys.path.insert(0, str(temp_dir))
    
    try:
        # Import the module
        try:
            module = importlib.import_module(module_name)
        except ImportError as e:
            print(f"\n❌ Error importing module '{module_name}': {e}")
            sys.exit(1)
        
        # Find all dataclasses
        dataclass_types = []
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and is_dataclass(obj):
                dataclass_types.append((name, obj))
        
        print(f"  Found {len(dataclass_types)} dataclasses")
        
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
                print(f"    ✓ {name}")
            except Exception as e:
                print(f"    ✗ Failed to convert {name}: {e}")
        
        # Second pass: Rebuild models to resolve forward references
        print(f"  Rebuilding models to resolve forward references...")
        for name, model in pydantic_models.items():
            try:
                model.model_rebuild(_types_namespace=model_namespace)
            except Exception as e:
                print(f"    Warning: Could not rebuild {name}: {e}")
        
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
        
        print(f"  ✓ Converted {len(pydantic_models)} models")
        print(f"  ✓ Saved to {models_file}")
        
        return pydantic_models, models_file
    
    finally:
        # Remove temp dir from sys.path
        if str(temp_dir) in sys.path:
            sys.path.remove(str(temp_dir))


def generate_json_schema(pydantic_models: dict, main_model_name: str, output_dir: Path = None) -> Path:
    """
    Generate unified JSON Schema from Pydantic models.
    
    Args:
        pydantic_models: Dictionary of Pydantic models
        main_model_name: Name of the main/root model
        output_dir: Directory to save schema file (default: 'schemas')
    
    Returns:
        Path to generated schema file
    """
    print(f"\n{'='*70}")
    print("Step 3: Generating JSON Schema")
    print(f"{'='*70}")
    print(f"  Main model: {main_model_name}")
    
    if main_model_name not in pydantic_models:
        available = ', '.join(pydantic_models.keys())
        print(f"\n❌ Error: Model '{main_model_name}' not found")
        print(f"Available models: {available}")
        sys.exit(1)
    
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
            print(f"  Removed old file: {old_file.name}")
    
    # Save schema
    with open(schema_path, 'w') as f:
        json.dump(schema, f, indent=2, default=str)
    
    print(f"  ✓ Generated unified schema: {schema_path}")
    
    if '$defs' in schema:
        print(f"  ✓ Main model: {main_model_name}")
        print(f"  ✓ Nested definitions: {len(schema['$defs'])} types")
        defs_list = list(schema['$defs'].keys())
        print(f"  ✓ Types: {', '.join(defs_list[:8])}" + 
              (f"... (+{len(defs_list) - 8} more)" if len(defs_list) > 8 else ""))
    
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
    
    print(f"  ✓ Created summary: {summary_file}")
    
    return schema_path


def main():
    parser = argparse.ArgumentParser(
        description="Convert XSD/WSDL files to JSON Schema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  # Process local XSD file
  python wsdl_to_schema.py sample-complex.xsd --main-model Order
  
  # Process local WSDL file
  python wsdl_to_schema.py service.wsdl --main-model OrderRequestType
  
  # Process WSDL from HTTP URL
  python wsdl_to_schema.py https://example.com/service?wsdl --main-model Order
  
  # Keep temporary files for debugging
  python wsdl_to_schema.py input.xsd --main-model Order --keep-temp
  
  # With custom output directory
  python wsdl_to_schema.py input.wsdl --main-model Request \\
      --output-dir custom_output
"""
    )
    
    parser.add_argument(
        'input_file',
        metavar='FILE',
        help='Path to XSD/WSDL file or HTTP/HTTPS URL'
    )
    
    parser.add_argument(
        '--main-model',
        required=True,
        help='Name of the main/root model for the unified schema (e.g., Order, Customer)'
    )
    
    parser.add_argument(
        '--output-dir',
        help='Output directory for all generated files (default: output/[INPUT_NAME])'
    )
    
    parser.add_argument(
        '--keep-temp',
        action='store_true',
        help='Keep temporary directory with generated dataclasses (for debugging)'
    )
    
    args = parser.parse_args()
    
    # Check if input is URL or local file
    is_url = args.input_file.startswith(('http://', 'https://'))
    
    if is_url:
        # Download from URL
        input_file = download_from_url(args.input_file)
    else:
        # Validate local file exists
        input_file = Path(args.input_file)
        if not input_file.exists():
            print(f"❌ Error: File not found: {args.input_file}")
            sys.exit(1)
        
        # Validate file type
        if input_file.suffix.lower() not in ['.xsd', '.wsdl']:
            print(f"⚠️  Warning: File extension '{input_file.suffix}' is not .xsd or .wsdl")
            print(f"    Proceeding anyway, but xsdata may not recognize the file format.")
    
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 18 + "XSD/WSDL TO JSON SCHEMA" + " " * 27 + "║")
    print("╚" + "═" * 68 + "╝")
    
    # Determine output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        # Use input filename as output directory name (preserve original name)
        output_dir = Path("output") / input_file.stem
    
    temp_dir = None
    try:
        # Step 1: Generate dataclasses from XSD/WSDL to temp directory
        module_name, temp_dir = generate_dataclasses(
            str(input_file), 
            keep_temp=args.keep_temp
        )
        
        # Step 2: Convert to Pydantic models
        pydantic_models, models_file = convert_to_pydantic(module_name, temp_dir, output_dir)
        
        # Step 3: Generate JSON Schema
        schema_file = generate_json_schema(pydantic_models, args.main_model, output_dir)
        
        # Final summary
        print(f"\n{'='*70}")
        print("✓ Conversion Complete!")
        print(f"{'='*70}")
        print(f"\nGenerated files:")
        print(f"  • Pydantic models: {models_file}")
        print(f"  • JSON Schema: {schema_file}")
        if temp_dir and args.keep_temp:
            print(f"  • Temp directory: {temp_dir} (preserved)")
        file_type = input_file.suffix.upper().lstrip('.')
        source = 'URL' if is_url else 'File'
        print(f"\nWorkflow: {source} ({file_type}) → Dataclass (xsdata) → Pydantic → JSON Schema")
        print()
    
    finally:
        # Clean up temporary directory unless --keep-temp is specified
        if temp_dir and not args.keep_temp:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
                print(f"  ✓ Cleaned up temporary directory")
            except Exception as e:
                print(f"  ⚠️ Warning: Could not clean up temp directory: {e}")


if __name__ == "__main__":
    main()
