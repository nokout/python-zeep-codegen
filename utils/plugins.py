"""
Plugin architecture for output format extensibility.

Provides a base interface and registry for output format plugins, allowing
custom output formats to be added without modifying core code.
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Type, Any, Optional
from pathlib import Path

logger: logging.Logger = logging.getLogger(__name__)


class OutputPlugin(ABC):
    """
    Abstract base class for output format plugins.
    
    All output plugins should inherit from this class and implement
    the generate method to produce output in their specific format.
    
    Attributes:
        name: Unique identifier for this plugin
        description: Human-readable description of the output format
    """
    
    name: str = "base"
    description: str = "Base output plugin"
    
    @abstractmethod
    def generate(
        self,
        pydantic_models: Dict[str, Type[Any]],
        main_model: str,
        output_path: Path,
        **options: Any
    ) -> Path:
        """
        Generate output in the plugin's format.
        
        Args:
            pydantic_models: Dictionary of Pydantic model classes
            main_model: Name of the main/root model
            output_path: Path where output should be written
            **options: Additional plugin-specific options
        
        Returns:
            Path to generated output file
        
        Raises:
            Exception: If generation fails
        """
        pass


class PluginRegistry:
    """
    Registry for managing output format plugins.
    
    Maintains a collection of registered plugins and provides methods
    to discover, register, and retrieve them.
    
    Example:
        >>> registry = PluginRegistry()
        >>> registry.register(JSONSchemaPlugin())
        >>> plugin = registry.get('json_schema')
        >>> plugin.generate(models, 'Order', Path('output.json'))
    """
    
    def __init__(self) -> None:
        """Initialize empty plugin registry."""
        self._plugins: Dict[str, OutputPlugin] = {}
    
    def register(self, plugin: OutputPlugin) -> None:
        """
        Register a new plugin.
        
        Args:
            plugin: Plugin instance to register
        
        Raises:
            ValueError: If plugin with same name already registered
        
        Example:
            >>> registry = PluginRegistry()
            >>> plugin = MyPlugin()
            >>> registry.register(plugin)
        """
        if plugin.name in self._plugins:
            raise ValueError(f"Plugin '{plugin.name}' already registered")
        
        self._plugins[plugin.name] = plugin
        logger.info(f"Registered plugin: {plugin.name} - {plugin.description}")
    
    def get(self, name: str) -> Optional[OutputPlugin]:
        """
        Get plugin by name.
        
        Args:
            name: Plugin name
        
        Returns:
            Plugin instance or None if not found
        
        Example:
            >>> registry = PluginRegistry()
            >>> plugin = registry.get('json_schema')
        """
        return self._plugins.get(name)
    
    def list_plugins(self) -> Dict[str, str]:
        """
        Get dictionary of all registered plugins.
        
        Returns:
            Dictionary mapping plugin names to descriptions
        
        Example:
            >>> registry = PluginRegistry()
            >>> plugins = registry.list_plugins()
            >>> for name, desc in plugins.items():
            ...     print(f"{name}: {desc}")
        """
        return {name: plugin.description for name, plugin in self._plugins.items()}
    
    def __repr__(self) -> str:
        """String representation of registry."""
        return f"PluginRegistry(plugins={list(self._plugins.keys())})"


# Global plugin registry instance
_default_registry: Optional[PluginRegistry] = None


def get_default_registry() -> PluginRegistry:
    """
    Get the default global plugin registry.
    
    Returns:
        Global PluginRegistry instance
    
    Example:
        >>> registry = get_default_registry()
        >>> registry.register(MyPlugin())
    """
    global _default_registry
    if _default_registry is None:
        _default_registry = PluginRegistry()
    return _default_registry
