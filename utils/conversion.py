"""
Shared conversion utilities for dataclass to Pydantic model conversion.
This module contains common logic used by both step2 and step3 to avoid duplication.
"""
from dataclasses import fields, is_dataclass, MISSING
from typing import Any
from pydantic import create_model


def dataclass_to_pydantic_model(dataclass_type: type, model_name: str = None) -> type:
    """
    Dynamically create a Pydantic model from a dataclass type.
    
    This function inspects the dataclass structure and creates an equivalent Pydantic model
    using Pydantic's create_model() function. It preserves field types, defaults, and
    whether fields are required or optional.
    
    Args:
        dataclass_type: The dataclass type to convert
        model_name: Optional name for the Pydantic model. If None, uses dataclass name.
    
    Returns:
        A dynamically created Pydantic model class
    
    Raises:
        ValueError: If the input is not a dataclass
    
    Example:
        ```python
        from dataclasses import dataclass
        from utils.conversion import dataclass_to_pydantic_model
        
        @dataclass
        class Person:
            name: str
            age: int
            email: str | None = None
        
        PersonModel = dataclass_to_pydantic_model(Person)
        person = PersonModel(name="Alice", age=30)
        ```
    """
    if not is_dataclass(dataclass_type):
        raise ValueError(f"{dataclass_type} is not a dataclass")
    
    if model_name is None:
        model_name = dataclass_type.__name__
    
    # Extract field information from the dataclass
    field_info = []
    for field in fields(dataclass_type):
        field_name = field.name
        field_type = field.type
        
        # Get default value if it exists
        if field.default is not MISSING:
            default_value = field.default
        elif field.default_factory is not MISSING:
            default_value = field.default_factory
        else:
            default_value = ...  # Required field in Pydantic
        
        field_info.append((field_name, field_type, default_value))
    
    # Build Pydantic field definitions
    pydantic_fields = {}
    for field_name, field_type, default_value in field_info:
        if default_value is ...:
            # Required field
            pydantic_fields[field_name] = (field_type, ...)
        else:
            # Optional or has default
            pydantic_fields[field_name] = (field_type, default_value)
    
    # Create the Pydantic model dynamically
    pydantic_model = create_model(model_name, **pydantic_fields)
    
    return pydantic_model


def inspect_dataclass_fields(dataclass_type: type) -> list[tuple[str, type, Any]]:
    """
    Inspect a dataclass and extract field information.
    
    Args:
        dataclass_type: The dataclass type to inspect
    
    Returns:
        List of (field_name, field_type, default_value) tuples
    
    Raises:
        ValueError: If the input is not a dataclass
    """
    if not is_dataclass(dataclass_type):
        raise ValueError(f"{dataclass_type} is not a dataclass")
    
    field_info = []
    for field in fields(dataclass_type):
        field_name = field.name
        field_type = field.type
        
        # Get default value if it exists
        if field.default is not MISSING:
            default_value = field.default
        elif field.default_factory is not MISSING:
            default_value = field.default_factory
        else:
            default_value = ...  # Required field in Pydantic
        
        field_info.append((field_name, field_type, default_value))
    
    return field_info
