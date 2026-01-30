"""
Shared conversion utilities for dataclass to Pydantic model conversion.

This module contains common logic used by the conversion pipeline to avoid duplication.
It provides functions for dynamically creating Pydantic models from dataclass types
using introspection and Pydantic's create_model() API.
"""
from dataclasses import fields, is_dataclass, MISSING, Field
from typing import Any, Type, Tuple, List, Optional, get_type_hints, Dict
from pydantic import create_model


def dataclass_to_pydantic_model(
    dataclass_type: Type[Any],
    model_name: Optional[str] = None
) -> Type[Any]:
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
    field_info: List[Tuple[str, Any, Any]] = []
    for field in fields(dataclass_type):
        field_name: str = field.name
        field_type: Any = field.type
        
        # Get default value if it exists
        default_value: Any
        if field.default is not MISSING:
            default_value = field.default
        elif field.default_factory is not MISSING:
            # For Pydantic, we need the factory function itself, not the result
            # Pydantic will handle calling it
            default_value = field.default_factory
        else:
            default_value = ...  # Required field in Pydantic
        
        field_info.append((field_name, field_type, default_value))
    
    # Build Pydantic field definitions
    pydantic_fields: Dict[str, Any] = {}
    for field_name, field_type, default_value in field_info:
        if default_value is ...:
            # Required field
            pydantic_fields[field_name] = (field_type, ...)
        else:
            # Optional or has default
            pydantic_fields[field_name] = (field_type, default_value)
    
    # Create the Pydantic model dynamically
    pydantic_model: Type[Any] = create_model(model_name, **pydantic_fields)
    
    return pydantic_model


def inspect_dataclass_fields(dataclass_type: Type[Any]) -> List[Tuple[str, Any, Any]]:
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
    
    field_info: List[Tuple[str, Any, Any]] = []
    for field in fields(dataclass_type):
        field_name: str = field.name
        field_type: Any = field.type
        
        # Get default value if it exists
        default_value: Any
        if field.default is not MISSING:
            default_value = field.default
        elif field.default_factory is not MISSING:
            default_value = field.default_factory
        else:
            default_value = ...  # Required field in Pydantic
        
        field_info.append((field_name, field_type, default_value))
    
    return field_info
