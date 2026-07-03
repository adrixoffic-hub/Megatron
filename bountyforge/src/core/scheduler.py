
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio
from datetime import datetime
from typing import list
class ScanScheduler:
    def __init__(self, targets: List[str], callback, time_str: str = "02:00"):
        """
        callback: Function to execute (e.g., run_full_pipeline)
        time_str: "HH:MM" 24-hour format
        """
        self.targets = targets
        self.callback = callback
        hour, minute = map(int, time_str.split(':'))
        self.trigger = CronTrigger(hour=hour, minute=minute)
        self.scheduler = AsyncIOScheduler()

    async def run_scheduled_job(self):
        print(f"[{datetime.now()}] Scheduled scan starting for {len(self.targets)} targets...")
        for target in self.targets:
            print(f"Scanning {target}...")
            await self.callback(target)
        print("Scheduled scan complete.")

    def start(self):
        self.scheduler.add_job(
            self.run_scheduled_job,
            trigger=self.trigger,
            id="daily_scan"
        )
        self.scheduler.start()
        print(f"🕒 Scheduler started. Daily scan at {self.trigger.hour}:{self.trigger.minute}")

    def stop(self):
        self.scheduler.shutdown()
