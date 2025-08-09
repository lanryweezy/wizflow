import pytest
import os
import time
from pathlib import Path
from threading import Thread
from unittest.mock import Mock

from wizflow.plugins.file_trigger import FileTriggerPlugin

@pytest.fixture
def trigger_plugin():
    """Fixture to create a FileTriggerPlugin instance and ensure it's stopped."""
    plugin = FileTriggerPlugin()
    yield plugin
    plugin.stop()

def test_file_trigger(trigger_plugin, tmp_path):
    """Test that the file trigger fires on file creation."""

    # Create a mock callback function
    on_trigger_mock = Mock()

    # Start the file trigger
    trigger_plugin.start(
        config={"path": str(tmp_path)},
        on_trigger=on_trigger_mock
    )

    # Give the observer some time to start
    time.sleep(0.1)

    # Create a new file in the directory
    new_file = tmp_path / "test_file.txt"
    new_file.write_text("hello")

    # Give the trigger time to fire
    time.sleep(0.1)

    # Check that the on_trigger callback was called
    on_trigger_mock.assert_called_once()

    # Check the arguments passed to the callback
    call_args = on_trigger_mock.call_args[0][0]
    assert call_args['event_type'] == 'created'
    assert Path(call_args['src_path']) == new_file
