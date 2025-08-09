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

    def get_function_definition(self) -> str:
        return '''
def process_file(filepath, operation="read", content_to_write="", variables={}, creds={}):
    """Process file operations"""
    try:
        if operation == "read":
            with open(filepath, 'r') as f:
                content = f.read()
            logger.info(f"📄 Read file: {filepath}")
            if content:
                return {"file_content": content}
            return None
        elif operation == "write":
            with open(filepath, 'w') as f:
                f.write(content_to_write)
            logger.info(f"✍️  Wrote to file: {filepath}")
            return None
    except Exception as e:
        logger.error(f"❌ File operation failed: {e}")
        return None
'''

    def get_function_call(self, config: Dict[str, Any]) -> str:
        filepath = self._resolve_template(config.get('filepath', 'data.txt'))
        operation = self._resolve_template(config.get('operation', 'read'))
        content = self._resolve_template(config.get('content', ''))

        return f"process_file(filepath={filepath}, operation={operation}, content_to_write={content}, variables=variables, creds=credentials)"
