"""
KazaALKIS Database Management Module
Handles SQLite database initialization and operations
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
import os

class KazaALKISDatabase:
    def __init__(self, db_path: str = None):
        """Initialize database connection"""
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "kazaalkis.db"
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
            print(f"✓ Connected to database: {self.db_path}")
            return True
        except Exception as e:
            print(f"✗ Database connection error: {e}")
            return False

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("✓ Database connection closed")

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
            print("✓ Database schema initialized")
            return True
        except Exception as e:
            print(f"✗ Schema initialization error: {e}")
            return False

    def _migrate_schema(self):
        """Add columns needed by newer open-data releases."""
        provenance_tables = [
            "calendar_days", "name_days", "saints", "quotes", "holidays",
            "fasting_notes", "moon_calendar"
        ]
        for table in provenance_tables:
            self._ensure_column(table, "source_reference_id", "INTEGER")

        source_columns = {
            "source_url": "TEXT",
            "licence_type": "TEXT",
            "public_domain_status": "TEXT",
            "imported_date": "TIMESTAMP",
            "confidence_level": "TEXT",
            "manual_review_required": "BOOLEAN DEFAULT 0",
        }
        for column, definition in source_columns.items():
            self._ensure_column("source_references", column, definition)

        self.cursor.execute("DROP INDEX IF EXISTS idx_message_logs_daily_success")

    def _ensure_column(self, table: str, column: str, definition: str):
        """Add a column when upgrading an existing SQLite database."""
        existing = {row[1] for row in self.cursor.execute(f"PRAGMA table_info({table})")}
        if column not in existing:
            self.cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def add_source_reference(self, source_name: str, source_url: str,
                             licence_type: str, public_domain_status: str,
                             confidence_level: str = "medium",
                             manual_review_required: bool = False,
                             source_type: str = None, record_count: int = 0):
        """Record provenance metadata and return its database ID."""
        self.cursor.execute("""
            INSERT INTO source_references
            (source_name, source_url, source_type, licence_type,
             public_domain_status, imported_date, confidence_level,
             manual_review_required, record_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            source_name, source_url, source_type, licence_type,
            public_domain_status, datetime.now().isoformat(), confidence_level,
            int(manual_review_required), record_count
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
            print(f"✓ Imported {count} name days from {json_file}")
            return count
        except Exception as e:
            print(f"✗ Error importing name days: {e}")
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
            print(f"✓ Imported {count} quotes from {json_file}")
            return count
        except Exception as e:
            print(f"✗ Error importing quotes: {e}")
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
            print(f"✓ Imported {count} holidays from {json_file}")
            return count
        except Exception as e:
            print(f"✗ Error importing holidays: {e}")
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
            print(f"✓ Imported {count} fasting periods from {json_file}")
            return count
        except Exception as e:
            print(f"✗ Error importing fasting periods: {e}")
            return 0

    def add_contact(self, name: str, phone: str, language: str = 'en', timezone: str = 'Europe/Athens'):
        """Add a contact to the database"""
        try:
            masked_phone = phone[-3:].rjust(len(phone), '*')

            self.cursor.execute("""
                INSERT INTO contacts (name, phone_number, phone_masked, language, timezone)
                VALUES (?, ?, ?, ?, ?)
            """, (name, phone, masked_phone, language, timezone))

            self.conn.commit()
            contact_id = self.cursor.lastrowid
            print(f"✓ Added contact: {name} ({masked_phone})")
            return contact_id
        except Exception as e:
            print(f"✗ Error adding contact: {e}")
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
            print(f"✗ Error retrieving today's data: {e}")
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
            self.cursor.execute("""
                INSERT INTO message_logs
                (contact_id, message_date, message_text, status, delivery_method, sent_at, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                contact_id,
                message_date,
                message_text,
                status,
                delivery_method,
                datetime.now().isoformat(),
                error_msg
            ))
            self.conn.commit()
            print(f"✓ Message logged (Contact ID: {contact_id}, Status: {status})")
            return True
        except Exception as e:
            print(f"✗ Error logging message: {e}")
            return False

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
