"""
Unit tests for the schema generation module.

Tests JSON Schema generation from Pydantic models.
"""
import pytest
from pathlib import Path
from pydantic import BaseModel
from typing import Optional, List
import json

from pipeline.schema import generate_json_schema
from exceptions import SchemaGenerationError


@pytest.mark.unit
def test_generate_json_schema_success(temp_test_dir: Path) -> None:
    """Test successful JSON schema generation."""
    # Create sample Pydantic models
    class Person(BaseModel):
        name: str
        age: int
    
    class Order(BaseModel):
        order_id: str
        customer: Person
    
    models = {
        'Person': Person,
        'Order': Order
    }
    
    schema_path = generate_json_schema(models, 'Order', temp_test_dir)
    
    assert schema_path.exists()
    assert schema_path.name == 'schema.json'
    
    # Read and validate schema
    with open(schema_path) as f:
        schema = json.load(f)
    
    assert schema['type'] == 'object'
    assert 'properties' in schema
    assert 'order_id' in schema['properties']
    assert 'customer' in schema['properties']


@pytest.mark.unit
def test_generate_json_schema_with_defs(temp_test_dir: Path) -> None:
    """Test schema generation with nested definitions."""
    class Address(BaseModel):
        street: str
        city: str
    
    class Customer(BaseModel):
        name: str
        address: Address
    
    models = {
        'Address': Address,
        'Customer': Customer
    }
    
    schema_path = generate_json_schema(models, 'Customer', temp_test_dir)
    
    with open(schema_path) as f:
        schema = json.load(f)
    
    # Should have $defs section
    assert '$defs' in schema


@pytest.mark.unit
def test_generate_json_schema_model_not_found(temp_test_dir: Path) -> None:
    """Test error when main model not found."""
    class Person(BaseModel):
        name: str
    
    models = {'Person': Person}
    
    with pytest.raises(SchemaGenerationError, match="Model 'Order' not found"):
        generate_json_schema(models, 'Order', temp_test_dir)


@pytest.mark.unit
def test_generate_json_schema_creates_summary(temp_test_dir: Path) -> None:
    """Test that summary file is created."""
    class Simple(BaseModel):
        value: str
    
    models = {'Simple': Simple}
    
    schema_path = generate_json_schema(models, 'Simple', temp_test_dir)
    summary_path = schema_path.parent / "summary.json"
    
    assert summary_path.exists()
    
    with open(summary_path) as f:
        summary = json.load(f)
    
    assert summary['main_model'] == 'Simple'
    assert summary['total_models'] == 1
    assert 'Simple' in summary['models']


@pytest.mark.unit
def test_generate_json_schema_optional_fields(temp_test_dir: Path) -> None:
    """Test schema generation with optional fields."""
    class OptionalExample(BaseModel):
        required: str
        optional: Optional[str] = None
    
    models = {'OptionalExample': OptionalExample}
    
    schema_path = generate_json_schema(models, 'OptionalExample', temp_test_dir)
    
    with open(schema_path) as f:
        schema = json.load(f)
    
    # Required field should be in required list
    assert 'required' in schema.get('required', [])
    # Optional field should not be required
    assert 'optional' not in schema.get('required', []) or 'optional' in schema['properties']


@pytest.mark.unit
def test_generate_json_schema_list_fields(temp_test_dir: Path) -> None:
    """Test schema generation with list fields."""
    class ListExample(BaseModel):
        items: List[str]
    
    models = {'ListExample': ListExample}
    
    schema_path = generate_json_schema(models, 'ListExample', temp_test_dir)
    
    with open(schema_path) as f:
        schema = json.load(f)
    
    # Should have array type for items
    items_prop = schema['properties']['items']
    assert items_prop['type'] == 'array'
