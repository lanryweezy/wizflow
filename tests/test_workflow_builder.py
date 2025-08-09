import pytest
from unittest.mock import MagicMock

from wizflow.core.workflow_builder import WorkflowBuilder

@pytest.fixture
def workflow_builder():
    """Fixture to create a WorkflowBuilder instance with a mock LLM interface."""
    llm_interface = MagicMock()
    return WorkflowBuilder(llm_interface)

def test_schema_validation_success(workflow_builder):
    """Test that a valid workflow passes schema validation."""
    valid_workflow = {
        "name": "Valid Workflow",
        "description": "A valid workflow.",
        "trigger": {"type": "manual"},
        "actions": [{"type": "api_call"}]
    }

    # This should not raise an exception
    validated_workflow = workflow_builder._validate_workflow(valid_workflow)
    assert validated_workflow is not None

def test_schema_validation_failure(workflow_builder, capsys):
    """Test that an invalid workflow fails schema validation."""
    invalid_workflow = {
        "name": "Invalid Workflow",
        "description": "This is missing the 'actions' key.",
        "trigger": {"type": "manual"}
    }

    workflow_builder._validate_workflow(invalid_workflow)

    captured = capsys.readouterr()
    output = captured.out

    assert "Workflow validation error" in output
    assert "'actions' is a required property" in output
