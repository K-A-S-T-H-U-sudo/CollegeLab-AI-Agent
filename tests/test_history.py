"""
Tests for Local SQLite Audit History and Reporting.
"""

import os
import tempfile
import pytest
from database.history import HistoryDatabase


def test_history_logging_and_export():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = HistoryDatabase(db_dir=tmpdir)
        row_id = db.log_event(
            computer_id="TEST-PC-01",
            lab_name="TEST LAB",
            category="Network",
            symptoms_summary="DNS resolution failed",
            diagnosis="DNS Name Resolution Problem",
            confidence="High",
            confidence_score=0.95,
            action_performed="Flush DNS Cache",
            verification_result="Problem Resolved"
        )
        assert row_id > 0

        # Query
        records = db.get_history()
        assert len(records) == 1
        assert records[0]["computer_id"] == "TEST-PC-01"
        assert records[0]["diagnosis"] == "DNS Name Resolution Problem"

        # Export CSV
        csv_path = os.path.join(tmpdir, "test_export.csv")
        assert db.export_to_csv(csv_path) is True
        assert os.path.exists(csv_path)
        with open(csv_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "TEST-PC-01" in content
