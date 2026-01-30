"""
Pipeline module for generating web form UIs from JSON Schema.

This module generates interactive web forms using React JSON Schema Form (RJSF).
"""
import logging
import json
import shutil
import html
from pathlib import Path
from datetime import datetime

from exceptions import UIGenerationError

logger = logging.getLogger(__name__)


def generate_web_ui(
    schema_file: Path,
    main_model_name: str,
    output_dir: Path,
    framework: str = "react"
) -> Path:
    """
    Generate web form UI from JSON Schema.
    
    Args:
        schema_file: Path to the JSON Schema file
        main_model_name: Name of the main/root model
        output_dir: Base output directory
        framework: UI framework to use (default: "react")
    
    Returns:
        Path to the UI output directory
    
    Raises:
        UIGenerationError: If UI generation fails
    """
    logger.info(f"Generating web UI with framework: {framework}")
    
    # Validate schema file exists
    if not schema_file.exists():
        raise UIGenerationError(f"Schema file not found: {schema_file}")
    
    # Load the schema
    try:
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema = json.load(f)
    except json.JSONDecodeError as e:
        raise UIGenerationError(f"Invalid JSON schema: {e}")
    except Exception as e:
        raise UIGenerationError(f"Failed to load schema: {e}")
    
    # Create UI output directory
    ui_dir = output_dir / "ui"
    ui_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate based on framework
    if framework == "react":
        _generate_react_form(schema, schema_file, main_model_name, ui_dir)
    else:
        raise UIGenerationError(
            f"Unsupported framework: {framework}. Supported: react"
        )
    
    logger.info(f"Generated UI files in: {ui_dir}")
    return ui_dir


def _generate_react_form(
    schema: dict,
    schema_file: Path,
    main_model_name: str,
    ui_dir: Path
) -> None:
    """
    Generate React JSON Schema Form HTML.
    
    Args:
        schema: The JSON schema dictionary
        schema_file: Path to the schema file
        main_model_name: Name of the main model
        ui_dir: Output directory for UI files
    """
    logger.debug("Generating React form HTML")
    
    # Load template
    template_path = Path(__file__).parent / "templates" / "react-form.html"
    if not template_path.exists():
        raise UIGenerationError(f"Template not found: {template_path}")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    except Exception as e:
        raise UIGenerationError(f"Failed to load template: {e}")
    
    # Prepare template variables - escape HTML to prevent XSS
    title = html.escape(f"{main_model_name} Web Form")
    schema_json = json.dumps(schema, indent=2)
    
    # Simple template replacement (not using Jinja2 to minimize dependencies)
    html_content = template.replace("{{ title }}", title)
    html_content = html_content.replace("{{ schema_json }}", schema_json)
    
    # Write HTML file
    html_file = ui_dir / "index.html"
    try:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"Created: {html_file}")
    except Exception as e:
        raise UIGenerationError(f"Failed to write HTML file: {e}")
    
    # Create symlink to schema for reference
    schema_link = ui_dir / "schema.json"
    try:
        # Remove existing symlink if present
        if schema_link.exists() or schema_link.is_symlink():
            schema_link.unlink()
        # Create relative symlink
        schema_link.symlink_to(f"../{schema_file.name}")
        logger.debug(f"Created symlink: {schema_link}")
    except Exception as e:
        # Symlinks might fail on some systems, copy instead
        logger.warning(f"Could not create symlink, copying instead: {e}")
        try:
            shutil.copy2(schema_file, schema_link)
            logger.debug(f"Copied schema to: {schema_link}")
        except Exception as copy_error:
            logger.warning(f"Could not copy schema: {copy_error}")
    
    # Generate README with usage instructions
    _generate_readme(schema, main_model_name, ui_dir)


def _generate_readme(
    schema: dict,
    main_model_name: str,
    ui_dir: Path
) -> None:
    """
    Generate README with integration instructions.
    
    Args:
        schema: The JSON schema dictionary
        main_model_name: Name of the main model
        ui_dir: Output directory for UI files
    """
    logger.debug("Generating README")
    
    # Load template
    template_path = Path(__file__).parent / "templates" / "ui-readme.md"
    if not template_path.exists():
        raise UIGenerationError(f"README template not found: {template_path}")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    except Exception as e:
        raise UIGenerationError(f"Failed to load README template: {e}")
    
    # Calculate statistics
    total_types = len(schema.get('$defs', {})) + 1  # +1 for main model
    nested_types = len(schema.get('$defs', {}))
    
    # Format model list - all items with leading dash for consistent markdown
    model_list = [f"- {main_model_name} (main)"]
    if '$defs' in schema:
        model_list.extend([f"- {name}" for name in sorted(schema['$defs'].keys())])
    model_list_str = '\n'.join(model_list)
    
    # Generation timestamp
    generation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Replace template variables
    readme_content = template.replace("{{ model_name }}", main_model_name)
    readme_content = readme_content.replace("{{ total_types }}", str(total_types))
    readme_content = readme_content.replace("{{ nested_types }}", str(nested_types))
    readme_content = readme_content.replace("{{ model_list }}", model_list_str)
    readme_content = readme_content.replace("{{ generation_date }}", generation_date)
    
    # Write README
    readme_file = ui_dir / "README.md"
    try:
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        logger.info(f"Created: {readme_file}")
    except Exception as e:
        raise UIGenerationError(f"Failed to write README: {e}")
