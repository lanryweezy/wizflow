"""
File Process Action Plugin for WizFlow
"""

from typing import Dict, Any, List
from .base import ActionPlugin


class FileProcessPlugin(ActionPlugin):
    """
    An action plugin to read from or write to files.
    """

    @property
    def name(self) -> str:
        return "file_process"

    output_variable_name = "file_content"

    def get_function_definition(self) -> str:
        return '''
def process_file(filepath, operation="read", content_to_write=""):
    """Process file operations"""
    try:
        if operation == "read":
            with open(filepath, 'r') as f:
                content = f.read()
            print(f"📄 Read file: {filepath}")
            return content
        elif operation == "write":
            with open(filepath, 'w') as f:
                f.write(content_to_write)
            print(f"✍️  Wrote to file: {filepath}")
            return True
    except Exception as e:
        print(f"❌ File operation failed: {e}")
        return None
'''

    def get_function_call(self, config: Dict[str, Any]) -> str:
        filepath = repr(config.get('filepath', 'data.txt'))
        operation = repr(config.get('operation', 'read'))
        content = repr(config.get('content', ''))

        call_str = f"process_file(filepath={filepath}, operation={operation}, content_to_write={content})"

        if self.output_variable_name and operation == "'read'":
            return f"variables['{self.output_variable_name}'] = {call_str}"
        return call_str
