"""
Webhook Trigger Plugin for WizFlow
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, Any, Callable
import json

from .trigger_base import TriggerPlugin
from ..logger import get_logger

class WebhookTriggerPlugin(TriggerPlugin):
    """
    A trigger plugin that starts an HTTP server and listens for webhooks.
    """
    def __init__(self):
        self.logger = get_logger(__name__)
        self.server = None

    @property
    def name(self) -> str:
        return "webhook"

    def start(self, config: Dict[str, Any], on_trigger: Callable[[Dict[str, Any]], None]):
        """Starts the HTTP server."""
        host = config.get("host", "localhost")
        port = int(config.get("port", 8080))

        class WebhookHandler(BaseHTTPRequestHandler):
            def do_POST(s):
                path = config.get("path", "/")
                if s.path == path:
                    content_length = int(s.headers['Content-Length'])
                    post_data = s.rfile.read(content_length)

                    s.send_response(200)
                    s.end_headers()
                    s.wfile.write(b'OK')

                    try:
                        data = json.loads(post_data)
                    except json.JSONDecodeError:
                        data = {"raw": post_data.decode('utf-8')}

                    on_trigger({"data": data})
                else:
                    s.send_error(404, "Not Found")

        self.server = HTTPServer((host, port), WebhookHandler)
        self.logger.info(f"Starting webhook server on http://{host}:{port}")

        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.server.server_close()
            self.logger.info("Webhook server stopped.")

    def stop(self):
        if self.server:
            self.server.shutdown()
