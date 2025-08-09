import pytest
import json
from pathlib import Path

from wizflow.cli import WizFlowCLI

@pytest.fixture
def cli_with_templates(monkeypatch, tmp_path):
    """Fixture to create a WizFlowCLI instance with a mock templates directory."""
    # Create mock templates dir and manifest
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    manifest = {
        "templates": [
            {"name": "test-template", "description": "A test template."}
        ]
    }
    (templates_dir / "manifest.json").write_text(json.dumps(manifest))

    # Create a mock template file
    template_workflow = {
        "name": "Test Template Workflow",
        "actions": [{"type": "api_call", "config": {"url": "https://test.com"}}]
    }
    (templates_dir / "test-template.json").write_text(json.dumps(template_workflow))

    # Set cwd to the temp directory so 'templates' is found
    monkeypatch.setattr(Path, 'cwd', lambda: tmp_path)

    cli = WizFlowCLI()
    # Override the templates and workflows directories for the test
    cli.templates_dir = templates_dir
    cli.workflows_dir = tmp_path / "workflows"
    cli.workflows_dir.mkdir(exist_ok=True)

    return cli

def test_list_templates(cli_with_templates, capsys):
    """Test the 'wizflow --templates list' command."""
    cli_with_templates.manage_templates(['list'])

    captured = capsys.readouterr()
    output = captured.out

    assert "Available Templates:" in output
    assert "test-template: A test template." in output

def test_use_template_success(cli_with_templates, capsys):
    """Test successfully using a template."""
    cli_with_templates.manage_templates(['use', 'test-template'])

    captured = capsys.readouterr()
    output = captured.out

    assert "✅ Template 'test-template' created" in output

    # Check that the files were created
    workflow_json_path = cli_with_templates.workflows_dir / "test-template.json"
    workflow_py_path = cli_with_templates.workflows_dir / "test-template.py"

    assert workflow_json_path.exists()
    assert workflow_py_path.exists()

    # Check that the generated python script is valid
    with open(workflow_py_path, 'r') as f:
        source_code = f.read()
    compile(source_code, str(workflow_py_path), 'exec')

def test_use_template_not_found(cli_with_templates, capsys):
    """Test using a template that doesn't exist."""
    cli_with_templates.manage_templates(['use', 'non-existent-template'])

    captured = capsys.readouterr()
    output = captured.out

    assert "❌ Template 'non-existent-template' not found." in output
