"""
Plugin Manager for WizFlow
Discovers, loads, and manages action and trigger plugins.
"""

import importlib
import inspect
import pkgutil
from typing import Dict, Optional, Type, Union

from wizflow.plugins.base import ActionPlugin
from wizflow.plugins.trigger_base import TriggerPlugin
from wizflow.logger import get_logger


class PluginManager:
    """
    Manages the discovery and loading of action and trigger plugins.
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.action_plugins: Dict[str, ActionPlugin] = {}
        self.trigger_plugins: Dict[str, TriggerPlugin] = {}
        self._load_plugins()

    def _load_plugins(self):
        """
        Dynamically discovers and loads plugins from the 'wizflow.plugins' package.
        """
        import wizflow.plugins

        plugin_package = wizflow.plugins
        prefix = plugin_package.__name__ + "."

        for importer, modname, ispkg in pkgutil.iter_modules(plugin_package.__path__, prefix):
            if modname in ['wizflow.plugins.base', 'wizflow.plugins.trigger_base']:
                continue

            try:
                module = importlib.import_module(modname)
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj):
                        if issubclass(obj, ActionPlugin) and obj is not ActionPlugin:
                            plugin_instance = obj()
                            self.action_plugins[plugin_instance.name] = plugin_instance
                            self.logger.debug(f"✅ Loaded action plugin: {plugin_instance.name}")
                        elif issubclass(obj, TriggerPlugin) and obj is not TriggerPlugin:
                            plugin_instance = obj()
                            self.trigger_plugins[plugin_instance.name] = plugin_instance
                            self.logger.debug(f"✅ Loaded trigger plugin: {plugin_instance.name}")
            except Exception as e:
                self.logger.error(f"❌ Failed to load plugin from {modname}: {e}")

    def get_action_plugin(self, name: str) -> Optional[ActionPlugin]:
        """
        Retrieves a loaded action plugin by its name.
        """
        return self.action_plugins.get(name)

    def get_all_action_plugins(self) -> Dict[str, ActionPlugin]:
        """
        Returns all loaded action plugins.
        """
        return self.action_plugins

    def get_trigger_plugin(self, name: str) -> Optional[TriggerPlugin]:
        """
        Retrieves a loaded trigger plugin by its name.
        """
        return self.trigger_plugins.get(name)

    def get_all_trigger_plugins(self) -> Dict[str, TriggerPlugin]:
        """
        Returns all loaded trigger plugins.
        """
        return self.trigger_plugins
