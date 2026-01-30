# Research Plan: WSDL to JSON Schema Conversion and Proof of Concept

## Objective
The primary goal of this research is to explore and implement a workflow for converting WSDL (XSD) definitions into JSON Schemas. The focus will be on handling complex XSD structures, including nested elements, collections (e.g., arrays, mappings), and sequences. The generated JSON Schemas will support editing JSON documents, which can then be converted into Python dictionaries for use with the `zeep` library to interact with web services.

## Steps

### 1. Research WSDL to JSON Schema Conversion Tools
- Investigate how `zeep` can parse WSDL (XSD) definitions and generate Python objects.
- Explore tools or libraries that can handle complex XSD structures, including nested elements, arrays, mappings, and sequences, and convert them into JSON Schemas.
- Evaluate the following:
  - Compatibility of tools with `zeep` and Pydantic models.
  - Support for handling nested elements and collections in XSD.
  - Community support, documentation, and stability of the tools.

### 2. Select Tools and Seek Clarification
- Based on the research, identify the most promising tools or libraries for the task.
- If necessary, seek clarification on specific requirements or trade-offs before finalizing the choice of tools.

### 3. Develop a Proof of Concept (PoC)
- Implement a workflow to:
  - Parse a complex WSDL (XSD) structure with nested elements, arrays, mappings, and sequences using `zeep`.
  - Convert the resulting Python objects into Pydantic models.
  - Generate JSON Schemas from the Pydantic models.
- Ensure the PoC demonstrates the ability to handle the specified complex structures.

### 4. Draft a Markdown Document
- Summarize the research findings and PoC in a structured Markdown document.
- Include:
  - An explanation of the WSDL to JSON Schema conversion process.
  - A description of the tools or libraries considered, their trade-offs, and the final selection.
  - Code snippets from the PoC demonstrating the workflow for nested elements, arrays, mappings, and sequences.
  - Challenges encountered and how they were addressed.

### 5. Seek Feedback
- Share the PoC and the Markdown document for review.
- Gather feedback on the approach, implementation, and recommendations.

### 6. Refine the PoC and Document
- Incorporate feedback to finalize the PoC and the Markdown document.

## Further Considerations
1. Should the PoC include specific examples of WSDL definitions with nested elements, arrays, and sequences? If so, do you have any sample WSDL files to use?
2. Are there any specific tools or libraries you are already considering or would like to prioritize for evaluation?

---

This document will serve as the foundation for the research and PoC implementation. Feedback and additional requirements are welcome before proceeding further.