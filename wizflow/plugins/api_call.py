"""
API Call Action Plugin for WizFlow
"""

from typing import Dict, Any, List
from .base import ActionPlugin


class ApiCallPlugin(ActionPlugin):
    """
    An action plugin to make HTTP API calls.
    """

    @property
    def name(self) -> str:
        return "api_call"

    output_variable_name = "api_result"

    @property
    def required_imports(self) -> List[str]:
        return ["import requests"]

    def get_function_definition(self) -> str:
        return '''
def make_api_call(url, method="GET", headers=None, data=None):
    """Make HTTP API call"""
    try:
        response = requests.request(method, url, headers=headers, json=data)
        response.raise_for_status()
        print(f"🌐 API call to {url} successful")
        return response.json() if response.content else None
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return None
'''

    def get_function_call(self, config: Dict[str, Any]) -> str:
        url = repr(config.get('url', 'https://api.example.com'))
        method = repr(config.get('method', 'GET'))
        headers = config.get('headers')
        data = config.get('data')

        call_parts = [f"url={url}", f"method={method}"]
        if headers:
            call_parts.append(f"headers={headers}")
        if data:
            call_parts.append(f"data={data}")

        return f"make_api_call({', '.join(call_parts)})"
