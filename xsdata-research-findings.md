# Research Findings: Exploring Tools for Handling Complex XSD Structures

## Objective
The goal of this research is to explore tools and libraries that can handle complex XSD structures, including nested elements, arrays, mappings, and sequences, and convert them into JSON Schemas. The findings focus on the `xsdata` library as a potential tool for this purpose.

---

## Findings on `xsdata`

### Overview
- `xsdata` is a Python library designed to generate Python data classes from XML Schema (XSD) definitions.
- It supports complex XSD structures, including nested elements, arrays, mappings, and sequences.
- The library can directly generate Pydantic models, which is highly relevant for this project.

### Key Features
1. **XSD Parsing**:
   - Parses XSD files and generates Python classes that map to the schema.
   - Handles complex structures effectively, including nested elements and sequences.

2. **Pydantic Support**:
   - Offers built-in support for generating Pydantic models directly from XSD files.
   - Pydantic models include type annotations and validation rules based on the XSD definitions.

3. **JSON Schema Generation**:
   - While `xsdata` does not directly generate JSON Schemas, the Pydantic models it generates can be used to produce JSON Schemas using Pydantic’s built-in `schema()` method.

4. **CLI Tool**:
   - Provides a command-line interface for generating models from XSD files, which can be integrated into automated workflows.

### Strengths
- Actively maintained and well-documented.
- Handles complex XSD structures effectively.
- Directly supports Pydantic and JSON Schema generation, reducing the need for additional tools.

### Limitations
- Limited community size compared to larger libraries like `xmlschema`.
- May require additional configuration for very complex or non-standard XSD structures.

---

## Example Workflow with `xsdata`

### Installation
To install `xsdata`, use the following command:
```bash
pip install xsdata
```

### Generating Pydantic Models from XSD
To generate Pydantic models from an XSD file, use the following command:
```bash
xsdata generate --package models --output pydantic sample.xsd
```
This command generates Pydantic models in the `models` package, which can then be used to validate and serialize data.

### Using Pydantic to Generate JSON Schemas
Once the Pydantic models are generated, JSON Schemas can be created using the `schema()` method provided by Pydantic:
```python
from models import SampleModel

# Generate JSON Schema from Pydantic model
schema = SampleModel.schema()
print(schema)
```

---

## Next Steps
1. **Evaluate Compatibility**:
   - Assess how well `xsdata` integrates with `zeep` and Pydantic for JSON Schema generation.
   - Test the workflow of using `zeep` to parse WSDL, `xsdata` to generate Pydantic models, and Pydantic to generate JSON Schemas.

2. **Document Findings**:
   - Summarize the results of the `xsdata` testing in the research document.

---

This document summarizes the findings so far on the `xsdata` library and its potential for handling complex XSD structures. Further steps will involve evaluating its compatibility with `zeep` and Pydantic models for JSON Schema generation.