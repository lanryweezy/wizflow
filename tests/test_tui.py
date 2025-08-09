import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock

from wizflow.tui import WorkflowEditor

@pytest.fixture
def mock_workflow_file(tmp_path):
    """Creates a mock workflow JSON file."""
    workflow_data = {
        "name": "Test TUI Workflow",
        "actions": [
            {"type": "api_call", "config": {"url": "https://test.com"}}
        ]
    }
    workflow_path = tmp_path / "test-workflow.json"
    workflow_path.write_text(json.dumps(workflow_data))
    return workflow_path

def test_workflow_editor_initialization(mock_workflow_file):
    """Test that the WorkflowEditor initializes correctly."""
    # We can't run the app, but we can test the constructor and data loading.
    editor = WorkflowEditor(str(mock_workflow_file))
    editor.run = MagicMock() # Mock the run method to prevent it from starting

    # Test that the workflow data was loaded
    assert editor.workflow_data is not None
    assert editor.workflow_data["name"] == "Test TUI Workflow"
    assert len(editor.workflow_data["actions"]) == 1
    assert editor.workflow_data["actions"][0]["type"] == "api_call"
