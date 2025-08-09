import pytest
from unittest.mock import MagicMock

from wizflow.core.llm_interface import LLMInterface, MockProvider

def test_json_extraction_with_markdown():
    """Test that JSON can be extracted from a markdown code block."""
    mock_response = """
Here is the workflow you requested:
```json
{
  "name": "Test Workflow",
  "description": "A test workflow.",
  "trigger": {"type": "manual"},
  "actions": []
}
```
I hope this helps!
"""
    mock_provider = MockProvider()
    mock_provider.generate = MagicMock(return_value=mock_response)

    plugin_manager = MagicMock()
    plugin_manager.get_all_plugins.return_value = {}
    llm_interface = LLMInterface(config=MagicMock(), plugin_manager=plugin_manager)
    llm_interface.provider = mock_provider

    workflow = llm_interface.generate_workflow("test description")

    assert workflow is not None
    assert workflow["name"] == "Test Workflow"

def test_retry_mechanism():
    """Test that the LLM interface retries on failure."""
    invalid_json_response = "This is not JSON."
    valid_json_response = '''
    {
      "name": "Valid Workflow",
      "description": "This is a valid workflow.",
      "trigger": {"type": "manual"},
      "actions": []
    }
    '''

    mock_provider = MockProvider()
    mock_provider.generate = MagicMock(side_effect=[invalid_json_response, valid_json_response])

    plugin_manager = MagicMock()
    plugin_manager.get_all_plugins.return_value = {}
    llm_interface = LLMInterface(config=MagicMock(), plugin_manager=plugin_manager)
    llm_interface.provider = mock_provider

    workflow = llm_interface.generate_workflow("test description")

    assert workflow is not None
    assert workflow["name"] == "Valid Workflow"
    # Check that the provider was called twice
    assert mock_provider.generate.call_count == 2
