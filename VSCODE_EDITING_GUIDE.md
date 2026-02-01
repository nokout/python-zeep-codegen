# VS Code Editing Guide

This guide explains how to use the `--individual-schemas` option to enable full VS Code support for editing JSON documents of any type defined in your XSD/WSDL.

## The Problem

When using the default unified schema mode, only the root type (specified by `--main-model`) can be edited with full VS Code IntelliSense. Types defined in the `$defs` section are not directly editable as top-level documents.

**Example Issue:**
If you generate a schema for an Order system with types like Order, Customer, and Product, you can only edit Order documents with autocomplete. To edit a standalone Customer or Product JSON, you'd need manual workarounds.

## The Solution: Individual Schemas

Use the `--individual-schemas` flag to generate a separate schema file for each type:

```bash
python wsdl_to_schema.py your-schema.xsd --main-model Order --individual-schemas
```

This creates:
- `Order.schema.json`
- `CustomerType.schema.json`
- `ProductType.schema.json`
- ... (one file per type)
- `index.json` (metadata and usage instructions)

## Using Individual Schemas in VS Code

### Step 1: Generate Individual Schemas

```bash
python wsdl_to_schema.py tests/sample.xsd --main-model Order \
    --output-dir ./schemas --individual-schemas
```

### Step 2: Create a JSON Document

Create a new `.json` file and add a `$schema` reference at the top:

**customer.json:**
```json
{
  "$schema": "./schemas/CustomerType.schema.json",
  "customer_id": "",
  "name": "",
  "contact": {
    
  }
}
```

### Step 3: Enjoy IntelliSense

As you type, VS Code will:
- ✅ Suggest valid property names
- ✅ Show expected types (string, number, boolean, etc.)
- ✅ Validate required vs. optional fields
- ✅ Display hover documentation from the schema
- ✅ Highlight errors for invalid values or missing required fields
- ✅ Offer autocomplete for nested objects

## Features in VS Code

### Autocomplete
Type a few characters and press `Ctrl+Space` to see suggestions:
- Property names from the schema
- Enum values (if the field is an enum)
- Valid types and structures

### Validation
VS Code validates your JSON in real-time:
- **Red squiggles** for errors (invalid types, unknown properties)
- **Yellow squiggles** for warnings
- Hover over squiggles to see detailed error messages

### Hover Documentation
Hover over property names to see:
- Type information
- Whether the field is required
- Default values (if specified)
- Descriptions (if present in the schema)

### Quick Fix
When VS Code detects an error, click the lightbulb icon or press `Ctrl+.` for quick fixes like:
- Remove invalid properties
- Add missing required properties
- Fix type mismatches

## Example Workflow

### Scenario: Creating Test Data for a SOAP Service

1. **Generate schemas:**
   ```bash
   python wsdl_to_schema.py service.wsdl --main-model Request \
       --individual-schemas --output-dir test-data
   ```

2. **Create test customer:**
   ```json
   {
     "$schema": "./CustomerType.schema.json",
     "customer_id": "TEST001",
     "name": "Test Customer",
     "contact": {
       "email": "test@example.com"
     },
     "billing_address": {
       "street": "123 Test St",
       "city": "Testville",
       "state": "TS",
       "postal_code": "12345",
       "country": "Testland"
     }
   }
   ```

3. **VS Code validates everything:**
   - If you forget `email` in `contact`, VS Code shows an error
   - If you misspell `postal_code` as `postalcode`, VS Code flags it
   - Autocomplete helps you build nested objects quickly

4. **Load in your application:**
   ```python
   import json
   from generated.pydantic_models import CustomerType
   
   with open('test-data/customer.json') as f:
       data = json.load(f)
   
   customer = CustomerType(**data)  # Validated!
   ```

## Schema File Naming Convention

Individual schema files follow this pattern:
- `{TypeName}.schema.json`

Examples:
- `Order.schema.json` (for Order or OrderType)
- `CustomerType.schema.json` (for CustomerType)
- `ProductType.schema.json` (for ProductType)

## Comparison: Unified vs. Individual

| Feature | Unified Mode | Individual Mode |
|---------|--------------|-----------------|
| Schema files | 1 file (with `$defs`) | 1 file per type |
| VS Code editing | Root type only | All types |
| Use case | Single document type | Multiple document types |
| Best for | Production APIs | Test data, development |
| File size | Larger (duplicates `$defs`) | Smaller per file |

## Advanced: Settings in VS Code

You can configure VS Code to automatically associate file patterns with schemas:

**.vscode/settings.json:**
```json
{
  "json.schemas": [
    {
      "fileMatch": ["**/customers/*.json"],
      "url": "./schemas/CustomerType.schema.json"
    },
    {
      "fileMatch": ["**/products/*.json"],
      "url": "./schemas/ProductType.schema.json"
    }
  ]
}
```

Now any `.json` file in the `customers/` directory automatically uses the Customer schema, even without the `$schema` property.

## Troubleshooting

### IntelliSense Not Working
- ✅ Check that the `$schema` path is correct (relative to the JSON file)
- ✅ Reload VS Code window (`Ctrl+Shift+P` → "Reload Window")
- ✅ Ensure the schema file is valid JSON
- ✅ Check the Output panel (View → Output → JSON Language Server)

### Schema Not Found
- ✅ Use relative paths in `$schema` (e.g., `"./schemas/Type.schema.json"`)
- ✅ Or use absolute paths
- ✅ Avoid spaces in file paths

### Validation Errors Don't Make Sense
- ✅ Check that you're using the correct schema file for your data
- ✅ Verify the XSD was converted correctly
- ✅ Try regenerating schemas with `--verbose` to debug

## Best Practices

1. **Use descriptive filenames** for your JSON documents (e.g., `customer-john-doe.json`)
2. **Organize by type** (e.g., `customers/`, `products/`, `orders/` directories)
3. **Version your schemas** if your XSD changes frequently
4. **Commit schemas to git** so team members have IntelliSense too
5. **Use `--individual-schemas`** for development, unified for production APIs

## See Also

- [VS Code JSON Documentation](https://code.visualstudio.com/docs/languages/json)
- [JSON Schema Specification](https://json-schema.org/)
- [Main README](README.md)

## Issue Resolution

This feature addresses **Issue #13**: "Confirm output is suitable for VS Code usage"

The individual schemas mode ensures that VS Code can provide full authoring support (IntelliSense, validation, hover docs) for **any** type defined in the XSD, not just the root type. This makes the tool suitable for VS Code editing workflows.
