"""
Base class for all action plugins in WizFlow.
"""

import re
from abc import ABC, abstractmethod
from typing import List, Dict, Any


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

    @abstractmethod
    def get_function_definition(self) -> str:
        """
        Returns the full Python code for the function that implements this action.
        The function should accept `variables` and `creds` dictionaries.
        e.g., "def send_email(to, subject, body, variables={}, creds={}): ..."
        """
        pass

    @abstractmethod
    def get_function_call(self, config: Dict[str, Any]) -> str:
        """
        Returns the Python code for calling the action's function.
        This method will receive the 'config' dictionary for the action from the workflow JSON.
        It should resolve any template strings in the config values.
        e.g., "send_email(to='test@example.com', subject='Hello', body=variables.get('summary'))"
        """
        pass

    def _resolve_template(self, value: Any, variables_dict_name: str = "variables") -> str:
        """
        Resolves a template string like '{{variable_name}}' into a Python expression.
        Handles both full and partial template strings.
        e.g. '{{foo}}' -> "variables.get('foo')"
        e.g. 'Status: {{foo}}' -> "f'Status: {variables.get(\"foo\")}'"
        """
        if not isinstance(value, str):
            return repr(value)

        pattern = re.compile(r"\{\{(.*?)\}\}")

        # Check for full match first, which is simpler and doesn't need an f-string
        full_match = pattern.fullmatch(value.strip())
        if full_match:
            var_name = full_match.group(1).strip()
            return f"{variables_dict_name}.get('{var_name}')"

        # For partial matches, construct an f-string expression
        if pattern.search(value):
            def replacer(match):
                var_name = match.group(1).strip()
                # Use a default value to avoid None in the f-string
                return f"{{{variables_dict_name}.get('{var_name}', '')}}"

            f_string_content = pattern.sub(replacer, value)
            return f'f"{f_string_content}"'

        # If no templates, just return the repr of the string
        return repr(value)
