"""Ancient Greek tradition source catalog for reviewed cultural parallels."""


ANCIENT_TRADITION_SOURCES = [
    {
        "source_name": "Perseus Digital Library",
        "source_url": "https://www.perseus.tufts.edu/",
        "source_type": "ancient_primary_text_reference",
        "license_type": "PUBLIC DOMAIN / CC varies by text",
        "public_domain_status": "public-domain and open-access material available",
        "confidence_score": 0.8,
        "manual_review_required": True,
        "notes": (
            "Use for primary-source checks in authors such as Pausanias, Plutarch, "
            "Herodotus, Hesiod, Homer, and Strabo. Verify each text/translation license."
        ),
    },
    {
        "source_name": "Theoi Classical Texts Library",
        "source_url": "https://www.theoi.com/Library.html",
        "source_type": "ancient_primary_text_reference",
        "license_type": "PUBLIC DOMAIN translations / site terms vary",
        "public_domain_status": "public-domain translations used in many entries",
        "confidence_score": 0.75,
        "manual_review_required": True,
        "notes": (
            "Useful gateway to public-domain classical translations and source citations. "
            "Treat Theoi article summaries as reference only; prefer the cited primary text."
        ),
    },
    {
        "source_name": "Project Gutenberg - A Smaller Dictionary of Greek and Roman Antiquities",
        "source_url": "https://www.gutenberg.org/ebooks/65909",
        "source_type": "ancient_secondary_reference",
        "license_type": "Public domain in the USA",
        "public_domain_status": "public-domain",
        "confidence_score": 0.7,
        "manual_review_required": True,
        "notes": (
            "Public-domain 19th-century reference for ancient customs, festivals, "
            "religion, institutions, and daily life. Use with modern caution."
        ),
    },
    {
        "source_name": "Internet Archive / Open Library - Dictionary of Greek and Roman Antiquities",
        "source_url": "https://openlibrary.org/works/OL17025496W/Dictionary_of_Greek_and_Roman_antiquities",
        "source_type": "ancient_secondary_reference",
        "license_type": "Public domain editions available",
        "public_domain_status": "public-domain editions available",
        "confidence_score": 0.7,
        "manual_review_required": True,
        "notes": (
            "Fuller public-domain reference work by William Smith. Good for festival "
            "and ritual background, but entries should be cross-checked."
        ),
    },
    {
        "source_name": "Wikisource - Dictionary of Greek and Roman Antiquities",
        "source_url": "https://en.wikisource.org/wiki/A_Dictionary_of_Greek_and_Roman_Antiquities",
        "source_type": "ancient_secondary_reference",
        "license_type": "Public domain",
        "public_domain_status": "public-domain",
        "confidence_score": 0.7,
        "manual_review_required": True,
        "notes": (
            "Readable public-domain entries for specific ancient festivals and customs, "
            "such as Daedala. Use concise paraphrase and cite the entry."
        ),
    },
    {
        "source_name": "Britannica ancient Greek religion articles",
        "source_url": "https://www.britannica.com/topic/Thesmophoria",
        "source_type": "ancient_secondary_reference",
        "license_type": "COPYRIGHTED - REVIEW/CORROBORATION ONLY",
        "public_domain_status": "not public-domain",
        "confidence_score": 0.65,
        "manual_review_required": True,
        "notes": (
            "Useful for quick scholarly corroboration of festivals such as Thesmophoria, "
            "but do not copy text into KazaALKIS."
        ),
    },
    {
        "source_name": "Wikipedia - Thargelia",
        "source_url": "https://en.wikipedia.org/wiki/Thargelia",
        "source_type": "ancient_seasonal_festival_reference",
        "license_type": "CC BY-SA 4.0 / public-domain incorporated text",
        "public_domain_status": "open-license reference; verify citations",
        "confidence_score": 0.7,
        "manual_review_required": True,
        "notes": (
            "Useful June-season reference: Thargelia was an Athenian festival of "
            "Apollo and Artemis in Thargelion, about late May, with purification "
            "and first-fruits themes."
        ),
    },
    {
        "source_name": "Wikipedia - Skira / Skirophoria",
        "source_url": "https://en.wikipedia.org/wiki/Skira",
        "source_type": "ancient_seasonal_festival_reference",
        "license_type": "CC BY-SA 4.0",
        "public_domain_status": "open-license reference; verify citations",
        "confidence_score": 0.65,
        "manual_review_required": True,
        "notes": (
            "Useful June-season reference: Skira/Skirophoria marked the dissolution "
            "of the old year in May/June and includes imagery of heat and protection "
            "of Attic soil."
        ),
    },
    {
        "source_name": "Reddit r/ancientgreece - Questions regarding Greek traditions and worship",
        "source_url": "https://www.reddit.com/r/ancientgreece/comments/1gnun51/questions_regarding_greek_traditions_and_worship/",
        "source_type": "ancient_practice_discussion_reference",
        "license_type": "REDDIT USER CONTENT - DISCUSSION LEAD ONLY",
        "public_domain_status": "not public-domain",
        "confidence_score": 0.35,
        "manual_review_required": True,
        "notes": (
            "Use only as a discussion lead for general practice themes: local cults, "
            "offerings, temples, festivals, and household/community worship. Do not "
            "treat as scholarly authority."
        ),
    },
]


def register_ancient_tradition_sources(db):
    """Register ancient-tradition references in source_registry."""
    registered = []
    for source in ANCIENT_TRADITION_SOURCES:
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
