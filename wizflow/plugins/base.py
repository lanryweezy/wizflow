"""
Base class for all action plugins in WizFlow.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class LoopVariable:
    """A wrapper class to indicate a variable is from a loop."""
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name


class ActionPlugin(ABC):
    """
    Abstract base class for an action plugin.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the action, e.g., 'send_email'."""
        pass

    @property
    def required_params(self) -> List[str]:
        """
        A list of required parameters from the workflow config.
        This can be used for validation. By default, no parameters are required.
        """
        return []

    @property
    def required_imports(self) -> List[str]:
        """
        A list of imports required for this plugin's code to run.
        e.g., ["import smtplib", "from email.mime.text import MIMEText"]
        """
        return []

    output_variable_name: Optional[str] = None

    def get_function_definition(self) -> str:
        """
        Returns the full Python code for the function that implements this action.
        This code will be injected into the generated workflow script.
        e.g., "def send_email(to, subject, body, creds={}): ..."
        """
        pass

    @abstractmethod
    def get_function_call(self, config: Dict[str, Any]) -> str:
        """
        Returns the Python code for calling the action's function.
        This method will receive the 'config' dictionary for the action from the workflow JSON.
        e.g., "send_email(to='test@example.com', subject='Hello', body='World', creds=credentials)"
        """
        pass
