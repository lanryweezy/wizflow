import pytest

from wizflow.core.plugin_manager import PluginManager
from wizflow.plugins.base import ActionPlugin

def test_plugin_manager_discovery():
    """Test that the PluginManager discovers all plugins."""
    manager = PluginManager()
    all_plugins = manager.get_all_plugins()

    # List of expected plugin names
    expected_plugins = [
        "send_email",
        "api_call",
        "web_scrape",
        "file_process",
        "send_whatsapp",
        "summarize",
        "log_message",
    ]

    assert len(all_plugins) == len(expected_plugins)
    for name in expected_plugins:
        assert name in all_plugins
        assert isinstance(all_plugins[name], ActionPlugin)

def test_get_plugin():
    """Test retrieving a single plugin."""
    manager = PluginManager()

    # Test getting a known plugin
    plugin = manager.get_plugin("send_email")
    assert plugin is not None
    assert plugin.name == "send_email"
    assert isinstance(plugin, ActionPlugin)

    # Test getting a non-existent plugin
    plugin = manager.get_plugin("non_existent_plugin")
    assert plugin is None
