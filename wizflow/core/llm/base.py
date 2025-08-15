"""
Base class for all LLM Providers in WizFlow.
"""
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate response from LLM"""
        pass
