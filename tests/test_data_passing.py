import pytest
from unittest.mock import patch

from wizflow.cli import WizFlowCLI

@pytest.fixture
def cli_instance(monkeypatch, tmp_path):
    """Fixture to create a WizFlowCLI instance for testing."""
    monkeypatch.setattr('pathlib.Path.cwd', lambda: tmp_path)
    cli = WizFlowCLI()
    cli.workflows_dir = tmp_path / "workflows"
    cli.workflows_dir.mkdir(exist_ok=True)
    return cli

def test_data_passing_code_generation(cli_instance):
    """Test that the generated code for data passing is correct."""

    workflow_json = {
        "name": "Data Passing Test",
        "trigger": {"type": "manual"},
        "actions": [
            {"type": "summarize", "config": {"input_text": "{{some_variable}}"}},
            {"type": "log_message", "config": {"message": "Summary was: {{summary}}"}}
        ]
    }

    code = cli_instance.generator.generate_code(workflow_json)

    assert "summarize_text(text=variables.get('some_variable')" in code
    # Check for the f-string implementation of template resolution
    assert 'log_message(message=f"Summary was: {variables.get(\'summary\', \'\')}"' in code
