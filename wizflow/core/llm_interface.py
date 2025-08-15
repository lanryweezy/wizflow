"""
LLM Interface for WizFlow - Handles communication with different AI providers
"""

import json
import re
from typing import Dict, Any

from .llm import (
    LLMProvider,
    OpenAIProvider,
    AnthropicProvider,
    MockProvider,
    OllamaProvider,
)


class LLMInterface:
    """Main interface for LLM operations"""
    
    def __init__(self, config):
        self.config = config
        self.provider = self._create_provider()
        self.system_prompt = self._get_system_prompt()
    
    def _create_provider(self) -> LLMProvider:
        """Create appropriate LLM provider based on configuration"""
        provider_name = self.config.llm_provider
        
        if provider_name == 'openai':
            api_key = self.config.openai_key
            if not api_key:
                print("⚠️  No OpenAI API key found, using mock provider")
                return MockProvider()
            return OpenAIProvider(api_key, self.config.model_name)
        
        elif provider_name == 'anthropic':
            api_key = self.config.anthropic_key
            if not api_key:
                print("⚠️  No Anthropic API key found, using mock provider")
                return MockProvider()
            return AnthropicProvider(api_key, self.config.model_name)

        elif provider_name == 'ollama':
            print("✅ Using Ollama provider.")
            model = getattr(self.config, 'ollama_model', 'llama3')
            base_url = getattr(self.config, 'ollama_base_url', 'http://localhost:11434/v1')
            return OllamaProvider(model=model, base_url=base_url)
        
        else:
            print(f"⚠️  Unknown provider '{provider_name}', using mock provider")
            return MockProvider()
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for workflow generation"""
        # This prompt is a simplified version for now
        return """
You are a Python automation expert. Your job is to take natural language task descriptions and
output ONLY a structured JSON describing the workflow.

JSON Schema:
{
  "name": "Short descriptive name",
  "description": "Brief description of what this workflow does",
  "trigger": { "type": "manual" },
  "actions": [ { "type": "action_type", "config": { "parameter": "value" } } ]
}

Available action types: summarize, send_email, send_whatsapp, log_message, api_call, web_scrape, file_process
"""
    
    def generate_workflow(self, description: str) -> Dict[str, Any]:
        """Generate workflow JSON from natural language description"""
        prompt = f"""
Create a workflow for this task: "{description}"

Return only the JSON workflow structure.
"""
        
        response = self.provider.generate(prompt, self.system_prompt)
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                return json.loads(response)
        except json.JSONDecodeError:
            return {
                "name": "Generated Workflow (fallback)",
                "description": description,
                "trigger": {"type": "manual"},
                "actions": []
            }
