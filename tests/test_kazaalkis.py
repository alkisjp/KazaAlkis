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
    for table in ("namedays", "holidays", "orthodox_calendar", "historical_events", "quotes", "astronomy"):
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
    assert "Γεια" in text
    db.close()


def test_template_commentary_generator_returns_bilingual_public_draft():
    commentary = CommentaryGenerator("template").generate({
        "date": "2026-06-02",
        "namedays": [{"names": "Alkis, Maria"}],
        "holidays": [],
        "quotes": [],
        "historical_events": [],
        "custom_notes": [],
    })
    assert commentary["english"]
    assert commentary["greek"]
    assert commentary["review_required"] is True
    assert commentary["provider"] == "template"


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
