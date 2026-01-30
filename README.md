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
usage: wsdl_to_schema.py [-h] --main-model MAIN_MODEL [--module MODULE]
                          [--models-dir MODELS_DIR]
                          [--output-schema OUTPUT_SCHEMA]
                          [--output-models OUTPUT_MODELS]
                          xsd_file

positional arguments:
  xsd_file              Path to XSD or WSDL file

required arguments:
  --main-model MAIN_MODEL
                        Name of the main/root model for the unified schema
                        (e.g., Order, Customer)

optional arguments:
  --module MODULE       Python module name for generated models
                        (default: auto-detect from XSD filename)
  --models-dir MODELS_DIR
                        Directory for generated dataclass models
                        (default: models)
  --output-schema OUTPUT_SCHEMA
                        Output path for JSON Schema
                        (default: schemas/unified_schema.json)
  --output-models OUTPUT_MODELS
                        Output path for Pydantic models
                        (default: generated/pydantic_models.py)
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
├── wsdl_to_schema.py              # Main entry point (unified pipeline)
├── utils/                          # Shared utilities
│   ├── __init__.py
│   └── conversion.py              # Shared conversion logic
├── models/                         # Generated dataclasses (xsdata output)
├── generated/                      # Generated Pydantic models
├── schemas/                        # Generated JSON Schemas
├── sample-complex.xsd             # Example XSD for testing
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── RESEARCH_FINDINGS.md           # Technical documentation
└── research-plan.md               # Research roadmap
```

## Contributing

Contributions are welcome! Areas for improvement:

- Support for WSDL 2.0 service definitions
- Streaming/batch processing for large schemas
- Additional output formats (OpenAPI, GraphQL schemas)
- Enhanced error messages and validation
- Automated testing suite

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