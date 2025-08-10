"""
Send Email Action Plugin for WizFlow
"""

from typing import Dict, Any, List
from .base import ActionPlugin


class SendEmailPlugin(ActionPlugin):
    """
    An action plugin to send emails using SMTP.
    """

    @property
    def name(self) -> str:
        return "send_email"

    @property
    def required_imports(self) -> List[str]:
        return [
            "import smtplib",
            "from email.mime.text import MIMEText",
            "from email.mime.multipart import MIMEMultipart",
        ]

    def get_function_definition(self) -> str:
        return '''
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
'''

    def get_function_call(self, config: Dict[str, Any]) -> str:
        to = repr(config.get('to', 'user@example.com'))
        subject = repr(config.get('subject', 'Workflow Notification'))
        message = repr(config.get('message', 'Workflow completed'))

        return f"send_email(to_email={to}, subject={subject}, body={message}, creds=credentials)"
