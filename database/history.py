"""
Local Audit History Database for CollegeLab AI Agent.
Stores diagnostic events in an embedded SQLite database on the local machine.
No telemetry or private data is ever uploaded externally.
"""

import os
import sqlite3
import json
import csv
import datetime
import contextlib
from typing import List, Dict, Any, Optional

import sys
import tempfile

DB_FILE_NAME = "college_lab_history.db"


def get_default_data_dir() -> str:
    """
    Determines a robust, writable directory for the SQLite database.
    Handles PyInstaller frozen environments, standard python runs, and fallback to AppData.
    """
    candidates = []
    
    # Candidate 1: Local project directory
    if getattr(sys, "frozen", False):
        candidates.append(os.path.dirname(sys.executable))
    else:
        candidates.append(os.path.dirname(os.path.abspath(__file__)))
        # Also try parent directory of database/ (project root)
        candidates.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Candidate 2: Windows %LOCALAPPDATA%
    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        candidates.append(os.path.join(local_appdata, "CollegeLabAI"))

    # Candidate 3: User home directory
    candidates.append(os.path.join(os.path.expanduser("~"), ".collegelab_ai"))

    # Candidate 4: System temp directory as ultimate fallback
    candidates.append(os.path.join(tempfile.gettempdir(), "CollegeLabAI"))

    for path in candidates:
        try:
            os.makedirs(path, exist_ok=True)
            test_file = os.path.join(path, ".write_test")
            with open(test_file, "w") as f:
                f.write("ok")
            os.remove(test_file)
            return path
        except Exception:
            continue

    return tempfile.gettempdir()


class HistoryDatabase:
    """Manages local SQLite diagnostic logs and audit history."""

    def __init__(self, db_dir: str = None):
        if db_dir is None:
            db_dir = get_default_data_dir()
        os.makedirs(db_dir, exist_ok=True)
        self.db_path = os.path.join(db_dir, DB_FILE_NAME)
        self._init_db()

    @contextlib.contextmanager
    def _get_connection(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        """Initializes schema if table does not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS diagnostic_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    computer_id TEXT NOT NULL,
                    lab_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    symptoms_summary TEXT NOT NULL,
                    diagnosis TEXT NOT NULL,
                    confidence TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    action_performed TEXT,
                    verification_result TEXT,
                    full_report_json TEXT
                )
            """)
            conn.commit()

    def log_event(
        self,
        computer_id: str,
        lab_name: str,
        category: str,
        symptoms_summary: str,
        diagnosis: str,
        confidence: str,
        confidence_score: float,
        action_performed: Optional[str] = None,
        verification_result: Optional[str] = None,
        full_report: Optional[Dict[str, Any]] = None
    ) -> int:
        """Records a completed diagnostic or resolution session."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_json = json.dumps(full_report or {})

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO diagnostic_history (
                    timestamp, computer_id, lab_name, category,
                    symptoms_summary, diagnosis, confidence, confidence_score,
                    action_performed, verification_result, full_report_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp, computer_id, lab_name, category,
                symptoms_summary, diagnosis, confidence, confidence_score,
                action_performed or "None (Observation Only)",
                verification_result or "Not Applicable",
                report_json
            ))
            conn.commit()
            return cursor.lastrowid

    def get_history(self, limit: int = 100, category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Queries historical diagnostic events."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if category_filter and category_filter != "All":
                cursor.execute("""
                    SELECT id, timestamp, computer_id, lab_name, category,
                           symptoms_summary, diagnosis, confidence, confidence_score,
                           action_performed, verification_result
                    FROM diagnostic_history
                    WHERE category = ?
                    ORDER BY id DESC LIMIT ?
                """, (category_filter, limit))
            else:
                cursor.execute("""
                    SELECT id, timestamp, computer_id, lab_name, category,
                           symptoms_summary, diagnosis, confidence, confidence_score,
                           action_performed, verification_result
                    FROM diagnostic_history
                    ORDER BY id DESC LIMIT ?
                """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_event_details(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves full JSON details for a specific historical entry."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM diagnostic_history WHERE id = ?", (event_id,))
            row = cursor.fetchone()
            if row:
                res = dict(row)
                if res.get("full_report_json"):
                    try:
                        res["full_report"] = json.loads(res["full_report_json"])
                    except Exception:
                        res["full_report"] = {}
                return res
        return None

    def export_to_csv(self, target_filepath: str) -> bool:
        """Exports diagnostic history to a CSV file for college laboratory reports."""
        try:
            history = self.get_history(limit=1000)
            if not history:
                return False

            keys = [
                "id", "timestamp", "computer_id", "lab_name", "category",
                "symptoms_summary", "diagnosis", "confidence", "confidence_score",
                "action_performed", "verification_result"
            ]

            with open(target_filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                for row in history:
                    writer.writerow({k: row.get(k, "") for k in keys})
            return True
        except Exception as e:
            print(f"[HistoryDatabase] CSV Export Error: {e}")
            return False

    def clear_all(self):
        """Clears all records from history database."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM diagnostic_history")
            conn.commit()


# Global database instance
history_db = HistoryDatabase()
