
import sqlite3
import json
from typing import List, Dict

class RegressionEngine:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def compare_scans(self, target: str) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, raw_data, scan_date FROM scans WHERE target = ? ORDER BY scan_date DESC LIMIT 2",
            (target,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) < 2:
            return {"error": "Need at least 2 scans for regression."}
        
        old = json.loads(rows[1][1])  # Second last
        new = json.loads(rows[0][1])  # Latest
        
        # Track by vulnerability name + host
        old_set = set((f['host'], f['name']) for f in old)
        new_set = set((f['host'], f['name']) for f in new)
        
        fixed = old_set - new_set
        new_vulns = new_set - old_set
        still_present = old_set & new_set
        
        return {
            "fixed": list(fixed),
            "new": list(new_vulns),
            "persistent": list(still_present),
            "fix_rate": f"{len(fixed)}/{len(old_set)}"
        }
