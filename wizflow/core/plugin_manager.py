"""
Plugin Manager for WizFlow
Discovers, loads, and manages action plugins.
"""

import importlib
import inspect
import pkgutil
from typing import Dict, Optional, Type

from wizflow.plugins.base import ActionPlugin


class PluginManager:
    """
    Manages the discovery and loading of action plugins.
    """

    def __init__(self):
        self.plugins: Dict[str, ActionPlugin] = {}
        self._load_plugins()

    def _load_plugins(self):
        """
        Dynamically discovers and loads plugins from the 'wizflow.plugins' package.
        """
        import wizflow.plugins

        plugin_package = wizflow.plugins
        prefix = plugin_package.__name__ + "."

        for importer, modname, ispkg in pkgutil.iter_modules(plugin_package.__path__, prefix):
            if modname == 'wizflow.plugins.base':
                continue

            try:
                module = importlib.import_module(modname)
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, ActionPlugin) and obj is not ActionPlugin:
                        plugin_instance = obj()
                        self.plugins[plugin_instance.name] = plugin_instance
                        print(f"✅ Loaded plugin: {plugin_instance.name}")
            except Exception as e:
                print(f"❌ Failed to load plugin from {modname}: {e}")

    def get_plugin(self, name: str) -> Optional[ActionPlugin]:
        """
        Retrieves a loaded plugin by its action name.

        Args:
            name: The name of the action (e.g., 'send_email').

        Returns:
            An instance of the ActionPlugin, or None if not found.
        """
        return self.plugins.get(name)

    def get_all_plugins(self) -> Dict[str, ActionPlugin]:
        """
        Returns all loaded plugins.
        """
        return self.plugins
