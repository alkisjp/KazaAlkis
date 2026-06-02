"""
WhatsApp Notification Module for KazaALKIS
Handles message delivery via WhatsApp
"""

import os
import requests
import re
from dotenv import load_dotenv
from typing import List, Dict, Tuple
from datetime import datetime
from pathlib import Path
try:
    from .path_manager import PROJECT_ROOT, get_paths
except ImportError:
    from path_manager import PROJECT_ROOT, get_paths

class WhatsAppNotifier:
    """Send WhatsApp notifications"""

    def __init__(self, provider: str = 'whatsapp_business_cloud'):
        """Initialize WhatsApp notifier"""
        load_dotenv(str(PROJECT_ROOT / "config" / ".env"))
        self.provider = provider
        self.sent_messages = []
        self.failed_messages = []

    def send_message(self, phone_number: str, message_text: str) -> Tuple[bool, str]:
        """Send WhatsApp message"""
        try:
            phone_number = normalize_phone_number(phone_number)
        except ValueError as e:
            return False, str(e)

        if self.provider == 'whatsapp_business_cloud':
            return self._send_business_cloud(phone_number, message_text)
        elif self.provider == 'twilio':
            return self._send_twilio(phone_number, message_text)
        elif self.provider == 'manual':
            return self._generate_manual_message(phone_number, message_text)
        else:
            return False, f"Unknown provider: {self.provider}"

    def send_batch(self, contacts: List[Dict], message_text: str) -> Dict:
        """Send message to multiple contacts"""
        results = {
            'total': len(contacts),
            'sent': 0,
            'failed': 0,
            'details': []
        }

        for contact in contacts:
            phone = contact.get('phone_number')
            masked = contact.get('phone_masked', phone[-3:].rjust(len(phone), '*'))

            success, response = self.send_message(phone, message_text)

            if success:
                results['sent'] += 1
                results['details'].append({
                    'phone': masked,
                    'status': 'sent',
                    'timestamp': datetime.now().isoformat()
                })
                print(f"✓ Message sent to {masked}")
            else:
                results['failed'] += 1
                results['details'].append({
                    'phone': masked,
                    'status': 'failed',
                    'error': response,
                    'timestamp': datetime.now().isoformat()
                })
                print(f"✗ Failed to send to {masked}: {response}")

        return results

    def _send_business_cloud(self, phone_number: str, message_text: str) -> Tuple[bool, str]:
        """Send via WhatsApp Business Cloud API"""
        try:
            access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
            phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
            business_account_id = os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID')

            if not all([access_token, phone_number_id, business_account_id]):
                return False, "Missing WhatsApp Business Cloud credentials"

            graph_version = os.getenv("WHATSAPP_GRAPH_VERSION", "v20.0")
            url = f"https://graph.facebook.com/{graph_version}/{phone_number_id}/messages"

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            payload = {
                'messaging_product': 'whatsapp',
                'recipient_type': 'individual',
                'to': phone_number,
                'type': 'text',
                'text': {
                    'preview_url': True,
                    'body': message_text
                }
            }

            response = requests.post(url, json=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                return True, f"Message ID: {response.json().get('messages', [{}])[0].get('id', 'unknown')}"
            else:
                error_msg = response.json().get('error', {}).get('message', response.text)
                if "(#131030)" in error_msg:
                    return False, (
                        "Meta rejected this recipient because it is not in the allowed test-recipient list. "
                        "In Meta Developers, open your app's WhatsApp > API Setup page, add and verify this "
                        "recipient number, then try again. If you are using a production sender, confirm that "
                        "the configured Phone Number ID belongs to that sender."
                    )
                return False, f"WhatsApp API error: {error_msg}"

        except Exception as e:
            return False, f"Exception: {str(e)}"

    def _send_twilio(self, phone_number: str, message_text: str) -> Tuple[bool, str]:
        """Send via Twilio WhatsApp API"""
        try:
            from twilio.rest import Client

            account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            twilio_phone = os.getenv('TWILIO_WHATSAPP_NUMBER')

            if not all([account_sid, auth_token, twilio_phone]):
                return False, "Missing Twilio credentials"

            client = Client(account_sid, auth_token)

            message = client.messages.create(
                from_=f'whatsapp:{twilio_phone}',
                body=message_text,
                to=f'whatsapp:{phone_number}'
            )

            return True, f"Message SID: {message.sid}"

        except Exception as e:
            return False, f"Twilio error: {str(e)}"

    def _generate_manual_message(self, phone_number: str, message_text: str) -> Tuple[bool, str]:
        """Generate message for manual copy/paste"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            masked = phone_number[-3:].rjust(len(phone_number), "*")
            output_dir = get_paths().app_output_dir / "manual_messages"
            output_dir.mkdir(parents=True, exist_ok=True)
            file_recipient = f"masked_{phone_number[-3:]}"
            message_file = output_dir / f"manual_message_{file_recipient}_{timestamp}.txt"

            with open(message_file, 'w', encoding='utf-8') as f:
                f.write(f"To: {masked}\n")
                f.write(f"Time: {datetime.now().isoformat()}\n")
                f.write("="*60 + "\n\n")
                f.write(message_text)
                f.write("\n\n" + "="*60)

            return True, f"Message prepared in {message_file} for manual sending"

        except Exception as e:
            return False, f"Manual message generation error: {str(e)}"

class BulkMessageSender:
    """Handle bulk message operations with logging"""

    def __init__(self, notifier: WhatsAppNotifier, db):
        """Initialize bulk sender"""
        self.notifier = notifier
        self.db = db

    def send_daily_message(self, message_text: str, language: str = 'en',
                           force: bool = False) -> Dict:
        """Send today's message to all active contacts"""

        try:
            self.db.cursor.execute("""
                SELECT id, name, phone_number, phone_masked FROM contacts WHERE is_active = 1
            """)

            contacts = [dict(row) for row in self.db.cursor.fetchall()]

            if not contacts:
                print("✗ No active contacts found")
                return {'total': 0, 'sent': 0, 'failed': 0, 'details': []}

            date_str = datetime.now().strftime('%Y-%m-%d')
            pending = []
            skipped = []
            for contact in contacts:
                if not force and self.db.was_sent_today(contact["id"], date_str):
                    skipped.append(contact)
                    self.db.log_message(
                        contact_id=contact["id"],
                        message_date=date_str,
                        message_text=message_text[:100],
                        status="skipped",
                        delivery_method=self.notifier.provider,
                        error_msg="Duplicate daily message blocked"
                    )
                else:
                    pending.append(contact)

            results = dict(self.notifier.send_batch(pending, message_text))
            results["total"] = len(contacts)
            results["skipped"] = len(skipped)

            for contact in pending:
                contact_id = contact['id']
                detail = next((d for d in results['details'] if d['phone'] == contact['phone_masked']), None)

                if detail:
                    status = 'sent' if detail['status'] == 'sent' else 'failed'
                    error_msg = detail.get('error', None)
                else:
                    status = 'skipped'
                    error_msg = 'Unknown'

                self.db.log_message(
                    contact_id=contact_id,
                    message_date=date_str,
                    message_text=message_text[:100],
                    status=status,
                    delivery_method=self.notifier.provider,
                    error_msg=error_msg
                )

            return results

        except Exception as e:
            print(f"✗ Error sending batch messages: {e}")
            return {'total': 0, 'sent': 0, 'failed': 0, 'details': [], 'error': str(e)}


def normalize_phone_number(phone_number: str) -> str:
    """Normalize Greek local or international phone numbers to E.164 format."""
    raw = str(phone_number or "").strip()
    compact = re.sub(r"[\s().-]", "", raw)
    if compact.startswith("00"):
        compact = "+" + compact[2:]
    if compact.startswith("+"):
        digits = compact[1:]
    else:
        digits = compact
        if digits.startswith("30") and len(digits) == 12:
            return "+" + digits
        if len(digits) == 10 and (digits.startswith("2") or digits.startswith("69")):
            return "+30" + digits
        raise ValueError(
            "Use a Greek local number such as 6912345678 or an international "
            "number such as +306912345678."
        )
    if not digits.isdigit() or not 8 <= len(digits) <= 15:
        raise ValueError("Phone number must use international E.164 format, for example +306912345678.")
    return "+" + digits

if __name__ == "__main__":
    notifier = WhatsAppNotifier(provider='manual')

    test_message = """
    ✨ Χρόνια πολλά! / Many Years! ✨

    Today's Kazamias Message:
    - Saint George's Day
    - Named saints: George, Giorgos
    - Quote: "Courage is the conquest of fear."

    Blessings from KazaALKIS
    """

    success, result = notifier.send_message("1234567890", test_message)
    print(f"Success: {success}")
    print(f"Result: {result}")
