import pytest
import time
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from threading import Thread

from wizflow.plugins.schedule_trigger import ScheduleTriggerPlugin

def test_schedule_trigger():
    """Test that the schedule trigger fires at the correct time."""

    on_trigger_mock = Mock()
    trigger_plugin = ScheduleTriggerPlugin()

    trigger_thread = Thread(
        target=trigger_plugin.start,
        args=({"schedule": "* * * * * *"}, on_trigger_mock),
        daemon=True
    )
    trigger_thread.start()

    # Give the trigger time to fire
    time.sleep(1.1)

    trigger_plugin.stop()
    trigger_thread.join(timeout=1)

    on_trigger_mock.assert_called()
