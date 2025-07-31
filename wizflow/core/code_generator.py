"""
Code Generator - Converts workflow JSON to executable Python code
"""

import json
from typing import Dict, Any, List
from pathlib import Path


class CodeGenerator:
    """Generates Python code from workflow JSON"""
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.action_templates = self._load_action_templates()
    
    def _load_action_templates(self) -> Dict[str, str]:
        """Load code templates for different action types"""
        return {
            'summarize': '''# Summarize text using AI
def summarize_text(text, max_length=100):
    \"\"\"Summarize text using a simple algorithm\"\"\"
    sentences = text.split('.')
    if len(sentences) <= 2:
        return text
    return '. '.join(sentences[:2]) + '.'

summary = summarize_text({input_text}, {max_length})
variables['summary'] = summary
print(f"📝 Summary: {{summary}}")''',
            
            'send_email': '''# Send email via SMTP
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email, subject, body, smtp_server="smtp.gmail.com", smtp_port=587, username="", password=""):
    \"\"\"Send email via SMTP\"\"\"
    try:
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        server.quit()
        
        print(f"📧 Email sent to {{to_email}}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {{e}}")
        return False

send_email({to}, {subject}, {message})''',
            
            'send_whatsapp': '''# Send WhatsApp message (requires Twilio or similar service)
def send_whatsapp(to_number, message):
    \"\"\"Send WhatsApp message (mock implementation)\"\"\"
    print(f"📱 WhatsApp to {{to_number}}: {{message}}")
    # In real implementation, use Twilio API:
    # from twilio.rest import Client
    # client = Client(account_sid, auth_token)
    # message = client.messages.create(
    #     from_='whatsapp:+14155238886',
    #     body=message,
    #     to=f'whatsapp:{{to_number}}'
    # )
    return True

send_whatsapp({to}, {message})''',
            
            'api_call': '''# Make HTTP API call
import requests

def make_api_call(url, method="GET", headers=None, data=None):
    \"\"\"Make HTTP API call\"\"\"
    try:
        response = requests.request(method, url, headers=headers, json=data)
        response.raise_for_status()
        print(f"🌐 API call to {{url}} successful")
        return response.json() if response.content else None
    except Exception as e:
        print(f"❌ API call failed: {{e}}")
        return None

api_result = make_api_call({url}, {method})
if api_result:
    variables['api_result'] = api_result''',
            
            'web_scrape': '''# Web scraping
import requests
from bs4 import BeautifulSoup

def scrape_web(url, selector=None):
    \"\"\"Scrape web content\"\"\"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        if selector:
            elements = soup.select(selector)
            content = [elem.get_text().strip() for elem in elements]
        else:
            content = soup.get_text().strip()
        
        print(f"🕷️  Scraped content from {{url}}")
        return content
    except Exception as e:
        print(f"❌ Web scraping failed: {{e}}")
        return None

scraped_content = scrape_web({url})
if scraped_content:
    variables['scraped_content'] = scraped_content''',
            
            'file_process': '''# File processing
def process_file(filepath, operation="read"):
    \"\"\"Process file operations\"\"\"
    try:
        if operation == "read":
            with open(filepath, 'r') as f:
                content = f.read()
            print(f"📄 Read file: {{filepath}}")
            return content
        elif operation == "write":
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"✍️  Wrote file: {{filepath}}")
            return True
    except Exception as e:
        print(f"❌ File operation failed: {{e}}")
        return None

file_content = process_file({filepath}, {operation})
if file_content:
    variables['file_content'] = file_content''',
        }
    
    def generate_code(self, workflow: Dict[str, Any]) -> str:
        """Generate Python code from workflow JSON"""
        print("🔄 Generating Python code...")
        
        # Start with base template
        code = self._get_base_template()
        
        # Add workflow metadata
        code += self._generate_metadata_section(workflow)
        
        # Add imports
        code += self._generate_imports(workflow)
        
        # Add main function
        code += self._generate_main_function(workflow)
        
        # Add action implementations
        code += self._generate_actions(workflow['actions'])
        
        # Add main execution
        code += self._generate_main_execution()
        
        return code
    
    def _get_base_template(self) -> str:
        """Get base Python template"""
        return '''#!/usr/bin/env python3
"""
Auto-generated workflow by WizFlow
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any

'''
    
    def _generate_metadata_section(self, workflow: Dict[str, Any]) -> str:
        """Generate metadata section"""
        metadata = json.dumps(workflow.get('metadata', {}), indent=4)
        return f'''
# Workflow Metadata
WORKFLOW_INFO = {metadata}

'''
    
    def _generate_imports(self, workflow: Dict[str, Any]) -> str:
        """Generate necessary imports based on actions"""
        imports = set()
        
        for action in workflow.get('actions', []):
            action_type = action.get('type')
            tool = action.get('tool')
            
            if action_type == 'send_email' or tool == 'smtp':
                imports.add('import smtplib')
                imports.add('from email.mime.text import MIMEText')
                imports.add('from email.mime.multipart import MIMEMultipart')
            
            elif action_type in ['api_call', 'web_scrape'] or tool == 'requests':
                imports.add('import requests')
            
            elif action_type == 'web_scrape':
                imports.add('from bs4 import BeautifulSoup')
            
            elif action_type == 'schedule_task' or tool == 'schedule':
                imports.add('import schedule')
                imports.add('import time')
        
        if imports:
            return '# Additional imports\n' + '\n'.join(sorted(imports)) + '\n\n'
        return ''
    
    def _generate_main_function(self, workflow: Dict[str, Any]) -> str:
        """Generate main workflow function"""
        return f'''
def run_workflow():
    """
    Main workflow function: {workflow.get('name', 'Generated Workflow')}
    Description: {workflow.get('description', 'Auto-generated workflow')}
    """
    print("🚀 Starting workflow: {workflow.get('name', 'Generated Workflow')}")
    print("📋 Description: {workflow.get('description', 'Auto-generated workflow')}")
    
    # Initialize variables for data passing between actions
    variables = {{}}
    
    try:
'''
    
    def _generate_actions(self, actions: List[Dict[str, Any]]) -> str:
        """Generate code for all actions"""
        code = ""
        
        for i, action in enumerate(actions, 1):
            code += f"\n        # Action {i}: {action.get('type', 'unknown')}\n"
            code += f"        print(f\"▶️  Executing action {i}: {action.get('type', 'unknown')}\")\n"
            
            action_code = self._generate_action_code(action)
            # Indent the action code properly (each line gets 8 spaces for proper nesting)
            indented_lines = []
            for line in action_code.split('\n'):
                if line.strip():  # Only indent non-empty lines
                    indented_lines.append('        ' + line)
                elif line == '':  # Keep empty lines as is
                    indented_lines.append('')
            code += '\n'.join(indented_lines) + '\n'
        
        code += '''
        print("✅ Workflow completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        return False

'''
        return code
    
    def _generate_action_code(self, action: Dict[str, Any]) -> str:
        """Generate code for a single action"""
        action_type = action.get('type')
        config = action.get('config', {})
        
        # Get template for this action type
        template = self.action_templates.get(action_type, self._get_default_template())
        
        # Replace placeholders with actual config values
        formatted_code = self._format_template(template, config)
        
        return formatted_code
    
    def _get_default_template(self) -> str:
        """Get default template for unknown action types"""
        return '''# Generic action
print("🔧 Executing generic action")
# Add your custom implementation here'''
    
    def _format_template(self, template: str, config: Dict[str, Any]) -> str:
        """Format template with config values"""
        formatted = template
        
        # Replace common placeholders
        replacements = {
            '{input_text}': repr(config.get('input_text', 'sample text')),
            '{max_length}': config.get('max_length', 100),
            '{to}': repr(config.get('to', 'user@example.com')),
            '{subject}': repr(config.get('subject', 'Workflow Notification')),
            '{message}': repr(config.get('message', 'Workflow completed')),
            '{url}': repr(config.get('url', 'https://api.example.com')),
            '{method}': repr(config.get('method', 'GET')),
            '{filepath}': repr(config.get('filepath', 'data.txt')),
            '{operation}': repr(config.get('operation', 'read')),
        }
        
        for placeholder, value in replacements.items():
            formatted = formatted.replace(placeholder, str(value))
        
        return formatted
    
    def _generate_main_execution(self) -> str:
        """Generate main execution block"""
        return '''
if __name__ == "__main__":
    success = run_workflow()
    sys.exit(0 if success else 1)
'''
