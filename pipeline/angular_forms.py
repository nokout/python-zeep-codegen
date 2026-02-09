"""
Pipeline module for generating Angular Reactive Forms from Pydantic models.

This module handles Step 4 (optional) of the conversion pipeline: taking Pydantic 
models and generating Angular TypeScript interfaces and Reactive Forms with Angular 
Material components.
"""
import logging
import json
from pathlib import Path
from typing import Dict, Type, Any, Optional, List, get_origin, get_args
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from exceptions import WSDLSchemaError

logger: logging.Logger = logging.getLogger(__name__)


class AngularFormGenerationError(WSDLSchemaError):
    """Raised when Angular form generation fails."""
    pass


def _get_typescript_type(python_type: Any) -> str:
    """
    Map Python/Pydantic types to TypeScript types.
    
    Args:
        python_type: Python type annotation
    
    Returns:
        TypeScript type string
    """
    # Handle None/Optional
    if python_type is type(None):
        return 'null'
    
    # Get origin for generic types (List, Optional, etc.)
    origin = get_origin(python_type)
    
    # Handle Union types (Optional is Union[X, None])
    if origin is not None:
        type_args = get_args(python_type)
        
        # Check for Optional (Union with None)
        if len(type_args) == 2 and type(None) in type_args:
            # This is Optional[T], get the non-None type
            inner_type = type_args[0] if type_args[1] is type(None) else type_args[1]
            return f"{_get_typescript_type(inner_type)} | null"
        
        # Handle List/list
        if origin is list or str(origin) == 'typing.List':
            if type_args:
                inner = _get_typescript_type(type_args[0])
                return f"{inner}[]"
            return 'any[]'
    
    # Handle basic types
    type_str = str(python_type)
    
    if python_type is str or 'str' in type_str:
        return 'string'
    elif python_type is int or 'int' in type_str:
        return 'number'
    elif python_type is float or 'float' in type_str:
        return 'number'
    elif python_type is bool or 'bool' in type_str:
        return 'boolean'
    elif python_type is Decimal or 'Decimal' in type_str:
        return 'number'
    elif python_type is datetime or 'datetime' in type_str:
        return 'string'  # ISO 8601 format
    elif python_type is date or 'date' in type_str:
        return 'string'  # ISO 8601 format
    elif hasattr(python_type, '__bases__') and Enum in python_type.__bases__:
        # Enum type
        return 'string'
    
    # Default to any for complex types
    return 'any'


def _is_array_field(field_info: FieldInfo) -> bool:
    """
    Check if a field is an array type.
    
    Args:
        field_info: Pydantic FieldInfo object
    
    Returns:
        True if field is an array, False otherwise
    """
    origin = get_origin(field_info.annotation)
    if origin is list or str(origin) == 'typing.List':
        return True
    return False


def _get_array_item_type(field_info: FieldInfo) -> Any:
    """
    Get the item type of an array field.
    
    Args:
        field_info: Pydantic FieldInfo object
    
    Returns:
        The type of array items, or None if not an array
    """
    origin = get_origin(field_info.annotation)
    if origin is list or str(origin) == 'typing.List':
        type_args = get_args(field_info.annotation)
        if type_args:
            return type_args[0]
    return None


def _is_complex_type(python_type: Any) -> bool:
    """
    Check if a type is a complex type (not a simple primitive).
    
    Args:
        python_type: Python type to check
    
    Returns:
        True if complex type, False if simple/primitive
    """
    if python_type is None:
        return False
    
    type_str = str(python_type)
    
    # Simple types
    simple_types = [str, int, float, bool, Decimal, datetime, date]
    if python_type in simple_types:
        return False
    
    if any(t in type_str for t in ['str', 'int', 'float', 'bool', 'Decimal', 'datetime', 'date']):
        return False
    
    # Enums are treated as simple (string select)
    if hasattr(python_type, '__bases__') and Enum in python_type.__bases__:
        return False
    
    # If it has model_fields, it's likely a Pydantic model (complex)
    if hasattr(python_type, 'model_fields'):
        return True
    
    return False


def _get_angular_material_component(
    field_name: str,
    field_type: str,
    is_required: bool,
    field_info: FieldInfo
) -> str:
    """
    Generate Angular Material form field HTML for a given field type.
    
    Args:
        field_name: Name of the field
        field_type: TypeScript type string
        is_required: Whether the field is required
        field_info: Pydantic FieldInfo object
    
    Returns:
        HTML string for the Angular Material component
    """
    label = field_name.replace('_', ' ').title()
    required_attr = ' required' if is_required else ''
    
    # Handle array types
    if field_type.endswith('[]'):
        return f'''  <mat-form-field appearance="outline">
    <mat-label>{label}</mat-label>
    <input matInput formControlName="{field_name}" placeholder="{label}"{required_attr}>
    <mat-hint>Comma-separated values</mat-hint>
  </mat-form-field>'''
    
    # Handle boolean
    if 'boolean' in field_type:
        return f'''  <mat-checkbox formControlName="{field_name}">
    {label}
  </mat-checkbox>'''
    
    # Handle number types
    if 'number' in field_type:
        return f'''  <mat-form-field appearance="outline">
    <mat-label>{label}</mat-label>
    <input matInput type="number" formControlName="{field_name}" placeholder="{label}"{required_attr}>
  </mat-form-field>'''
    
    # Handle date/datetime
    if field_type == 'string' and ('date' in field_name.lower() or 'time' in field_name.lower()):
        return f'''  <mat-form-field appearance="outline">
    <mat-label>{label}</mat-label>
    <input matInput type="date" formControlName="{field_name}" placeholder="{label}"{required_attr}>
  </mat-form-field>'''
    
    # Default: text input
    return f'''  <mat-form-field appearance="outline">
    <mat-label>{label}</mat-label>
    <input matInput formControlName="{field_name}" placeholder="{label}"{required_attr}>
  </mat-form-field>'''


def _generate_form_array_component(
    field_name: str,
    item_type: Any,
    is_complex: bool
) -> str:
    """
    Generate Angular FormArray component with add/edit/remove functionality.
    
    Args:
        field_name: Name of the array field
        item_type: Type of items in the array
        is_complex: Whether items are complex objects or simple types
    
    Returns:
        HTML string for the FormArray component
    """
    label = field_name.replace('_', ' ').title()
    singular_name = field_name.rstrip('s') if field_name.endswith('s') else field_name
    singular_label = singular_name.replace('_', ' ').title()
    
    if is_complex:
        # For complex objects, show a table/list with add/edit/remove buttons
        item_type_name = item_type.__name__ if hasattr(item_type, '__name__') else 'Item'
        
        return f'''  <!-- FormArray for {label} -->
  <div class="form-array-section">
    <h3>{label}</h3>
    
    <div *ngIf="{field_name}Array.length === 0" class="empty-message">
      No {label.lower()} added yet
    </div>
    
    <div *ngFor="let item of {field_name}Array.controls; let i = index" class="array-item">
      <mat-card>
        <mat-card-content>
          <div [formGroupName]="i">
            <!-- Fields for {item_type_name} will be generated here -->
            <p><strong>{singular_label} #{{{{i + 1}}}}</strong></p>
            <div class="item-summary">{{{{get{item_type_name}Summary(i)}}}}</div>
          </div>
        </mat-card-content>
        <mat-card-actions>
          <button mat-button color="warn" type="button" (click)="remove{item_type_name}(i)">
            <mat-icon>delete</mat-icon> Remove
          </button>
        </mat-card-actions>
      </mat-card>
    </div>
    
    <button mat-raised-button color="accent" type="button" (click)="add{item_type_name}()" class="add-button">
      <mat-icon>add</mat-icon> Add {singular_label}
    </button>
  </div>'''
    else:
        # For simple types, show a chip list with add/remove
        return f'''  <!-- FormArray for {label} (simple type) -->
  <div class="form-array-section">
    <mat-form-field appearance="outline" class="full-width">
      <mat-label>{label}</mat-label>
      <mat-chip-grid #chipGrid aria-label="{label}">
        <mat-chip-row *ngFor="let item of {field_name}Array.controls; let i = index"
                      (removed)="remove{singular_label.replace(' ', '')}(i)">
          {{{{item.value}}}}
          <button matChipRemove>
            <mat-icon>cancel</mat-icon>
          </button>
        </mat-chip-row>
      </mat-chip-grid>
      <input placeholder="Add {singular_label.lower()}"
             [matChipInputFor]="chipGrid"
             (matChipInputTokenEnd)="add{singular_label.replace(' ', '')}($event)"/>
    </mat-form-field>
  </div>'''


def _generate_typescript_interface(
    model_name: str,
    model: Type[BaseModel]
) -> str:
    """
    Generate TypeScript interface from Pydantic model.
    
    Args:
        model_name: Name of the model
        model: Pydantic model class
    
    Returns:
        TypeScript interface definition
    """
    lines: List[str] = [f"export interface {model_name} {{"]
    
    for field_name, field_info in model.model_fields.items():
        ts_type = _get_typescript_type(field_info.annotation)
        optional = '?' if not field_info.is_required() else ''
        lines.append(f"  {field_name}{optional}: {ts_type};")
    
    lines.append("}")
    return '\n'.join(lines)


def _generate_angular_component(
    model_name: str,
    model: Type[BaseModel]
) -> Dict[str, str]:
    """
    Generate Angular component files (TypeScript, HTML, CSS) for a Pydantic model.
    
    Args:
        model_name: Name of the model
        model: Pydantic model class
    
    Returns:
        Dictionary with keys 'ts', 'html', 'css' containing file contents
    """
    component_name = f"{model_name.lower()}-form"
    class_name = f"{model_name}FormComponent"
    
    # Generate TypeScript interface
    interface = _generate_typescript_interface(model_name, model)
    
    # Generate form fields
    form_fields: List[str] = []
    validators: List[str] = []
    
    for field_name, field_info in model.model_fields.items():
        # Determine validators
        field_validators: List[str] = []
        if field_info.is_required():
            field_validators.append('Validators.required')
        
        # Add constraints if available
        if hasattr(field_info, 'metadata') and field_info.metadata:
            for constraint in field_info.metadata:
                if hasattr(constraint, 'min_length'):
                    field_validators.append(f'Validators.minLength({constraint.min_length})')
                if hasattr(constraint, 'max_length'):
                    field_validators.append(f'Validators.maxLength({constraint.max_length})')
                if hasattr(constraint, 'pattern'):
                    field_validators.append(f'Validators.pattern({constraint.pattern!r})')
        
        validator_str = f"[{', '.join(field_validators)}]" if field_validators else '[]'
        
        # Default value - handle Pydantic special values
        default_val = 'null'
        
        # Check if field has a real default value
        if field_info.default is not PydanticUndefined and field_info.default is not None:
            # Handle different types of defaults
            if isinstance(field_info.default, str):
                default_val = f"'{field_info.default}'"
            elif isinstance(field_info.default, bool):
                default_val = str(field_info.default).lower()
            elif isinstance(field_info.default, (int, float)):
                default_val = str(field_info.default)
            elif isinstance(field_info.default, list):
                default_val = '[]'
            elif isinstance(field_info.default, dict):
                default_val = '{}'
            else:
                # For any other type, use null
                default_val = 'null'
        elif field_info.default_factory is not None:
            # Handle default_factory (e.g., list, dict factories)
            default_val = '[]'  # Most common case is list/dict factories
        
        form_fields.append(f"      {field_name}: [{default_val}, {validator_str}]")
        if field_validators:
            validators.append(field_name)
    
    form_group = ',\n'.join(form_fields)
    
    # Generate TypeScript component
    ts_content = f'''import {{ Component, OnInit }} from '@angular/core';
import {{ FormBuilder, FormGroup, Validators }} from '@angular/forms';

{interface}

@Component({{
  selector: 'app-{component_name}',
  templateUrl: './{component_name}.component.html',
  styleUrls: ['./{component_name}.component.css']
}})
export class {class_name} implements OnInit {{
  {model_name.lower()}Form!: FormGroup;

  constructor(private fb: FormBuilder) {{}}

  ngOnInit(): void {{
    this.{model_name.lower()}Form = this.fb.group({{
{form_group}
    }});
  }}

  onSubmit(): void {{
    if (this.{model_name.lower()}Form.valid) {{
      const formValue: {model_name} = this.{model_name.lower()}Form.value;
      console.log('{model_name} form submitted:', formValue);
      // TODO: Implement form submission logic (e.g., HTTP POST to API)
    }}
  }}

  onReset(): void {{
    this.{model_name.lower()}Form.reset();
  }}
}}
'''
    
    # Generate HTML template
    html_fields: List[str] = []
    for field_name, field_info in model.model_fields.items():
        ts_type = _get_typescript_type(field_info.annotation)
        is_required = field_info.is_required()
        component_html = _get_angular_material_component(
            field_name, ts_type, is_required, field_info
        )
        html_fields.append(component_html)
    
    html_content = f'''<div class="form-container">
  <h2>{model_name} Form</h2>
  
  <form [formGroup]="{model_name.lower()}Form" (ngSubmit)="onSubmit()">
{chr(10).join(html_fields)}

    <div class="button-row">
      <button mat-raised-button color="primary" type="submit" [disabled]="!{model_name.lower()}Form.valid">
        Submit
      </button>
      <button mat-raised-button type="button" (click)="onReset()">
        Reset
      </button>
    </div>
  </form>
</div>
'''
    
    # Generate CSS
    css_content = '''.form-container {
  max-width: 600px;
  margin: 2rem auto;
  padding: 2rem;
}

h2 {
  margin-bottom: 1.5rem;
  color: #333;
}

mat-form-field {
  width: 100%;
  margin-bottom: 1rem;
}

mat-checkbox {
  margin-bottom: 1rem;
}

.button-row {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.button-row button {
  flex: 1;
}
'''
    
    return {
        'ts': ts_content,
        'html': html_content,
        'css': css_content
    }


def _generate_module_file(model_name: str) -> str:
    """
    Generate Angular module file that imports necessary Angular Material modules.
    
    Args:
        model_name: Name of the model
    
    Returns:
        TypeScript module file content
    """
    component_name = f"{model_name.lower()}-form"
    class_name = f"{model_name}FormComponent"
    
    return f'''import {{ NgModule }} from '@angular/core';
import {{ CommonModule }} from '@angular/common';
import {{ ReactiveFormsModule }} from '@angular/forms';

// Angular Material imports
import {{ MatFormFieldModule }} from '@angular/material/form-field';
import {{ MatInputModule }} from '@angular/material/input';
import {{ MatButtonModule }} from '@angular/material/button';
import {{ MatCheckboxModule }} from '@angular/material/checkbox';
import {{ MatDatepickerModule }} from '@angular/material/datepicker';
import {{ MatNativeDateModule }} from '@angular/material/core';

import {{ {class_name} }} from './{component_name}.component';

@NgModule({{
  declarations: [
    {class_name}
  ],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatCheckboxModule,
    MatDatepickerModule,
    MatNativeDateModule
  ],
  exports: [
    {class_name}
  ]
}})
export class {model_name}FormModule {{ }}
'''


def _generate_readme(model_name: str) -> str:
    """
    Generate README with setup and usage instructions.
    
    Args:
        model_name: Name of the model
    
    Returns:
        README content
    """
    component_name = f"{model_name.lower()}-form"
    
    return f'''# {model_name} Angular Form

This directory contains an auto-generated Angular Reactive Form with Angular Material components for the `{model_name}` model.

## Prerequisites

- Angular 15+ (recommended)
- Angular Material installed

## Installation

If you haven't installed Angular Material yet:

```bash
ng add @angular/material
```

## Setup

1. Import the module in your app:

```typescript
// In your app.module.ts or feature module
import {{ {model_name}FormModule }} from './path-to/{component_name}/{component_name}.module';

@NgModule({{
  imports: [
    // ... other imports
    {model_name}FormModule
  ]
}})
```

2. Use the component in your template:

```html
<app-{component_name}></app-{component_name}>
```

## Component Structure

- `{component_name}.component.ts` - Component logic with reactive form
- `{component_name}.component.html` - Angular Material form template
- `{component_name}.component.css` - Component styles
- `{component_name}.module.ts` - Module with Material imports

## Validation

The form includes validation rules derived from the Pydantic model:
- Required fields are marked with validators
- String length constraints are enforced
- Pattern matching for specific formats

## Customization

You can customize:
- Form layout and styling in the CSS file
- Validation messages
- Submit logic in the `onSubmit()` method
- Additional form controls or Material components

## API Integration

To integrate with a backend API, update the `onSubmit()` method in the component:

```typescript
onSubmit(): void {{
  if (this.{model_name.lower()}Form.valid) {{
    const formValue: {model_name} = this.{model_name.lower()}Form.value;
    
    // Example HTTP POST
    this.http.post('/api/{model_name.lower()}', formValue)
      .subscribe({{
        next: (response) => console.log('Success:', response),
        error: (error) => console.error('Error:', error)
      }});
  }}
}}
```

## Generated From

This form was auto-generated from a Pydantic model definition using python-zeep-codegen.

Source: WSDL/XSD → Pydantic Model → Angular Form
'''


def generate_angular_forms(
    pydantic_models: Dict[str, Type[Any]],
    main_model_name: str,
    output_dir: Optional[Path] = None
) -> Path:
    """
    Generate Angular Reactive Forms with TypeScript interfaces and Angular Material components.
    
    Creates a complete Angular component with:
    - TypeScript interface matching the Pydantic model
    - Reactive form with FormBuilder
    - Angular Material form fields
    - Validation rules from Pydantic constraints
    
    Args:
        pydantic_models: Dictionary mapping model names to Pydantic model classes
        main_model_name: Name of the main model to generate form for
        output_dir: Directory to save Angular component files (default: 'output/angular')
    
    Returns:
        Path to generated Angular component directory
    
    Raises:
        AngularFormGenerationError: If main model not found or generation fails
    
    Example:
        >>> models = {'Order': OrderModel}
        >>> path = generate_angular_forms(models, 'Order')
        >>> print(path)
        output/angular/order-form
    """
    logger.info(f"Generating Angular Reactive Form for model: {main_model_name}")
    
    if main_model_name not in pydantic_models:
        available: str = ', '.join(pydantic_models.keys())
        error_msg: str = (
            f"Model '{main_model_name}' not found. "
            f"Available models: {available}"
        )
        logger.error(error_msg)
        raise AngularFormGenerationError(error_msg)
    
    main_model: Type[Any] = pydantic_models[main_model_name]
    
    # Determine output directory
    if output_dir:
        angular_dir: Path = Path(output_dir) / "angular"
    else:
        angular_dir = Path("output") / "angular"
    
    component_name = f"{main_model_name.lower()}-form"
    component_dir: Path = angular_dir / component_name
    component_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Creating Angular component at: {component_dir}")
    
    try:
        # Generate component files
        component_files = _generate_angular_component(main_model_name, main_model)
        
        # Write TypeScript component
        ts_file = component_dir / f"{component_name}.component.ts"
        with open(ts_file, 'w') as f:
            f.write(component_files['ts'])
        logger.info(f"Created TypeScript component: {ts_file.name}")
        
        # Write HTML template
        html_file = component_dir / f"{component_name}.component.html"
        with open(html_file, 'w') as f:
            f.write(component_files['html'])
        logger.info(f"Created HTML template: {html_file.name}")
        
        # Write CSS styles
        css_file = component_dir / f"{component_name}.component.css"
        with open(css_file, 'w') as f:
            f.write(component_files['css'])
        logger.info(f"Created CSS file: {css_file.name}")
        
        # Write module file
        module_file = component_dir / f"{component_name}.module.ts"
        module_content = _generate_module_file(main_model_name)
        with open(module_file, 'w') as f:
            f.write(module_content)
        logger.info(f"Created module file: {module_file.name}")
        
        # Write README
        readme_file = component_dir / "README.md"
        readme_content = _generate_readme(main_model_name)
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        logger.info(f"Created README: {readme_file.name}")
        
        # Create summary file
        summary_file = angular_dir / "generation-summary.json"
        summary = {
            "model": main_model_name,
            "component_name": component_name,
            "component_path": str(component_dir),
            "files_generated": [
                f"{component_name}.component.ts",
                f"{component_name}.component.html",
                f"{component_name}.component.css",
                f"{component_name}.module.ts",
                "README.md"
            ],
            "field_count": len(main_model.model_fields),
            "fields": list(main_model.model_fields.keys())
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Created generation summary: {summary_file}")
        
        logger.info(f"✓ Angular form generation complete!")
        logger.info(f"Generated {len(main_model.model_fields)} form fields")
        
        return component_dir
        
    except Exception as e:
        error_msg = f"Failed to generate Angular forms: {e}"
        logger.error(error_msg)
        raise AngularFormGenerationError(error_msg)
