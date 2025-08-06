import pytest
from wizflow.plugins.log_message import LogMessagePlugin

@pytest.fixture
def plugin():
    """Fixture to create a LogMessagePlugin instance."""
    return LogMessagePlugin()

def test_plugin_name(plugin):
    """Test that the plugin's name is correct."""
    assert plugin.name == "log_message"

def test_required_imports(plugin):
    """Test that the plugin has no required imports."""
    assert plugin.required_imports == []

def test_get_function_definition(plugin):
    """Test the generated function definition."""
    definition = plugin.get_function_definition()
    assert "def log_message(message, level=\"INFO\"):" in definition
    assert 'print(f"[{level}] {message}")' in definition

def test_get_function_call(plugin):
    """Test the generated function call."""
    config = {
        "message": "Hello, World!",
        "level": "DEBUG"
    }
    call = plugin.get_function_call(config)
    assert call == "log_message(message='Hello, World!', level='DEBUG')"

def test_get_function_call_with_defaults(plugin):
    """Test the generated function call with default values."""
    config = {}
    call = plugin.get_function_call(config)
    assert call == "log_message(message='No message provided.', level='INFO')"
