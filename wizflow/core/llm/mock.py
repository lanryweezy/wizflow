"""
Mock LLM Provider for WizFlow
"""

from .base import LLMProvider


class MockProvider(LLMProvider):
    """Mock provider for testing without API keys"""

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate mock response"""
        # This mock response is taken from the original implementation
        return '''
        {
          "name": "Email to WhatsApp Alert",
          "description": "Forward email summaries to WhatsApp",
          "trigger": {
            "type": "email",
            "filter": "from:boss@example.com"
          },
          "actions": [
            {
              "type": "summarize",
              "tool": "gpt",
              "config": {
                "max_length": 100
              }
            },
            {
              "type": "send_whatsapp",
              "config": {
                "to": "+1234567890",
                "message": "Email Summary: {{summary}}"
              }
            }
          ]
        }
        '''
