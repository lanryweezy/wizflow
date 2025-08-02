"""
Workflow Builder - Converts natural language to structured workflows
"""

import json
from typing import Dict, Any
from pathlib import Path
from .llm_interface import LLMInterface
import jsonschema


class WorkflowBuilder:
    """Builds workflows from natural language descriptions"""
    
    def __init__(self, llm_interface: LLMInterface):
        self.llm = llm_interface
        self.schema = self._load_schema()

    def _load_schema(self) -> Dict[str, Any]:
        """Loads the workflow JSON schema."""
        schema_path = Path(__file__).parent.parent / "schemas" / "workflow_schema.json"
        with open(schema_path, 'r') as f:
            return json.load(f)

    def build_from_description(self, description: str) -> Dict[str, Any]:
        """Build workflow from natural language description"""
        print("🔄 Generating workflow structure...")
        
        # Generate workflow using LLM
        workflow = self.llm.generate_workflow(description)
        
        # Validate and enhance the workflow
        workflow = self._validate_workflow(workflow)
        workflow = self._enhance_workflow(workflow, description)
        
        return workflow
    
    def _validate_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and fix workflow structure using JSON schema."""
        try:
            jsonschema.validate(instance=workflow, schema=self.schema)
            print("✅ Workflow structure is valid.")
        except jsonschema.exceptions.ValidationError as e:
            print(f"⚠️  Workflow validation error: {e.message}")
            print("   Attempting to fix the workflow...")
            # Fallback to simple validation and fixing
            if 'name' not in workflow:
                workflow['name'] = 'Generated Workflow'
            if 'description' not in workflow:
                workflow['description'] = 'Auto-generated workflow'
            if 'trigger' not in workflow:
                workflow['trigger'] = {'type': 'manual'}
            if 'actions' not in workflow:
                workflow['actions'] = []
            return workflow

        # Simple validation as a fallback
        if 'name' not in workflow:
            workflow['name'] = 'Generated Workflow'
        
        if 'description' not in workflow:
            workflow['description'] = 'Auto-generated workflow'
        
        if 'trigger' not in workflow:
            workflow['trigger'] = {'type': 'manual'}
        
        if 'actions' not in workflow:
            workflow['actions'] = []
        
        # Validate actions
        valid_actions = []
        for action in workflow.get('actions', []):
            if isinstance(action, dict) and 'type' in action:
                if 'tool' not in action:
                    action['tool'] = self._get_default_tool(action['type'])
                if 'config' not in action:
                    action['config'] = {}
                valid_actions.append(action)
        
        workflow['actions'] = valid_actions
        return workflow
    
    def _get_default_tool(self, action_type: str) -> str:
        """Get default tool for action type"""
        defaults = {
            'summarize': 'gpt',
            'send_email': 'smtp',
            'send_whatsapp': 'twilio',
            'send_sms': 'twilio',
            'read_email': 'imap',
            'web_scrape': 'requests',
            'file_process': 'python',
            'api_call': 'requests',
            'schedule_task': 'schedule',
            'database_query': 'sqlite3',
            'spreadsheet_update': 'gspread'
        }
        return defaults.get(action_type, 'python')
    
    def _enhance_workflow(self, workflow: Dict[str, Any], description: str) -> Dict[str, Any]:
        """Enhance workflow with additional metadata"""
        workflow['metadata'] = {
            'generated_from': description,
            'version': '1.0',
            'created_by': 'WizFlow CLI'
        }
        
        # Add variable substitution info
        workflow['variables'] = self._extract_variables(workflow)
        
        return workflow
    
    def _extract_variables(self, workflow: Dict[str, Any]) -> Dict[str, str]:
        """Extract variables that need substitution"""
        variables = {}
        
        # Scan actions for template variables
        for action in workflow.get('actions', []):
            config = action.get('config', {})
            for key, value in config.items():
                if isinstance(value, str) and '{{' in value and '}}' in value:
                    # Extract variable names
                    import re
                    vars_in_value = re.findall(r'\{\{(\w+)\}\}', value)
                    for var in vars_in_value:
                        variables[var] = f"Value for {var}"
        
        return variables
    
    def save_workflow(self, workflow: Dict[str, Any], filepath: str):
        """Save workflow to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(workflow, f, indent=2)
    
    def load_workflow(self, filepath: str) -> Dict[str, Any]:
        """Load workflow from JSON file"""
        with open(filepath) as f:
            return json.load(f)
