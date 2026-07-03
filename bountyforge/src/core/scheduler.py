from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import List, Callable, Awaitable, Any

class ScanScheduler:
    def __init__(self, targets: List[str], callback: Callable[[str], Awaitable[Any]], time_str: str = "02:00"):
        """
        targets: List of domains to scan
        callback: Async function that takes a single domain (str) and returns Awaitable
        time_str: "HH:MM" 24-hour format
        """
        self.targets = targets
        self.callback = callback
        try:
            hour, minute = map(int, time_str.split(':'))
            self.trigger = CronTrigger(hour=hour, minute=minute)
        except ValueError:
            self.trigger = CronTrigger(hour=2, minute=0)  # Fallback to 2 AM
        self.scheduler = AsyncIOScheduler()

    def start(self):
        """Start the scheduler."""
        for target in self.targets:
            # ✅ Fixed: pass target as a string, not wrapped in a list
            self.scheduler.add_job(
                lambda t=target: self.callback(t),   # <-- changed from self.callback([t])
                trigger=self.trigger,
                id=f"scan_{target}"
            )
        self.scheduler.start()

    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
