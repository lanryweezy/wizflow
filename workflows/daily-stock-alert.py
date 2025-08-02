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
    ALLOWED_MODULES = set(json.loads('["email.mime.text", "requests", "sys", "email.mime.multipart", "wizflow.core.config", "wizflow.core.credentials", "smtplib", "json", "typing", "os", "datetime", "wizflow.core.llm_interface"]'))

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
WORKFLOW_INFO = {}

# Additional imports
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
import smtplib

# --- Action Function Definitions ---

def make_api_call(url, method="GET", headers=None, data=None):
    """Make HTTP API call"""
    try:
        response = requests.request(method, url, headers=headers, json=data)
        response.raise_for_status()
        print(f"🌐 API call to {url} successful")
        # Store result in variables for chaining
        api_result = response.json() if response.content else None
        if api_result:
            variables['api_result'] = api_result
        return api_result
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return None


def send_email(to_email, subject, body, smtp_server="smtp.gmail.com", smtp_port=587, creds={}):
    """Send email via SMTP using stored credentials"""
    username = creds.get("smtp_user")
    password = creds.get("smtp_pass")

    if not username or not password:
        print("❌ SMTP credentials (smtp_user, smtp_pass) not found. Cannot send email.")
        return False

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

        print(f"📧 Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

# --- End Action Function Definitions ---

def run_workflow():
    """
    Main workflow function: Daily Stock Alert
    Description: Sends a daily email with the price of a chosen stock.
    """
    print("🚀 Starting workflow: Daily Stock Alert")
    print("📋 Description: Sends a daily email with the price of a chosen stock.")

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

        # Action 1: api_call
        print(f"▶️  Executing action 1: api_call")
        make_api_call(url='https://api.example.com/stock/AAPL', method='GET')

        # Action 2: send_email
        if variables.get('api_result', {}).get('price'):
            print(f"▶️  Executing conditional action: send_email")
                send_email(to_email='user@example.com', subject='Daily Stock Price for AAPL', body='The current price of AAPL is {{api_result.price}}', creds=credentials)

        print("✅ Workflow completed successfully")
        return True

    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        return False

if __name__ == "__main__":
    success = run_workflow()
    sys.exit(0 if success else 1)
