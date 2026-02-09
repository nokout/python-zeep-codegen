"""
Unit tests for Angular form generation module.

Tests the conversion from Pydantic models to Angular Reactive Forms.
"""
import pytest
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

from pipeline.angular_forms import (
    generate_angular_forms,
    AngularFormGenerationError,
    _get_typescript_type,
    _generate_typescript_interface,
    _generate_angular_component,
    _get_angular_material_component
)


class SampleEnum(str, Enum):
    """Sample enum for testing."""
    OPTION_A = "option_a"
    OPTION_B = "option_b"


class SimplePydanticModel(BaseModel):
    """Simple Pydantic model for testing."""
    name: str
    age: int
    active: bool


class ComplexPydanticModel(BaseModel):
    """Complex Pydantic model with various field types."""
    username: str = Field(min_length=3, max_length=50)
    email: str
    age: Optional[int] = None
    is_admin: bool = False
    tags: List[str] = []
    status: SampleEnum = SampleEnum.OPTION_A


@pytest.mark.unit
def test_get_typescript_type_basic() -> None:
    """Test TypeScript type mapping for basic types."""
    assert _get_typescript_type(str) == 'string'
    assert _get_typescript_type(int) == 'number'
    assert _get_typescript_type(float) == 'number'
    assert _get_typescript_type(bool) == 'boolean'


@pytest.mark.unit
def test_get_typescript_type_optional() -> None:
    """Test TypeScript type mapping for Optional types."""
    from typing import Optional
    
    # Optional[str] should become "string | null"
    ts_type = _get_typescript_type(Optional[str])
    assert 'string' in ts_type
    assert 'null' in ts_type


@pytest.mark.unit
def test_get_typescript_type_list() -> None:
    """Test TypeScript type mapping for List types."""
    from typing import List
    
    ts_type = _get_typescript_type(List[str])
    assert ts_type == 'string[]'


@pytest.mark.unit
def test_generate_typescript_interface() -> None:
    """Test TypeScript interface generation."""
    interface = _generate_typescript_interface('SimplePydanticModel', SimplePydanticModel)
    
    assert 'export interface SimplePydanticModel' in interface
    assert 'name:' in interface
    assert 'age:' in interface
    assert 'active:' in interface
    assert 'string' in interface
    assert 'number' in interface
    assert 'boolean' in interface


@pytest.mark.unit
def test_generate_typescript_interface_optional() -> None:
    """Test TypeScript interface with optional fields."""
    interface = _generate_typescript_interface('ComplexPydanticModel', ComplexPydanticModel)
    
    assert 'export interface ComplexPydanticModel' in interface
    assert 'username:' in interface  # required
    assert 'age?:' in interface  # optional


@pytest.mark.unit
def test_get_angular_material_component_text() -> None:
    """Test Angular Material component generation for text input."""
    from pydantic.fields import FieldInfo
    
    field_info = FieldInfo(annotation=str, default=None)
    html = _get_angular_material_component('username', 'string', True, field_info)
    
    assert 'mat-form-field' in html
    assert 'matInput' in html
    assert 'formControlName="username"' in html
    assert 'required' in html


@pytest.mark.unit
def test_get_angular_material_component_number() -> None:
    """Test Angular Material component generation for number input."""
    from pydantic.fields import FieldInfo
    
    field_info = FieldInfo(annotation=int, default=None)
    html = _get_angular_material_component('age', 'number', False, field_info)
    
    assert 'mat-form-field' in html
    assert 'type="number"' in html
    assert 'formControlName="age"' in html


@pytest.mark.unit
def test_get_angular_material_component_boolean() -> None:
    """Test Angular Material component generation for checkbox."""
    from pydantic.fields import FieldInfo
    
    field_info = FieldInfo(annotation=bool, default=False)
    html = _get_angular_material_component('is_admin', 'boolean', False, field_info)
    
    assert 'mat-checkbox' in html
    assert 'formControlName="is_admin"' in html


@pytest.mark.unit
def test_generate_angular_component() -> None:
    """Test Angular component generation."""
    files = _generate_angular_component('SimplePydanticModel', SimplePydanticModel)
    
    assert 'ts' in files
    assert 'html' in files
    assert 'css' in files
    
    # Check TypeScript component
    ts_content = files['ts']
    assert 'import { Component, OnInit }' in ts_content
    assert 'import { FormBuilder, FormGroup, Validators }' in ts_content
    assert 'export class SimplePydanticModelFormComponent' in ts_content
    assert 'ngOnInit' in ts_content
    assert 'onSubmit' in ts_content
    assert 'onReset' in ts_content
    
    # Check HTML template
    html_content = files['html']
    assert 'formGroup="simplepydanticmodelForm"' in html_content or '[formGroup]' in html_content
    assert 'mat-form-field' in html_content or 'mat-checkbox' in html_content
    assert 'mat-raised-button' in html_content
    
    # Check CSS
    css_content = files['css']
    assert '.form-container' in css_content
    assert 'mat-form-field' in css_content


@pytest.mark.unit
def test_generate_angular_component_with_validators() -> None:
    """Test Angular component generation with validators."""
    files = _generate_angular_component('ComplexPydanticModel', ComplexPydanticModel)
    
    ts_content = files['ts']
    # Should include Validators.required for required fields
    assert 'Validators.required' in ts_content


@pytest.mark.unit
def test_generate_angular_forms_success(temp_test_dir: Path) -> None:
    """Test successful Angular form generation."""
    models = {'SimplePydanticModel': SimplePydanticModel}
    output_dir = temp_test_dir / "output"
    
    component_dir = generate_angular_forms(models, 'SimplePydanticModel', output_dir)
    
    assert component_dir.exists()
    assert component_dir.is_dir()
    
    # Check that all expected files were created
    component_name = 'simplepydanticmodel-form'
    assert (component_dir / f"{component_name}.component.ts").exists()
    assert (component_dir / f"{component_name}.component.html").exists()
    assert (component_dir / f"{component_name}.component.css").exists()
    assert (component_dir / f"{component_name}.module.ts").exists()
    assert (component_dir / "README.md").exists()
    
    # Check summary file
    summary_file = output_dir / "angular" / "generation-summary.json"
    assert summary_file.exists()


@pytest.mark.unit
def test_generate_angular_forms_model_not_found(temp_test_dir: Path) -> None:
    """Test Angular form generation with non-existent model."""
    models = {'SimplePydanticModel': SimplePydanticModel}
    output_dir = temp_test_dir / "output"
    
    with pytest.raises(AngularFormGenerationError) as excinfo:
        generate_angular_forms(models, 'NonExistentModel', output_dir)
    
    assert 'not found' in str(excinfo.value).lower()
    assert 'SimplePydanticModel' in str(excinfo.value)


@pytest.mark.unit
def test_generate_angular_forms_complex_model(temp_test_dir: Path) -> None:
    """Test Angular form generation with complex model."""
    models = {'ComplexPydanticModel': ComplexPydanticModel}
    output_dir = temp_test_dir / "output"
    
    component_dir = generate_angular_forms(models, 'ComplexPydanticModel', output_dir)
    
    assert component_dir.exists()
    
    # Read generated TypeScript component
    component_name = 'complexpydanticmodel-form'
    ts_file = component_dir / f"{component_name}.component.ts"
    ts_content = ts_file.read_text()
    
    # Check that all fields are present
    assert 'username' in ts_content
    assert 'email' in ts_content
    assert 'age' in ts_content
    assert 'is_admin' in ts_content
    assert 'tags' in ts_content
    assert 'status' in ts_content


@pytest.mark.unit
def test_generate_angular_forms_module_file(temp_test_dir: Path) -> None:
    """Test that module file is generated correctly."""
    models = {'SimplePydanticModel': SimplePydanticModel}
    output_dir = temp_test_dir / "output"
    
    component_dir = generate_angular_forms(models, 'SimplePydanticModel', output_dir)
    
    component_name = 'simplepydanticmodel-form'
    module_file = component_dir / f"{component_name}.module.ts"
    module_content = module_file.read_text()
    
    # Check Angular Material imports
    assert 'MatFormFieldModule' in module_content
    assert 'MatInputModule' in module_content
    assert 'MatButtonModule' in module_content
    assert 'MatCheckboxModule' in module_content
    assert 'ReactiveFormsModule' in module_content
    
    # Check component import and declaration
    assert 'SimplePydanticModelFormComponent' in module_content


@pytest.mark.unit
def test_generate_angular_forms_readme(temp_test_dir: Path) -> None:
    """Test that README is generated with instructions."""
    models = {'SimplePydanticModel': SimplePydanticModel}
    output_dir = temp_test_dir / "output"
    
    component_dir = generate_angular_forms(models, 'SimplePydanticModel', output_dir)
    
    readme_file = component_dir / "README.md"
    readme_content = readme_file.read_text()
    
    # Check for key sections
    assert 'SimplePydanticModel' in readme_content
    assert 'Prerequisites' in readme_content
    assert 'Installation' in readme_content
    assert 'ng add @angular/material' in readme_content
    assert 'Setup' in readme_content
    assert 'Usage' in readme_content or 'Component' in readme_content
