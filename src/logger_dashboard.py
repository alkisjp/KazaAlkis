"""
Logger and Dashboard Module for KazaALKIS
Provides logging and dashboard functionality
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import json
try:
    from .path_manager import get_paths
except ImportError:
    from path_manager import get_paths

class KazaALKISLogger:
    """Logging system for KazaALKIS"""

    def __init__(self, log_dir: str = None):
        """Initialize logger"""
        if log_dir is None:
            log_dir = get_paths().app_log_dir
        else:
            log_dir = Path(log_dir)

        log_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir = log_dir
        self.log_file = log_dir / f"kazaalkis_{datetime.now().strftime('%Y%m%d')}.log"

    def log(self, level: str, message: str, context: str = ""):
        """Log a message"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] {context}: {message}\n"

        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error writing to log: {e}")

    def info(self, message: str, context: str = ""):
        """Log info message"""
        self.log("INFO", message, context)

    def warning(self, message: str, context: str = ""):
        """Log warning message"""
        self.log("WARNING", message, context)

    def error(self, message: str, context: str = ""):
        """Log error message"""
        self.log("ERROR", message, context)

    def success(self, message: str, context: str = ""):
        """Log success message"""
        self.log("SUCCESS", message, context)

class KazaALKISDashboard:
    """Dashboard for KazaALKIS status and information"""

    def __init__(self, db):
        """Initialize dashboard"""
        self.db = db

    def show_dashboard(self):
        """Display dashboard"""
        print("\n" + "="*70)

    def show_validation_dashboard(self):
        """Display provenance and data-quality warnings."""
        warnings = self.db.get_validation_warnings()
        print("\n" + "="*70)
        print("KazaALKIS Open-Data Validation Dashboard")
        print("="*70)
        for name, rows in warnings.items():
            print(f"  {name.replace('_', ' ').title()}: {len(rows)}")
        print("="*70 + "\n")
        print("KazaALKIS Dashboard")
        print("="*70 + "\n")

        print("📅 Today's Message")
        print("-" * 70)
        today_data = self.db.get_today_data()

        if today_data:
            print(f"  Date: {today_data['date']}")
            print(f"  Name Days: {len(today_data['namedays'])} found")
            print(f"  Holidays: {len(today_data['holidays'])} found")
            print(f"  Quotes: {len(today_data['quotes'])} found")
            if today_data['fasting']:
                print(f"  Fasting: {today_data['fasting']['name']}")
        else:
            print("  ✗ No data available for today")

        print("\n👥 Contacts Summary")
        print("-" * 70)
        try:
            self.db.cursor.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active
                FROM contacts
            """)
            result = self.db.cursor.fetchone()

            if result:
                total = result[0]
                active = result[1] if result[1] else 0
                print(f"  Total Contacts: {total}")
                print(f"  Active Contacts: {active}")
                print(f"  Inactive: {total - active}")
        except Exception as e:
            print(f"  ✗ Error: {e}")

        print("\n" + "="*70)
