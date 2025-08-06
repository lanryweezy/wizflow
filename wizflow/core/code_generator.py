"""
Code Generator - Converts workflow JSON to executable Python code using a plugin architecture
"""

import json
from typing import Dict, Any, List, Set

from .plugin_manager import PluginManager
from wizflow.plugins.base import ActionPlugin, LoopVariable


class CodeGenerator:
    """Generates Python code from workflow JSON using a plugin architecture"""

    def __init__(self):
        print("Initializing PluginManager to load plugins...")
        self.plugin_manager = PluginManager()

    def generate_code(self, workflow: Dict[str, Any]) -> str:
        """Generate Python code from workflow JSON"""
        print("🔄 Generating Python code using plugin architecture...")

        required_plugins = self._get_required_plugins(workflow)
        
        # Get a set of all modules that need to be allowed for import
        allowed_modules = self._get_allowed_modules(required_plugins)

        code = self._get_base_template(allowed_modules)
        code += self._generate_metadata_section(workflow)
        code += self._generate_imports(required_plugins)
        code += self._generate_action_definitions(required_plugins)
        code += self._generate_main_function(workflow, required_plugins)
        code += self._generate_main_execution()

        return code

    def _get_required_plugins(self, workflow: Dict[str, Any]) -> Set[ActionPlugin]:
        """Get the set of unique plugins required for this workflow."""
        plugins = set()
        for action in workflow.get('actions', []):
            action_type = action.get('type')
            plugin = self.plugin_manager.get_plugin(action_type)
            if plugin:
                plugins.add(plugin)
            else:
                print(f"⚠️  Warning: No plugin found for action type '{action_type}'. It will be skipped.")
        return plugins

    def _get_allowed_modules(self, plugins: Set[ActionPlugin]) -> Set[str]:
        """
        Gathers a set of all module names that should be whitelisted for import.
        """
        # Start with a set of always-allowed, basic modules
        allowed = {'json', 'sys', 'datetime', 'typing', 'os'}
        
        for plugin in plugins:
            for imp in plugin.required_imports:
                # e.g., "from wizflow.core.config import Config" -> "wizflow.core.config"
                # e.g., "import requests" -> "requests"
                parts = imp.split()
                if parts[0] == 'import':
                    allowed.add(parts[1])
                elif parts[0] == 'from':
                    allowed.add(parts[1])
        
        # Add the core credential and config modules, as they are used by the template
        allowed.add('wizflow.core.credentials')
        allowed.add('wizflow.core.config')
        allowed.add('wizflow.core.llm_interface')
        
        return allowed

    def _get_base_template(self, allowed_modules: Set[str]) -> str:
        """Get base Python template"""
        
        allowed_modules_str = json.dumps(list(allowed_modules))
        
        return f'''#!/usr/bin/env python3
"""
Auto-generated workflow by WizFlow
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Assuming wizflow is installed or in python path
try:
    from wizflow.core.credentials import CredentialManager
except ImportError:
    # Fallback for running script standalone
    class CredentialManager:
        def load_credentials(self):
            print("Warning: Standalone script, credentials will be empty.")
            return {{}}

# --- Security Sandbox: Restrict Imports ---
import json
_original_import = __import__
def _secure_import(name, globals=None, locals=None, fromlist=(), level=0):
    ALLOWED_MODULES = set(json.loads('{allowed_modules_str}'))
    
    # Allow relative imports
    if name.startswith('wizflow.') and level > 0:
        pass
    # Also allow any sub-modules of an allowed module
    elif '.'.join(name.split('.')[:-1]) in ALLOWED_MODULES:
        pass
    elif name not in ALLOWED_MODULES:
        # Check for submodules
        parts = name.split('.')
        if parts[0] not in ALLOWED_MODULES:
                raise ImportError(f"Disallowed import: '{{name}}'")

    return _original_import(name, globals, locals, fromlist, level)

# Overriding the import function to enable the sandbox.
__builtins__['__import__'] = _secure_import
# --- End Security Sandbox ---

'''

    def _generate_metadata_section(self, workflow: Dict[str, Any]) -> str:
        """Generate metadata section"""
        metadata = json.dumps(workflow.get('metadata', {}), indent=4)
        return f'''
# Workflow Metadata
WORKFLOW_INFO = {metadata}
'''

    def _generate_imports(self, plugins: Set[ActionPlugin]) -> str:
        """Generate necessary imports based on required plugins."""
        imports = set()
        for plugin in plugins:
            imports.update(plugin.required_imports)

        if not imports:
            return ""
        
        return '\n# Additional imports\n' + '\n'.join(sorted(list(imports))) + '\n'

    def _generate_action_definitions(self, plugins: Set[ActionPlugin]) -> str:
        """Generate the Python function definitions for all required actions."""
        code = "\n# --- Action Function Definitions ---\n"
        for plugin in plugins:
            code += plugin.get_function_definition()
            code += "\n"
        code += "# --- End Action Function Definitions ---\n"
        return code

    def _generate_main_function(self, workflow: Dict[str, Any], plugins: Set[ActionPlugin]) -> str:
        """Generate the main run_workflow() function."""
        name = workflow.get('name', 'Generated Workflow')
        description = workflow.get('description', 'Auto-generated workflow')

        main_func_header = f'''
def run_workflow():
    """
    Main workflow function: {name}
    Description: {description}
    """
    print("🚀 Starting workflow: {name}")
    print("📋 Description: {description}")

    # Initialize variables for data passing between actions
    variables = {{}}

    # Load credentials
    try:
        cred_manager = CredentialManager()
        credentials = cred_manager.load_credentials()
        print("🔒 Credentials loaded.")
    except Exception as e:
        print(f"❌ Error loading credentials: {{e}}")
        credentials = {{}}

    try:
'''
        action_calls_code = self._generate_action_calls(workflow)

        main_func_footer = '''
        print("✅ Workflow completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        return False
'''
        return main_func_header + action_calls_code + main_func_footer

    def _generate_action_calls(self, workflow: Dict[str, Any]) -> str:
        """Generate the sequence of action calls inside the main function."""
        code = ""
        for i, action in enumerate(workflow.get('actions', []), 1):
            action_type = action.get('type', 'unknown')
            condition = action.get('condition')
            loop = action.get('loop')
            config = action.get('config', {})

            print(f"DEBUG: Action {i}: type={action_type}, condition={condition}, loop={loop}")

            code += f"\n        # Action {i}: {action_type}\n"

            plugin = self.plugin_manager.get_plugin(action_type)
            if not plugin:
                code += f"        print(\"🤷‍♂️ Action '{action_type}' skipped (no plugin found).\")\n"
                continue

            # Determine the call string
            call_str = plugin.get_function_call(config)
            if plugin.output_variable_name:
                call_str = f"variables['{plugin.output_variable_name}'] = {call_str}"
            print(f"DEBUG: call_str = {call_str}")

            # Handle loops and conditions
            if loop:
                loop_var, list_var = self._parse_loop_string(loop)
                print(f"DEBUG: loop_var={loop_var}, list_var={list_var}")
                # We need to re-generate the call string for inside the loop
                looped_config = self._substitute_loop_variable(config, loop_var)
                call_in_loop = plugin.get_function_call(looped_config)
                if plugin.output_variable_name:
                    call_in_loop = f"variables['{plugin.output_variable_name}'] = {call_in_loop}"
                print(f"DEBUG: call_in_loop = {call_in_loop}")

                code += f"        for {loop_var} in {list_var}:\n"
                if condition:
                    cond_str = self._format_condition_string(condition, loop_var=loop_var)
                    print(f"DEBUG: cond_str (in loop) = {cond_str}")
                    code += f"            if {cond_str}:\n"
                    code += f"                {call_in_loop}\n"
                else:
                    code += f"            {call_in_loop}\n"
            elif condition:
                cond_str = self._format_condition_string(condition)
                print(f"DEBUG: cond_str = {cond_str}")
                code += f"        if {cond_str}:\n"
                code += f"            {call_str}\n"
            else:
                code += f"        {call_str}\n"

        print(f"DEBUG: final generated code for actions:\n{code}")
        return code

    def _format_condition_string(self, condition: str, loop_var: str = None) -> str:
        """
        Formats a condition string, replacing {{var}} placeholders.
        e.g., "{{api_result.price}} > 200" -> "variables.get('api_result', {}).get('price', 0) > 200"
        """
        import re

        def replacer(match):
            parts = match.group(1).strip().split('.')
            if len(parts) == 1:
                return f"variables.get('{parts[0]}')"
            else:
                # e.g., api_result.price -> .get('price', 0)
                getters = [f".get('{part}')" for part in parts[1:]]
                return f"variables.get('{parts[0]}', {{}}){''.join(getters)}"

        # A more robust regex to handle nested properties
        if loop_var:
            # Special handling for the loop variable, which is not in the 'variables' dict
            condition = condition.replace(f'{{{{{loop_var}}}}}', loop_var)

        return re.sub(r'\{\{\s*([\w\.]+)\s*\}\}', replacer, condition)

    def _parse_loop_string(self, loop_str: str) -> tuple[str, str]:
        """
        Parses a loop string like 'item in my_list' into ('item', 'variables.get("my_list", [])').
        """
        parts = loop_str.split(' in ')
        loop_var = parts[0].strip()
        list_name = parts[1].strip()

        # Format the list variable to access it from the 'variables' dict
        list_var_str = f"variables.get('{list_name}', [])"
        return loop_var, list_var_str

    def _substitute_loop_variable(self, config: dict, loop_var: str) -> dict:
        """
        Substitutes the loop variable placeholder in a config dictionary.
        e.g., {'text': '{{item}}'} -> {'text': LoopVariable('item')}
        """
        new_config = {}
        for key, value in config.items():
            if isinstance(value, str) and f'{{{{{loop_var}}}}}' in value:
                # This is a simplification; it assumes the whole string is the variable
                new_config[key] = LoopVariable(loop_var)
            else:
                new_config[key] = value
        return new_config

    def _generate_main_execution(self) -> str:
        """Generate main execution block"""
        return '''
if __name__ == "__main__":
    success = run_workflow()
    sys.exit(0 if success else 1)
'''
