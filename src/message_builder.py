"""
Message Builder Module
Composes daily Kazamias messages in various tones and languages
"""

from datetime import datetime
from typing import Dict, List

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

        if today_data.get('historical_events'):
            lines.append(self._build_historical_section(today_data['historical_events']))
            lines.append("")

        if today_data.get('custom_notes'):
            lines.append(self._build_custom_notes_section(today_data['custom_notes']))
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
            names_str = ", ".join(names[:3])

            if self.language == 'bilingual':
                lines.append(f"  • {saint}")
                lines.append(f"    Names: {names_str}")
            elif self.language == 'gr':
                lines.append(f"  • {saint}")
                lines.append(f"    Ονόματα: {names_str}")
            else:
                lines.append(f"  • {saint}")
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

        icon = "✝️"

        if self.language == 'bilingual':
            lines.append(f"{icon} Fasting Period / Περίοδος Νηστείας")
            lines.append(f"  {fasting_name} ({fasting_type})")
        elif self.language == 'gr':
            lines.append(f"{icon} Περίοδος Νηστείας")
            lines.append(f"  {fasting_name} ({fasting_type})")
        else:
            lines.append(f"{icon} Fasting Period")
            lines.append(f"  {fasting_name} ({fasting_type})")

        return "\n".join(lines)

    def _build_historical_section(self, events: List[Dict]) -> str:
        """Build an on-this-day section."""
        header = "On This Day / Σαν σήμερα" if self.language == "bilingual" else (
            "Σαν σήμερα" if self.language == "gr" else "On This Day"
        )
        return "\n".join([header] + [f"  {item['event']}" for item in events[:3]])

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
