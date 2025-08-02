import pytest
from unittest.mock import patch, MagicMock
import subprocess

from wizflow.cli import WizFlowCLI

@pytest.fixture
def cli_instance(monkeypatch, tmp_path):
    """Fixture to create a WizFlowCLI instance for testing."""
    monkeypatch.setattr('pathlib.Path.cwd', lambda: tmp_path)
    cli = WizFlowCLI()
    # Force the CLI to use the MockProvider for predictable output
    from wizflow.core.llm_interface import MockProvider
    monkeypatch.setattr(cli.llm, 'provider', MockProvider())
    return cli

def test_list_plugins(cli_instance, capsys):
    """Test the 'wizflow --plugins list' command."""
    cli_instance.manage_plugins(['list'])

    captured = capsys.readouterr()
    output = captured.out

    assert "Installed Plugins:" in output
    assert "send_email" in output
    assert "web_scrape" in output

@patch('subprocess.run')
def test_install_plugin_success(mock_subprocess_run, cli_instance, capsys):
    """Test successful installation of a new plugin."""
    mock_subprocess_run.return_value = MagicMock(
        check=lambda: None,
        stdout="",
        stderr=""
    )

    cli_instance.manage_plugins(['install', 'wizflow-plugin-youtube'])

    captured = capsys.readouterr()
    output = captured.out

    assert "Installing 'wizflow-plugin-youtube'" in output
    assert "✅ Plugin 'wizflow-plugin-youtube' installed successfully." in output

    # Check that git clone was called correctly
    mock_subprocess_run.assert_called_once()
    args, kwargs = mock_subprocess_run.call_args
    assert args[0][0] == "git"
    assert args[0][1] == "clone"
    assert "wizflow-plugin-youtube.git" in args[0][2]

@patch('subprocess.run')
def test_install_plugin_failure(mock_subprocess_run, cli_instance, capsys):
    """Test failed installation of a new plugin."""
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, "git", stderr="repository not found")

    cli_instance.manage_plugins(['install', 'wizflow-plugin-youtube'])

    captured = capsys.readouterr()
    output = captured.out

    assert "Failed to install plugin" in output
    assert "repository not found" in output

def test_install_plugin_not_found(cli_instance, capsys):
    """Test installing a plugin that doesn't exist in the repository."""
    cli_instance.manage_plugins(['install', 'non-existent-plugin'])

    captured = capsys.readouterr()
    output = captured.out

    assert "Plugin 'non-existent-plugin' not found in repository." in output
