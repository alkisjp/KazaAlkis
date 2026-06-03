"""Astrology and moon-phase source catalog for light daily sky notes."""


ASTROLOGY_SOURCES = [
    {
        "source_name": "People.com astrology and horoscope coverage",
        "source_url": "https://people.com/",
        "source_type": "astrology_reference",
        "license_type": "COPYRIGHTED - STYLE/REFERENCE ONLY",
        "public_domain_status": "not public-domain",
        "confidence_score": 0.35,
        "manual_review_required": True,
        "notes": (
            "Use only as a current-pop-culture reference for horoscope style. "
            "Do not copy horoscope text."
        ),
    },
    {
        "source_name": "YourTango zodiac coverage",
        "source_url": "https://www.yourtango.com/zodiac/",
        "source_type": "astrology_reference",
        "license_type": "COPYRIGHTED - STYLE/REFERENCE ONLY",
        "public_domain_status": "not public-domain",
        "confidence_score": 0.35,
        "manual_review_required": True,
        "notes": (
            "Use only as a current-pop-culture reference for zodiac themes and tone. "
            "Do not copy horoscope text."
        ),
    },
    {
        "source_name": "timeanddate.com Moon Phases",
        "source_url": "https://www.timeanddate.com/moon/phases/",
        "source_type": "moon_phase_reference",
        "license_type": "COPYRIGHTED - VERIFY/CORROBORATION ONLY",
        "public_domain_status": "not public-domain",
        "confidence_score": 0.6,
        "manual_review_required": True,
        "notes": (
            "Use to verify local moon phase displays. KazaALKIS calculates its own "
            "moon phase label and symbol rather than copying page text."
        ),
    },
    {
        "source_name": "timeanddate.com Moon Phases Amsterdam",
        "source_url": "https://www.timeanddate.com/moon/phases/netherlands/amsterdam",
        "source_type": "moon_phase_reference",
        "license_type": "COPYRIGHTED - VERIFY/CORROBORATION ONLY",
        "public_domain_status": "not public-domain",
        "confidence_score": 0.6,
        "manual_review_required": True,
        "notes": (
            "Amsterdam-specific moon phase reference for visual verification. "
            "Do not scrape or republish table text."
        ),
    },
]


def register_astrology_sources(db):
    """Register astrology and moon references in source_registry."""
    registered = []
    for source in ASTROLOGY_SOURCES:
        db.cursor.execute("""
            SELECT id FROM source_registry
            WHERE source_name = ? AND source_url = ?
            LIMIT 1
        """, (source["source_name"], source["source_url"]))
        row = db.cursor.fetchone()
        if row:
            registered.append(row[0])
            continue
        registered.append(db.add_source_registry_entry(**source))
    return registered
