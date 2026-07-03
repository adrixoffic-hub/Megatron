import sqlite3
import json
from typing import List, Dict, Any

class RegressionEngine:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def compare_scans(self, target: str) -> Dict[str, Any]:
        """Compare the last two scans for a target."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT raw_data FROM scans WHERE target = ? ORDER BY scan_date DESC LIMIT 2",
            (target,)
        )
        rows = cursor.fetchall()
        conn.close()

        if len(rows) < 2:
            return {"error": "Need at least 2 scans for regression testing."}

        try:
            old = json.loads(rows[1][0])  # Second most recent
            new = json.loads(rows[0][0])  # Most recent
        except (json.JSONDecodeError, IndexError):
            return {"error": "Invalid scan data in database."}

        old_set = set((f.get('host', ''), f.get('name', '')) for f in old)
        new_set = set((f.get('host', ''), f.get('name', '')) for f in new)

        return {
            "fixed": list(old_set - new_set),
            "new": list(new_set - old_set),
            "persistent": list(old_set & new_set),
            "fix_rate": f"{len(old_set - new_set)}/{len(old_set)}" if old_set else "N/A"
        }
