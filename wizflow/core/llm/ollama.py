"""
Ollama Provider for WizFlow
"""

from .base import LLMProvider


class OllamaProvider(LLMProvider):
    """
    Provider for a local Ollama instance.
    Uses the openai library to connect to the OpenAI-compatible API endpoint.
    """

    def __init__(self, model: str, base_url: str = "http://localhost:11434/v1"):
        self.model = model
        self.base_url = base_url
        try:
            import openai
            self.client = openai.OpenAI(
                base_url=self.base_url,
                api_key="ollama"  # Required for the library, but not used by Ollama
            )
        except ImportError:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate response using a local Ollama model."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Error connecting to Ollama at {self.base_url}. Is Ollama running?")
            print(f"   Error details: {e}")
            # Return a fallback JSON to avoid crashing the whole process
            return '{"name": "Ollama Connection Error", "description": "Could not connect to the local Ollama server.", "trigger": {"type": "manual"}, "actions": []}'
