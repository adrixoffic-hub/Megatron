
from src.tools.runner import ToolRunner

class MasscanWrapper:
    def __init__(self, runner):
        self.runner = runner

    async def scan(self, ip, rate=10000):
        return await self.runner.run_masscan(ip, rate)
