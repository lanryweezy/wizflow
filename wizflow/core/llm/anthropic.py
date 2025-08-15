"""
Anthropic Provider for WizFlow
"""

from .base import LLMProvider


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""

    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key
        self.model = model
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("Anthropic library not installed. Install with: pip install anthropic")

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate response using Anthropic"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            system=system_prompt if system_prompt else "You are a helpful assistant.",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
