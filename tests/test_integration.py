import pytest
import os
from pathlib import Path

from wizflow.cli import WizFlowCLI
from wizflow.core.llm_interface import MockProvider

@pytest.fixture
def cli_instance(monkeypatch, tmp_path):
    """Fixture to create a WizFlowCLI instance for testing."""
    # Use a temporary directory for workflows
    workflows_dir = tmp_path / "workflows"
    monkeypatch.setattr('pathlib.Path.cwd', lambda: tmp_path)

    cli = WizFlowCLI()
    # Override the workflows directory
    cli.workflows_dir = workflows_dir
    cli.workflows_dir.mkdir(exist_ok=True)

    # Force the CLI to use the MockProvider for predictable output
    monkeypatch.setattr(cli.llm, 'provider', MockProvider())

    return cli

def test_end_to_end_workflow_generation(cli_instance):
    """
    Test the full workflow generation process from description to Python script.
    """
    description = "When I get an email from my boss, send a summary to my WhatsApp"
    output_name = "test_whatsapp_alert"

    # Generate the workflow
    json_path_str, py_path_str = cli_instance.generate_workflow(description, output_name)

    json_path = Path(json_path_str)
    py_path = Path(py_path_str)

    # 1. Check if files were created
    assert json_path.exists()
    assert py_path.exists()
    assert json_path.name == f"{output_name}.json"
    assert py_path.name == f"{output_name}.py"

    # 2. Check if the Python script is syntactically valid
    try:
        with open(py_path, 'r') as f:
            source_code = f.read()
        compile(source_code, str(py_path), 'exec')
    except SyntaxError as e:
        pytest.fail(f"Generated Python script has a syntax error: {e}\n\n--- Code ---\n{source_code}")

    # 3. Check if the generated code contains expected elements from the mock response
    with open(py_path, 'r') as f:
        code = f.read()

    # The mock provider generates a workflow with 'summarize' and 'send_whatsapp'
    assert "def summarize_text(" in code
    assert "def send_whatsapp(" in code
    assert "send_whatsapp(to_number='+1234567890'" in code # Check call code
