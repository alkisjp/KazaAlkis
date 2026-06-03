"""
Message Builder Module
Composes daily Kazamias messages in various tones and languages
"""

from datetime import datetime
from typing import Dict, List
try:
    from .cultural_reflection import build_cultural_reflection
    from .sky_note import build_sky_note
except ImportError:
    from cultural_reflection import build_cultural_reflection
    from sky_note import build_sky_note

class MessageBuilder:
    """Build daily Kazamias messages"""

    GREETINGS_EN = {
        'formal': 'Good morning',
        'friendly': 'Good day',
        'traditional': 'May God bless your day',
        'humorous': 'Rise and shine!'
    }

    GREETINGS_GR = {
        'formal': 'Καλημέρα',
        'friendly': 'Καλημέρα',
        'traditional': 'Καλημέρα και Καλή Χρονιά',
        'humorous': 'Ξύπνα και λάμψε!'
    }

    NAMEDAY_INTRO_EN = {
        'formal': 'Today\'s commemorated saints:',
        'friendly': 'Today we celebrate:',
        'traditional': 'This day is sacred to:',
        'humorous': 'Today\'s lucky name day people:'
    }

    NAMEDAY_INTRO_GR = {
        'formal': 'Σήμερα εορτάζουν:',
        'friendly': 'Σήμερα γιορτάζουμε:',
        'traditional': 'Η ημέρα αυτή αφιερώνεται σε:',
        'humorous': 'Σήμερα είναι η μέρα των ευτυχών:'
    }

    QUOTE_INTRO_EN = {
        'formal': 'Thought for today:',
        'friendly': 'Today\'s wisdom:',
        'traditional': 'A word from the ancient sages:',
        'humorous': 'Today\'s random wisdom:'
    }

    QUOTE_INTRO_GR = {
        'formal': 'Σκέψη της ημέρας:',
        'friendly': 'Σοφία της ημέρας:',
        'traditional': 'Λόγος από τους αρχαίους σοφούς:',
        'humorous': 'Αυτή η σκέψη είναι για σας:'
    }

    def __init__(self, language: str = 'en', tone: str = 'friendly'):
        """Initialize message builder"""
        self.language = language
        self.tone = tone

    def build_daily_message(self, today_data: Dict) -> str:
        """Build complete daily message"""
        lines = []

        lines.append(self._build_header(today_data.get('date')))
        lines.append("")
        lines.append(self._calendar_label())
        lines.append("")

        if today_data.get('namedays'):
            lines.append(self._build_namedays_section(today_data['namedays']))
            lines.append("")

        if today_data.get('holidays'):
            lines.append(self._build_holiday_section(today_data['holidays']))
            lines.append("")

        if today_data.get('quotes'):
            lines.append(self._build_quote_section(today_data['quotes']))
            lines.append("")

        if today_data.get('fasting'):
            lines.append(self._build_fasting_section(today_data['fasting']))
            lines.append("")

        reflection = build_cultural_reflection(today_data)
        if reflection:
            lines.append(self._build_cultural_reflection_section(reflection))
            lines.append("")

        sky_note = build_sky_note(today_data.get('date'))
        if sky_note:
            lines.append(self._build_sky_note_section(sky_note))
            lines.append("")

        if today_data.get('historical_events'):
            lines.append(self._build_historical_section(today_data['historical_events']))
            lines.append("")

        if today_data.get('parallel_traditions'):
            lines.append(self._build_parallel_traditions_section(today_data['parallel_traditions']))
            lines.append("")

        if today_data.get('custom_notes'):
            lines.append(self._build_custom_notes_section(today_data['custom_notes']))
            lines.append("")

        context = self._build_context_section(today_data)
        if context:
            lines.append(context)
            lines.append("")

        lines.append(self._build_closing())

        return "\n".join(lines)

    def _build_header(self, date_str: str = None) -> str:
        """Build message header"""
        today = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.now()
        date_str = today.strftime('%A, %d %B %Y')

        if self.language == 'bilingual':
            en_greeting = self.GREETINGS_EN[self.tone]
            gr_greeting = self.GREETINGS_GR[self.tone]
            greek_months = {
                1: 'Ιανουαρίου', 2: 'Φεβρουαρίου', 3: 'Μαρτίου',
                4: 'Απριλίου', 5: 'Μαΐου', 6: 'Ιουνίου',
                7: 'Ιουλίου', 8: 'Αυγούστου', 9: 'Σεπτεμβρίου',
                10: 'Οκτωβρίου', 11: 'Νοεμβρίου', 12: 'Δεκεμβρίου'
            }
            gr_date_str = f'{today.day} {greek_months[today.month]} {today.year}'

            return f"{en_greeting}, {date_str}\n{gr_greeting}, {gr_date_str}\n{'='*40}"
        elif self.language == 'gr':
            greek_months = {
                1: 'Ιανουαρίου', 2: 'Φεβρουαρίου', 3: 'Μαρτίου',
                4: 'Απριλίου', 5: 'Μαΐου', 6: 'Ιουνίου',
                7: 'Ιουλίου', 8: 'Αυγούστου', 9: 'Σεπτεμβρίου',
                10: 'Οκτωβρίου', 11: 'Νοεμβρίου', 12: 'Δεκεμβρίου'
            }
            gr_date_str = f'{today.day} {greek_months[today.month]} {today.year}'

            greeting = self.GREETINGS_GR[self.tone]
            return f"{greeting}, {gr_date_str}\n{'='*40}"
        else:
            greeting = self.GREETINGS_EN[self.tone]
            return f"{greeting}, {date_str}\n{'='*40}"

    def _calendar_label(self):
        """Avoid implying affiliation with a licensed Kazamias publication."""
        if self.language == "en":
            return "Daily Greek calendar and proverb"
        if self.language == "gr":
            return "Ημερήσιο ελληνικό ημερολόγιο"
        return "Daily Greek calendar and proverb / Ημερήσιο ελληνικό ημερολόγιο"

    def _build_namedays_section(self, namedays: List[Dict]) -> str:
        """Build name days section"""
        lines = []

        if self.language == 'bilingual':
            lines.append(f"{self.NAMEDAY_INTRO_EN[self.tone]} / {self.NAMEDAY_INTRO_GR[self.tone]}")
        elif self.language == 'gr':
            lines.append(self.NAMEDAY_INTRO_GR[self.tone])
        else:
            lines.append(self.NAMEDAY_INTRO_EN[self.tone])

        for nameday in namedays:
            saint = nameday.get('saint', 'Unknown Saint')
            names = nameday.get('names', '').split(', ')
            names_str = ", ".join(names[:8])
            title = "Name-day calendar entry" if saint in (
                "Greek nameday seed",
                "Reviewed GetGreece calendar entry",
            ) else saint

            if self.language == 'bilingual':
                lines.append(f"  • {title}")
                lines.append(f"    Names: {names_str}")
            elif self.language == 'gr':
                title = "Καταχώριση εορτολογίου" if saint in (
                    "Greek nameday seed",
                    "Reviewed GetGreece calendar entry",
                ) else saint
                lines.append(f"  • {title}")
                lines.append(f"    Ονόματα: {names_str}")
            else:
                lines.append(f"  • {title}")
                lines.append(f"    Names: {names_str}")

        if self.language == 'bilingual':
            lines.append("\n✨ Χρόνια πολλά και καλή υγεία! / Many years and good health! ✨")
        elif self.language == 'gr':
            lines.append("\n✨ Χρόνια πολλά και καλή υγεία! ✨")
        else:
            lines.append("\n✨ Many years and good health! ✨")

        return "\n".join(lines)

    def _build_holiday_section(self, holidays: List[Dict]) -> str:
        """Build holiday section"""
        lines = []

        header_en = "🇬🇷 Important Holiday"
        header_gr = "🇬🇷 Σημαντική Εορτή"

        if self.language == 'bilingual':
            lines.append(f"{header_en} / {header_gr}")
        elif self.language == 'gr':
            lines.append(header_gr)
        else:
            lines.append(header_en)

        for holiday in holidays:
            name = holiday.get('name', 'Holiday')
            holiday_type = holiday.get('type', 'Observance')

            lines.append(f"  {name} ({holiday_type})")

        return "\n".join(lines)

    def _build_quote_section(self, quotes: List[Dict]) -> str:
        """Build quote section"""
        lines = []

        if self.language == 'bilingual':
            lines.append(f"{self.QUOTE_INTRO_EN[self.tone]} / {self.QUOTE_INTRO_GR[self.tone]}")
        elif self.language == 'gr':
            lines.append(self.QUOTE_INTRO_GR[self.tone])
        else:
            lines.append(self.QUOTE_INTRO_EN[self.tone])

        quote = quotes[0] if quotes else None
        if quote:
            quote_text = quote.get('quote', '')
            author = quote.get('author', 'Anonymous')
            lines.append(f"\n  \"{quote_text}\"")
            lines.append(f"  — {author}")

        return "\n".join(lines)

    def _build_fasting_section(self, fasting: Dict) -> str:
        """Build fasting note section"""
        lines = []

        fasting_name = fasting.get('name', 'Fasting Period')
        fasting_type = fasting.get('fasting_type', 'Observance')
        description = fasting.get('description') or ''

        icon = "✝️"

        if self.language == 'bilingual':
            lines.append(f"{icon} Fasting Period / Περίοδος Νηστείας")
            lines.append(
                f"  {fasting_name} ({fasting_type}) / "
                f"{self._translate_fasting_name(fasting_name)} ({self._translate_fasting_type(fasting_type)})"
            )
            if description:
                lines.append(f"  {description}")
        elif self.language == 'gr':
            lines.append(f"{icon} Περίοδος Νηστείας")
            lines.append(f"  {self._translate_fasting_name(fasting_name)} ({self._translate_fasting_type(fasting_type)})")
            if description:
                lines.append(f"  {self._translate_fasting_description(description)}")
        else:
            lines.append(f"{icon} Fasting Period")
            lines.append(f"  {fasting_name} ({fasting_type})")
            if description:
                lines.append(f"  {description}")

        return "\n".join(lines)

    def _build_context_section(self, today_data: Dict) -> str:
        """Add helpful context when reviewed calendar data is sparse."""
        has_namedays = bool(today_data.get('namedays'))
        has_quotes = bool(today_data.get('quotes'))
        has_events = bool(today_data.get('historical_events'))
        has_holidays = bool(today_data.get('holidays'))
        has_traditions = bool(today_data.get('parallel_traditions'))
        has_reflection = bool(build_cultural_reflection(today_data))
        fasting = today_data.get('fasting')

        if has_namedays and has_quotes and (has_events or has_holidays or has_traditions):
            return ""

        en_lines = ["Today’s Context"]
        gr_lines = ["Σημερινό πλαίσιο"]

        if not has_namedays:
            en_lines.append("- No reviewed name-day entry is available yet for this date.")
            gr_lines.append("- Δεν υπάρχει ακόμη ελεγμένη καταχώριση εορτολογίου για αυτή την ημερομηνία.")
        if not has_traditions and not has_reflection:
            en_lines.append("- A reviewed Orthodox/ancient Greek parallel tradition has not been selected yet.")
            gr_lines.append("- Δεν έχει επιλεγεί ακόμη ελεγμένη παράλληλη ορθόδοξη και αρχαιοελληνική παράδοση.")

        if len(en_lines) == 1 and len(gr_lines) == 1:
            return ""

        if self.language == "en":
            return "\n".join(en_lines)
        if self.language == "gr":
            return "\n".join(gr_lines)
        return "\n".join(en_lines + [""] + gr_lines)

    def _translate_fasting_description(self, description: str) -> str:
        """Translate known bundled fasting descriptions without inventing facts."""
        translations = {
            "The 40-day period of fasting before Easter":
                "Η περίοδος νηστείας των 40 ημερών πριν από το Πάσχα",
            "Two-week period of fasting before the Dormition of the Virgin Mary":
                "Δεκαπενθήμερη περίοδος νηστείας πριν από την Κοίμηση της Θεοτόκου",
            "Fasting period before Christmas, traditionally starting on the feast of St. Philip the Apostle":
                "Περίοδος νηστείας πριν από τα Χριστούγεννα, με παραδοσιακή έναρξη στη μνήμη του Αποστόλου Φιλίππου",
            "Period of fasting between Pentecost and the feast of St. Peter and St. Paul":
                "Περίοδος νηστείας ανάμεσα στην Πεντηκοστή και την εορτή των Αγίων Πέτρου και Παύλου",
            "Traditional Orthodox fasting on Wednesdays and Fridays throughout the year":
                "Παραδοσιακή ορθόδοξη νηστεία κάθε Τετάρτη και Παρασκευή μέσα στο έτος",
        }
        return translations.get(description, description)

    def _translate_fasting_name(self, name: str) -> str:
        """Translate known bundled fasting names."""
        translations = {
            "Great Lent (Sarakosti)": "Μεγάλη Τεσσαρακοστή",
            "Dormition Fast (Dekapentaugoustou)": "Νηστεία Δεκαπενταύγουστου",
            "Christmas Fast (Nisteia Hristougennon)": "Νηστεία Χριστουγέννων",
            "Apostles' Fast": "Νηστεία των Αγίων Αποστόλων",
            "Apostles Fast": "Νηστεία των Αγίων Αποστόλων",
            "Wednesday and Friday Fasts": "Νηστεία Τετάρτης και Παρασκευής",
        }
        return translations.get(name, name)

    def _translate_fasting_type(self, fasting_type: str) -> str:
        """Translate known fasting category labels."""
        translations = {
            "major_fast": "μεγάλη νηστεία",
            "minor_fast": "μικρή νηστεία",
            "weekly": "εβδομαδιαία νηστεία",
            "observance": "τήρηση",
        }
        return translations.get(str(fasting_type).lower(), fasting_type)

    def _build_historical_section(self, events: List[Dict]) -> str:
        """Build an on-this-day section."""
        header = "On This Day / Σαν σήμερα" if self.language == "bilingual" else (
            "Σαν σήμερα" if self.language == "gr" else "On This Day"
        )
        return "\n".join([header] + [f"  {item['event']}" for item in events[:3]])

    def _build_cultural_reflection_section(self, reflection: Dict) -> str:
        """Build meaningful Orthodox/ancient Greek cultural commentary."""
        if self.language == "en":
            return "Cultural Meaning\n  " + reflection["english"]
        if self.language == "gr":
            return "Πολιτιστικό νόημα\n  " + reflection["greek"]
        return "\n".join([
            "Cultural Meaning / Πολιτιστικό νόημα",
            f"  {reflection['english']}",
            "",
            f"  {reflection['greek']}",
        ])

    def _build_sky_note_section(self, sky_note: Dict) -> str:
        """Build astrology and moon phase section."""
        if self.language == "en":
            return "Astrology & Moon\n  " + sky_note["english"]
        if self.language == "gr":
            return "Αστρολογία & Σελήνη\n  " + sky_note["greek"]
        return "\n".join([
            "Astrology & Moon / Αστρολογία & Σελήνη",
            f"  {sky_note['english']}",
            "",
            f"  {sky_note['greek']}",
        ])

    def _build_parallel_traditions_section(self, traditions: List[Dict]) -> str:
        """Build Orthodox and ancient Greek cultural parallel notes."""
        header = "Parallel Traditions / Παράλληλες Παραδόσεις" if self.language == "bilingual" else (
            "Παράλληλες Παραδόσεις" if self.language == "gr" else "Parallel Traditions"
        )
        lines = [header]
        for item in traditions[:2]:
            region = item.get("region")
            orthodox_title = item.get("orthodox_title") or "Orthodox tradition"
            orthodox_description = item.get("orthodox_description") or ""
            ancient_title = item.get("ancient_title") or "Ancient Greek parallel"
            ancient_description = item.get("ancient_description") or ""
            relationship = item.get("relationship_note") or (
                "This is presented as a cultural comparison, not as proof of direct continuity."
            )

            if region:
                lines.append(f"  Region / Περιοχή: {region}")
            lines.append(f"  Orthodox / Ορθόδοξο: {orthodox_title}")
            if orthodox_description:
                lines.append(f"    {orthodox_description}")
            lines.append(f"  Ancient Greek parallel / Αρχαιοελληνικός παραλληλισμός: {ancient_title}")
            if ancient_description:
                lines.append(f"    {ancient_description}")
            lines.append(f"  Note / Σημείωση: {relationship}")
        return "\n".join(lines)

    def _build_custom_notes_section(self, notes: List[Dict]) -> str:
        """Build user-written comments."""
        header = "Calendar Note / Σημείωμα" if self.language == "bilingual" else (
            "Σημείωμα" if self.language == "gr" else "Calendar Note"
        )
        return "\n".join([header] + [f"  {item['note']}" for item in notes[:3]])

    def _build_closing(self) -> str:
        """Build message closing"""
        if self.language == 'bilingual':
            return "="*40 + "\n✝️ Blessings from KazaALKIS / Ευλογίες από το KazaALKIS ✝️"
        elif self.language == 'gr':
            return f"{'='*40}\n✝️ Ευλογίες από το KazaALKIS ✝️"
        else:
            return f"{'='*40}\n✝️ Blessings from KazaALKIS ✝️"

if __name__ == "__main__":
    test_data = {
        'date': '2026-04-23',
        'namedays': [{'saint': 'St. George', 'names': 'George, Giorgos, Giorgio'}],
        'quotes': [{'quote': 'Courage is the conquest of fear.', 'author': 'Anonymous', 'language': 'en'}],
        'holidays': [{'name': 'St. George Day', 'type': 'religious'}],
        'fasting': None
    }

    for language in ['en', 'gr', 'bilingual']:
        for tone in ['friendly', 'formal', 'traditional', 'humorous']:
            builder = MessageBuilder(language=language, tone=tone)
            msg = builder.build_daily_message(test_data)
            print(f"\n{'='*60}\nLanguage: {language}, Tone: {tone}\n{'='*60}\n{msg}")
