from pathlib import Path
from unittest.mock import Mock, patch

from database import KazaALKISDatabase
from config_manager import ConfigurationManager
from message_builder import MessageBuilder
from path_manager import PathManager
from whatsapp_notifier import BulkMessageSender, WhatsAppNotifier, normalize_phone_number
from KazaALKIS_launcher import KazaALKISLauncher
from website_publisher import WebsitePublisher
from commentary_generator import CommentaryGenerator
from nameday_sources import NAMEDAY_SOURCES, register_nameday_sources
from ancient_tradition_sources import ANCIENT_TRADITION_SOURCES, register_ancient_tradition_sources
from astrology_sources import ASTROLOGY_SOURCES, register_astrology_sources
from data_importer import DataImporter
from sky_note import build_sky_note
from recipe_recommendations import build_daily_recipes


def make_db(tmp_path):
    db = KazaALKISDatabase(str(tmp_path / "kazaalkis.db"))
    assert db.connect()
    assert db.initialize_schema()
    return db


def test_path_manager_routes_runtime_resources_to_ai_root(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_ROOT", str(tmp_path))
    paths = PathManager()
    assert paths.logs == tmp_path / "logs"
    assert paths.outputs == tmp_path / "outputs"
    assert paths.venvs == tmp_path / "venvs"
    assert paths.tmp == tmp_path / "tmp"


def test_default_delivery_mode_is_manual(tmp_path):
    config = ConfigurationManager(str(tmp_path / "config"))
    assert config.get("whatsapp_provider") == "manual"
    assert "not configured" in config.get_delivery_status()


def test_phase2_default_database_path_uses_ai_runtime_root(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_ROOT", str(tmp_path))
    config = ConfigurationManager(str(tmp_path / "config"))
    assert config.get("database_path") == str(tmp_path / "KazaAlkis" / "db" / "kazaalkis.db")


def test_phase2_config_migrates_old_project_database_default(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_ROOT", str(tmp_path))
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    old_project_db = Path(__file__).resolve().parents[1] / "data" / "kazaalkis.db"
    (config_dir / "kazaalkis_config.json").write_text(
        '{"database_path": "' + str(old_project_db).replace("\\", "\\\\") + '", "whatsapp_provider": "manual"}',
        encoding="utf-8",
    )
    config = ConfigurationManager(str(config_dir))
    assert config.get("database_path") == str(tmp_path / "KazaAlkis" / "db" / "kazaalkis.db")


def test_phase2_database_schema_contains_required_tables_and_columns(tmp_path):
    db = make_db(tmp_path)
    schema = db.get_schema_summary()
    required_tables = {
        "namedays",
        "holidays",
        "orthodox_calendar",
        "historical_events",
        "quotes",
        "astronomy",
        "contacts",
        "opt_in_log",
        "message_log",
        "source_registry",
        "daily_message_cache",
        "parallel_traditions",
    }
    assert required_tables.issubset(schema)
    required_content_columns = {
        "id",
        "date",
        "description",
        "source_name",
        "source_url",
        "license_type",
        "import_date",
        "confidence_score",
        "manual_review_required",
    }
    for table in ("namedays", "holidays", "orthodox_calendar", "historical_events", "quotes", "astronomy", "parallel_traditions"):
        assert required_content_columns.issubset(set(schema[table]))
    assert {"name", "phone", "language", "timezone", "opt_in_status", "active", "created_at", "updated_at"}.issubset(
        set(schema["contacts"])
    )
    db.close()


def test_phase2_message_log_mirrors_legacy_log(tmp_path):
    db = make_db(tmp_path)
    contact_id = db.add_contact("Alkis", "6912345678")
    assert db.log_message(contact_id, "2026-06-03", "hello", "sent", "manual")
    assert db.cursor.execute("SELECT COUNT(*) FROM message_logs").fetchone()[0] == 1
    assert db.cursor.execute("SELECT COUNT(*) FROM message_log").fetchone()[0] == 1
    row = db.cursor.execute("SELECT phone_masked, status FROM message_log").fetchone()
    assert row["phone_masked"] == "*******678"
    assert row["status"] == "sent"
    db.close()


def test_schema_and_validation_report_missing_provenance(tmp_path):
    db = make_db(tmp_path)
    db.cursor.execute("INSERT INTO quotes (date, quote) VALUES (?, ?)", ("2026-06-01", "Test"))
    db.conn.commit()
    warnings = db.get_validation_warnings()
    assert ("quotes", 1) in warnings["missing_source"]
    source_id = db.add_source_reference("Manual", "local://manual", "", "user_entered")
    assert source_id == 1
    assert len(db.get_validation_warnings()["missing_licence"]) == 1
    db.close()


def test_nameday_review_sources_are_registered_with_safe_license_flags(tmp_path):
    db = make_db(tmp_path)
    ids = register_nameday_sources(db)
    assert len(ids) == len(NAMEDAY_SOURCES)
    rows = list(db.cursor.execute("""
        SELECT source_name, license_type, manual_review_required
        FROM source_registry
        WHERE source_type IN ('nameday_seed_dataset', 'nameday_review_reference')
        ORDER BY id
    """))
    assert any(row["source_name"] == "alexstyl/Greek-namedays" and row["license_type"] == "Unlicense" for row in rows)
    review_only = [row for row in rows if row["source_name"] != "alexstyl/Greek-namedays"]
    assert review_only
    assert all(row["manual_review_required"] == 1 for row in review_only)
    assert all("ONLY" in row["license_type"] or row["license_type"] == "Unlicense" for row in rows)
    second_ids = register_nameday_sources(db)
    assert second_ids == ids
    db.close()


def test_ancient_tradition_sources_are_registered_with_safe_license_flags(tmp_path):
    db = make_db(tmp_path)
    ids = register_ancient_tradition_sources(db)
    assert len(ids) == len(ANCIENT_TRADITION_SOURCES)
    rows = list(db.cursor.execute("""
        SELECT source_name, license_type, manual_review_required
        FROM source_registry
        WHERE source_type LIKE 'ancient_%'
        ORDER BY id
    """))
    assert any("Perseus" in row["source_name"] for row in rows)
    assert any(row["source_name"] == "Wikipedia - Thargelia" for row in rows)
    assert any(row["source_name"].startswith("Reddit r/ancientgreece") for row in rows)
    assert any(row["license_type"] == "COPYRIGHTED - REVIEW/CORROBORATION ONLY" for row in rows)
    assert all(row["manual_review_required"] == 1 for row in rows)
    second_ids = register_ancient_tradition_sources(db)
    assert second_ids == ids
    db.close()


def test_astrology_sources_are_registered_with_safe_license_flags(tmp_path):
    db = make_db(tmp_path)
    ids = register_astrology_sources(db)
    assert len(ids) == len(ASTROLOGY_SOURCES)
    rows = list(db.cursor.execute("""
        SELECT source_name, license_type, manual_review_required
        FROM source_registry
        WHERE source_type IN ('astrology_reference', 'moon_phase_reference')
        ORDER BY id
    """))
    assert any(row["source_name"] == "YourTango zodiac coverage" for row in rows)
    assert any(row["source_name"] == "timeanddate.com Moon Phases Amsterdam" for row in rows)
    assert all(row["manual_review_required"] == 1 for row in rows)
    assert all("COPYRIGHTED" in row["license_type"] for row in rows)
    assert register_astrology_sources(db) == ids
    db.close()


def test_sky_note_generates_zodiac_and_moon_symbol():
    note = build_sky_note("2026-06-03")
    assert note["zodiac"] == "Gemini"
    assert note["zodiac_greek"] == "Δίδυμοι"
    assert note["moon_symbol"] in {"🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"}
    assert "light cultural sky note" in note["english"]


def test_daily_recipes_select_one_fasting_and_one_ancient_recipe():
    recipes = build_daily_recipes("2026-06-03")
    assert recipes["fasting"]["title"]
    assert recipes["fasting"]["url"].startswith("https://")
    assert recipes["ancient"]["title"]
    assert recipes["ancient"]["url"].startswith("https://")
    assert "not republished" in recipes["notice"]


def test_message_builder_uses_data_date_and_open_data_label():
    message = MessageBuilder("en", "friendly").build_daily_message({
        "date": "2026-04-23",
        "namedays": [],
        "quotes": [],
        "holidays": [],
        "fasting": None,
        "historical_events": [{"event": "A historical note"}],
        "custom_notes": [{"note": "A user note"}],
    })
    assert "Thursday, 23 April 2026" in message
    assert "Daily Greek calendar and proverb" in message
    assert "A historical note" in message
    assert "A user note" in message


def test_alexstyl_nameday_import_populates_today_data(tmp_path, monkeypatch):
    db = make_db(tmp_path)
    importer = DataImporter(db)

    def fake_fetch_json(url):
        if "recurring" in url:
            return {"data": [
                {"date": "03/06", "names": ["Ιερία", "Ιέρεια"]},
                {"date": "03/06", "names": ["Υπατία", "Υπατή", "Υπατούλα", "Πατούλα"]},
            ]}
        return {"special": [
            {"toEaster": 1, "main": "2α Διακαινησίμου - Δευτέρα", "variations": ["Πασχαλία"]},
        ]}

    monkeypatch.setattr(importer, "_fetch_json", fake_fetch_json)
    assert importer.import_alexstyl_namedays(2026) == 3
    data = db.get_today_data("2026-06-03")
    names = " ".join(row["names"] for row in data["namedays"])
    assert "Ιερία" in names
    assert "Υπατία" in names
    easter_monday = db.get_today_data("2026-04-13")
    assert "Πασχαλία" in easter_monday["namedays"][0]["names"]
    assert importer.import_alexstyl_namedays(2026) == 0
    db.close()


def test_nameday_override_replaces_seed_rows_for_preferred_calendar(tmp_path, monkeypatch):
    db = make_db(tmp_path)
    importer = DataImporter(db)

    def fake_fetch_json(url):
        if "recurring" in url:
            return {"data": [
                {"date": "03/06", "names": ["Ιερία", "Ιέρεια"]},
                {"date": "03/06", "names": ["Υπατία", "Υπατή"]},
            ]}
        return {"special": []}

    monkeypatch.setattr(importer, "_fetch_json", fake_fetch_json)
    importer.import_alexstyl_namedays(2026)
    assert len(db.get_today_data("2026-06-03")["namedays"]) == 2

    importer.apply_nameday_override(
        date_str="2026-06-03",
        names=["Lucillian", "Paula", "Patroklos"],
        saint="Reviewed GetGreece calendar entry",
        source_name="GetGreece Greek Name Day Calendar",
        source_url="https://www.getgreece.com/post/greek-name-day-calendar",
        license_type="COPYRIGHTED - FACTUAL DATE CORRECTION ONLY",
    )
    data = db.get_today_data("2026-06-03")
    assert len(data["namedays"]) == 1
    assert data["namedays"][0]["names"] == "Lucillian, Paula, Patroklos"
    assert data["namedays"][0]["saint"] == "Reviewed GetGreece calendar entry"
    db.close()


def test_reviewed_nameday_entry_hides_seed_rows_for_same_date(tmp_path):
    db = make_db(tmp_path)
    db.cursor.execute(
        "INSERT INTO name_days (date, names, saint) VALUES (?, ?, ?)",
        ("2026-06-03", "Ιερία, Ιέρεια", "Greek nameday seed"),
    )
    db.cursor.execute(
        "INSERT INTO name_days (date, names, saint) VALUES (?, ?, ?)",
        ("2026-06-03", "Lucillian, Paula, Patroklos", "Reviewed GetGreece calendar entry"),
    )
    db.conn.commit()
    data = db.get_today_data("2026-06-03")
    assert data["namedays"] == [{
        "names": "Lucillian, Paula, Patroklos",
        "saint": "Reviewed GetGreece calendar entry",
    }]
    db.close()


def test_message_builder_adds_context_when_daily_data_is_sparse():
    message = MessageBuilder("bilingual", "humorous").build_daily_message({
        "date": "2026-06-03",
        "namedays": [],
        "quotes": [],
        "holidays": [],
        "fasting": {
            "name": "Apostles' Fast",
            "fasting_type": "minor_fast",
            "description": "Period of fasting between Pentecost and the feast of St. Peter and St. Paul",
        },
        "historical_events": [],
        "custom_notes": [],
    })
    assert "Apostles' Fast" in message
    assert "Νηστεία των Αγίων Αποστόλων" in message
    assert "Period of fasting between Pentecost" in message
    assert "Cultural Meaning" in message
    assert "Astrology & Moon" in message
    assert "Gemini" in message
    assert "Moon:" in message
    assert "preparation after Pentecost" in message
    assert "Thargelia" in message
    assert "Skira" in message
    assert "αρχαιοελληνικός παραλληλισμός" in message
    assert "Today’s Context" in message
    assert "Σημερινό πλαίσιο" in message
    assert "Δεν υπάρχει ακόμη ελεγμένη καταχώριση" in message
    assert "public-domain proverb or quote still needs" not in message
    assert "Greek-related “on this day” item has not been imported" not in message


def test_message_builder_omits_redundant_context_when_meaning_exists():
    message = MessageBuilder("bilingual", "friendly").build_daily_message({
        "date": "2026-06-03",
        "namedays": [{"names": "Lucillian, Paula, Patroklos", "saint": "Reviewed GetGreece calendar entry"}],
        "quotes": [],
        "holidays": [],
        "fasting": {
            "name": "Apostles' Fast",
            "fasting_type": "minor_fast",
            "description": "Period of fasting between Pentecost and the feast of St. Peter and St. Paul",
        },
        "historical_events": [],
        "custom_notes": [],
        "parallel_traditions": [],
    })
    assert "Cultural Meaning" in message
    assert "Today’s Context" not in message
    assert "Σημερινό πλαίσιο" not in message


def test_parallel_traditions_flow_into_preview_and_today_data(tmp_path):
    db = make_db(tmp_path)
    db.cursor.execute("""
        INSERT INTO parallel_traditions
        (date, orthodox_title, orthodox_description, region,
         ancient_title, ancient_description, relationship_note,
         source_name, license_type, confidence_score, manual_review_required)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "2026-04-12",
        "Easter lamb and red eggs",
        "Families gather after the Resurrection service and share a festive meal.",
        "Peloponnese",
        "Spring sacrifice and communal feasting",
        "Ancient spring festivals also used shared meals to mark renewal.",
        "Presented as a thematic comparison, not a claim of direct survival.",
        "Manual reviewed note",
        "user_curated",
        0.8,
        0,
    ))
    db.conn.commit()
    data = db.get_today_data("2026-04-12")
    message = MessageBuilder("bilingual", "friendly").build_daily_message(data)
    assert "Parallel Traditions" in message
    assert "Easter lamb and red eggs" in message
    assert "Spring sacrifice and communal feasting" in message
    assert data["parallel_traditions"][0]["region"] == "Peloponnese"
    db.close()


def test_manual_fallback_masks_phone_and_uses_ai_outputs(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_ROOT", str(tmp_path))
    notifier = WhatsAppNotifier("manual")
    ok, result = notifier.send_message("306900000000", "hello")
    assert ok
    output = next((tmp_path / "outputs" / "KazaALKIS" / "manual_messages").glob("*.txt"))
    assert "306900000000" not in output.name
    assert "306900000000" not in output.read_text(encoding="utf-8")
    assert str(output) in result


def test_whatsapp_cloud_uses_meta_graph_endpoint(monkeypatch):
    monkeypatch.setenv("WHATSAPP_ACCESS_TOKEN", "token")
    monkeypatch.setenv("WHATSAPP_PHONE_NUMBER_ID", "phone-id")
    monkeypatch.setenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "account-id")
    response = Mock(status_code=200)
    response.json.return_value = {"messages": [{"id": "message-id"}]}
    notifier = WhatsAppNotifier("whatsapp_business_cloud")
    with patch("whatsapp_notifier.requests.post", return_value=response) as post:
        ok, _ = notifier.send_message("306900000000", "hello")
    assert ok
    assert post.call_args.args[0] == "https://graph.facebook.com/v20.0/phone-id/messages"


def test_whatsapp_cloud_explains_allowed_test_recipient_error(monkeypatch):
    monkeypatch.setenv("WHATSAPP_ACCESS_TOKEN", "token")
    monkeypatch.setenv("WHATSAPP_PHONE_NUMBER_ID", "phone-id")
    monkeypatch.setenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "account-id")
    response = Mock(status_code=400)
    response.json.return_value = {
        "error": {"message": "(#131030) Recipient phone number not in allowed list"}
    }
    notifier = WhatsAppNotifier("whatsapp_business_cloud")
    with patch("whatsapp_notifier.requests.post", return_value=response):
        ok, message = notifier.send_message("6912345678", "hello")
    assert not ok
    assert "allowed test-recipient list" in message
    assert "WhatsApp > API Setup" in message


def test_phone_normalization_accepts_greek_local_and_international_numbers():
    assert normalize_phone_number("6912345678") == "+306912345678"
    assert normalize_phone_number("2101234567") == "+302101234567"
    assert normalize_phone_number("00306912345678") == "+306912345678"
    assert normalize_phone_number("+44 7700 900123") == "+447700900123"


def test_send_test_message_uses_stored_contact_name(tmp_path):
    db = make_db(tmp_path)
    db.add_contact("Alkis", "6912345678")
    launcher = object.__new__(KazaALKISLauncher)
    launcher.db = db
    launcher.config = Mock()
    launcher.config.get.return_value = "manual"
    with patch("builtins.input", return_value="alkis"), \
         patch("KazaALKIS_launcher.WhatsAppNotifier.send_message", return_value=(True, "ok")) as send:
        launcher.send_test_message()
    assert send.call_args.args[0] == "6912345678"
    db.close()


def test_website_publisher_exports_public_calendar_data_only(tmp_path):
    db = make_db(tmp_path)
    db.cursor.execute("""
        INSERT INTO name_days (date, names, saint) VALUES (?, ?, ?)
    """, ("2026-06-02", "Alkis", "Test Saint"))
    db.conn.commit()
    commentary = {"english": "Hello", "greek": "Γεια", "review_required": False}
    latest, history = WebsitePublisher(db, str(tmp_path)).publish("2026-06-02", commentary=commentary)
    text = latest.read_text(encoding="utf-8")
    assert latest.exists()
    assert history.exists()
    assert "Alkis" in text
    assert "phone" not in text
    assert "contact" not in text
    assert "official Kazamias" not in text
    assert "Γεια" in text
    db.close()


def test_website_publisher_exports_generated_cultural_reflection(tmp_path):
    db = make_db(tmp_path)
    db.cursor.execute("""
        INSERT INTO fasting_notes
        (start_date, end_date, name, fasting_type, description)
        VALUES (?, ?, ?, ?, ?)
    """, (
        "2026-06-01",
        "2026-06-29",
        "Apostles' Fast",
        "minor_fast",
        "Period of fasting between Pentecost and the feast of St. Peter and St. Paul",
    ))
    db.conn.commit()
    latest, _ = WebsitePublisher(db, str(tmp_path)).publish("2026-06-03")
    text = latest.read_text(encoding="utf-8")
    assert "cultural_reflection" in text
    assert "sky_note" in text
    assert "daily_recipes" in text
    assert "Tasting History" in text
    assert "Aphrodite" in text
    assert "Gemini" in text
    assert "preparation after Pentecost" in text
    assert "πολιτιστικό παραλληλισμό" in text
    db.close()


def test_website_publisher_exports_parallel_traditions(tmp_path):
    db = make_db(tmp_path)
    db.cursor.execute("""
        INSERT INTO parallel_traditions
        (date, orthodox_title, ancient_title, relationship_note)
        VALUES (?, ?, ?, ?)
    """, (
        "2026-04-12",
        "Orthodox Easter customs",
        "Ancient spring renewal customs",
        "A cultural comparison only.",
    ))
    db.conn.commit()
    latest, _ = WebsitePublisher(db, str(tmp_path)).publish("2026-04-12")
    text = latest.read_text(encoding="utf-8")
    assert "parallel_traditions" in text
    assert "sky_note" in text
    assert "Orthodox Easter customs" in text
    assert "Ancient spring renewal customs" in text
    db.close()


def test_template_commentary_generator_returns_bilingual_public_draft():
    commentary = CommentaryGenerator("template").generate({
        "date": "2026-06-02",
        "namedays": [{"names": "Alkis, Maria"}],
        "holidays": [{"name": "Local Holiday"}],
        "quotes": [{"quote": "Μέτρον άριστον", "author": "Public-domain proverb"}],
        "historical_events": [{"event": "A Greek historical note"}],
        "parallel_traditions": [{
            "orthodox_title": "Orthodox Easter customs",
            "ancient_title": "Ancient spring renewal customs",
            "relationship_note": "Presented as thematic comparison only.",
        }],
        "custom_notes": [],
    })
    assert "Alkis, Maria" in commentary["english"]
    assert "Alkis, Maria" in commentary["greek"]
    assert "Local Holiday" in commentary["english"]
    assert "Μέτρον άριστον" in commentary["greek"]
    assert "A Greek historical note" in commentary["english"]
    assert "Orthodox Easter customs" in commentary["english"]
    assert "Ancient spring renewal customs" in commentary["greek"]
    assert commentary["review_required"] is True
    assert commentary["provider"] == "template"


def test_template_commentary_has_clean_greek_fallback_when_data_missing():
    commentary = CommentaryGenerator("template").generate({
        "date": "2026-06-03",
        "namedays": [],
        "holidays": [],
        "quotes": [],
        "historical_events": [],
        "parallel_traditions": [],
        "custom_notes": [],
    })
    assert "the names celebrated today" not in commentary["greek"]
    assert "μόνο μετά από έλεγχο" in commentary["greek"]
    assert "Wednesday, 03 June 2026" in commentary["english"]
    assert "3 Ιουνίου 2026" in commentary["greek"]


def test_template_commentary_uses_fasting_for_meaningful_parallel_context():
    commentary = CommentaryGenerator("template").generate({
        "date": "2026-06-03",
        "namedays": [],
        "holidays": [],
        "fasting": {
            "name": "Apostles' Fast",
            "fasting_type": "minor_fast",
            "description": "Period of fasting between Pentecost and the feast of St. Peter and St. Paul",
        },
        "quotes": [],
        "historical_events": [],
        "parallel_traditions": [],
        "custom_notes": [],
    })
    assert "preparation after Pentecost" in commentary["english"]
    assert "Thargelia" in commentary["english"]
    assert "Skira" in commentary["english"]
    assert "Moon:" in commentary["english"]
    assert "Gemini" in commentary["english"]
    assert "Νηστείας των Αγίων Αποστόλων" in commentary["greek"]
    assert "αρχαιοελληνικός παραλληλισμός" in commentary["greek"]


def test_duplicate_send_is_skipped_unless_forced(tmp_path):
    db = make_db(tmp_path)
    contact_id = db.add_contact("Test", "306900000000")
    db.log_message(contact_id, "2026-06-01", "previous", "sent", "manual")
    notifier = Mock(provider="manual")
    notifier.send_batch.return_value = {"total": 0, "sent": 0, "failed": 0, "details": []}
    sender = BulkMessageSender(notifier, db)
    with patch("whatsapp_notifier.datetime") as clock:
        clock.now.return_value.strftime.return_value = "2026-06-01"
        result = sender.send_daily_message("new")
        forced = sender.send_daily_message("forced", force=True)
    assert result["skipped"] == 1
    assert notifier.send_batch.call_args_list[0].args[0] == []
    assert len(notifier.send_batch.call_args_list[1].args[0]) == 1
    assert forced["skipped"] == 0
    db.close()
