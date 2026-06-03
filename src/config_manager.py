"""
Configuration Manager for KazaALKIS
Handles user setup and configuration storage
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv, set_key
try:
    from .path_manager import PROJECT_ROOT, get_paths
except ImportError:
    from path_manager import PROJECT_ROOT, get_paths

class ConfigurationManager:
    """Manage KazaALKIS configuration"""

    def __init__(self, config_dir: str = None):
        """Initialize configuration manager"""
        if config_dir is None:
            config_dir = PROJECT_ROOT / "config"
        else:
            config_dir = Path(config_dir)

        config_dir.mkdir(parents=True, exist_ok=True)

        self.config_dir = config_dir
        self.config_file = config_dir / "kazaalkis_config.json"
        self.env_file = config_dir / ".env"

        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from JSON file"""
        defaults = self._default_config()
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                return self._upgrade_loaded_config(defaults | loaded)
            except Exception as e:
                print(f"Error loading config: {e}")

        return defaults

    def _upgrade_loaded_config(self, config: dict) -> dict:
        """Apply non-destructive config migrations."""
        old_project_db = str(PROJECT_ROOT / 'data' / 'kazaalkis.db')
        new_runtime_db = self._default_config()['database_path']
        if config.get('database_path') == old_project_db:
            config['database_path'] = new_runtime_db
        return config

    def _default_config(self) -> dict:
        """Return default configuration"""
        paths = get_paths()
        return {
            'project_name': 'KazaALKIS',
            'version': '1.1.0',
            'ai_root': str(paths.ai_root),
            'database_path': str(paths.app_db_path),
            'source_data_path': '',
            'whatsapp_provider': 'manual',
            'contacts_file': str(PROJECT_ROOT / 'data' / 'contacts.json'),
            'logs_path': str(paths.app_log_dir),
            'outputs_path': str(paths.app_output_dir),
            'tmp_path': str(paths.app_tmp_dir),
            'sending_time': '08:00',
            'language': 'bilingual',
            'message_tone': 'friendly',
            'timezone': 'Europe/Athens',
            'auto_schedule': False,
            'schedule_frequency': 'daily',
            'log_retention_days': 90,
            'enable_logging': True,
            'privacy_mask_contacts': True
            ,
            'commentary_provider': 'template',
            'commentary_model': 'llama3.1',
            'ollama_url': 'http://127.0.0.1:11434'
        }

    def _save_config(self):
        """Save configuration to JSON file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"✓ Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            print(f"✗ Error saving config: {e}")
            return False

    def setup_first_time(self):
        """Interactive first-time setup"""
        print("\n" + "="*60)
        print("KazaALKIS - First Time Setup")
        print("="*60 + "\n")

        db_path = input("Enter open-data calendar source path (leave blank to skip): ").strip()
        if db_path:
            self.config['source_data_path'] = db_path

        print("\nWhatsApp Provider Options:")
        print("1. WhatsApp Business Cloud API (Recommended)")
        print("2. Twilio WhatsApp API")
        print("3. Manual message copy/paste")

        provider_choice = input("Select provider (1-3) [default: 1]: ").strip() or "1"
        providers = {
            '1': 'whatsapp_business_cloud',
            '2': 'twilio',
            '3': 'manual'
        }
        self.config['whatsapp_provider'] = providers.get(provider_choice, 'whatsapp_business_cloud')

        print("\nPreferred Language:")
        print("1. English")
        print("2. Greek (Ελληνικά)")
        print("3. Bilingual")

        lang_choice = input("Select language (1-3) [default: 3]: ").strip() or "3"
        languages = {
            '1': 'en',
            '2': 'gr',
            '3': 'bilingual'
        }
        self.config['language'] = languages.get(lang_choice, 'bilingual')

        print("\nMessage Tone:")
        print("1. Formal")
        print("2. Friendly")
        print("3. Traditional")
        print("4. Humorous")

        tone_choice = input("Select tone (1-4) [default: 2]: ").strip() or "2"
        tones = {
            '1': 'formal',
            '2': 'friendly',
            '3': 'traditional',
            '4': 'humorous'
        }
        self.config['message_tone'] = tones.get(tone_choice, 'friendly')

        sending_time = input("Preferred sending time (HH:MM format) [default: 08:00]: ").strip() or "08:00"
        self.config['sending_time'] = sending_time

        auto_schedule = input("Enable daily auto-schedule? (y/n) [default: n]: ").strip().lower() == 'y'
        self.config['auto_schedule'] = auto_schedule

        self._save_config()
        print("\n✓ Setup completed! Configuration saved.\n")

    def setup_whatsapp_api(self, provider: str = None):
        """Setup WhatsApp API credentials"""
        if provider is None:
            provider = self.config.get('whatsapp_provider')

        print(f"\n{'='*60}")
        print(f"WhatsApp API Setup - {provider}")
        print(f"{'='*60}\n")

        if provider == 'whatsapp_business_cloud':
            print("WhatsApp Business Cloud API Setup:")
            print("Get your credentials from: https://developers.facebook.com/\n")

            access_token = input("Enter your WhatsApp Business Access Token: ").strip()
            phone_number_id = input("Enter your Phone Number ID: ").strip()
            business_account_id = input("Enter your Business Account ID: ").strip()

            self._set_env_variable('WHATSAPP_ACCESS_TOKEN', access_token)
            self._set_env_variable('WHATSAPP_PHONE_NUMBER_ID', phone_number_id)
            self._set_env_variable('WHATSAPP_BUSINESS_ACCOUNT_ID', business_account_id)

            print("\n✓ WhatsApp Business Cloud credentials saved to .env")

        elif provider == 'twilio':
            print("Twilio WhatsApp API Setup:")
            print("Get your credentials from: https://www.twilio.com/\n")

            account_sid = input("Enter your Twilio Account SID: ").strip()
            auth_token = input("Enter your Twilio Auth Token: ").strip()
            twilio_phone = input("Enter your Twilio WhatsApp Number: ").strip()

            self._set_env_variable('TWILIO_ACCOUNT_SID', account_sid)
            self._set_env_variable('TWILIO_AUTH_TOKEN', auth_token)
            self._set_env_variable('TWILIO_WHATSAPP_NUMBER', twilio_phone)

            print("\n✓ Twilio credentials saved to .env")

    def load_environment(self):
        """Load the application-specific environment file."""
        load_dotenv(str(self.env_file))

    def _set_env_variable(self, key: str, value: str):
        """Set environment variable in .env file"""
        try:
            if not self.env_file.exists():
                self.env_file.touch()

            set_key(str(self.env_file), key, value)
        except Exception as e:
            print(f"Error setting environment variable: {e}")

    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)

    def set(self, key: str, value):
        """Set configuration value"""
        self.config[key] = value
        return self._save_config()

    def get_all(self) -> dict:
        """Get all configuration"""
        return self.config.copy()

    def validate_setup(self) -> tuple:
        """Validate that configuration is complete"""
        errors = []

        if not self.config.get('whatsapp_provider'):
            errors.append("WhatsApp provider not configured")

        if self.config.get('whatsapp_provider') != 'manual':
            load_dotenv(str(self.env_file))

            if self.config.get('whatsapp_provider') == 'whatsapp_business_cloud':
                if not os.getenv('WHATSAPP_ACCESS_TOKEN'):
                    errors.append("WhatsApp Business Cloud API credentials missing")

            elif self.config.get('whatsapp_provider') == 'twilio':
                if not os.getenv('TWILIO_ACCOUNT_SID'):
                    errors.append("Twilio API credentials missing")

        if not self.config.get('database_path'):
            errors.append("Database path not configured")

        if errors:
            return False, "\n".join(f"  ✗ {e}" for e in errors)

        return True, "✓ Configuration is complete and valid"

    def get_delivery_status(self) -> str:
        """Return a concise operator-facing delivery setup status."""
        provider = self.config.get('whatsapp_provider', 'manual')
        if provider == 'manual':
            return "Manual TXT export mode active. Live WhatsApp sending is not configured."
        is_valid, message = self.validate_setup()
        if is_valid:
            return f"Live WhatsApp delivery configured: {provider}"
        return f"Live WhatsApp delivery is not ready: {message.replace(chr(10), ' ')}"

    def print_config(self):
        """Print current configuration"""
        print("\n" + "="*60)
        print("Current KazaALKIS Configuration")
        print("="*60)

        for key, value in self.config.items():
            if 'path' in key.lower() or 'token' in key.lower():
                if value and len(str(value)) > 20:
                    value = str(value)[:15] + "..."

            print(f"  {key:<25} : {value}")

        print("="*60 + "\n")

if __name__ == "__main__":
    config = ConfigurationManager()
    config.setup_first_time()
    choice = input("\nSetup WhatsApp API now? (y/n): ").strip().lower() == 'y'
    if choice:
        config.setup_whatsapp_api()
    is_valid, message = config.validate_setup()
    print(f"\nConfiguration Validation:\n{message}")
    config.print_config()
