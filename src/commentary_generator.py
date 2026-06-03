"""Generate bilingual public commentary drafts for KazaALKIS."""

import json
import os
from datetime import datetime

import requests
try:
    from .cultural_reflection import build_cultural_reflection
    from .sky_note import build_sky_note
except ImportError:
    from cultural_reflection import build_cultural_reflection
    from sky_note import build_sky_note


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
            "fasting": today_data.get("fasting"),
            "quotes": today_data.get("quotes", []),
            "historical_events": today_data.get("historical_events", []),
            "parallel_traditions": today_data.get("parallel_traditions", []),
            "sky_note": build_sky_note(today_data.get("date")),
            "custom_notes": today_data.get("custom_notes", []),
        }
        return (
            "Create a short public bilingual commentary for a Greek daily calendar. "
            "Return only JSON with keys english and greek. Do not mention official "
            "Kazamias. Do not invent names, holidays, or historical facts. Keep each "
            "language to 2-3 warm sentences. If parallel_traditions are provided, "
            "compare Orthodox and ancient Greek practices carefully as cultural parallels; "
            "do not claim direct continuity unless the data explicitly says so.\n\n"
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
        fasting = today_data.get("fasting")
        quotes = today_data.get("quotes", [])
        events = today_data.get("historical_events", [])
        traditions = today_data.get("parallel_traditions", [])
        english_date, greek_date = self._format_dates(date)
        reflection = build_cultural_reflection(today_data)
        sky_note = build_sky_note(date)
        if not namedays and not holidays and not fasting and not quotes and not events and not traditions:
            return self._empty_day_commentary(english_date, greek_date)
        english_names, greek_names = self._name_phrases(namedays)
        english_holiday, greek_holiday = self._holiday_phrases(holidays)
        english_fasting, greek_fasting = self._fasting_phrases(fasting)
        english_quote, greek_quote = self._quote_phrases(quotes)
        english_event, greek_event = self._event_phrases(events)
        english_tradition, greek_tradition = self._tradition_phrases(traditions)
        english_reflection = reflection["english"] if reflection else ""
        greek_reflection = reflection["greek"] if reflection else ""
        english_sky = sky_note["english"] if sky_note else ""
        greek_sky = sky_note["greek"] if sky_note else ""
        return {
            "english": " ".join([
                f"For {english_date}, {english_names}",
                f"{english_holiday}",
                f"{english_fasting}",
                f"{english_quote}",
                f"{english_event}",
                f"{english_tradition}",
                f"{english_reflection}",
                f"{english_sky}",
            ]).strip(),
            "greek": " ".join([
                f"Για τις {greek_date}, {greek_names}",
                f"{greek_holiday}",
                f"{greek_fasting}",
                f"{greek_quote}",
                f"{greek_event}",
                f"{greek_tradition}",
                f"{greek_reflection}",
                f"{greek_sky}",
            ]).strip(),
            "provider": "template",
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "review_required": True,
        }

    def _empty_day_commentary(self, english_date, greek_date):
        return {
            "english": (
                f"For {english_date}, the local KazaALKIS database has no reviewed public calendar "
                "records ready for publication yet. Today’s note stays intentionally modest: a quiet "
                "reminder that open cultural data is only published here after review."
            ),
            "greek": (
                f"Για τις {greek_date}, η τοπική βάση του KazaALKIS δεν έχει ακόμη ελεγμένες δημόσιες "
                "καταχωρίσεις έτοιμες για δημοσίευση. Το σημερινό σχόλιο μένει επίτηδες λιτό: μια "
                "ήρεμη υπενθύμιση ότι τα πολιτιστικά δεδομένα δημοσιεύονται εδώ μόνο μετά από έλεγχο."
            ),
            "provider": "template",
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "review_required": True,
        }

    def _format_dates(self, date_text):
        try:
            date = datetime.strptime(date_text, "%Y-%m-%d")
        except (TypeError, ValueError):
            return str(date_text or "today"), str(date_text or "σήμερα")
        english = date.strftime("%A, %d %B %Y")
        greek_months = {
            1: "Ιανουαρίου", 2: "Φεβρουαρίου", 3: "Μαρτίου",
            4: "Απριλίου", 5: "Μαΐου", 6: "Ιουνίου",
            7: "Ιουλίου", 8: "Αυγούστου", 9: "Σεπτεμβρίου",
            10: "Οκτωβρίου", 11: "Νοεμβρίου", 12: "Δεκεμβρίου",
        }
        greek = f"{date.day} {greek_months[date.month]} {date.year}"
        return english, greek

    def _extract_names(self, namedays):
        names = []
        for item in namedays:
            raw = item.get("names") or item.get("name") or ""
            names.extend([name.strip() for name in raw.split(",") if name.strip()])
        return names

    def _name_phrases(self, namedays):
        names = self._extract_names(namedays)
        if not names:
            return (
                "there is no reviewed name-day entry in the local database yet.",
                "δεν υπάρχει ακόμη ελεγμένη καταχώριση εορτολογίου στην τοπική βάση.",
            )
        listed = ", ".join(names[:5])
        return (
            f"KazaALKIS sends warm name-day wishes to {listed}.",
            f"το KazaALKIS στέλνει ζεστές ευχές για τη γιορτή των {listed}.",
        )

    def _holiday_phrases(self, holidays):
        if not holidays:
            return (
                "No public holiday is recorded for today in the reviewed sources.",
                "Δεν έχει καταγραφεί δημόσια εορτή για σήμερα στις ελεγμένες πηγές.",
            )
        holiday = holidays[0].get("name") or holidays[0].get("title") or "today's public holiday"
        return (
            f"The day also notes {holiday} from the public calendar data.",
            f"Η ημέρα σημειώνει επίσης: {holiday}, σύμφωνα με τα δημόσια ημερολογιακά δεδομένα.",
        )

    def _fasting_phrases(self, fasting):
        if not fasting:
            return ("", "")
        name = fasting.get("name") or "an Orthodox fasting period"
        description = fasting.get("description") or ""
        return (
            f"The Orthodox calendar also places today within {name}. {description}".strip(),
            f"Το ορθόδοξο ημερολόγιο τοποθετεί επίσης τη σημερινή ημέρα στην περίοδο: {name}. {description}".strip(),
        )

    def _quote_phrases(self, quotes):
        if not quotes:
            return (
                "A reviewed public-domain proverb or quote has not been selected yet.",
                "Δεν έχει επιλεγεί ακόμη ελεγμένο γνωμικό ή απόφθεγμα δημόσιου τομέα.",
            )
        quote = quotes[0].get("quote") or quotes[0].get("description") or ""
        author = quotes[0].get("author") or quotes[0].get("title") or "unknown source"
        return (
            f"The day’s thought is “{quote}” attributed to {author}.",
            f"Το γνωμικό της ημέρας είναι «{quote}», με απόδοση σε {author}.",
        )

    def _event_phrases(self, events):
        if not events:
            return (
                "No Greek-related historical item has been selected for publication.",
                "Δεν έχει επιλεγεί ακόμη ελληνικό ιστορικό γεγονός για δημοσίευση.",
            )
        event = events[0].get("event") or events[0].get("title") or events[0].get("description")
        return (
            f"For “on this day,” the selected note is: {event}",
            f"Στο «Σαν σήμερα», η επιλεγμένη αναφορά είναι: {event}",
        )

    def _tradition_phrases(self, traditions):
        if not traditions:
            return (
                "No reviewed Orthodox and ancient Greek parallel tradition has been selected yet.",
                "Δεν έχει επιλεγεί ακόμη ελεγμένη παράλληλη ορθόδοξη και αρχαιοελληνική παράδοση.",
            )
        item = traditions[0]
        orthodox_title = item.get("orthodox_title") or "the Orthodox tradition"
        ancient_title = item.get("ancient_title") or "an ancient Greek parallel"
        region = item.get("region")
        relationship = item.get("relationship_note") or (
            "The comparison is cultural and thematic, not proof of direct continuity."
        )
        region_en = f" in {region}" if region else ""
        region_gr = f" στην περιοχή {region}" if region else ""
        return (
            f"The cultural note compares {orthodox_title}{region_en} with {ancient_title}. {relationship}",
            f"Το πολιτιστικό σημείωμα συγκρίνει το {orthodox_title}{region_gr} με το {ancient_title}. {relationship}",
        )
