#!/usr/bin/env python3
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
            return {}

# --- Security Sandbox: Restrict Imports ---
import json
_original_import = __import__
def _secure_import(name, globals=None, locals=None, fromlist=(), level=0):
    ALLOWED_MODULES = set(json.loads('["typing", "os", "wizflow.core.llm_interface", "datetime", "sys", "json", "wizflow.core.credentials", "wizflow.core.config"]'))

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
            raise ImportError(f"Disallowed import: '{name}'")

    return _original_import(name, globals, locals, fromlist, level)

# Overriding the import function to enable the sandbox.
__builtins__['__import__'] = _secure_import
# --- End Security Sandbox ---


# Workflow Metadata
WORKFLOW_INFO = {
    "generated_from": "Check Apple stock price every morning and email me the results",
    "version": "1.0",
    "created_by": "WizFlow CLI"
}

# Additional imports
from wizflow.core.config import Config
from wizflow.core.llm_interface import LLMInterface

# --- Action Function Definitions ---

def send_whatsapp(to_number, message, creds={}):
    """Send WhatsApp message using Twilio"""
    account_sid = creds.get("twilio_sid")
    auth_token = creds.get("twilio_token")
    from_whatsapp_number = creds.get("twilio_whatsapp_from")

    if not all([account_sid, auth_token, from_whatsapp_number]):
        print("❌ Twilio credentials (twilio_sid, twilio_token, twilio_whatsapp_from) not found.")
        print(f"📱 Mocking WhatsApp to {to_number}: {message}")
        return False

    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)
        msg = client.messages.create(
            from_=f'whatsapp:{from_whatsapp_number}',
            body=message,
            to=f'whatsapp:{to_number}'
        )
        print(f"📱 WhatsApp sent to {to_number} (SID: {msg.sid})")
        return True
    except ImportError:
        print("❌ Twilio library not installed. Please run: pip install twilio")
        return False
    except Exception as e:
        print(f"❌ Failed to send WhatsApp: {e}")
        return False


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

        variables['summary'] = summary
        print(f"📝 Summary: {summary}")
        return summary
    except Exception as e:
        print(f"❌ AI summarization failed: {e}")
        return None

# --- End Action Function Definitions ---

def run_workflow():
    """
    Main workflow function: Email to WhatsApp Alert
    Description: Forward email summaries to WhatsApp
    """
    print(f"🚀 Starting workflow: Email to WhatsApp Alert")
    print(f"📋 Description: Forward email summaries to WhatsApp")

    # Initialize variables for data passing between actions
    variables = {}

    # Load credentials
    try:
        cred_manager = CredentialManager()
        credentials = cred_manager.load_credentials()
        print("🔒 Credentials loaded.")
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        credentials = {}

    try:

        # Action 1: summarize
        print(f"▶️  Executing action 1: summarize")
        summarize_text(text='Sample text to summarize.', max_length=100)

        # Action 2: send_whatsapp
        print(f"▶️  Executing action 2: send_whatsapp")
        send_whatsapp(to_number='+1234567890', message='Email Summary: {{summary}}', creds=credentials)

        print("✅ Workflow completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        return False

if __name__ == "__main__":
    success = run_workflow()
    sys.exit(0 if success else 1)
