# Data Importer Module
# Handles importing from various Kazamias data sources

import csv
import json
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

if __name__ == "__main__":
    print("Data importer module loaded")
