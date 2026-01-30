"""
Configuration management module.

Supports loading configuration from YAML and TOML files to provide
default values for CLI options.
"""
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # type: ignore

logger: logging.Logger = logging.getLogger(__name__)


class Config:
    """
    Configuration manager for python-zeep-codegen.
    
    Loads and manages configuration from YAML or TOML files. Configuration
    can provide default values for CLI options like output directories,
    verbosity, and temp directory management.
    
    Attributes:
        data: Dictionary containing configuration values
        
    Example YAML config:
        ```yaml
        # .zeep-codegen.yaml
        output_dir: ./generated
        keep_temp: false
        verbose: false
        timeout: 30
        ```
    
    Example TOML config:
        ```toml
        # .zeep-codegen.toml
        output_dir = "./generated"
        keep_temp = false
        verbose = false
        timeout = 30
        ```
    """
    
    def __init__(self, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize configuration.
        
        Args:
            data: Optional initial configuration dictionary
        """
        self.data: Dict[str, Any] = data or {}
    
    @classmethod
    def load_from_file(cls, config_path: Path) -> 'Config':
        """
        Load configuration from YAML or TOML file.
        
        Args:
            config_path: Path to configuration file (.yaml, .yml, or .toml)
        
        Returns:
            Config instance with loaded data
        
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file format is unsupported
        
        Example:
            >>> config = Config.load_from_file(Path('.zeep-codegen.yaml'))
            >>> print(config.get('output_dir'))
            ./generated
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        suffix = config_path.suffix.lower()
        
        if suffix in ['.yaml', '.yml']:
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f) or {}
            logger.info(f"Loaded YAML config from {config_path}")
        elif suffix == '.toml':
            with open(config_path, 'rb') as f:
                data = tomllib.load(f)
            logger.info(f"Loaded TOML config from {config_path}")
        else:
            raise ValueError(f"Unsupported config file format: {suffix}")
        
        return cls(data)
    
    @classmethod
    def discover(cls, start_path: Optional[Path] = None) -> Optional['Config']:
        """
        Discover and load configuration file from current or parent directories.
        
        Searches for .zeep-codegen.yaml, .zeep-codegen.yml, or .zeep-codegen.toml
        in the current directory and parent directories.
        
        Args:
            start_path: Directory to start search from (default: current directory)
        
        Returns:
            Config instance if found, None otherwise
        
        Example:
            >>> config = Config.discover()
            >>> if config:
            ...     print("Found config:", config.get('output_dir'))
        """
        if start_path is None:
            start_path = Path.cwd()
        
        config_names = [
            '.zeep-codegen.yaml',
            '.zeep-codegen.yml',
            '.zeep-codegen.toml'
        ]
        
        current_dir = start_path
        
        # Search up to root directory
        while True:
            for config_name in config_names:
                config_path = current_dir / config_name
                if config_path.exists():
                    logger.info(f"Discovered config file: {config_path}")
                    return cls.load_from_file(config_path)
            
            # Move to parent directory
            parent = current_dir.parent
            if parent == current_dir:
                # Reached root
                break
            current_dir = parent
        
        logger.debug("No config file found")
        return None
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        
        Example:
            >>> config = Config({'output_dir': './gen'})
            >>> config.get('output_dir')
            './gen'
            >>> config.get('missing', 'default')
            'default'
        """
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self.data[key] = value
    
    def merge(self, other: Dict[str, Any]) -> None:
        """
        Merge another configuration dictionary into this one.
        
        Args:
            other: Dictionary to merge (takes precedence)
        
        Example:
            >>> config = Config({'a': 1, 'b': 2})
            >>> config.merge({'b': 3, 'c': 4})
            >>> config.get('b')
            3
        """
        self.data.update(other)
    
    def __repr__(self) -> str:
        """String representation of config."""
        return f"Config({self.data})"
