import pytest
from unittest.mock import patch, MagicMock

from wizflow.interactive_builder import InteractiveWorkflowBuilder

@pytest.fixture
def builder():
    """Fixture to create an InteractiveWorkflowBuilder instance."""
    with patch('wizflow.interactive_builder.PluginManager'):
        builder = InteractiveWorkflowBuilder()
        # Mock the plugins for predictable test results
        builder.plugin_manager.get_all_plugins.return_value = {
            'send_email': MagicMock(),
            'log_message': MagicMock()
        }
        return builder

@patch('builtins.input')
def test_build_full_workflow(mock_input, builder):
    """Test building a full workflow interactively."""
    # Mock the return values of plugin names
    plugin_names = ['send_email', 'log_message']
    builder.plugin_manager.get_all_plugins.return_value = {name: MagicMock(name=name) for name in plugin_names}

    # Mock a sequence of user inputs
    mock_input.side_effect = [
        "Test Workflow",  # name
        "A test description",  # description
        "2",  # trigger type (schedule)
        "0 0 * * *",  # schedule cron
        "1",  # action type (send_email)
        "test@example.com",  # email to
        "Test Subject",  # email subject
        "Test Body",  # email body
        "2",  # action type (log_message)
        "Workflow finished",  # log message
        "INFO", # log level
        "3",  # done adding actions
    ]

    workflow = builder.build()

    assert workflow['name'] == "Test Workflow"
    assert workflow['description'] == "A test description"
    assert workflow['trigger']['type'] == "schedule"
    assert workflow['trigger']['schedule'] == "0 0 * * *"
    assert len(workflow['actions']) == 2

    assert workflow['actions'][0]['type'] == "send_email"
    assert workflow['actions'][0]['config']['to'] == "test@example.com"

    assert workflow['actions'][1]['type'] == "log_message"
    assert workflow['actions'][1]['config']['message'] == "Workflow finished"

@patch('builtins.input')
def test_build_with_invalid_choices(mock_input, builder):
    """Test the builder's resilience to invalid user input."""
    # Mock the return values of plugin names
    plugin_names = ['send_email', 'log_message']
    builder.plugin_manager.get_all_plugins.return_value = {name: MagicMock(name=name) for name in plugin_names}

    mock_input.side_effect = [
        "Test Name",
        "Test Desc",
        "99",  # invalid trigger choice
        "1",  # action (send_email)
        "a@b.com", "subj", "body",
        "99", # invalid action choice
        "3", # done
    ]

    workflow = builder.build()

    # Should default to 'manual' trigger
    assert workflow['trigger']['type'] == "manual"
    assert len(workflow['actions']) == 1
