import pytest
from unittest.mock import patch, MagicMock

# Adjust path to import from the root wizflow module
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from wizflow.core.llm import OllamaProvider

@patch('openai.OpenAI')
def test_ollama_provider_init(MockOpenAIClient):
    """Test that OllamaProvider initializes the OpenAI client correctly."""

    provider = OllamaProvider(model="test-model", base_url="http://test:1234/v1")

    MockOpenAIClient.assert_called_once_with(
        base_url="http://test:1234/v1",
        api_key="ollama"
    )
    assert provider.model == "test-model"

@patch('openai.OpenAI')
def test_ollama_provider_generate(MockOpenAIClient):
    """Test that OllamaProvider calls the generate method with the correct parameters."""

    # Mock the entire client and its response
    mock_client_instance = MockOpenAIClient.return_value
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Test response from Ollama"
    mock_client_instance.chat.completions.create.return_value = mock_response

    provider = OllamaProvider(model="test-model")
    response = provider.generate("Test prompt", system_prompt="Test system prompt")

    mock_client_instance.chat.completions.create.assert_called_once()

    # Check the arguments passed to the create method
    call_args, call_kwargs = mock_client_instance.chat.completions.create.call_args
    assert call_kwargs['model'] == 'test-model'
    assert call_kwargs['messages'] == [
        {"role": "system", "content": "Test system prompt"},
        {"role": "user", "content": "Test prompt"}
    ]

    assert response == "Test response from Ollama"
