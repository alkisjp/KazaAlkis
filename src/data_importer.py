# Data Importer Module
# Handles importing from various Kazamias data sources

import csv
import json
from datetime import date, timedelta
from pathlib import Path
from typing import List, Dict
import openpyxl
import requests

class DataImporter:
    """Import data from various sources"""

    def __init__(self, db):
        """Initialize importer"""
        self.db = db

    def import_csv(self, csv_file: str, data_type: str,
                   source_reference_id: int = None) -> int:
        """Import data from CSV file"""
        try:
            rows_imported = 0

            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    if data_type == 'namedays':
                        self.db.cursor.execute("""
                            INSERT INTO name_days (date, names, saint, source_reference_id)
                            VALUES (?, ?, ?, ?)
                        """, (row.get('date'), row.get('names'), row.get('saint'),
                              source_reference_id))

                    elif data_type == 'holidays':
                        self.db.cursor.execute("""
                            INSERT INTO holidays
                            (date, name, type, description, source_reference_id)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            row.get('date'),
                            row.get('name'),
                            row.get('type'),
                            row.get('description', ''),
                            source_reference_id
                        ))

                    elif data_type == 'proverbs':
                        self.db.cursor.execute("""
                            INSERT INTO quotes
                            (date, quote, author, language, category, source_reference_id)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            row.get('date'), row.get('quote'), row.get('author', 'Anonymous'),
                            row.get('language', 'gr'), 'proverb', source_reference_id
                        ))

                    rows_imported += 1

            self.db.conn.commit()
            print(f"✓ Imported {rows_imported} rows from {csv_file}")
            return rows_imported

        except Exception as e:
            print(f"✗ Error importing CSV: {e}")
            return 0

    def import_namedays_json(self, json_file: str, source_reference_id: int) -> int:
        """Import an open-data Greek namedays JSON file."""
        return self.db.import_namedays_from_json(json_file, source_reference_id)

    def import_manual_excel(self, excel_file: str, sheet_name: str,
                            data_type: str, source_reference_id: int) -> int:
        """Convert a simple headed worksheet to rows and import supported records."""
        workbook = openpyxl.load_workbook(excel_file, read_only=True, data_only=True)
        sheet = workbook[sheet_name]
        rows = sheet.iter_rows(values_only=True)
        headers = [str(value) for value in next(rows)]
        count = 0
        for values in rows:
            row = dict(zip(headers, values))
            if data_type == "custom_notes":
                self.db.cursor.execute("""
                    INSERT INTO custom_notes (date, note, source_reference_id)
                    VALUES (?, ?, ?)
                """, (row.get("date"), row.get("note"), source_reference_id))
                count += 1
            elif data_type == "historical_events":
                self.db.cursor.execute("""
                    INSERT INTO historical_events (date, event, source_reference_id)
                    VALUES (?, ?, ?)
                """, (row.get("date"), row.get("event"), source_reference_id))
                count += 1
        self.db.conn.commit()
        return count

    def import_openholidays(self, url: str, source_reference_id: int) -> int:
        """Import holidays from an OpenHolidays-compatible JSON response."""
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        count = 0
        for item in response.json():
            names = item.get("name", [])
            name = names[0].get("text") if names else item.get("name", "Holiday")
            self.db.cursor.execute("""
                INSERT OR REPLACE INTO holidays
                (date, name, type, description, source_reference_id)
                VALUES (?, ?, ?, ?, ?)
            """, (
                item.get("startDate"), name, "public_holiday",
                item.get("type", ""), source_reference_id
            ))
            count += 1
        self.db.conn.commit()
        return count

    def import_wikimedia_events(self, url: str, date_str: str,
                                source_reference_id: int) -> int:
        """Import Wikimedia on-this-day events from a JSON response."""
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        count = 0
        for item in response.json().get("events", []):
            text = item.get("text")
            if not text:
                continue
            self.db.cursor.execute("""
                INSERT INTO historical_events (date, event, source_reference_id)
                VALUES (?, ?, ?)
            """, (date_str, text, source_reference_id))
            count += 1
        self.db.conn.commit()
        return count

    def import_alexstyl_namedays(self, year: int,
                                 recurring_url: str = None,
                                 easter_url: str = None) -> int:
        """Import Unlicense Greek nameday seed data for a concrete year."""
        recurring_url = recurring_url or (
            "https://raw.githubusercontent.com/alexstyl/Greek-namedays/main/recurring_namedays.json"
        )
        easter_url = easter_url or (
            "https://raw.githubusercontent.com/alexstyl/Greek-namedays/main/relative_to_easter.json"
        )
        source_reference_id = self._get_alexstyl_source_reference()
        source_registry_id = self._get_alexstyl_source_registry()

        recurring = self._fetch_json(recurring_url).get("data", [])
        special = self._fetch_json(easter_url).get("special", [])
        imported = 0

        for item in recurring:
            day, month = self._parse_day_month(item.get("date"))
            if not day or not month:
                continue
            names = item.get("names") or []
            if not names:
                continue
            date_str = f"{year:04d}-{month:02d}-{day:02d}"
            imported += self._upsert_nameday_seed(
                date_str=date_str,
                names=names,
                saint="Greek nameday seed",
                source_reference_id=source_reference_id,
                source_registry_id=source_registry_id,
            )

        easter = self._orthodox_easter(year)
        for item in special:
            names = [item.get("main")] + list(item.get("variations") or [])
            names = [name for name in names if name]
            if not names:
                continue
            target_date = easter + timedelta(days=int(item.get("toEaster", 0)))
            imported += self._upsert_nameday_seed(
                date_str=target_date.isoformat(),
                names=names,
                saint="Greek Easter-relative nameday seed",
                source_reference_id=source_reference_id,
                source_registry_id=source_registry_id,
            )

        self.db.conn.commit()
        return imported

    def apply_nameday_override(self, date_str: str, names: List[str], saint: str,
                               source_name: str, source_url: str,
                               license_type: str = "REVIEWED REFERENCE",
                               confidence_score: float = 0.85) -> int:
        """Replace seed namedays for one date with a reviewed preferred entry."""
        names_text = ", ".join(dict.fromkeys(str(name).strip() for name in names if str(name).strip()))
        if not names_text:
            return 0

        source_reference_id = self._get_or_create_source_reference(
            source_name=source_name,
            source_url=source_url,
            license_type=license_type,
            public_domain_status="reviewed factual correction",
            source_type="nameday_review_reference",
            confidence_level="high",
        )
        source_registry_id = self._get_or_create_source_registry(
            source_name=source_name,
            source_url=source_url,
            license_type=license_type,
            public_domain_status="reviewed factual correction",
            source_type="nameday_review_reference",
            confidence_score=confidence_score,
            notes="Reviewed date-level correction selected by operator as preferred calendar.",
        )

        self.db.cursor.execute("DELETE FROM name_days WHERE date = ?", (date_str,))
        self.db.cursor.execute("DELETE FROM namedays WHERE date = ?", (date_str,))
        self.db.cursor.execute("""
            INSERT INTO name_days
            (date, names, saint, feast_name, source_reference_id,
             source_registry_id, source_name, source_url, license_type,
             confidence_score, manual_review_required)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date_str,
            names_text,
            saint,
            saint,
            source_reference_id,
            source_registry_id,
            source_name,
            source_url,
            license_type,
            confidence_score,
            0,
        ))
        self.db.cursor.execute("""
            INSERT INTO namedays
            (date, name, description, source_reference_id,
             source_registry_id, source_name, source_url, license_type,
             confidence_score, manual_review_required)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date_str,
            names_text,
            saint,
            source_reference_id,
            source_registry_id,
            source_name,
            source_url,
            license_type,
            confidence_score,
            0,
        ))
        self.db.conn.commit()
        return 1

    def _fetch_json(self, url: str):
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()

    def _get_alexstyl_source_reference(self) -> int:
        source_name = "alexstyl/Greek-namedays"
        source_url = "https://github.com/alexstyl/Greek-namedays"
        self.db.cursor.execute("""
            SELECT id FROM source_references
            WHERE source_name = ? AND source_url = ?
            LIMIT 1
        """, (source_name, source_url))
        row = self.db.cursor.fetchone()
        if row:
            return row[0]
        return self.db.add_source_reference(
            source_name=source_name,
            source_url=source_url,
            licence_type="Unlicense",
            public_domain_status="public-domain-style open source",
            confidence_level="medium",
            manual_review_required=True,
            source_type="nameday_seed_dataset",
        )

    def _get_or_create_source_reference(self, source_name: str, source_url: str,
                                        license_type: str, public_domain_status: str,
                                        source_type: str, confidence_level: str) -> int:
        self.db.cursor.execute("""
            SELECT id FROM source_references
            WHERE source_name = ? AND source_url = ?
            LIMIT 1
        """, (source_name, source_url))
        row = self.db.cursor.fetchone()
        if row:
            return row[0]
        return self.db.add_source_reference(
            source_name=source_name,
            source_url=source_url,
            licence_type=license_type,
            public_domain_status=public_domain_status,
            confidence_level=confidence_level,
            manual_review_required=True,
            source_type=source_type,
        )

    def _get_alexstyl_source_registry(self) -> int:
        source_name = "alexstyl/Greek-namedays"
        source_url = "https://github.com/alexstyl/Greek-namedays"
        self.db.cursor.execute("""
            SELECT id FROM source_registry
            WHERE source_name = ? AND source_url = ?
            LIMIT 1
        """, (source_name, source_url))
        row = self.db.cursor.fetchone()
        if row:
            return row[0]
        return self.db.add_source_registry_entry(
            source_name=source_name,
            source_url=source_url,
            source_type="nameday_seed_dataset",
            license_type="Unlicense",
            public_domain_status="public-domain-style open source",
            confidence_score=0.65,
            manual_review_required=True,
            notes=(
                "JSON nameday seed data. Repository uses Unlicense, but README says "
                "the list was gathered from various websites, so entries require review."
            ),
        )

    def _get_or_create_source_registry(self, source_name: str, source_url: str,
                                       license_type: str, public_domain_status: str,
                                       source_type: str, confidence_score: float,
                                       notes: str) -> int:
        self.db.cursor.execute("""
            SELECT id FROM source_registry
            WHERE source_name = ? AND source_url = ?
            LIMIT 1
        """, (source_name, source_url))
        row = self.db.cursor.fetchone()
        if row:
            return row[0]
        return self.db.add_source_registry_entry(
            source_name=source_name,
            source_url=source_url,
            source_type=source_type,
            license_type=license_type,
            public_domain_status=public_domain_status,
            confidence_score=confidence_score,
            manual_review_required=True,
            notes=notes,
        )

    def _upsert_nameday_seed(self, date_str: str, names: List[str], saint: str,
                             source_reference_id: int, source_registry_id: int) -> int:
        names_text = ", ".join(dict.fromkeys(str(name).strip() for name in names if str(name).strip()))
        if not names_text:
            return 0
        self.db.cursor.execute("""
            INSERT INTO name_days
            (date, names, saint, feast_name, source_reference_id,
             source_registry_id, source_name, source_url, license_type,
             confidence_score, manual_review_required)
            SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM name_days
                WHERE date = ? AND COALESCE(names, '') = ?
            )
        """, (
            date_str,
            names_text,
            saint,
            saint,
            source_reference_id,
            source_registry_id,
            "alexstyl/Greek-namedays",
            "https://github.com/alexstyl/Greek-namedays",
            "Unlicense",
            0.65,
            1,
            date_str,
            names_text,
        ))
        inserted = self.db.cursor.rowcount
        self.db.cursor.execute("""
            INSERT INTO namedays
            (date, name, description, source_reference_id,
             source_registry_id, source_name, source_url, license_type,
             confidence_score, manual_review_required)
            SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM namedays
                WHERE date = ? AND COALESCE(name, '') = ?
            )
        """, (
            date_str,
            names_text,
            saint,
            source_reference_id,
            source_registry_id,
            "alexstyl/Greek-namedays",
            "https://github.com/alexstyl/Greek-namedays",
            "Unlicense",
            0.65,
            1,
            date_str,
            names_text,
        ))
        return max(inserted, self.db.cursor.rowcount)

    def _parse_day_month(self, value: str):
        try:
            day, month = str(value).split("/", 1)
            return int(day), int(month)
        except (TypeError, ValueError):
            return None, None

    def _orthodox_easter(self, year: int) -> date:
        """Meeus Julian algorithm converted to Gregorian date."""
        a = year % 4
        b = year % 7
        c = year % 19
        d = (19 * c + 15) % 30
        e = (2 * a + 4 * b - d + 34) % 7
        month = (d + e + 114) // 31
        day = ((d + e + 114) % 31) + 1
        julian_easter = date(year, month, day)
        return julian_easter + timedelta(days=13)

if __name__ == "__main__":
    print("Data importer module loaded")
