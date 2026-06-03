"""Generate bilingual public commentary drafts for KazaALKIS."""

import json
import os
from datetime import datetime

import requests


class CommentaryGenerator:
    """Generate short English/Greek commentary from public calendar data."""

    def __init__(self, provider: str = "template", model: str = "",
                 ollama_url: str = "http://127.0.0.1:11434"):
        self.provider = provider or "template"
        self.model = model or "llama3.1"
        self.ollama_url = ollama_url.rstrip("/")

    def generate(self, today_data):
        """Generate a reviewable bilingual commentary draft."""
        prompt = self._build_prompt(today_data)
        if self.provider == "ollama":
            text = self._generate_ollama(prompt)
            return self._parse_or_wrap(text, "ollama")
        if self.provider == "openai_compatible":
            text = self._generate_openai_compatible(prompt)
            return self._parse_or_wrap(text, "openai_compatible")
        return self._template_commentary(today_data)

    def _build_prompt(self, today_data):
        public_context = {
            "date": today_data.get("date"),
            "namedays": today_data.get("namedays", []),
            "holidays": today_data.get("holidays", []),
            "quotes": today_data.get("quotes", []),
            "historical_events": today_data.get("historical_events", []),
            "custom_notes": today_data.get("custom_notes", []),
        }
        return (
            "Create a short public bilingual commentary for a Greek daily calendar. "
            "Return only JSON with keys english and greek. Do not mention official "
            "Kazamias. Do not invent names, holidays, or historical facts. Keep each "
            "language to 2-3 warm sentences.\n\n"
            f"Calendar data:\n{json.dumps(public_context, ensure_ascii=False)}"
        )

    def _generate_ollama(self, prompt):
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
            timeout=60,
        )
        response.raise_for_status()
        return response.json().get("response", "")

    def _generate_openai_compatible(self, prompt):
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_COMPATIBLE_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        if not api_key:
            raise ValueError("OPENAI_API_KEY or OPENAI_COMPATIBLE_API_KEY is required")
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.6,
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def _parse_or_wrap(self, text, provider):
        try:
            parsed = json.loads(text)
            english = str(parsed.get("english", "")).strip()
            greek = str(parsed.get("greek", "")).strip()
        except json.JSONDecodeError:
            english = text.strip()
            greek = ""
        return {
            "english": english,
            "greek": greek,
            "provider": provider,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "review_required": True,
        }

    def _template_commentary(self, today_data):
        date = today_data.get("date", "today")
        namedays = today_data.get("namedays", [])
        holidays = today_data.get("holidays", [])
        names = []
        for item in namedays:
            names.extend([name.strip() for name in item.get("names", "").split(",") if name.strip()])
        name_text = ", ".join(names[:4]) if names else "the names celebrated today"
        holiday_text = holidays[0]["name"] if holidays else "the rhythm of the Greek calendar"
        return {
            "english": (
                f"For {date}, KazaALKIS marks {name_text} with a warm Χρόνια πολλά. "
                f"Today’s note follows {holiday_text} and keeps the calendar simple, public, and human."
            ),
            "greek": (
                f"Για τις {date}, το KazaALKIS θυμάται {name_text} με ένα ζεστό Χρόνια πολλά. "
                f"Το σημερινό σημείωμα ακολουθεί το ελληνικό ημερολόγιο με απλότητα και σεβασμό."
            ),
            "provider": "template",
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "review_required": True,
        }
