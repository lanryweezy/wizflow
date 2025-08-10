import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

from wizflow.cli import main

@patch('wizflow.cli.WizFlowCLI')
def test_main_generate(MockWizFlowCLI, capsys):
    """Test the 'generate' command."""
    mock_cli_instance = MockWizFlowCLI.return_value
    mock_cli_instance.generate_workflow.return_value = ('/path/to/workflow.json', '/path/to/workflow.py')

    with patch('builtins.input', return_value='n'):
        sys.argv = ['wizflow', 'generate', 'test description', '--name', 'test_workflow']
        main()

    mock_cli_instance.generate_workflow.assert_called_once_with('test description', 'test_workflow')
    mock_cli_instance.run_workflow.assert_not_called()

@patch('wizflow.cli.getpass.getpass')
@patch('wizflow.cli.WizFlowCLI')
def test_main_credentials_add(MockWizFlowCLI, mock_getpass, capsys):
    """Test the 'credentials add' command."""
    mock_cli_instance = MockWizFlowCLI.return_value
    mock_getpass.return_value = "test_password"

    sys.argv = ['wizflow', 'credentials', 'add', 'test_service', 'test_user']
    main()

    mock_cli_instance.credentials.save_credential.assert_called_once_with('test_service', 'test_user', 'test_password')

@patch('wizflow.cli.WizFlowCLI')
def test_main_credentials_get(MockWizFlowCLI, capsys):
    """Test the 'credentials get' command."""
    mock_cli_instance = MockWizFlowCLI.return_value
    mock_cli_instance.credentials.get_credential.return_value = "some_password"

    sys.argv = ['wizflow', 'credentials', 'get', 'test_service', 'test_user']
    main()

    mock_cli_instance.credentials.get_credential.assert_called_once_with('test_service', 'test_user')
    captured = capsys.readouterr()
    assert "Value exists (hidden for security)." in captured.out

@patch('builtins.input', return_value='y')
@patch('wizflow.cli.WizFlowCLI')
def test_main_credentials_delete(MockWizFlowCLI, mock_input, capsys):
    """Test the 'credentials delete' command."""
    mock_cli_instance = MockWizFlowCLI.return_value

    sys.argv = ['wizflow', 'credentials', 'delete', 'test_service', 'test_user']
    main()

    mock_cli_instance.credentials.delete_credential.assert_called_once_with('test_service', 'test_user')

def test_main_no_command(capsys):
    """Test running with no command."""
    with pytest.raises(SystemExit) as e:
        sys.argv = ['wizflow']
        main()

    assert e.value.code != 0
    captured = capsys.readouterr()
    assert 'usage: wizflow' in captured.err
    assert 'the following arguments are required: command' in captured.err
