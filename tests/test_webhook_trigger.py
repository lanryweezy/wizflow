import pytest
import requests
import time
from threading import Thread
from unittest.mock import Mock

from wizflow.plugins.webhook_trigger import WebhookTriggerPlugin

@pytest.fixture
def trigger_plugin():
    """Fixture to create a WebhookTriggerPlugin instance and ensure it's stopped."""
    plugin = WebhookTriggerPlugin()
    yield plugin
    plugin.stop()

def test_webhook_trigger(trigger_plugin):
    """Test that the webhook trigger fires on an HTTP request."""

    on_trigger_mock = Mock()

    port = 8081 # Use a different port to avoid conflicts

    trigger_thread = Thread(
        target=trigger_plugin.start,
        args=({"port": port}, on_trigger_mock),
        daemon=True
    )
    trigger_thread.start()

    time.sleep(0.1) # Give the server time to start

    try:
        # Send a POST request to the webhook
        response = requests.post(f"http://localhost:{port}/", json={"test": "data"})
        assert response.status_code == 200
        assert response.text == "OK"

        time.sleep(0.1) # Give the trigger time to fire

        on_trigger_mock.assert_called_once()

        call_args = on_trigger_mock.call_args[0][0]
        assert call_args['data'] == {"test": "data"}
    finally:
        # Ensure the server is stopped even if the test fails
        trigger_plugin.stop()
        trigger_thread.join(timeout=1)
