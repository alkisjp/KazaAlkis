"""Publish a privacy-safe daily calendar payload for the static website."""

import json
from datetime import datetime
from pathlib import Path

try:
    from .message_builder import MessageBuilder
except ImportError:
    from message_builder import MessageBuilder


class WebsitePublisher:
    """Write public calendar data only; never export contacts or delivery logs."""

    def __init__(self, db, website_root: str = None):
        self.db = db
        self.website_root = Path(website_root or Path(__file__).resolve().parent.parent)
        self.output_dir = self.website_root / "public_notifications"
        self.history_dir = self.output_dir / "history"

    def build_payload(self, date_str: str = None, language: str = "bilingual",
                      tone: str = "friendly", commentary=None):
        """Build a static-site payload from public calendar fields."""
        data = self.db.get_today_data(date_str)
        if data is None:
            raise ValueError("Unable to retrieve calendar data")
        message = MessageBuilder(language=language, tone=tone).build_daily_message(data)
        return {
            "date": data["date"],
            "title": "Ημερήσιο ελληνικό ημερολόγιο",
            "message": message,
            "namedays": data.get("namedays", []),
            "holidays": data.get("holidays", []),
            "quotes": data.get("quotes", []),
            "historical_events": data.get("historical_events", []),
            "custom_notes": data.get("custom_notes", []),
            "commentary": commentary,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "disclaimer": "KazaALKIS is not an official Kazamias publication.",
        }

    def publish(self, date_str: str = None, language: str = "bilingual",
                tone: str = "friendly", commentary=None):
        """Write latest and dated JSON files for GitHub Pages publication."""
        payload = self.build_payload(date_str, language, tone, commentary)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        latest_file = self.output_dir / "latest.json"
        history_file = self.history_dir / f"{payload['date']}.json"
        content = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
        latest_file.write_text(content, encoding="utf-8")
        history_file.write_text(content, encoding="utf-8")
        return latest_file, history_file
