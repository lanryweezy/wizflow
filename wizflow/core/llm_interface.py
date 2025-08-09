"""
LLM Interface for WizFlow - Handles communication with different AI providers
"""

import json
import re
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate response from LLM"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")
    
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate response using OpenAI"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1
        )
        return response.choices[0].message.content


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


class MockProvider(LLMProvider):
    """Mock provider for testing without API keys"""
    
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate mock response, checking for conditional keywords."""
        prompt_lower = prompt.lower()
        if 'if' in prompt_lower and 'stock' in prompt_lower:
            return '''
            {
              "name": "Conditional Stock Alert",
              "description": "If stock price is above a threshold, send an email.",
              "trigger": { "type": "manual" },
              "actions": [
                {
                  "type": "api_call",
                  "config": { "url": "https://api.example.com/stock/AAPL" }
                },
                {
                  "type": "send_email",
                  "condition": "variables.get('api_result', {}).get('price', 0) > 200",
                  "config": {
                    "to": "user@example.com",
                    "subject": "Stock Alert: AAPL",
                    "message": "AAPL stock price is over $200!"
                  }
                }
              ]
            }
            '''
        elif 'for each' in prompt_lower and 'article' in prompt_lower:
            return '''
            {
              "name": "Summarize Scraped Articles",
        elif 'api call' in prompt_lower and 'email' in prompt_lower:
            return '''
            {
              "name": "API to Email",
              "description": "Call an API and email the result.",
              "trigger": { "type": "manual" },
              "actions": [
                {
                  "type": "api_call",
                  "config": { "url": "https://api.example.com/data" }
                },
                {
                  "type": "send_email",
                  "config": {
                    "to": "user@example.com",
                    "subject": "API Data",
                    "message": "The data is: {{api_result}}"
                  }
                }
              ]
            }
            '''
              "description": "For each article scraped, summarize its content.",
              "trigger": { "type": "manual" },
              "actions": [
                {
                  "type": "web_scrape",
                  "config": { "url": "https://example.com/articles" }
                },
                {
                  "type": "summarize",
                  "loop": "article in scraped_content",
                  "config": {
                    "input_text": "{{article}}"
                  }
                }
              ]
            }
            '''
        else:
            return '''
            {
              "name": "Email to WhatsApp Alert",
              "description": "Forward email summaries to WhatsApp",
              "trigger": { "type": "email", "filter": "from:boss@example.com" },
              "actions": [
                {
                  "type": "summarize",
                  "config": { "max_length": 100 }
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


from .plugin_manager import PluginManager

class LLMInterface:
    """Main interface for LLM operations"""
    
    def __init__(self, config, plugin_manager: PluginManager):
        self.config = config
        self.plugin_manager = plugin_manager
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
        
        else:
            print(f"⚠️  Unknown provider '{provider_name}', using mock provider")
            return MockProvider()
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for workflow generation"""
        return """
You are a Python automation expert. Your job is to take natural language task descriptions and:
1. Output ONLY a structured JSON describing the workflow
2. The JSON should be ready to convert into Python code

JSON Schema:
{
  "name": "Short descriptive name",
  "description": "Brief description of what this workflow does",
  "trigger": {
    "type": "email|schedule|file|webhook|manual",
    "filter": "Optional filter criteria",
    "schedule": "Optional cron expression for scheduled tasks"
  },
  "actions": [
    {
      "type": "action_type",
    "condition": "Optional: A Python expression string that must evaluate to True for the action to run. e.g. 'variables.get(\"price\", 0) > 100'",
    "loop": "Optional: A Python 'for' loop expression over a list in 'variables'. e.g., 'item in scraped_content'",
      "tool": "library_or_service",
      "config": {
        "parameter": "value"
      }
    }
  ]
}

You can use the output of one action as the input for another.
For example, the `api_call` action saves its result to a variable named `api_result`.
You can use this in a subsequent action's config, like `message: 'The result is {{api_result.some_key}}'`.

Available actions and their outputs:
{action_list}

Return ONLY the JSON, no explanation or code blocks.
"""
        action_list_parts = []
        all_plugins = self.plugin_manager.get_all_plugins()
        for name, plugin in all_plugins.items():
            part = f"- `{name}`"
            if plugin.output_variable_name:
                part += f" (saves output to `{plugin.output_variable_name}`)"
            action_list_parts.append(part)

        action_list = "\n".join(action_list_parts)
        base_prompt = """
You are a Python automation expert. Your job is to take natural language task descriptions and:
1. Output ONLY a structured JSON describing the workflow
2. The JSON should be ready to convert into Python code

JSON Schema:
{
  "name": "Short descriptive name",
  "description": "Brief description of what this workflow does",
  "trigger": {
    "type": "email|schedule|file|webhook|manual",
    "filter": "Optional filter criteria",
    "schedule": "Optional cron expression for scheduled tasks"
  },
  "actions": [
    {
      "type": "action_type",
    "condition": "Optional: A Python expression string that must evaluate to True for the action to run. e.g. 'variables.get(\"price\", 0) > 100'",
    "loop": "Optional: A Python 'for' loop expression over a list in 'variables'. e.g., 'item in scraped_content'",
      "tool": "library_or_service",
      "config": {
        "parameter": "value"
      }
    }
  ]
}

You can use the output of one action as the input for another.
For example, the `api_call` action saves its result to a variable named `api_result`.
You can use this in a subsequent action's config, like `message: 'The result is {{api_result.some_key}}'`.

Available actions and their outputs:
{action_list}

Return ONLY the JSON, no explanation or code blocks.
"""
        return base_prompt.format(action_list=action_list)
    
    def generate_workflow(self, description: str) -> Dict[str, Any]:
        """Generate workflow JSON from natural language, with retries."""
        prompt = f"""
Create a workflow for this task: "{description}"

Return only the JSON workflow structure.
"""
        last_error = None
        for attempt in range(2): # Try up to 2 times
            if last_error:
                print(f"🔄 Retrying LLM generation (Attempt {attempt + 1})...")
                prompt = f"""
The previous attempt failed. Please fix the JSON output.
Error: {last_error}
Original Task: "{description}"
Return only the corrected JSON workflow structure.
"""

            response = self.provider.generate(prompt, self.system_prompt)

            try:
                # Extract JSON from response
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                    else:
                        json_str = response # Try to parse the whole thing

                return json.loads(json_str)

            except json.JSONDecodeError as e:
                last_error = f"JSONDecodeError: {e}"
                continue

        # If all attempts fail, return a fallback structure
        print("❌ LLM generation failed after multiple attempts.")
        return {
            "name": "Fallback Workflow",
            "description": f"Could not generate workflow for: {description}",
            "trigger": {"type": "manual"},
            "actions": [{"type": "api_call", "config": {"url": "https://httpbin.org/get"}}]
        }
