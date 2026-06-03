"""Local zodiac and moon-phase notes for daily messages."""

from datetime import datetime, timezone


SYNODIC_MONTH_DAYS = 29.530588853
KNOWN_NEW_MOON = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)

MOON_PHASES = [
    ("New Moon", "Νέα Σελήνη", "🌑"),
    ("Waxing Crescent", "Αύξων μηνίσκος", "🌒"),
    ("First Quarter", "Πρώτο τέταρτο", "🌓"),
    ("Waxing Gibbous", "Αύξων αμφίκυρτος", "🌔"),
    ("Full Moon", "Πανσέληνος", "🌕"),
    ("Waning Gibbous", "Φθίνων αμφίκυρτος", "🌖"),
    ("Last Quarter", "Τελευταίο τέταρτο", "🌗"),
    ("Waning Crescent", "Φθίνων μηνίσκος", "🌘"),
]

ZODIAC_DATES = [
    ("Capricorn", "Αιγόκερως", (12, 22), (1, 19)),
    ("Aquarius", "Υδροχόος", (1, 20), (2, 18)),
    ("Pisces", "Ιχθύες", (2, 19), (3, 20)),
    ("Aries", "Κριός", (3, 21), (4, 19)),
    ("Taurus", "Ταύρος", (4, 20), (5, 20)),
    ("Gemini", "Δίδυμοι", (5, 21), (6, 20)),
    ("Cancer", "Καρκίνος", (6, 21), (7, 22)),
    ("Leo", "Λέων", (7, 23), (8, 22)),
    ("Virgo", "Παρθένος", (8, 23), (9, 22)),
    ("Libra", "Ζυγός", (9, 23), (10, 22)),
    ("Scorpio", "Σκορπιός", (10, 23), (11, 21)),
    ("Sagittarius", "Τοξότης", (11, 22), (12, 21)),
]

ZODIAC_THEMES = {
    "Gemini": (
        "Gemini season favors conversation, curiosity, short journeys, and flexible plans.",
        "Η εποχή των Διδύμων ευνοεί τη συζήτηση, την περιέργεια, τις μικρές μετακινήσεις και τα ευέλικτα σχέδια.",
    ),
    "Cancer": (
        "Cancer season turns attention toward home, memory, care, and emotional steadiness.",
        "Η εποχή του Καρκίνου στρέφει την προσοχή στο σπίτι, τη μνήμη, τη φροντίδα και τη συναισθηματική σταθερότητα.",
    ),
    "Leo": (
        "Leo season highlights warmth, confidence, creativity, and generous presence.",
        "Η εποχή του Λέοντα φωτίζει τη ζεστασιά, την αυτοπεποίθηση, τη δημιουργικότητα και τη γενναιόδωρη παρουσία.",
    ),
}


def build_sky_note(date_text):
    """Return a bilingual zodiac and moon note for a YYYY-MM-DD date."""
    date = _parse_date(date_text)
    zodiac_en, zodiac_gr = _zodiac_for_date(date)
    phase_en, phase_gr, symbol, moon_age = _moon_phase_for_date(date)
    theme_en, theme_gr = ZODIAC_THEMES.get(zodiac_en, (
        f"{zodiac_en} season invites a simple daily reflection rather than a prediction.",
        f"Η εποχή του ζωδίου {zodiac_gr} προσκαλεί σε απλό καθημερινό στοχασμό, όχι σε πρόβλεψη.",
    ))
    return {
        "zodiac": zodiac_en,
        "zodiac_greek": zodiac_gr,
        "moon_phase": phase_en,
        "moon_phase_greek": phase_gr,
        "moon_symbol": symbol,
        "moon_age_days": round(moon_age, 1),
        "english": (
            f"{symbol} Moon: {phase_en}, about {moon_age:.1f} days into the lunar cycle. "
            f"Zodiac season: {zodiac_en}. {theme_en} "
            "This is offered as a light cultural sky note, not as certainty or advice."
        ),
        "greek": (
            f"{symbol} Σελήνη: {phase_gr}, περίπου {moon_age:.1f} ημέρες στον σεληνιακό κύκλο. "
            f"Εποχή ζωδίου: {zodiac_gr}. {theme_gr} "
            "Προσφέρεται ως ελαφρύ πολιτιστικό σημείωμα ουρανού, όχι ως βεβαιότητα ή συμβουλή."
        ),
    }


def _parse_date(date_text):
    if isinstance(date_text, datetime):
        return date_text.date()
    return datetime.strptime(str(date_text), "%Y-%m-%d").date()


def _zodiac_for_date(date):
    current = (date.month, date.day)
    for name_en, name_gr, start, end in ZODIAC_DATES:
        if start <= end:
            if start <= current <= end:
                return name_en, name_gr
        elif current >= start or current <= end:
            return name_en, name_gr
    return "Capricorn", "Αιγόκερως"


def _moon_phase_for_date(date):
    moment = datetime(date.year, date.month, date.day, 12, 0, tzinfo=timezone.utc)
    moon_age = ((moment - KNOWN_NEW_MOON).total_seconds() / 86400.0) % SYNODIC_MONTH_DAYS
    index = int((moon_age + SYNODIC_MONTH_DAYS / 16) / (SYNODIC_MONTH_DAYS / 8)) % 8
    phase_en, phase_gr, symbol = MOON_PHASES[index]
    return phase_en, phase_gr, symbol, moon_age
