"""
Unit tests for individual JSON Schema generation.

Tests the new individual schema generation mode for VS Code editing support.
"""
import pytest
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
import json

from pipeline.schema import generate_individual_schemas
from exceptions import SchemaGenerationError


@pytest.mark.unit
def test_generate_individual_schemas_success(temp_test_dir: Path) -> None:
    """Test successful individual schema generation."""
    # Create sample Pydantic models
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
    
    schema_dir = generate_individual_schemas(models, temp_test_dir)
    
    assert schema_dir.exists()
    assert schema_dir == temp_test_dir
    
    # Check that individual schema files were created
    address_schema = temp_test_dir / "Address.schema.json"
    customer_schema = temp_test_dir / "Customer.schema.json"
    index_file = temp_test_dir / "index.json"
    
    assert address_schema.exists()
    assert customer_schema.exists()
    assert index_file.exists()
    
    # Validate Address schema
    with open(address_schema) as f:
        schema = json.load(f)
    
    assert schema['type'] == 'object'
    assert 'properties' in schema
    assert 'street' in schema['properties']
    assert 'city' in schema['properties']
    
    # Validate Customer schema has reference to Address
    with open(customer_schema) as f:
        schema = json.load(f)
    
    assert 'properties' in schema
    assert 'name' in schema['properties']
    assert 'address' in schema['properties']


@pytest.mark.unit
def test_generate_individual_schemas_creates_index(temp_test_dir: Path) -> None:
    """Test that index file is created with correct metadata."""
    class Simple(BaseModel):
        value: str
    
    class Complex(BaseModel):
        data: Simple
    
    models = {
        'Simple': Simple,
        'Complex': Complex
    }
    
    schema_dir = generate_individual_schemas(models, temp_test_dir)
    index_path = schema_dir / "index.json"
    
    assert index_path.exists()
    
    with open(index_path) as f:
        index = json.load(f)
    
    assert index['total_schemas'] == 2
    assert 'Simple.schema.json' in index['generated_schemas']
    assert 'Complex.schema.json' in index['generated_schemas']
    assert 'usage' in index
    assert 'vscode' in index['usage']


@pytest.mark.unit
def test_generate_individual_schemas_with_multiple_models(temp_test_dir: Path) -> None:
    """Test schema generation with many models."""
    class Type1(BaseModel):
        value: str
    
    class Type2(BaseModel):
        data: int
    
    class Type3(BaseModel):
        flag: bool
    
    models = {
        'Type1': Type1,
        'Type2': Type2,
        'Type3': Type3
    }
    
    schema_dir = generate_individual_schemas(models, temp_test_dir)
    
    # Check all schema files exist
    for name in ['Type1', 'Type2', 'Type3']:
        schema_file = temp_test_dir / f"{name}.schema.json"
        assert schema_file.exists()
        
        with open(schema_file) as f:
            schema = json.load(f)
        assert schema['type'] == 'object'
        assert 'properties' in schema


@pytest.mark.unit
def test_generate_individual_schemas_cleans_old_files(temp_test_dir: Path) -> None:
    """Test that old schema files are removed before generating new ones."""
    # Create an old file
    old_file = temp_test_dir / "OldSchema.schema.json"
    old_file.write_text('{"old": true}')
    
    class NewModel(BaseModel):
        value: str
    
    models = {'NewModel': NewModel}
    
    schema_dir = generate_individual_schemas(models, temp_test_dir)
    
    # Old file should be removed
    assert not old_file.exists()
    
    # New file should exist
    new_file = temp_test_dir / "NewModel.schema.json"
    assert new_file.exists()


@pytest.mark.unit
def test_generate_individual_schemas_with_nested_refs(temp_test_dir: Path) -> None:
    """Test that nested type references are preserved in individual schemas."""
    class Inner(BaseModel):
        value: str
    
    class Middle(BaseModel):
        inner: Inner
    
    class Outer(BaseModel):
        middle: Middle
    
    models = {
        'Inner': Inner,
        'Middle': Middle,
        'Outer': Outer
    }
    
    schema_dir = generate_individual_schemas(models, temp_test_dir)
    
    # Check Outer schema has references to nested types
    outer_schema = temp_test_dir / "Outer.schema.json"
    with open(outer_schema) as f:
        schema = json.load(f)
    
    # Should have $defs section with referenced types
    assert '$defs' in schema
    assert 'Middle' in schema['$defs']


@pytest.mark.unit
def test_generate_individual_schemas_with_empty_models() -> None:
    """Test that empty model dictionary is handled gracefully."""
    from pathlib import Path
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir)
        models = {}
        
        # Should complete without errors
        schema_dir = generate_individual_schemas(models, temp_path)
        
        # Index file should still be created
        index_file = schema_dir / "index.json"
        assert index_file.exists()
        
        import json
        with open(index_file) as f:
            index = json.load(f)
        
        assert index['total_schemas'] == 0
        assert len(index['generated_schemas']) == 0


@pytest.mark.unit
def test_generate_individual_schemas_io_error(temp_test_dir: Path, monkeypatch) -> None:
    """Test that IO errors during schema generation are caught."""
    import json
    from unittest.mock import Mock
    
    class FailingModel(BaseModel):
        value: str
    
    models = {'FailingModel': FailingModel}
    
    # Mock json.dump to raise an error
    original_dump = json.dump
    def failing_dump(*args, **kwargs):
        raise IOError("Simulated IO error")
    
    monkeypatch.setattr('json.dump', failing_dump)
    
    # Should raise SchemaGenerationError wrapping the IOError
    with pytest.raises(SchemaGenerationError, match="Failed to generate schema"):
        generate_individual_schemas(models, temp_test_dir)
