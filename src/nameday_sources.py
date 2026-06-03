"""Nameday source catalog for import and review workflows."""


NAMEDAY_SOURCES = [
    {
        "source_name": "alexstyl/Greek-namedays",
        "source_url": "https://github.com/alexstyl/Greek-namedays",
        "source_type": "nameday_seed_dataset",
        "license_type": "Unlicense",
        "public_domain_status": "public-domain-style open source",
        "confidence_score": 0.65,
        "manual_review_required": True,
        "notes": (
            "JSON nameday seed data. Repository uses Unlicense, but README says "
            "the list was gathered from various websites, so entries require review."
        ),
    },
    {
        "source_name": "Pansamian Brotherhood Greek Namedays",
        "source_url": "https://www.pansamianvic.com/greek-namedays",
        "source_type": "nameday_review_reference",
        "license_type": "UNKNOWN - REVIEW/CORROBORATION ONLY",
        "public_domain_status": "not public-domain verified",
        "confidence_score": 0.45,
        "manual_review_required": True,
        "notes": (
            "Community-published nameday list. Use for manual comparison only; "
            "do not scrape or republish wholesale without permission."
        ),
    },
    {
        "source_name": "Glossa Houses Greek Name Days PDF",
        "source_url": "https://glossa-houses.com/wp-content/uploads/2017/05/Greek-Name-Days.pdf",
        "source_type": "nameday_review_reference",
        "license_type": "UNKNOWN - REVIEW/CORROBORATION ONLY",
        "public_domain_status": "not public-domain verified",
        "confidence_score": 0.45,
        "manual_review_required": True,
        "notes": (
            "PDF nameday calendar and alphabetical list. Use for manual comparison "
            "only unless permission or a permissive license is confirmed."
        ),
    },
    {
        "source_name": "GetGreece Greek Name Day Calendar",
        "source_url": "https://www.getgreece.com/post/greek-name-day-calendar",
        "source_type": "nameday_review_reference",
        "license_type": "COPYRIGHTED - REVIEW/CORROBORATION ONLY",
        "public_domain_status": "not public-domain",
        "confidence_score": 0.45,
        "manual_review_required": True,
        "notes": (
            "GetGreece terms reserve original website content. Use for manual "
            "comparison only; do not copy the article/list into KazaALKIS."
        ),
    },
]


def register_nameday_sources(db):
    """Register nameday seed and review sources in source_registry."""
    registered = []
    for source in NAMEDAY_SOURCES:
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
