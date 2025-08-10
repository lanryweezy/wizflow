import pytest
from wizflow.cli import WizFlowCLI

@pytest.fixture
def cli_instance(monkeypatch, tmp_path):
    """Fixture to create a WizFlowCLI instance for testing."""
    monkeypatch.setattr('pathlib.Path.cwd', lambda: tmp_path)
    cli = WizFlowCLI()
    cli.workflows_dir = tmp_path / "workflows"
    cli.workflows_dir.mkdir(exist_ok=True)
    return cli

def test_code_generation_with_retry(cli_instance):
    """
    Test that code is generated with a retry loop when on_error.retry is specified.
    """
    workflow_json = {
        "name": "Retry Test Workflow",
        "trigger": {"type": "manual"},
        "actions": [
            {
                "type": "log_message",
                "config": {"message": "Trying something..."},
                "on_error": {
                    "retry": {
                        "count": 5,
                        "delay_seconds": 10
                    }
                }
            }
        ]
    }

    code = cli_instance.generator.generate_code(workflow_json)

    assert "import time" in code
    assert "for attempt in range(5):" in code
    assert "try:" in code
    assert "except Exception as e:" in code
    assert "time.sleep(10)" in code
    assert "raise RuntimeError(f\"Action 'log_message' failed permanently.\")" in code

def test_code_generation_without_retry(cli_instance):
    """
    Test that code is generated without a retry loop for a standard action.
    """
    workflow_json = {
        "name": "No Retry Test Workflow",
        "trigger": {"type": "manual"},
        "actions": [
            {
                "type": "log_message",
                "config": {"message": "Just a simple message."}
            }
        ]
    }

    code = cli_instance.generator.generate_code(workflow_json)

    assert "for attempt in range" not in code
    assert "time.sleep" not in code
    assert "raise RuntimeError" not in code
