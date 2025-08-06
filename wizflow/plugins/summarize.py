"""
Summarize Text Action Plugin for WizFlow
"""

from typing import Dict, Any, List
from .base import ActionPlugin, LoopVariable


class SummarizePlugin(ActionPlugin):
    """
    An action plugin to summarize text.
    """

    @property
    def name(self) -> str:
        return "summarize"

    output_variable_name = "summary"

    @property
    def required_imports(self) -> List[str]:
        return [
            "from wizflow.core.config import Config",
            "from wizflow.core.llm_interface import LLMInterface",
        ]

    def get_function_definition(self) -> str:
        return '''
def summarize_text(text, max_length=100):
    """
    Summarize text using the configured LLM provider.
    """
    print("🧠 Performing AI summarization...")
    try:
        # Initialize LLM interface within the function
        config = Config()
        llm = LLMInterface(config)

        system_prompt = f"Summarize the following text in under {max_length} words."
        prompt = text

        summary = llm.provider.generate(prompt, system_prompt)

        print(f"📝 Summary: {summary}")
        return summary
    except Exception as e:
        print(f"❌ AI summarization failed: {e}")
        return None
'''

    def get_function_call(self, config: Dict[str, Any]) -> str:
        input_text_val = config.get('input_text', 'Sample text to summarize.')

        if isinstance(input_text_val, LoopVariable):
            input_text = str(input_text_val)
        else:
            input_text = repr(input_text_val)

        max_length = config.get('max_length', 100)

        return f"summarize_text(text={input_text}, max_length={max_length})"
