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
        """Generate mock response"""
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
      "tool": "library_or_service",
      "config": {
        "parameter": "value"
      }
    }
  ]
}

Available action types:
- summarize: Summarize text using AI
- send_email: Send email via SMTP
- send_whatsapp: Send WhatsApp message
- send_sms: Send SMS via Twilio
- read_email: Read emails via IMAP
- web_scrape: Scrape web content
- file_process: Process files
- api_call: Make HTTP API calls
- schedule_task: Schedule recurring tasks
- database_query: Query databases
- spreadsheet_update: Update Google Sheets/Excel

Tools/Libraries available:
- gpt: For AI text processing
- smtp: For sending emails
- imap: For reading emails
- requests: For HTTP requests
- twilio: For SMS/WhatsApp
- gspread: For Google Sheets
- sqlite3: For local database
- schedule: For task scheduling
- beautifulsoup: For web scraping

Return ONLY the JSON, no explanation or code blocks.
"""
    
    def generate_workflow(self, description: str) -> Dict[str, Any]:
        """Generate workflow JSON from natural language description"""
        prompt = f"""
Create a workflow for this task: "{description}"

Return only the JSON workflow structure.
"""
        
        response = self.provider.generate(prompt, self.system_prompt)
        
        # Extract JSON from response
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                return json.loads(response)
        except json.JSONDecodeError:
            # Fallback to a basic structure
            return {
                "name": "Generated Workflow",
                "description": description,
                "trigger": {"type": "manual"},
                "actions": [
                    {
                        "type": "api_call",
                        "tool": "requests",
                        "config": {
                            "url": "https://httpbin.org/get",
                            "method": "GET"
                        }
                    }
                ]
            }
