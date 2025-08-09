"""
Send WhatsApp Action Plugin for WizFlow
"""

from typing import Dict, Any, List
from .base import ActionPlugin


class SendWhatsappPlugin(ActionPlugin):
    """
    An action plugin to send WhatsApp messages using Twilio.
    """

    @property
    def name(self) -> str:
        return "send_whatsapp"

    @property
    def required_imports(self) -> List[str]:
        # The 'from twilio.rest import Client' is handled inside the function
        # to provide a better error message if Twilio is not installed.
        return []

    def get_function_definition(self) -> str:
        return '''
def send_whatsapp(to_number, message, variables={}, creds={}):
    """Send WhatsApp message using Twilio"""
    account_sid = creds.get("twilio_sid")
    auth_token = creds.get("twilio_token")
    from_whatsapp_number = creds.get("twilio_whatsapp_from")

    if not all([account_sid, auth_token, from_whatsapp_number]):
        logger.warning("❌ Twilio credentials (twilio_sid, twilio_token, twilio_whatsapp_from) not found.")
        logger.info(f"📱 Mocking WhatsApp to {to_number}: {message}")
        return False

    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)
        msg = client.messages.create(
            from_=f'whatsapp:{from_whatsapp_number}',
            body=message,
            to=f'whatsapp:{to_number}'
        )
        logger.info(f"📱 WhatsApp sent to {to_number} (SID: {msg.sid})")
        return True
    except ImportError:
        logger.error("❌ Twilio library not installed. Please run: pip install twilio")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to send WhatsApp: {type(e).__name__}")
        return False
'''

    def get_function_call(self, config: Dict[str, Any]) -> str:
        to = self._resolve_template(config.get('to', '+1234567890'))
        message = self._resolve_template(config.get('message', 'Workflow message'))

        return f"send_whatsapp(to_number={to}, message={message}, variables=variables, creds=credentials)"
