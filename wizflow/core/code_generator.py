"""
Code Generator - Converts workflow JSON to executable Python code using a plugin architecture
"""

import json
from typing import Dict, Any, List, Set

from .plugin_manager import PluginManager
from wizflow.plugins.base import ActionPlugin
from ..logger import get_logger


class CodeGenerator:
    """Generates Python code from workflow JSON using a plugin architecture"""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.logger.debug("Initializing PluginManager to load plugins...")
        self.plugin_manager = PluginManager()

    def generate_code(self, workflow: Dict[str, Any]) -> str:
        """Generate Python code from workflow JSON"""
        self.logger.debug("🔄 Generating Python code using plugin architecture...")

        required_plugins = self._get_required_plugins(workflow)
        
        # Get a set of all modules that need to be allowed for import
        allowed_modules = self._get_allowed_modules(required_plugins)

        code = self._get_base_template(allowed_modules)
        code += self._generate_metadata_section(workflow)
        code += self._generate_imports(workflow, required_plugins)
        code += self._generate_action_definitions(required_plugins)
        code += self._generate_main_function(workflow, required_plugins)
        code += self._generate_main_execution(workflow)

        return code

    def _get_required_plugins(self, workflow: Dict[str, Any]) -> Set[ActionPlugin]:
        """Get the set of unique plugins required for this workflow."""
        plugins = set()
        for action in workflow.get('actions', []):
            action_type = action.get('type')
            plugin = self.plugin_manager.get_action_plugin(action_type)
            if plugin:
                plugins.add(plugin)
            else:
                self.logger.warning(f"⚠️  Warning: No plugin found for action type '{action_type}'. It will be skipped.")
        return plugins

    def _get_allowed_modules(self, plugins: Set[ActionPlugin]) -> Set[str]:
        """
        Gathers a set of all module names that should be whitelisted for import.
        """
        # Start with a set of always-allowed, basic modules
        allowed = {'json', 'sys', 'datetime', 'typing', 'os', 'logging'}
        
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
import logging
from datetime import datetime
from typing import Dict, Any

# --- Logger Setup ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(message)s'))
if not logger.handlers:
    logger.addHandler(handler)
# --- End Logger Setup ---

# Assuming wizflow is installed or in python path
try:
    from wizflow.core.credentials import CredentialManager
except ImportError:
    # Fallback for running script standalone
    class CredentialManager:
        def load_credentials(self):
            logger.warning("Warning: Standalone script, credentials will be empty.")
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

    def _generate_imports(self, workflow: Dict[str, Any], plugins: Set[ActionPlugin]) -> str:
        """Generate necessary imports based on required plugins."""
        imports = set()
        for plugin in plugins:
            imports.update(plugin.required_imports)

        trigger_type = workflow.get("trigger", {}).get("type")
        if trigger_type == 'file':
            imports.add("import time")
            imports.add("from watchdog.observers import Observer")
            imports.add("from watchdog.events import FileSystemEventHandler")

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
    logger.info(f"🚀 Starting workflow: {name}")
    logger.info(f"📋 Description: {description}")

    # Initialize variables for data passing between actions
    variables = {{}}

    # Load credentials
    try:
        cred_manager = CredentialManager()
        credentials = cred_manager.load_credentials()
        logger.debug("🔒 Credentials loaded.")
    except Exception as e:
        logger.error(f"❌ Error loading credentials: {{e}}")
        credentials = {{}}

    try:
'''
        action_calls_code = self._generate_action_calls(workflow)

        main_func_footer = '''
        logger.info("✅ Workflow completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Workflow failed: {e}")
        return False
'''
        return main_func_header + action_calls_code + main_func_footer

    def _generate_action_calls(self, workflow: Dict[str, Any]) -> str:
        """Generate the sequence of action calls inside the main function."""
        code = ""
        for i, action in enumerate(workflow.get('actions', []), 1):
            action_type = action.get('type', 'unknown')

            code += f"\n        # Action {i}: {action_type}\n"
            code += f"        logger.info(f\"▶️  Executing action {i}: {action_type}\")\n"

            plugin = self.plugin_manager.get_action_plugin(action_type)
            if plugin:
                call_code = plugin.get_function_call(action.get('config', {}))
                # Indent the action call code properly
                indented_lines = ['        ' + line for line in call_code.split('\n')]
                code += '\n'.join(indented_lines) + '\n'
            else:
                code += f"        logger.warning(\"🤷‍♂️ Action '{action_type}' skipped (no plugin found).\")\n"
        
        return code

    def _generate_main_execution(self, workflow: Dict[str, Any]) -> str:
        """Generate main execution block"""
        trigger_type = workflow.get("trigger", {}).get("type", "manual")

        if trigger_type == "manual":
            return '''
if __name__ == "__main__":
    success = run_workflow()
    sys.exit(0 if success else 1)
'''
        elif trigger_type == "file":
            path = workflow.get("trigger", {}).get("path", ".")
            return f'''
class FileTriggerHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            logger.info(f"New file created: {{event.src_path}}")
            run_workflow()

if __name__ == "__main__":
    path = "{path}"
    logger.info(f"Watching for new files in {{path}}...")
    event_handler = FileTriggerHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
'''
        else:
            return f'''
if __name__ == "__main__":
    logger.error("Unknown trigger type: {trigger_type}")
    sys.exit(1)
'''
