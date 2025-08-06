"""
Log Message Action Plugin for WizFlow
"""

from typing import Dict, Any, List
from .base import ActionPlugin


class LogMessagePlugin(ActionPlugin):
    """
    An action plugin to log a message to the console.
    """

    @property
    def name(self) -> str:
        return "log_message"

    def get_function_definition(self) -> str:
        return '''
def log_message(message, level="INFO"):
    """Logs a message to the console."""
    print(f"[{level}] {message}")
'''

    def get_function_call(self, config: Dict[str, Any]) -> str:
        message = repr(config.get('message', 'No message provided.'))
        level = repr(config.get('level', 'INFO'))
        return f"log_message(message={message}, level={level})"
