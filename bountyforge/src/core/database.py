import aiosqlite
import json
from datetime import datetime

class Database:
    def __init__(self, config):
        self.path = config.get('database', {}).get('path', 'bounty.db')

    async def init_db(self):
        async with aiosqlite.connect(self.path) as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT, scan_date TIMESTAMP, total_findings INTEGER,
                critical_count INTEGER, high_count INTEGER, raw_data TEXT
            )''')
            await db.execute('''CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER, host TEXT, vulnerability TEXT,
                severity TEXT, description TEXT, remediation TEXT
            )''')
            await db.commit()

    async def save_scan(self, target, findings):
        async with aiosqlite.connect(self.path) as db:
            critical = sum(1 for f in findings if f.get('severity') == 'Critical')
            high = sum(1 for f in findings if f.get('severity') == 'High')
            cur = await db.execute(
                "INSERT INTO scans (target, scan_date, total_findings, critical_count, high_count, raw_data) VALUES (?, ?, ?, ?, ?, ?)",
                (target, datetime.now(), len(findings), critical, high, json.dumps(findings))
            )
            scan_id = cur.lastrowid
            for f in findings:
                await db.execute(
                    "INSERT INTO findings (scan_id, host, vulnerability, severity, description, remediation) VALUES (?, ?, ?, ?, ?, ?)",
                    (scan_id, f.get('host'), f.get('name'), f.get('severity'), f.get('description'), f.get('remediation'))
                )
            await db.commit()
            return scan_id
