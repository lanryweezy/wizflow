"""
Configuration management for WizFlow
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Configuration manager for WizFlow"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".wizflow"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(exist_ok=True)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        # Check environment variables first
        env_key = f"WIZFLOW_{key.upper()}"
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value
        
        # Then check config file
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self._config[key] = value
        self._save_config()
    
    @property
    def openai_key(self) -> Optional[str]:
        """Get OpenAI API key"""
        return self.get('openai_key') or os.getenv('OPENAI_API_KEY')
    
    @property
    def anthropic_key(self) -> Optional[str]:
        """Get Anthropic API key"""
        return self.get('anthropic_key') or os.getenv('ANTHROPIC_API_KEY')
    
    @property
    def llm_provider(self) -> str:
        """Get preferred LLM provider"""
        return self.get('llm_provider', 'openai')
    
    @property
    def model_name(self) -> str:
        """Get model name for the selected provider"""
        provider = self.llm_provider
        if provider == 'openai':
            return self.get('openai_model', 'gpt-4')
        elif provider == 'anthropic':
            return self.get('anthropic_model', 'claude-3-sonnet-20240229')
        else:
            return 'gpt-4'
    
    def validate_setup(self) -> tuple[bool, str]:
        """Validate that required configuration is present"""
        provider = self.llm_provider
        
        if provider == 'openai' and not self.openai_key:
            return False, "OpenAI API key not configured. Set with: wizflow --config openai_key=your_key"
        elif provider == 'anthropic' and not self.anthropic_key:
            return False, "Anthropic API key not configured. Set with: wizflow --config anthropic_key=your_key"
        
        return True, "Configuration is valid"
