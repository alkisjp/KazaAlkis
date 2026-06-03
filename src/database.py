"""
KazaALKIS Database Management Module
Handles SQLite database initialization and operations
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
try:
    from .path_manager import get_paths
except ImportError:
    from path_manager import get_paths

class KazaALKISDatabase:
    def __init__(self, db_path: str = None):
        """Initialize database connection"""
        if db_path is None:
            db_path = get_paths().app_db_path
        else:
            db_path = Path(db_path)

        # Ensure parent directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        """Connect to database"""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            print(f"OK: Connected to database: {self.db_path}")
            return True
        except Exception as e:
            print(f"ERROR: Database connection error: {e}")
            return False

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("OK: Database connection closed")

    def initialize_schema(self):
        """Create database schema"""
        try:
            # Calendar days table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS calendar_days (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT UNIQUE NOT NULL,
                    day_of_week TEXT,
                    week_number INTEGER,
                    moon_phase TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Name days table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS name_days (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    names TEXT,
                    saint TEXT,
                    feast_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (date) REFERENCES calendar_days(date)
                )
            """)

            # Saints table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS saints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    feast_date TEXT,
                    description TEXT,
                    icon_reference TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Quotes table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS quotes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    quote TEXT,
                    author TEXT,
                    language TEXT DEFAULT 'en',
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (date) REFERENCES calendar_days(date)
                )
            """)

            # Holidays table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS holidays (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT UNIQUE NOT NULL,
                    name TEXT,
                    type TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (date) REFERENCES calendar_days(date)
                )
            """)

            # Fasting notes table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS fasting_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    name TEXT,
                    fasting_type TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Moon calendar table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS moon_calendar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT UNIQUE NOT NULL,
                    moon_phase TEXT,
                    illumination REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (date) REFERENCES calendar_days(date)
                )
            """)

            # Source references table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS source_references (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_name TEXT,
                    source_url TEXT,
                    source_type TEXT,
                    licence_type TEXT,
                    public_domain_status TEXT,
                    imported_date TIMESTAMP,
                    confidence_level TEXT,
                    manual_review_required BOOLEAN DEFAULT 0,
                    record_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS source_registry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_name TEXT NOT NULL,
                    source_url TEXT,
                    source_type TEXT,
                    license_type TEXT,
                    public_domain_status TEXT,
                    import_date TIMESTAMP,
                    confidence_score REAL DEFAULT 0.5,
                    manual_review_required BOOLEAN DEFAULT 0,
                    record_count INTEGER DEFAULT 0,
                    last_checked_at TIMESTAMP,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self._create_canonical_content_tables()

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS historical_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    event TEXT NOT NULL,
                    source_reference_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_reference_id) REFERENCES source_references(id)
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS custom_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    note TEXT NOT NULL,
                    source_reference_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_reference_id) REFERENCES source_references(id)
                )
            """)

            # Contacts table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone_number TEXT,
                    phone_masked TEXT,
                    language TEXT DEFAULT 'en',
                    timezone TEXT DEFAULT 'Europe/Athens',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS opt_in_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_id INTEGER,
                    phone_masked TEXT,
                    event_type TEXT NOT NULL,
                    event_source TEXT,
                    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (contact_id) REFERENCES contacts(id)
                )
            """)

            # Message logs table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS message_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_id INTEGER NOT NULL,
                    message_date TEXT NOT NULL,
                    message_text TEXT,
                    status TEXT,
                    delivery_method TEXT,
                    sent_at TIMESTAMP,
                    error_message TEXT,
                    retry_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contact_id) REFERENCES contacts(id)
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS message_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_id INTEGER,
                    message_date TEXT NOT NULL,
                    channel TEXT DEFAULT 'whatsapp',
                    provider TEXT,
                    status TEXT NOT NULL,
                    phone_masked TEXT,
                    message_preview TEXT,
                    template_name TEXT,
                    provider_message_id TEXT,
                    api_response TEXT,
                    error_message TEXT,
                    retry_count INTEGER DEFAULT 0,
                    sent_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contact_id) REFERENCES contacts(id)
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_message_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    language TEXT DEFAULT 'bilingual',
                    tone TEXT DEFAULT 'friendly',
                    format TEXT DEFAULT 'whatsapp_short',
                    message_text TEXT NOT NULL,
                    source_ids TEXT,
                    commentary_ids TEXT,
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    approved_at TIMESTAMP,
                    published_at TIMESTAMP,
                    UNIQUE(date, language, tone, format)
                )
            """)

            # Configuration table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS configuration (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self._migrate_schema()
            self._attach_legacy_provenance()

            self.conn.commit()
            print("OK: Database schema initialized")
            return True
        except Exception as e:
            print(f"ERROR: Schema initialization error: {e}")
            return False

    def _create_canonical_content_tables(self):
        """Create Phase 2 canonical content tables."""
        content_tables = {
            "namedays": "name TEXT",
            "holidays": "name TEXT",
            "orthodox_calendar": "name TEXT",
            "historical_events": "title TEXT",
            "quotes": None,
            "astronomy": "title TEXT",
        }
        for table, name_column in content_tables.items():
            if table == "quotes":
                continue
            self.cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    {name_column},
                    description TEXT,
                    source_name TEXT,
                    source_url TEXT,
                    license_type TEXT,
                    import_date TIMESTAMP,
                    confidence_score REAL DEFAULT 0.5,
                    manual_review_required BOOLEAN DEFAULT 0,
                    source_registry_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_registry_id) REFERENCES source_registry(id)
                )
            """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS astronomy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                title TEXT,
                description TEXT,
                sunrise TEXT,
                sunset TEXT,
                moon_phase TEXT,
                source_name TEXT,
                source_url TEXT,
                license_type TEXT,
                import_date TIMESTAMP,
                confidence_score REAL DEFAULT 0.5,
                manual_review_required BOOLEAN DEFAULT 0,
                source_registry_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_registry_id) REFERENCES source_registry(id)
            )
        """)

    def _migrate_schema(self):
        """Add columns needed by newer open-data releases."""
        provenance_tables = [
            "calendar_days", "name_days", "saints", "quotes", "holidays",
            "fasting_notes", "moon_calendar", "historical_events", "custom_notes",
            "namedays", "orthodox_calendar", "astronomy"
        ]
        for table in provenance_tables:
            self._ensure_column(table, "source_reference_id", "INTEGER")

        content_tables = [
            "name_days", "namedays", "holidays", "orthodox_calendar",
            "historical_events", "quotes", "astronomy", "saints",
            "fasting_notes", "moon_calendar", "custom_notes"
        ]
        content_columns = {
            "title": "TEXT",
            "description": "TEXT",
            "source_name": "TEXT",
            "source_url": "TEXT",
            "license_type": "TEXT",
            "import_date": "TIMESTAMP",
            "confidence_score": "REAL DEFAULT 0.5",
            "manual_review_required": "BOOLEAN DEFAULT 0",
            "source_registry_id": "INTEGER",
            "updated_at": "TIMESTAMP",
            "license_type": "TEXT",
        }
        for table in content_tables:
            for column, definition in content_columns.items():
                self._ensure_column(table, column, definition)

        source_columns = {
            "source_url": "TEXT",
            "license_type": "TEXT",
            "licence_type": "TEXT",
            "public_domain_status": "TEXT",
            "imported_date": "TIMESTAMP",
            "import_date": "TIMESTAMP",
            "confidence_level": "TEXT",
            "confidence_score": "REAL DEFAULT 0.5",
            "manual_review_required": "BOOLEAN DEFAULT 0",
        }
        for column, definition in source_columns.items():
            self._ensure_column("source_references", column, definition)

        contact_columns = {
            "phone": "TEXT",
            "opt_in_status": "TEXT DEFAULT 'unknown'",
            "active": "BOOLEAN DEFAULT 1",
            "updated_at": "TIMESTAMP",
        }
        for column, definition in contact_columns.items():
            self._ensure_column("contacts", column, definition)

        astronomy_columns = {
            "sunrise": "TEXT",
            "sunset": "TEXT",
            "moon_phase": "TEXT",
        }
        for column, definition in astronomy_columns.items():
            self._ensure_column("astronomy", column, definition)

        compatibility_columns = {
            "historical_events": {"event": "TEXT"},
            "custom_notes": {"note": "TEXT"},
            "namedays": {"name": "TEXT"},
        }
        for table, columns in compatibility_columns.items():
            for column, definition in columns.items():
                self._ensure_column(table, column, definition)

        message_columns = {
            "phone_masked": "TEXT",
            "template_name": "TEXT",
            "provider_message_id": "TEXT",
            "api_response": "TEXT",
        }
        for column, definition in message_columns.items():
            self._ensure_column("message_logs", column, definition)

        self.cursor.execute("DROP INDEX IF EXISTS idx_message_logs_daily_success")
        self._backfill_phase2_columns()

        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_namedays_date ON namedays(date)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_holidays_date ON holidays(date)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_orthodox_calendar_date ON orthodox_calendar(date)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_historical_events_date ON historical_events(date)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_quotes_date ON quotes(date)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_astronomy_date ON astronomy(date)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_message_log_date_status ON message_log(message_date, status)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_opt_in ON contacts(opt_in_status, active)")

    def _ensure_column(self, table: str, column: str, definition: str):
        """Add a column when upgrading an existing SQLite database."""
        existing = {row[1] for row in self.cursor.execute(f"PRAGMA table_info({table})")}
        if column not in existing:
            self.cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def _backfill_phase2_columns(self):
        """Populate new compatibility columns from legacy fields."""
        self.cursor.execute("""
            UPDATE contacts
            SET phone = COALESCE(phone, phone_number),
                active = COALESCE(active, is_active),
                updated_at = COALESCE(updated_at, created_at)
        """)
        self.cursor.execute("""
            UPDATE name_days
            SET title = COALESCE(title, names),
                description = COALESCE(description, saint),
                updated_at = COALESCE(updated_at, created_at)
        """)
        self.cursor.execute("""
            UPDATE holidays
            SET title = COALESCE(title, name),
                updated_at = COALESCE(updated_at, created_at)
        """)
        self.cursor.execute("""
            UPDATE quotes
            SET title = COALESCE(title, author),
                description = COALESCE(description, quote),
                updated_at = COALESCE(updated_at, created_at)
        """)
        self.cursor.execute("""
            UPDATE historical_events
            SET title = COALESCE(title, event),
                description = COALESCE(description, event),
                updated_at = COALESCE(updated_at, created_at)
        """)
        self.cursor.execute("""
            INSERT INTO namedays
            (date, name, description, source_registry_id, source_reference_id,
             created_at, updated_at)
            SELECT nd.date, nd.names, nd.saint, nd.source_registry_id,
                   nd.source_reference_id, nd.created_at, nd.created_at
            FROM name_days nd
            WHERE NOT EXISTS (
                SELECT 1 FROM namedays n
                WHERE n.date = nd.date AND COALESCE(n.name, '') = COALESCE(nd.names, '')
            )
        """)

    def add_source_reference(self, source_name: str, source_url: str,
                             licence_type: str, public_domain_status: str,
                             confidence_level: str = "medium",
                             manual_review_required: bool = False,
                             source_type: str = None, record_count: int = 0):
        """Record provenance metadata and return its database ID."""
        self.cursor.execute("""
            INSERT INTO source_references
            (source_name, source_url, source_type, licence_type, license_type,
             public_domain_status, imported_date, confidence_level,
             manual_review_required, record_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            source_name, source_url, source_type, licence_type, licence_type,
            public_domain_status, datetime.now().isoformat(), confidence_level,
            int(manual_review_required), record_count
        ))
        self.conn.commit()
        return self.cursor.lastrowid

    def add_source_registry_entry(self, source_name: str, source_url: str,
                                  license_type: str, public_domain_status: str,
                                  source_type: str = None,
                                  confidence_score: float = 0.5,
                                  manual_review_required: bool = False,
                                  record_count: int = 0,
                                  notes: str = None):
        """Record a Phase 2 canonical source-registry entry."""
        self.cursor.execute("""
            INSERT INTO source_registry
            (source_name, source_url, source_type, license_type,
             public_domain_status, import_date, confidence_score,
             manual_review_required, record_count, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            source_name, source_url, source_type, license_type,
            public_domain_status, datetime.now().isoformat(),
            confidence_score, int(manual_review_required), record_count, notes
        ))
        self.conn.commit()
        return self.cursor.lastrowid

    def _get_manual_review_source(self, source_url: str = "local://legacy-sample-data"):
        """Return a conservative provenance record for unverified local samples."""
        self.cursor.execute("""
            SELECT id FROM source_references
            WHERE source_name = ? AND source_url = ?
            LIMIT 1
        """, ("Bundled sample data - review required", source_url))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        return self.add_source_reference(
            source_name="Bundled sample data - review required",
            source_url=source_url,
            licence_type="UNKNOWN - DO NOT PUBLISH",
            public_domain_status="unverified",
            confidence_level="low",
            manual_review_required=True,
            source_type="local_sample",
        )

    def _attach_legacy_provenance(self):
        """Mark pre-migration content for review instead of treating it as cleared."""
        tables = ("name_days", "quotes", "holidays", "fasting_notes")
        needs_source = any(
            self.cursor.execute(
                f"SELECT 1 FROM {table} WHERE source_reference_id IS NULL LIMIT 1"
            ).fetchone()
            for table in tables
        )
        if not needs_source:
            return
        source_id = self._get_manual_review_source()
        for table in tables:
            self.cursor.execute(
                f"UPDATE {table} SET source_reference_id = ? "
                "WHERE source_reference_id IS NULL",
                (source_id,)
            )

    def import_namedays_from_json(self, json_file: str, source_reference_id: int = None):
        """Import name days from JSON file"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                namedays = json.load(f)

            count = 0
            source_reference_id = source_reference_id or self._get_manual_review_source(
                Path(json_file).resolve().as_uri()
            )
            for item in namedays:
                self.cursor.execute("""
                    INSERT OR REPLACE INTO name_days
                    (date, names, saint, feast_name, source_reference_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    item.get('date'),
                    item.get('names'),
                    item.get('saint'),
                    item.get('names'),
                    source_reference_id or item.get('source_reference_id')
                ))
                count += 1

            self.conn.commit()
            print(f"OK: Imported {count} name days from {json_file}")
            return count
        except Exception as e:
            print(f"ERROR: Error importing name days: {e}")
            return 0

    def import_quotes_from_json(self, json_file: str, source_reference_id: int = None):
        """Import quotes from JSON file"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                quotes = json.load(f)

            count = 0
            source_reference_id = source_reference_id or self._get_manual_review_source(
                Path(json_file).resolve().as_uri()
            )
            for item in quotes:
                self.cursor.execute("""
                    INSERT INTO quotes
                    (date, quote, author, language, source_reference_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    item.get('date'),
                    item.get('quote'),
                    item.get('author'),
                    item.get('language', 'en'),
                    source_reference_id or item.get('source_reference_id')
                ))
                count += 1

            self.conn.commit()
            print(f"OK: Imported {count} quotes from {json_file}")
            return count
        except Exception as e:
            print(f"ERROR: Error importing quotes: {e}")
            return 0

    def import_holidays_from_json(self, json_file: str, source_reference_id: int = None):
        """Import holidays from JSON file"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                holidays = json.load(f)

            count = 0
            source_reference_id = source_reference_id or self._get_manual_review_source(
                Path(json_file).resolve().as_uri()
            )
            for item in holidays:
                self.cursor.execute("""
                    INSERT OR REPLACE INTO holidays
                    (date, name, type, description, source_reference_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    item.get('date'),
                    item.get('name'),
                    item.get('type'),
                    item.get('description', ''),
                    source_reference_id or item.get('source_reference_id')
                ))
                count += 1

            self.conn.commit()
            print(f"OK: Imported {count} holidays from {json_file}")
            return count
        except Exception as e:
            print(f"ERROR: Error importing holidays: {e}")
            return 0

    def import_fasting_from_json(self, json_file: str, source_reference_id: int = None):
        """Import fasting periods from JSON file"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                fasting_periods = json.load(f)

            count = 0
            source_reference_id = source_reference_id or self._get_manual_review_source(
                Path(json_file).resolve().as_uri()
            )
            for item in fasting_periods:
                self.cursor.execute("""
                    INSERT INTO fasting_notes
                    (start_date, end_date, name, fasting_type, description, source_reference_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    item.get('start_date'),
                    item.get('end_date'),
                    item.get('name'),
                    item.get('type'),
                    item.get('description', ''),
                    source_reference_id or item.get('source_reference_id')
                ))
                count += 1

            self.conn.commit()
            print(f"OK: Imported {count} fasting periods from {json_file}")
            return count
        except Exception as e:
            print(f"ERROR: Error importing fasting periods: {e}")
            return 0

    def add_contact(self, name: str, phone: str, language: str = 'en', timezone: str = 'Europe/Athens'):
        """Add a contact to the database"""
        try:
            masked_phone = phone[-3:].rjust(len(phone), '*')

            self.cursor.execute("""
                INSERT INTO contacts
                (name, phone_number, phone, phone_masked, language, timezone,
                 opt_in_status, is_active, active, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, phone, phone, masked_phone, language, timezone,
                "unknown", 1, 1, datetime.now().isoformat()
            ))

            self.conn.commit()
            contact_id = self.cursor.lastrowid
            print(f"OK: Added contact: {name} ({masked_phone})")
            return contact_id
        except Exception as e:
            print(f"ERROR: Error adding contact: {e}")
            return None

    def get_today_data(self, date_str: str = None):
        """Get all today's data for message composition"""
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')

        try:
            result = {
                'date': date_str,
                'namedays': [],
                'quotes': [],
                'holidays': [],
                'fasting': None,
                'historical_events': [],
                'custom_notes': []
            }

            self.cursor.execute("""
                SELECT names, saint FROM name_days WHERE date = ?
            """, (date_str,))
            result['namedays'] = [dict(row) for row in self.cursor.fetchall()]

            self.cursor.execute("""
                SELECT quote, author, language FROM quotes WHERE date = ?
            """, (date_str,))
            result['quotes'] = [dict(row) for row in self.cursor.fetchall()]

            self.cursor.execute("""
                SELECT name, type FROM holidays WHERE date = ?
            """, (date_str,))
            result['holidays'] = [dict(row) for row in self.cursor.fetchall()]

            self.cursor.execute("""
                SELECT name, fasting_type FROM fasting_notes
                WHERE ? BETWEEN start_date AND end_date
            """, (date_str,))
            fasting = self.cursor.fetchone()
            if fasting:
                result['fasting'] = dict(fasting)

            self.cursor.execute("""
                SELECT event FROM historical_events WHERE date = ?
            """, (date_str,))
            result['historical_events'] = [dict(row) for row in self.cursor.fetchall()]

            self.cursor.execute("""
                SELECT note FROM custom_notes WHERE date = ?
            """, (date_str,))
            result['custom_notes'] = [dict(row) for row in self.cursor.fetchall()]

            return result
        except Exception as e:
            print(f"ERROR: Error retrieving today's data: {e}")
            return None

    def was_sent_today(self, contact_id: int, message_date: str) -> bool:
        """Return whether a successful message already exists for this contact/day."""
        self.cursor.execute("""
            SELECT 1 FROM message_logs
            WHERE contact_id = ? AND message_date = ? AND status = 'sent'
            LIMIT 1
        """, (contact_id, message_date))
        return self.cursor.fetchone() is not None

    def get_validation_warnings(self):
        """Return records needing provenance or data-quality attention."""
        warnings = {
            "missing_source": [],
            "missing_licence": [],
            "duplicate_names": [],
            "duplicate_quotes": [],
            "movable_feast_uncertainty": [],
            "manual_review_required": [],
        }
        for table in ("name_days", "quotes", "holidays", "historical_events", "custom_notes"):
            warnings["missing_source"].extend(
                [(table, row[0]) for row in self.cursor.execute(
                    f"SELECT id FROM {table} WHERE source_reference_id IS NULL"
                )]
            )
        warnings["missing_licence"] = list(self.cursor.execute("""
            SELECT id, source_name FROM source_references
            WHERE licence_type IS NULL OR TRIM(licence_type) = ''
        """))
        warnings["duplicate_names"] = list(self.cursor.execute("""
            SELECT date, names, COUNT(*) FROM name_days
            GROUP BY date, names HAVING COUNT(*) > 1
        """))
        warnings["duplicate_quotes"] = list(self.cursor.execute("""
            SELECT quote, COUNT(*) FROM quotes
            GROUP BY quote HAVING COUNT(*) > 1
        """))
        warnings["movable_feast_uncertainty"] = list(self.cursor.execute("""
            SELECT id, name FROM holidays
            WHERE LOWER(COALESCE(name, '')) LIKE '%easter%'
               OR LOWER(COALESCE(name, '')) LIKE '%pentecost%'
        """))
        warnings["manual_review_required"] = list(self.cursor.execute("""
            SELECT id, source_name FROM source_references
            WHERE manual_review_required = 1
        """))
        return warnings

    def log_message(self, contact_id: int, message_date: str, message_text: str,
                   status: str, delivery_method: str, error_msg: str = None):
        """Log a message send attempt"""
        try:
            phone_masked = None
            self.cursor.execute("SELECT phone_masked FROM contacts WHERE id = ?", (contact_id,))
            contact = self.cursor.fetchone()
            if contact:
                phone_masked = contact["phone_masked"]
            self.cursor.execute("""
                INSERT INTO message_logs
                (contact_id, message_date, message_text, status, delivery_method,
                 sent_at, error_message, phone_masked)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                contact_id,
                message_date,
                message_text,
                status,
                delivery_method,
                datetime.now().isoformat(),
                error_msg,
                phone_masked
            ))
            self.cursor.execute("""
                INSERT INTO message_log
                (contact_id, message_date, provider, status, phone_masked,
                 message_preview, error_message, sent_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                contact_id, message_date, delivery_method, status, phone_masked,
                message_text[:160] if message_text else None, error_msg,
                datetime.now().isoformat()
            ))
            self.conn.commit()
            print(f"OK: Message logged (Contact ID: {contact_id}, Status: {status})")
            return True
        except Exception as e:
            print(f"ERROR: Error logging message: {e}")
            return False

    def get_schema_summary(self):
        """Return table and column metadata for tests and dashboard checks."""
        tables = [
            row[0] for row in self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
        ]
        return {
            table: [row[1] for row in self.cursor.execute(f"PRAGMA table_info({table})")]
            for table in tables
        }

if __name__ == "__main__":
    db = KazaALKISDatabase()
    if db.connect():
        db.initialize_schema()

        data_path = Path(__file__).parent.parent / "data"
        db.import_namedays_from_json(str(data_path / "kazamias_namedays_2026.json"))
        db.import_quotes_from_json(str(data_path / "kazamias_quotes_2026.json"))
        db.import_holidays_from_json(str(data_path / "greek_holidays_2026.json"))
        db.import_fasting_from_json(str(data_path / "fasting_periods_2026.json"))

        today_data = db.get_today_data()
        print(f"\nToday's data: {today_data}")

        db.close()
