# Copilot Coding Agent Instructions

## Repository Overview

**python-zeep-codegen** is a Python-based tool that bridges the gap between legacy SOAP/WSDL services and modern development workflows. The tool converts WSDL/XSD definitions into developer-friendly artifacts.

**Purpose**: Convert XSD/WSDL schemas → Python Dataclasses → Pydantic Models → JSON Schemas

**Key Technologies**:
- Python 3.12+
- xsdata (26.1) - XSD to dataclass generation
- Pydantic (2.12.5) - data validation and JSON schema generation
- Click - CLI interface
- lxml - XML parsing

## Project Structure

```
python-zeep-codegen/
├── wsdl_to_schema.py          # Main CLI entry point
├── pipeline/                   # Core conversion pipeline
│   ├── __init__.py
│   ├── download.py            # URL/file download logic
│   ├── generate.py            # xsdata dataclass generation
│   ├── convert.py             # Dataclass to Pydantic conversion
│   └── schema.py              # JSON Schema generation
├── utils/                      # Shared utilities
│   ├── __init__.py
│   └── conversion.py          # Core conversion logic
├── exceptions.py              # Custom exception hierarchy
├── requirements.txt           # Python dependencies
├── .xsdata.xml               # xsdata configuration
├── .gitignore                # Git ignore patterns
├── models/                   # Generated dataclasses (ignored)
├── generated/                # Generated Pydantic models (ignored)
├── schemas/                  # Generated JSON schemas (ignored)
└── output/                   # Default output directory (ignored)
```

## Setup and Dependencies

### Installation
```bash
# Clone and navigate to repository
git clone https://github.com/nokout/python-zeep-codegen.git
cd python-zeep-codegen

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Dependency Management
- Use `requirements.txt` for dependency management
- Pin major versions for stability (e.g., `pydantic==2.12.5`)
- Include comments explaining dependency purposes
- Keep dependencies minimal - only add if absolutely necessary
- Development dependencies like pytest, mypy, ruff are currently commented out but should be considered for production use

## Build, Test, and Run

### Running the Tool
```bash
# Basic usage
python wsdl_to_schema.py input.xsd --main-model Order

# With verbose output
python wsdl_to_schema.py input.xsd --main-model Order --verbose

# Keep temporary files for debugging
python wsdl_to_schema.py input.xsd --main-model Order --keep-temp

# Custom output directory
python wsdl_to_schema.py input.wsdl --main-model Request --output-dir custom_output
```

### Testing
- Currently no formal test suite exists
- Manual testing should use `sample-complex.xsd` and `sample.wsdl` as test files
- When adding features, validate with these sample files before committing

### Linting and Formatting
- No formal linting is currently configured, but recommendations:
  - **ruff**: Modern, fast Python linter and formatter (recommended for future use)
  - **mypy**: Type checking (especially important given heavy use of type hints)
  - Line length: 79 characters (per .xsdata.xml config)
- Consider adding `.flake8`, `pyproject.toml`, or `ruff.toml` configuration in future

## Coding Standards

### Python Style
- Follow PEP 8 conventions
- Maximum line length: 79 characters (consistent with xsdata config)
- Use snake_case for functions and variables
- Use PascalCase for class names
- Use SCREAMING_SNAKE_CASE for constants

### Type Hints
- **ALWAYS use type hints** for function signatures
- Example:
  ```python
  def convert_to_pydantic(module_name: str, temp_dir: Path, output_dir: Path | None = None) -> tuple[dict, Path]:
      """Convert dataclasses to Pydantic models."""
      ...
  ```
- Use modern Python 3.12+ type syntax:
  - Use `list[str]` instead of `List[str]`
  - Use `str | None` instead of `Optional[str]`
  - Use `int | str` instead of `Union[int, str]`
- Use `Path` from `pathlib` for file system paths, not strings

### Docstrings
- Use triple-quoted strings for all docstrings
- Module docstrings: Brief description at top of file
- Function/method docstrings: 
  - One-line summary
  - Args section with types and descriptions
  - Returns section with type and description
  - Raises section for exceptions
- Class docstrings: Purpose and usage
- Use Google-style format for hand-written code (Args:, Returns:, Raises:)
- Note: xsdata-generated code uses reStructuredText format per `.xsdata.xml` config
- Example:
  ```python
  def example_function(param1: str, param2: int) -> bool:
      """
      Brief description of what the function does.
      
      Args:
          param1: Description of param1
          param2: Description of param2
      
      Returns:
          Description of return value
      
      Raises:
          ValueError: When something goes wrong
      """
  ```

### Error Handling
- Use custom exception hierarchy from `exceptions.py`
- All exceptions inherit from `WSDLSchemaError`
- Use specific exception types:
  - `DownloadError`: URL/file download failures
  - `ValidationError`: Input validation failures
  - `XSDGenerationError`: xsdata generation failures
  - `ConversionError`: Dataclass to Pydantic conversion failures
  - `SchemaGenerationError`: JSON schema generation failures
- Always provide descriptive error messages
- Use logger for debugging information before raising exceptions

### Logging
- Import and use the logging module: `import logging`
- Create logger at module level: `logger = logging.getLogger(__name__)`
- Use appropriate log levels:
  - `logger.debug()`: Detailed debugging information
  - `logger.info()`: General informational messages
  - `logger.warning()`: Warning messages
  - `logger.error()`: Error messages
- The CLI configures logging based on `--verbose` flag

### Imports
- Group imports in this order:
  1. Standard library imports
  2. Third-party imports
  3. Local application imports
- Use absolute imports, not relative imports (per .xsdata.xml config)
- Sort imports alphabetically within groups

### File Organization
- Keep related functionality in pipeline modules
- Place shared utilities in `utils/` directory
- Keep exceptions in centralized `exceptions.py`
- Main CLI logic in `wsdl_to_schema.py`

## xsdata Configuration

The `.xsdata.xml` file controls code generation. Key settings:
- Output package: `models/`
- Format: dataclasses with `repr=True`, `eq=True`
- Naming conventions: PascalCase for classes, snake_case for fields
- Line length: 79 characters
- No relative imports

Do not modify this file without understanding the impact on generated code.

## Pull Requests and Commits

### Commit Messages
- Use descriptive commit messages
- Start with a verb in present tense (e.g., "Add", "Fix", "Update", "Remove")
- Keep first line under 72 characters
- Add detailed description if needed in subsequent lines
- Examples:
  - `Add support for WSDL 2.0 service definitions`
  - `Fix error handling in URL download logic`
  - `Update Pydantic models to handle nested enums`

### Pull Request Guidelines
- Reference related issues using `Fixes #<issue-number>` or `Resolves #<issue-number>`
- Provide clear description of changes
- Include examples of usage if adding new features
- Test changes with sample files before submitting
- Keep PRs focused - one feature or fix per PR
- Update README.md if adding user-facing features

### Code Review
- Code should be self-documenting with clear variable names and docstrings
- Avoid unnecessary complexity
- Ensure backward compatibility when possible
- Consider performance implications for large schemas

## Security and Best Practices

### Input Validation
- Validate file paths exist before processing
- Check file extensions (`.xsd`, `.wsdl`)
- Validate URLs before downloading
- Handle network errors gracefully

### Security Guidelines
- **NEVER commit secrets or credentials**
- Use environment variables for sensitive configuration
- Validate and sanitize all external input
- Be cautious with dynamic imports and code execution
- Handle temporary files securely (clean up after use)

### File System Operations
- Use `Path` objects from `pathlib` for cross-platform compatibility
- Resolve to absolute paths when passing to external tools or for validation
- Use relative paths for user-facing output and display
- Clean up temporary directories (unless `--keep-temp` flag is used)
- Respect .gitignore patterns - don't commit generated files

### Generated Files
- `models/`, `generated/`, `schemas/`, and `output/` directories are gitignored
- These contain generated code and should not be committed
- Use `--output-dir` to specify custom output locations if needed

## Design Patterns

### Three-Stage Pipeline
The tool follows a clear three-stage pipeline pattern:

1. **XSD → Dataclasses** (`pipeline/generate.py`)
   - Uses xsdata CLI to generate Python dataclasses
   - Outputs to temporary directory
   - Configurable via `.xsdata.xml`

2. **Dataclasses → Pydantic** (`pipeline/convert.py`)
   - Dynamic introspection using `dataclasses.fields()`
   - Two-pass model building for forward reference resolution
   - Preserves type information and defaults

3. **Pydantic → JSON Schema** (`pipeline/schema.py`)
   - Uses Pydantic's built-in `model_json_schema()`
   - Generates unified schema with `$defs`
   - Self-contained and portable output

### Key Principles
- **Generic Conversion**: Code works with any XSD structure - no hardcoding
- **Type Safety**: Full type hints throughout
- **Modularity**: Clear separation of concerns in pipeline stages
- **Error Handling**: Comprehensive exception hierarchy
- **Logging**: Verbose mode for debugging

## Agent Guidance

### When Making Changes
- Understand the three-stage pipeline before modifying core logic
- Test with both `sample-complex.xsd` and `sample.wsdl`
- Consider impact on generated code quality
- Maintain backward compatibility when possible
- Add logging statements for debugging

### When Uncertain
- Ask clarifying questions before starting major changes
- Review existing patterns in similar modules
- Check how xsdata generates dataclasses
- Verify Pydantic model creation preserves types
- Test with sample files to validate behavior

### Common Tasks
- Adding new CLI options: Modify `wsdl_to_schema.py` with Click decorators
- Extending pipeline: Add new module in `pipeline/` directory
- Custom exceptions: Add to `exceptions.py` hierarchy
- Shared utilities: Add to `utils/` directory

### Future Enhancements
The project documentation mentions several areas for future work:
- WSDL 2.0 service definitions support
- Streaming/batch processing for large schemas
- Additional output formats (OpenAPI, GraphQL)
- Automated testing suite (pytest)
- Enhanced error messages
- Web form generation integration

## References

- [xsdata Documentation](https://xsdata.readthedocs.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [zeep Documentation](https://docs.python-zeep.org/)
- [JSON Schema Specification](https://json-schema.org/)
- [PEP 8 - Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)

---

**This file resolves issue #8: Add base Copilot instructions file**
