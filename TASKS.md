# Development Tasks

## Status Legend
- ✅ Completed
- 🔄 In Progress
- ⏸️ Blocked/Paused
- ⏭️ To Do

---

## Completed Tasks

### ✅ Task 1: Audit models/ and utils/ folders
**Status**: Completed  
**Description**: Check models/ folder for obsolete generated outputs. Verify what's being used vs what can be removed. Check utils/ folder to ensure conversion.py is properly imported and utilized in wsdl_to_schema.py.

**Results**:
- models/sample_complex.py - Generated dataclasses, actively used
- utils/conversion.py - Actively imported and used in wsdl_to_schema.py
- All files are needed, no obsolete content found

---

## In Progress Tasks

### 🔄 Task 2: Review xsdata configuration for broad XSD/WSDL compatibility
**Status**: In Progress  
**Description**: Review .xsdata.xml configuration file. Evaluate if current settings are appropriate for diverse XSD/WSDL files or if adjustments are needed for broader compatibility. Consider edge cases like different namespaces, schema versions, and XSD features.

**Current Assessment**:
- Configuration is well-structured with standard naming conventions
- Common namespace substitutions (SOAP, XML Schema, WSDL) are in place
- Dataclasses format is widely compatible
- Configuration appears appropriate for diverse XSD/WSDL files
- May need specific adjustments for edge cases

**Next Steps**:
- Test with various WSDL files to validate compatibility
- Document any edge cases that require configuration changes

---

## To Do Tasks

### ⏭️ Task 3: Add WSDL file support (in addition to XSD)
**Status**: To Do  
**Priority**: High  
**Description**: Extend input file processing to handle WSDL files (not just XSD). WSDL files contain XSD schemas embedded within them. Need to extract XSD portion or use xsdata's WSDL support directly.

**Requirements**:
- Accept .wsdl files as input
- Use xsdata's native WSDL support
- Extract and process type definitions from WSDL
- Handle WSDL-specific elements (services, bindings, ports)

**Notes**:
- xsdata already supports WSDL files natively
- May need to adjust file detection logic
- Test with real-world WSDL examples

---

### ⏭️ Task 4: Support fetching WSDL/XSD from HTTP sources
**Status**: To Do  
**Priority**: High  
**Description**: Add capability to fetch WSDL/XSD files from HTTP/HTTPS URLs instead of only local files. Handle network errors, timeouts, and cache downloaded files.

**Requirements**:
- Detect URL input (http:// or https://)
- Download file to temporary location
- Handle network errors gracefully (timeouts, 404, connection errors)
- Optional: Cache downloaded files
- Support authentication if needed
- Example usage: `python wsdl_to_schema.py https://example.com/service?wsdl --main-model Order`

**Implementation Notes**:
- Use requests library for HTTP downloads
- Add retry logic for transient failures
- Store downloaded files in temp directory or cache
- Clean up temp files after processing (or cache for reuse)

---

### ⏭️ Task 5: Eliminate persistent dataclass file dependency
**Status**: To Do  
**Priority**: Critical  
**Description**: Perform deep analysis on sample_complex.py dataclass file. The current implementation incorrectly relies on a pre-existing dataclass file. Since we have a unified script, all dataclass information should be generated on-the-fly based on the input XSD/WSDL. There should be NO reliance on external dataclass definitions to generate Pydantic models and schemas.

**Current Problem**:
- wsdl_to_schema.py currently imports from pre-generated models/sample_complex.py
- This creates a circular dependency: we need the models to exist before we can process them
- The tool should work with ANY XSD/WSDL file without pre-existing Python code

**Required Changes**:
1. **Analyze current dataclass generation flow**:
   - How xsdata generates dataclasses
   - How we currently import and use them
   - Where the circular dependency occurs

2. **Redesign pipeline**:
   - Generate dataclasses in memory or temporary location
   - Dynamically import generated modules
   - Process without requiring persistent Python files

3. **Implementation options**:
   - Option A: Generate to temp directory, import dynamically, clean up after
   - Option B: Use xsdata programmatic API to generate in-memory representations
   - Option C: Parse XSD directly without intermediate dataclass step (complex)

4. **Testing**:
   - Test with multiple different XSD files
   - Verify no persistent files are required
   - Ensure models/ directory can be empty before processing

**Success Criteria**:
- User can run: `python wsdl_to_schema.py any-new-file.xsd --main-model SomeType`
- No pre-existing Python files required in models/
- All generation happens on-the-fly
- Output includes both generated dataclasses AND schemas

---

### ⏭️ Task 6: Organize outputs into parameter-named folders
**Status**: To Do  
**Priority**: Medium  
**Description**: Organize generated outputs (dataclasses, Pydantic models, schemas) into a single output folder named after input parameters. This provides better organization and allows multiple XSD files to coexist.

**Requirements**:
- Create output directory structure: `output/[xsd-name]/`
- Subdirectories: `models/`, `pydantic/`, `schemas/`
- Example: `output/sample-complex/models/sample_complex.py`
- Support custom output directory via CLI parameter

**Benefits**:
- Multiple XSD files can be processed without conflicts
- Clear organization of generated artifacts
- Easy to clean up or archive outputs

---

### ⏭️ Task 7: Migrate CLI from argparse to Click
**Status**: To Do  
**Priority**: Low  
**Description**: Replace argparse with Click library for a more modern, declarative CLI interface. Click provides better command composition, automatic help generation, and cleaner parameter handling.

**Requirements**:
- Replace argparse with Click decorators
- Maintain all existing functionality
- Improve help text and error messages
- Add command groups if needed for future expansion
- Consider adding --verbose flag for debug output

**Benefits**:
- More maintainable CLI code
- Better auto-generated help
- Easier to add subcommands in future
- Type validation built-in

---

## Notes

### Dependencies to Add
- `requests` - For HTTP download support (Task 4)
- `click` - For CLI improvement (Task 7)

### Critical Path
The most critical task is **Task 5** (Eliminate dataclass file dependency) as it affects the core architecture and determines how the other tasks should be implemented.

**Recommended Order**:
1. Task 5 (Critical - fixes architecture)
2. Task 3 (High - WSDL support)
3. Task 4 (High - HTTP support)
4. Task 6 (Medium - output organization)
5. Task 2 (Complete - xsdata config review)
6. Task 7 (Low - CLI improvement)

---

## Future Considerations

- **Testing**: Add pytest test suite
- **Documentation**: Add API documentation for programmatic usage
- **Performance**: Optimize for large WSDL files
- **Validation**: Add schema validation before generation
- **Error Handling**: Improve error messages for common issues
