"""
KazaALKIS - Main Launcher
Entry point for the Kazamias Daily Herald application
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from database import KazaALKISDatabase
from config_manager import ConfigurationManager
from message_builder import MessageBuilder
from whatsapp_notifier import WhatsAppNotifier, BulkMessageSender
from logger_dashboard import KazaALKISLogger, KazaALKISDashboard
from calendar_exporter import CalendarExporter
from path_manager import get_paths
from website_publisher import WebsitePublisher
from commentary_generator import CommentaryGenerator

class KazaALKISLauncher:
    """Main application launcher"""

    def __init__(self):
        """Initialize launcher"""
        get_paths().ensure_runtime_dirs()
        self.config = ConfigurationManager()
        self.db = KazaALKISDatabase(self.config.get('database_path'))
        self.db.connect()

    def show_menu(self):
        """Display main menu"""
        print("\n" + "="*60)
        print(self.config.get_delivery_status())
        print("="*60)
        print("KazaALKIS - Daily Greek Calendar")
        print("="*60)
        print("\n1.  Setup project")
        print("2.  Import open-data calendar source")
        print("3.  Preview today's message")
        print("4.  Send today's message")
        print("5.  Send test message")
        print("6.  Edit contacts")
        print("7.  View logs")
        print("8.  View configuration")
        print("9.  Validation dashboard")
        print("10. Export logs to Excel")
        print("11. Export monthly name days to Excel")
        print("12. Generate bilingual website commentary draft")
        print("13. Publish approved website JSON")
        print("14. Commit and push website update")
        print("15. Exit")
        print("\n" + "="*60)

    def run(self):
        """Run application"""
        while True:
            self.show_menu()
            choice = input("\nSelect option (1-15): ").strip()

            if choice == "1":
                self.setup_project()
            elif choice == "2":
                self.import_database()
            elif choice == "3":
                self.preview_message()
            elif choice == "4":
                self.send_message()
            elif choice == "5":
                self.send_test_message()
            elif choice == "6":
                self.edit_contacts()
            elif choice == "7":
                self.view_logs()
            elif choice == "8":
                self.config.print_config()
            elif choice == "9":
                KazaALKISDashboard(self.db).show_validation_dashboard()
            elif choice == "10":
                CalendarExporter(self.db).export_logs_xlsx()
            elif choice == "11":
                year = int(input("Year: ").strip() or datetime.now().year)
                month = int(input("Month (1-12): ").strip() or datetime.now().month)
                CalendarExporter(self.db).export_monthly_namedays_xlsx(year, month)
            elif choice == "12":
                self.generate_website_commentary_draft()
            elif choice == "13":
                self.publish_website_json()
            elif choice == "14":
                self.commit_and_push_website_update()
            elif choice == "15":
                self.exit_app()
            else:
                print("✗ Invalid choice. Please try again.")

    def setup_project(self):
        """Setup project"""
        print("\n" + "="*60)
        print("Project Setup")
        print("="*60 + "\n")

        print("Initializing database...")
        self.db.initialize_schema()

        print("\nImporting 2026 calendar data...")
        data_path = Path(__file__).parent / "data"

        self.db.import_namedays_from_json(str(data_path / "kazamias_namedays_2026.json"))
        self.db.import_quotes_from_json(str(data_path / "kazamias_quotes_2026.json"))
        self.db.import_holidays_from_json(str(data_path / "greek_holidays_2026.json"))
        self.db.import_fasting_from_json(str(data_path / "fasting_periods_2026.json"))

        print("\nConfiguring KazaALKIS...")
        self.config.setup_first_time()

        choice = input("\nSetup WhatsApp API now? (y/n): ").strip().lower() == 'y'
        if choice:
            self.config.setup_whatsapp_api()

        print("\n✓ Project setup completed!")

    def import_database(self):
        """Import Kazamias database"""
        print("\n" + "="*60)
        print("Import Open-Data Calendar Source")
        print("="*60 + "\n")

        print("Supported formats:")
        print("1. SQLite (.db)")
        print("2. CSV (.csv)")
        print("3. Excel (.xlsx)")
        print("4. JSON (.json)")

        db_path = input("\nEnter database file path: ").strip()

        if not Path(db_path).exists():
            print(f"✗ File not found: {db_path}")
            return

        print(f"✓ Database import initiated for {db_path}")

    def preview_message(self):
        """Preview today's message"""
        print("\n" + "="*60)
        print("Today's Message Preview")
        print("="*60 + "\n")

        today_data = self.db.get_today_data()

        if today_data is None:
            print("✗ Unable to retrieve today's data")
            return

        language = self.config.get('language', 'bilingual')
        tone = self.config.get('message_tone', 'friendly')

        builder = MessageBuilder(language=language, tone=tone)
        message = builder.build_daily_message(today_data)

        print(message)
        print("\n" + "="*60)

    def send_message(self):
        """Send today's message"""
        print("\n" + "="*60)
        print("Send Today's Message")
        print("="*60 + "\n")

        today_data = self.db.get_today_data()

        if today_data is None:
            print("✗ Unable to retrieve today's data")
            return

        language = self.config.get('language', 'bilingual')
        tone = self.config.get('message_tone', 'friendly')

        builder = MessageBuilder(language=language, tone=tone)
        message = builder.build_daily_message(today_data)

        print("Message preview:")
        print(message[:200] + "..." if len(message) > 200 else message)

        confirm = input("\n\nProceed with sending? (y/n): ").strip().lower() == 'y'
        if not confirm:
            print("✗ Sending cancelled")
            return

        provider = self.config.get('whatsapp_provider', 'manual')
        print(f"Delivery mode: {provider}")
        notifier = WhatsAppNotifier(provider=provider)
        sender = BulkMessageSender(notifier, self.db)

        print("\nSending messages...")
        force = input("Force send even if already sent today? (y/n): ").strip().lower() == 'y'
        results = sender.send_daily_message(message, language=language, force=force)

        print(f"\n✓ Results:")
        print(f"  Total contacts: {results['total']}")
        print(f"  Sent: {results['sent']}")
        print(f"  Failed: {results['failed']}")
        print(f"  Skipped: {results.get('skipped', 0)}")

    def send_test_message(self):
        """Send test message"""
        print("\n" + "="*60)
        print("Send Test Message")
        print("="*60 + "\n")

        self.db.cursor.execute("""
            SELECT id, name, phone_number, phone_masked
            FROM contacts
            WHERE is_active = 1
            ORDER BY name
        """)
        contacts = [dict(row) for row in self.db.cursor.fetchall()]
        if not contacts:
            print("No active contacts found. Add a contact first.")
            return

        print("Stored contacts:")
        for contact in contacts:
            print(f"  {contact['name']} ({contact['phone_masked']})")

        recipient_name = input("Enter recipient name: ").strip()
        matches = [
            contact for contact in contacts
            if contact["name"].casefold() == recipient_name.casefold()
        ]
        if not matches:
            print(f"Recipient not found: {recipient_name}")
            return
        if len(matches) > 1:
            print("Multiple active contacts have that name. Please make contact names unique.")
            return

        recipient = matches[0]
        phone = recipient["phone_number"]

        test_message = """
        ✨ TEST MESSAGE from KazaALKIS ✨

        This is a test message to verify WhatsApp connectivity.

        If you receive this, the system is working correctly!

        Blessings from KazaALKIS
        """

        provider = self.config.get('whatsapp_provider', 'manual')
        notifier = WhatsAppNotifier(provider=provider)

        print(f"\nSending test message to {recipient['name']} ({recipient['phone_masked']}) via {provider}...")
        success, result = notifier.send_message(phone, test_message)

        if success:
            print(f"✓ Test message sent: {result}")
        else:
            print(f"✗ Test message failed: {result}")

    def edit_contacts(self):
        """Edit contacts"""
        print("\n" + "="*60)
        print("Edit Contacts")
        print("="*60 + "\n")

        print("1. Add contact")
        print("2. View contacts")
        print("3. Back to menu")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            name = input("Enter name: ").strip()
            phone = input("Enter phone number: ").strip()
            language = input("Language (en/gr/bilingual) [default: bilingual]: ").strip() or "bilingual"

            contact_id = self.db.add_contact(name, phone, language=language)
            if contact_id:
                print(f"✓ Contact added (ID: {contact_id})")

        elif choice == "2":
            self.db.cursor.execute("SELECT id, name, phone_masked, language FROM contacts WHERE is_active = 1")
            contacts = self.db.cursor.fetchall()

            if not contacts:
                print("No contacts found")
            else:
                print(f"\n{'ID':<3} {'Name':<20} {'Phone':<15} {'Language':<10}")
                print("-" * 50)
                for row in contacts:
                    print(f"{row[0]:<3} {row[1]:<20} {row[2]:<15} {row[3]:<10}")

    def view_logs(self):
        """View message logs"""
        print("\n" + "="*60)
        print("Message Logs")
        print("="*60 + "\n")

        days = input("View logs from last N days (default 7): ").strip() or "7"

        try:
            self.db.cursor.execute("""
                SELECT m.sent_at, c.name, m.status
                FROM message_logs m
                JOIN contacts c ON m.contact_id = c.id
                WHERE m.sent_at >= datetime('now', '-' || ? || ' days')
                ORDER BY m.sent_at DESC
                LIMIT 50
            """, (int(days),))

            logs = self.db.cursor.fetchall()

            if not logs:
                print(f"No logs found for the last {days} days")
            else:
                print(f"{'Timestamp':<25} {'Contact':<20} {'Status':<10}")
                print("-" * 55)
                for row in logs:
                    print(f"{row[0]:<25} {row[1]:<20} {row[2]:<10}")

        except Exception as e:
            print(f"✗ Error retrieving logs: {e}")

    def publish_website_json(self):
        """Export a privacy-safe public payload for the static website."""
        language = self.config.get('language', 'bilingual')
        tone = self.config.get('message_tone', 'friendly')
        try:
            commentary = self._load_commentary_draft_for_approval()
        except RuntimeError as e:
            print(e)
            return
        latest, history = WebsitePublisher(self.db).publish(
            language=language, tone=tone, commentary=commentary
        )
        print(f"Website JSON updated: {latest}")
        print(f"Website history updated: {history}")
        print("Review the files, then use option 14 to publish on GitHub Pages.")

    def generate_website_commentary_draft(self):
        """Generate and save a reviewable bilingual commentary draft."""
        today_data = self.db.get_today_data()
        if today_data is None:
            print("Unable to retrieve today's data")
            return
        provider = self.config.get('commentary_provider', 'template')
        model = self.config.get('commentary_model', 'llama3.1')
        ollama_url = self.config.get('ollama_url', 'http://127.0.0.1:11434')
        generator = CommentaryGenerator(provider=provider, model=model, ollama_url=ollama_url)
        try:
            commentary = generator.generate(today_data)
        except Exception as e:
            print(f"AI commentary generation failed: {e}")
            print("Falling back to safe local template commentary.")
            commentary = CommentaryGenerator(provider="template").generate(today_data)

        draft_file = self._commentary_draft_path(today_data["date"])
        draft_file.parent.mkdir(parents=True, exist_ok=True)
        draft_file.write_text(json.dumps(commentary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("\nEnglish commentary:")
        print(commentary.get("english", ""))
        print("\nGreek commentary:")
        print(commentary.get("greek", ""))
        print(f"\nDraft saved for review: {draft_file}")

    def _commentary_draft_path(self, date_str=None):
        date_str = date_str or datetime.now().strftime("%Y-%m-%d")
        return get_paths().app_output_dir / "website_commentary_drafts" / f"{date_str}.json"

    def _load_commentary_draft_for_approval(self):
        today_data = self.db.get_today_data()
        if not today_data:
            return None
        draft_file = self._commentary_draft_path(today_data["date"])
        if not draft_file.exists():
            include = input("No commentary draft found. Publish without commentary? (y/n): ").strip().lower()
            if include == "y":
                return None
            print("Publish cancelled. Generate a commentary draft first with option 12.")
            raise RuntimeError("No approved commentary draft")
        commentary = json.loads(draft_file.read_text(encoding="utf-8"))
        print("\nCommentary draft:")
        print(f"EN: {commentary.get('english', '')}")
        print(f"GR: {commentary.get('greek', '')}")
        approved = input("\nApprove this commentary for the public website? (y/n): ").strip().lower()
        if approved != "y":
            raise RuntimeError("Commentary not approved")
        commentary["review_required"] = False
        commentary["approved_at"] = datetime.now().isoformat(timespec="seconds")
        return commentary

    def commit_and_push_website_update(self):
        """Commit and push only public website notification payload files."""
        latest = Path("public_notifications") / "latest.json"
        history_dir = Path("public_notifications") / "history"
        if not latest.exists():
            print("No public_notifications/latest.json found. Publish website JSON first.")
            return
        history_files = sorted(history_dir.glob("*.json")) if history_dir.exists() else []
        files = [str(latest)] + [str(path) for path in history_files]
        confirm = input("Commit and push public website JSON files to GitHub? (y/n): ").strip().lower()
        if confirm != "y":
            print("Push cancelled.")
            return
        subprocess.run(["git", "add", "-f", *files], check=True)
        status = subprocess.run(
            ["git", "diff", "--cached", "--quiet", "--", *files],
            check=False,
        )
        if status.returncode == 0:
            print("No website JSON changes to commit.")
            return
        subprocess.run(["git", "commit", "-m", "Publish daily website notification"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Website notification pushed to GitHub Pages.")

    def exit_app(self):
        """Exit application"""
        print("\n✓ Thank you for using KazaALKIS!")
        self.db.close()
        sys.exit(0)

def main():
    """Main entry point"""
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        launcher = KazaALKISLauncher()
        launcher.run()
    except KeyboardInterrupt:
        print("\n✗ Application interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
