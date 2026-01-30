# python-zeep-codegen

A Python-based tool for converting WSDL/XSD definitions into modern, developer-friendly artifacts including Pydantic models and JSON Schemas.

## Overview

`python-zeep-codegen` bridges the gap between legacy SOAP/WSDL services and modern development workflows. It generates:

- **Python Dataclasses** from XSD schemas (via xsdata)
- **Pydantic Models** for data validation and type safety
- **JSON Schemas** for API documentation, form generation, and cross-platform compatibility
- **Interactive Web Forms** for visualizing and testing data structures

The tool is designed to work alongside [zeep](https://docs.python-zeep.org/) for SOAP operations while providing static type information and modern data validation.

## Features

✅ **Automated Pipeline**: Single command converts XSD → Dataclasses → Pydantic → JSON Schema  
✅ **Complex Structure Support**: Handles nested elements, arrays, enums, attributes, and mappings  
✅ **Unified Schema Generation**: Creates self-contained JSON Schema with `$defs` for all types  
✅ **Web Form Generation**: Auto-generate interactive forms from JSON Schemas using React JSON Schema Form  
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
1. Generate Python dataclasses in a temporary directory
2. Convert them to Pydantic models in `output/sample-complex/pydantic_models.py`
3. Generate unified JSON Schema in `output/sample-complex/schema.json`

### Generate Interactive Web Form

Add `--generate-ui` to create an interactive web form:

```bash
python wsdl_to_schema.py sample-complex.xsd --main-model Order --generate-ui
```

This generates:
- `output/sample-complex/ui/index.html` - Interactive form (open in browser)
- `output/sample-complex/ui/README.md` - Integration guide
- `output/sample-complex/ui/schema.json` - Schema reference (symlinked)

**Try it now**: Open `output/sample-complex/ui/index.html` in your browser to see the form!

![Web Form UI Screenshot](https://github.com/user-attachments/assets/1a89c859-211e-4053-b3c4-c3fd450ce45f)

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

### Pipeline with Optional Web UI

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│  XSD/WSDL   │─────────│  Dataclasses│─────────│   Pydantic  │─────────│    JSON     │
│    File     │ xsdata  │   (typed)   │ dynamic │   Models    │ builtin │   Schema    │
└─────────────┘         └─────────────┘         └─────────────┘         └──────┬──────┘
                                                                                │
                                                                                │ optional
                                                                                │ --generate-ui
                                                                                ▼
                                                                         ┌─────────────┐
                                                                         │  Web Form   │
                                                                         │     UI      │
                                                                         │   (React)   │
                                                                         └─────────────┘
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

**Step 4: JSON Schema → Web Form UI** (optional, via `--generate-ui`)
- Uses React JSON Schema Form (RJSF) library
- CDN-hosted dependencies (no build required)
- Generates standalone HTML with embedded schema
- Includes integration guide and customization instructions

### Generated Files

```
output/sample-complex/                  # Output directory (one per input file)
├── pydantic_models.py                  # Step 2: Pydantic models
├── schema.json                         # Step 3: JSON Schema
├── summary.json                        # Metadata and statistics
└── ui/                                 # Step 4: Web Form UI (optional)
    ├── index.html                      # Interactive form (open in browser)
    ├── schema.json                     # Schema reference (symlinked)
    └── README.md                       # Integration instructions
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

### Example 4: Generate Interactive Web Form

```bash
# Generate form with default settings (React JSON Schema Form)
python wsdl_to_schema.py order-system.xsd --main-model Order --generate-ui

# Specify UI framework explicitly
python wsdl_to_schema.py order-system.xsd --main-model Order --generate-ui --ui-framework react
```

**Generated UI Files:**
```
output/order-system/ui/
├── index.html       # Standalone interactive form (open in browser)
├── schema.json      # JSON Schema reference (symlinked)
└── README.md        # Integration instructions and customization guide
```

**Features of Generated Form:**
- ✅ Zero dependencies - CDN-hosted libraries
- ✅ Client-side validation from JSON Schema
- ✅ Mobile-responsive design
- ✅ Support for nested objects, arrays, enums
- ✅ Real-time validation feedback
- ✅ Easy integration into existing projects

**Customization:**
The generated `README.md` includes detailed instructions for:
- Customizing form styling
- Integrating into React/Vue/Angular projects
- Adding custom validation logic
- Connecting to backend APIs

## Command-Line Reference

```
usage: wsdl_to_schema.py [OPTIONS] INPUT_FILE

positional arguments:
  INPUT_FILE              Path to XSD/WSDL file or HTTP/HTTPS URL

required arguments:
  --main-model TEXT       Name of the main/root model for the unified schema
                          (e.g., Order, Customer)

optional arguments:
  --output-dir PATH       Output directory for all generated files
                          (default: output/[INPUT_NAME])
  --keep-temp             Keep temporary directory with generated dataclasses
                          (for debugging)
  -v, --verbose           Enable verbose debug output
  --generate-ui           Generate interactive web form UI from the JSON Schema
  --ui-framework [react]  UI framework to use for form generation
                          (default: react)
  --help                  Show this message and exit
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