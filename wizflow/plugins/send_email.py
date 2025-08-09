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
def send_email(to_email, subject, body, smtp_server="smtp.gmail.com", smtp_port=587, variables={}, creds={}):
    """Send email via SMTP using stored credentials"""
    username = creds.get("smtp_user")
    password = creds.get("smtp_pass")

    if not username or not password:
        logger.error("❌ SMTP credentials (smtp_user, smtp_pass) not found. Cannot send email.")
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

        logger.info(f"📧 Email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send email: {e}")
        return False
'''

    def get_function_call(self, config: Dict[str, Any]) -> str:
        to = self._resolve_template(config.get('to', 'user@example.com'))
        subject = self._resolve_template(config.get('subject', 'Workflow Notification'))
        message = self._resolve_template(config.get('message', 'Workflow completed'))

        return f"send_email(to_email={to}, subject={subject}, body={message}, variables=variables, creds=credentials)"
