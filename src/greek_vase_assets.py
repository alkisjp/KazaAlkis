"""Daily Greek vase banner assets with strict license validation."""

import json
from datetime import datetime
from pathlib import Path

try:
    from .path_manager import get_paths
except ImportError:
    from path_manager import get_paths


ACCEPTED_LICENSES = {
    "Public Domain",
    "CC0",
    "Open Access with commercial reuse allowed",
}

VASE_CACHE_FILENAME = "greek_vase_daily_assets.json"


SEED_VASE_ASSETS = [
    {
        "id": "met-250545",
        "title": "Terracotta amphora (jar)",
        "object_type": "Amphora",
        "date": "ca. 530-520 BCE",
        "culture": "Greek, Attic",
        "period": "Archaic",
        "museum": "The Metropolitan Museum of Art",
        "source_url": "https://www.metmuseum.org/art/collection/search/250545",
        "image_url": "https://images.metmuseum.org/CRDImages/gr/original/DP115343.jpg",
        "license": "Public Domain",
        "license_verified": True,
        "attribution_required": False,
        "attribution_text": "The Metropolitan Museum of Art, Rogers Fund, 1917",
        "myth_keywords": ["Apollo", "Athena", "Dionysus", "chariot"],
        "original_description": (
            "Attic terracotta amphora attributed to the Antimenes Painter; Met metadata "
            "tags include Apollo, Athena, Dionysus, horses, and chariots."
        ),
        "llm_rephrased_description": (
            "This Attic amphora gathers several divine presences into one painted vessel: "
            "Apollo, Athena, and Dionysus appear in the Met metadata alongside horses and "
            "chariots. Rather than reading it as a single certain myth, KazaALKIS presents "
            "it as a glimpse of the sacred world around an ancient Greek vase: gods, motion, "
            "procession, and ritual energy carried on terracotta."
        ),
        "last_used_date": None,
        "usage_status": "available",
    },
    {
        "id": "met-255154",
        "title": "Terracotta amphora (jar)",
        "object_type": "Amphora",
        "date": "ca. 530 BCE",
        "culture": "Greek, Attic",
        "period": "Archaic",
        "museum": "The Metropolitan Museum of Art",
        "source_url": "https://www.metmuseum.org/art/collection/search/255154",
        "image_url": "https://images.metmuseum.org/CRDImages/gr/original/DP116936.jpg",
        "license": "Public Domain",
        "license_verified": True,
        "attribution_required": False,
        "attribution_text": "The Metropolitan Museum of Art, Purchase, Joseph Pulitzer Bequest, 1963",
        "myth_keywords": ["Herakles", "Apollo", "Dionysus", "satyrs", "maenads"],
        "original_description": (
            "Attic terracotta amphora signed by Andokides; Met metadata tags include "
            "Herakles, Apollo, Dionysus, maenads, and satyrs."
        ),
        "llm_rephrased_description": (
            "This amphora belongs to the mythic atmosphere of Herakles and the gods. "
            "The Met metadata links it with Herakles, Apollo, Dionysus, maenads, and satyrs, "
            "so the vase can be read as a meeting point between heroic labor and festival "
            "energy. KazaALKIS treats the scene carefully: a public-domain object, a ritual "
            "vessel, and a small painted doorway into archaic Greek imagination."
        ),
        "last_used_date": None,
        "usage_status": "available",
    },
    {
        "id": "met-251345",
        "title": "Terracotta hydria (water jar)",
        "object_type": "Hydria",
        "date": "ca. 530-520 BCE",
        "culture": "Greek, Attic",
        "period": "Archaic",
        "museum": "The Metropolitan Museum of Art",
        "source_url": "https://www.metmuseum.org/art/collection/search/251345",
        "image_url": "https://images.metmuseum.org/CRDImages/gr/original/DP115342.jpg",
        "license": "Public Domain",
        "license_verified": True,
        "attribution_required": False,
        "attribution_text": "The Metropolitan Museum of Art, Rogers Fund, 1923",
        "myth_keywords": ["Triton", "sea travel", "water", "heroes"],
        "original_description": (
            "Attic terracotta hydria attributed to an artist related to the Antimenes Painter; "
            "Met metadata tags include Triton, animals, men, and women."
        ),
        "llm_rephrased_description": (
            "A hydria was made for water, so a scene associated with Triton feels especially alive: "
            "the sea enters the shape of the vessel itself. The Met tags this Attic jar with Triton, "
            "figures, and animals. KazaALKIS reads it as a sea-colored reminder of ancient travel, "
            "danger, and divine presence around water, without adding a myth beyond the source metadata."
        ),
        "last_used_date": None,
        "usage_status": "available",
    },
    {
        "id": "met-255214",
        "title": "Terracotta lekythos (oil flask)",
        "object_type": "Lekythos",
        "date": "ca. 500-490 BCE",
        "culture": "Greek, Attic",
        "period": "Late Archaic",
        "museum": "The Metropolitan Museum of Art",
        "source_url": "https://www.metmuseum.org/art/collection/search/255214",
        "image_url": "https://images.metmuseum.org/CRDImages/gr/original/DP1057.jpg",
        "license": "Public Domain",
        "license_verified": True,
        "attribution_required": False,
        "attribution_text": "The Metropolitan Museum of Art, Rogers Fund, 1966",
        "myth_keywords": ["Apollo", "Artemis", "Athena", "ritual oil"],
        "original_description": (
            "Attic terracotta lekythos attributed to the manner of the Sappho Painter; "
            "Met metadata tags include Apollo, Artemis, Athena, and animals."
        ),
        "llm_rephrased_description": (
            "The lekythos was an oil flask, a vessel close to ritual, grooming, and funerary practice. "
            "Here the Met metadata names Apollo, Artemis, and Athena, placing the small object in a "
            "bright divine company. KazaALKIS presents it as a quiet daily banner: oil, offering, and "
            "the presence of gods who shaped music, hunting, wisdom, and civic protection."
        ),
        "last_used_date": None,
        "usage_status": "available",
    },
    {
        "id": "met-247193",
        "title": "Terracotta aryballos (oil flask)",
        "object_type": "Aryballos",
        "date": "ca. 595-570 BCE",
        "culture": "Greek, Corinthian",
        "period": "Middle Corinthian",
        "museum": "The Metropolitan Museum of Art",
        "source_url": "https://www.metmuseum.org/art/collection/search/247193",
        "image_url": "https://images.metmuseum.org/CRDImages/gr/original/DP119907.jpg",
        "license": "Public Domain",
        "license_verified": True,
        "attribution_required": False,
        "attribution_text": "The Metropolitan Museum of Art, Rogers Fund, 1906",
        "myth_keywords": ["centaurs", "Herakles", "wildness", "athletics"],
        "original_description": (
            "Corinthian terracotta aryballos attributed to the Otterlo Painter; "
            "Met metadata tags include centaurs."
        ),
        "llm_rephrased_description": (
            "This small Corinthian oil flask carries the wild world of centaurs into a handheld object. "
            "Because aryballoi were associated with scented oil and athletic life, the creaturely image "
            "feels like a meeting of body, contest, and myth. KazaALKIS describes it as a disciplined "
            "little vessel with untamed imagery, staying close to the Met’s centaur metadata."
        ),
        "last_used_date": None,
        "usage_status": "available",
    },
]


FALLBACK_VASE_BANNER = {
    "id": "fallback-greek-vase",
    "title": "Greek Vase Banner Unavailable",
    "object_type": "Fallback",
    "date": "",
    "culture": "Ancient Greek",
    "period": "",
    "museum": "KazaALKIS",
    "source_url": "",
    "image_url": "",
    "license": "No image selected",
    "license_verified": False,
    "attribution_required": False,
    "attribution_text": "",
    "myth_keywords": [],
    "original_description": "No verified public-domain vase image is available today.",
    "llm_rephrased_description": (
        "Today’s vase banner is waiting for a verified public-domain image. KazaALKIS only "
        "shows ancient artwork when rights metadata is clear and safe for public reuse."
    ),
    "last_used_date": None,
    "usage_status": "fallback",
}


def default_vase_cache_path():
    return get_paths().app_root / "data" / VASE_CACHE_FILENAME


class GreekVaseAssetManager:
    """Manage verified Greek vase assets and daily non-repeating selection."""

    def __init__(self, cache_path=None):
        self.cache_path = Path(cache_path or default_vase_cache_path())

    def ensure_cache(self):
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.cache_path.exists():
            self.save_assets(SEED_VASE_ASSETS)
        return self.load_assets()

    def load_assets(self):
        if not self.cache_path.exists():
            return []
        return json.loads(self.cache_path.read_text(encoding="utf-8"))

    def save_assets(self, assets):
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(
            json.dumps(assets, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def select_daily_asset(self, date_text=None, force_refresh=False, override_id=None):
        date_text = date_text or datetime.now().strftime("%Y-%m-%d")
        assets = self.ensure_cache()
        valid_assets = [asset for asset in assets if self.is_valid_asset(asset)]
        if not valid_assets:
            return dict(FALLBACK_VASE_BANNER)

        if not force_refresh:
            todays_asset = next(
                (asset for asset in valid_assets if asset.get("last_used_date") == date_text),
                None,
            )
            if todays_asset:
                return dict(todays_asset)

        selected = None
        if override_id:
            selected = next((asset for asset in valid_assets if asset.get("id") == override_id), None)

        if selected is None:
            available = [asset for asset in valid_assets if asset.get("usage_status") != "used"]
            if not available:
                for asset in assets:
                    if self.is_valid_asset(asset):
                        asset["usage_status"] = "available"
                available = [asset for asset in assets if self.is_valid_asset(asset)]
            day_index = datetime.strptime(date_text, "%Y-%m-%d").timetuple().tm_yday
            selected = available[day_index % len(available)]

        for asset in assets:
            if asset.get("id") == selected.get("id"):
                asset["last_used_date"] = date_text
                asset["usage_status"] = "used"
                selected = asset
                break
        self.save_assets(assets)
        return dict(selected)

    def is_valid_asset(self, asset):
        return (
            bool(asset.get("id"))
            and bool(asset.get("image_url"))
            and bool(asset.get("source_url"))
            and asset.get("license") in ACCEPTED_LICENSES
            and asset.get("license_verified") is True
            and asset.get("usage_status") != "rejected"
        )


def build_vase_whatsapp_caption(asset):
    """Build a short optional WhatsApp caption for the selected vase."""
    if not asset or asset.get("id") == FALLBACK_VASE_BANNER["id"]:
        return FALLBACK_VASE_BANNER["llm_rephrased_description"]
    return (
        f"🏺 Greek Vase & Myth: {asset['title']}\n"
        f"{asset.get('llm_rephrased_description', '')}\n"
        f"Source: {asset.get('museum', '')} | {asset.get('license', '')}\n"
        f"Read more: {asset.get('source_url', '')}"
    )


GREEK_VASE_ASSET_SCHEMA = {
    "id": "string",
    "title": "string",
    "object_type": "string",
    "date": "string",
    "culture": "string",
    "period": "string",
    "museum": "string",
    "source_url": "string",
    "image_url": "string",
    "license": "Public Domain | CC0 | Open Access with commercial reuse allowed",
    "license_verified": "boolean",
    "attribution_required": "boolean",
    "attribution_text": "string",
    "myth_keywords": ["string"],
    "original_description": "string",
    "llm_rephrased_description": "string",
    "last_used_date": "YYYY-MM-DD | null",
    "usage_status": "available | used | rejected | fallback",
}
