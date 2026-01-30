# python-zeep-codegen

A Python-based tool for converting WSDL/XSD definitions into modern, developer-friendly artifacts including Pydantic models and JSON Schemas.

## Overview

`python-zeep-codegen` bridges the gap between legacy SOAP/WSDL services and modern development workflows. It generates:

- **Python Dataclasses** from XSD schemas (via xsdata)
- **Pydantic Models** for data validation and type safety
- **JSON Schemas** for API documentation, form generation, and cross-platform compatibility

The tool is designed to work alongside [zeep](https://docs.python-zeep.org/) for SOAP operations while providing static type information and modern data validation.

## Features

✅ **Automated Pipeline**: Single command converts XSD → Dataclasses → Pydantic → JSON Schema  
✅ **Complex Structure Support**: Handles nested elements, arrays, enums, attributes, and mappings  
✅ **Unified Schema Generation**: Creates self-contained JSON Schema with `$defs` for all types  
✅ **Type Safety**: Full static type checking with mypy  
✅ **Zero Hardcoding**: Generic conversion logic works with any WSDL/XSD  
✅ **Coexistence Model**: Works alongside zeep for SOAP operations  
✅ **Configuration Files**: Support for YAML/TOML config files for default settings  
✅ **Plugin Architecture**: Extensible output format system  
✅ **Comprehensive Testing**: 39 passing tests with pytest  
✅ **Production Ready**: Context managers, proper error handling, logging  

## Installation

### Prerequisites

- Python 3.12+
- pip or uv package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/nokout/python-zeep-codegen.git
cd python-zeep-codegen

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

Convert an XSD file to JSON Schema in one command:

```bash
python wsdl_to_schema.py sample-complex.xsd --main-model Order
```

This will:
1. Generate Python dataclasses in `models/`
2. Convert them to Pydantic models in `generated/pydantic_models.py`
3. Generate unified JSON Schema in `schemas/unified_schema.json`

### With Custom Module Name

If you've already generated models or want to use a specific module:

```bash
python wsdl_to_schema.py input.xsd --main-model Customer --module custom.models
```

### With Custom Output Paths

```bash
python wsdl_to_schema.py input.xsd --main-model Order \
    --models-dir generated_models \
    --output-schema schemas/order_schema.json \
    --output-models generated/models.py
```

## Architecture

### Three-Step Pipeline

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│  XSD/WSDL   │─────────│  Dataclasses│─────────│   Pydantic  │─────────│    JSON     │
│    File     │ xsdata  │   (typed)   │ dynamic │   Models    │ builtin │   Schema    │
└─────────────┘         └─────────────┘         └─────────────┘         └─────────────┘
```

**Step 1: XSD → Dataclasses** (via xsdata)
- Uses `xsdata generate` CLI
- Produces Python dataclasses with type annotations
- Handles complex XSD structures (nested, arrays, enums, attributes)

**Step 2: Dataclasses → Pydantic Models** (dynamic conversion)
- Uses `dataclasses.fields()` for introspection
- Creates Pydantic models with `create_model()`
- Preserves types, defaults, and requirements
- Two-pass approach resolves forward references

**Step 3: Pydantic → JSON Schema** (Pydantic's built-in)
- Uses `model_json_schema()` 
- Generates unified schema with `$defs` section
- All types defined once, referenced via `$ref`
- Self-contained and portable

### Generated Files

```
project/
├── models/                          # Step 1 output
│   └── sample_complex.py           # xsdata-generated dataclasses
├── generated/                       # Step 2 output
│   └── pydantic_models.py          # Pydantic models (for reference)
└── schemas/                         # Step 3 output
    ├── unified_schema.json         # Main JSON Schema
    └── summary.json                # Metadata
```

## Usage Examples

### Example 1: Basic Order System

```bash
python wsdl_to_schema.py order-system.xsd --main-model Order
```

**Input**: `order-system.xsd` with OrderType, CustomerType, ProductType

**Output**: `schemas/unified_schema.json`
```json
{
  "$defs": {
    "CustomerType": { "properties": {...}, "required": [...] },
    "ProductType": { "properties": {...}, "required": [...] }
  },
  "properties": {
    "order_id": {"type": "string"},
    "customer": {"$ref": "#/$defs/CustomerType"},
    "items": {
      "type": "array",
      "items": {"$ref": "#/$defs/ProductType"}
    }
  },
  "required": ["order_id", "customer"],
  "type": "object"
}
```

### Example 2: Programmatic Usage

```python
from wsdl_to_schema import generate_dataclasses, convert_to_pydantic, generate_json_schema

# Step 1: Generate dataclasses
module_name = generate_dataclasses("input.xsd", "models")

# Step 2: Convert to Pydantic
pydantic_models, models_file = convert_to_pydantic(module_name)

# Step 3: Generate JSON Schema
schema_file = generate_json_schema(pydantic_models, "Order")
```

### Example 3: Integration with Zeep

```python
from zeep import Client
from models.sample_complex import OrderType
import dataclasses

# Use zeep for SOAP operations
client = Client('http://example.com/service?wsdl')
response = client.service.GetOrder(order_id="12345")

# Convert zeep response to dict
response_dict = dataclasses.asdict(response)

# Validate with generated Pydantic model
from generated.pydantic_models import Order
validated_order = Order(**response_dict)

# Use validated data
print(validated_order.model_dump_json())
```

## Command-Line Reference

```
usage: wsdl_to_schema.py [-h] --main-model MAIN_MODEL [--output-dir OUTPUT_DIR]
                          [--keep-temp] [--verbose] [--config CONFIG]
                          xsd_file

positional arguments:
  xsd_file              Path to XSD or WSDL file

required arguments:
  --main-model MAIN_MODEL
                        Name of the main/root model for the unified schema
                        (e.g., Order, Customer)

optional arguments:
  --output-dir OUTPUT_DIR
                        Output directory for all generated files
                        (default: output/[INPUT_NAME] or from config)
  --keep-temp           Keep temporary directory with generated dataclasses
                        (for debugging)
  --verbose, -v         Enable verbose debug output
  --config CONFIG       Path to configuration file (YAML or TOML)
                        If not specified, searches for .zeep-codegen.yaml/.toml
```

## Configuration Files

You can provide default values for CLI options using a configuration file. The tool automatically discovers `.zeep-codegen.yaml` or `.zeep-codegen.toml` in the current or parent directories.

### YAML Format (.zeep-codegen.yaml)

```yaml
# Output directory for generated files
output_dir: ./generated

# Keep temporary directory after conversion
keep_temp: false

# Enable verbose/debug logging
verbose: false

# HTTP timeout in seconds for downloading remote WSDL/XSD
timeout: 30
```

### TOML Format (.zeep-codegen.toml)

```toml
# Output directory for generated files
output_dir = "./generated"

# Keep temporary directory after conversion
keep_temp = false

# Enable verbose/debug logging
verbose = false

# HTTP timeout in seconds
timeout = 30
```

### Using Configuration

```bash
# Auto-discover config file in current/parent directories
python wsdl_to_schema.py input.xsd --main-model Order

# Specify config file explicitly
python wsdl_to_schema.py input.xsd --main-model Order --config my-config.yaml

# CLI arguments override config file values
python wsdl_to_schema.py input.xsd --main-model Order --verbose  # Overrides config
```

## Development

### Type Checking

The project uses mypy for static type checking:

```bash
# Run type checker
python -m mypy wsdl_to_schema.py pipeline/ utils/ plugins/ exceptions.py

# Type checking is configured in mypy.ini
```

### Testing

Comprehensive test suite with pytest:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_conversion.py

# Run with coverage
pytest --cov=pipeline --cov=utils

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

**Test Coverage:**
- 39 passing tests
- Unit tests for all pipeline modules
- Integration tests with real XSD files
- Mocked external dependencies (subprocess, requests)
- Context manager and error handling tests

## Plugin Architecture

The tool supports extensible output formats through a plugin system.

### Built-in Plugins

- **json_schema**: JSON Schema output (default)
- **pydantic_code**: Python source code with Pydantic models

### Creating Custom Plugins

```python
from utils.plugins import OutputPlugin, get_default_registry
from pathlib import Path
from typing import Dict, Type, Any

class MyCustomPlugin(OutputPlugin):
    name = "my_format"
    description = "My custom output format"
    
    def generate(
        self,
        pydantic_models: Dict[str, Type[Any]],
        main_model: str,
        output_path: Path,
        **options: Any
    ) -> Path:
        # Generate your custom format
        with open(output_path, 'w') as f:
            f.write("# My custom format\n")
            # ... your logic here
        return output_path

# Register the plugin
registry = get_default_registry()
registry.register(MyCustomPlugin())
```

## Advanced: Manual Step Execution

If you need to run steps separately, you can use xsdata directly and then the unified tool:

```bash
# Step 1: Generate dataclasses manually with xsdata
xsdata generate -p models your-schema.xsd

# Step 2 & 3: Use the unified tool with the pre-generated module
python wsdl_to_schema.py your-schema.xsd --main-model YourModel --module models.your_schema
```

## Research & Development

This project includes comprehensive research documentation:

- **[RESEARCH_FINDINGS.md](RESEARCH_FINDINGS.md)**: Detailed analysis of the conversion pipeline, technical challenges, and solutions
- **[research-plan.md](research-plan.md)**: Original research plan and progress tracking
- **[xsdata-research-findings.md](xsdata-research-findings.md)**: xsdata tool evaluation

### Key Technical Achievements

1. **Generic Conversion**: Zero hardcoded models - works with any XSD structure
2. **Forward Reference Resolution**: Two-pass model building with comprehensive namespace
3. **Unified Schema**: Single JSON Schema file with `$defs` for all types (no duplication)
4. **Enum Handling**: Preserves original Enum classes in Pydantic models

### Future Work

- ⏳ **Zeep Runtime Integration Testing**: Validate coexistence model with actual SOAP services
- ⏳ **Web Form Generation**: Research Angular JSON Schema form libraries
- ⏳ **WSDL Service/Binding Handling**: Extend beyond XSD type definitions

## Project Structure

```
python-zeep-codegen/
├── wsdl_to_schema.py              # Main CLI entry point
├── exceptions.py                   # Custom exception hierarchy
├── pipeline/                       # Pipeline modules
│   ├── __init__.py
│   ├── download.py                # URL download functionality
│   ├── generate.py                # xsdata dataclass generation
│   ├── convert.py                 # Dataclass to Pydantic conversion
│   └── schema.py                  # JSON Schema generation
├── utils/                          # Shared utilities
│   ├── __init__.py
│   ├── conversion.py              # Conversion helpers
│   ├── temp_manager.py            # Context managers for resources
│   ├── config.py                  # Configuration file support
│   └── plugins.py                 # Plugin architecture
├── plugins/                        # Output format plugins
│   └── __init__.py                # Built-in plugins (JSON Schema, Pydantic)
├── tests/                          # Test suite
│   ├── conftest.py                # Test fixtures
│   ├── test_*.py                  # Unit and integration tests
│   └── ...
├── output/                         # Generated outputs (not in repo)
├── .temp/                          # Temporary files (not in repo)
├── sample-complex.xsd             # Example XSD for testing
├── sample.wsdl                    # Example WSDL for testing
├── requirements.txt               # Python dependencies
├── mypy.ini                       # Type checker configuration
├── pytest.ini                     # Test configuration
├── .zeep-codegen.example.yaml    # Example YAML config
├── .zeep-codegen.example.toml    # Example TOML config
├── README.md                      # This file
└── RESEARCH_FINDINGS.md           # Technical documentation
```

## Contributing

Contributions are welcome! The project now has:

- **Type Safety**: Full mypy type checking with strict settings
- **Test Coverage**: 39 passing tests covering core functionality
- **Plugin Architecture**: Easy to add new output formats
- **Configuration System**: YAML/TOML config file support

### Development Setup

```bash
# Install dependencies including dev tools
pip install -r requirements.txt

# Run type checking
python -m mypy wsdl_to_schema.py pipeline/ utils/ plugins/ exceptions.py

# Run tests
pytest -v

# Run tests with coverage
pytest --cov=pipeline --cov=utils
```

### Areas for Improvement

- Support for WSDL 2.0 service definitions
- Additional output formats (OpenAPI, GraphQL schemas)
- Performance optimizations (caching, streaming)
- Enhanced error messages and validation
- CI/CD pipeline integration

## License

See [LICENSE](LICENSE) for details.

## References

- [xsdata Documentation](https://xsdata.readthedocs.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [zeep Documentation](https://docs.python-zeep.org/)
- [JSON Schema Specification](https://json-schema.org/)

---

**Author**: nokout  
**Repository**: [python-zeep-codegen](https://github.com/nokout/python-zeep-codegen)


Currently, the project focuses on:
- Generating schemas that are easier to use in contemporary codebases.
- Potentially creating proxies and web forms to simplify interactions with web services.