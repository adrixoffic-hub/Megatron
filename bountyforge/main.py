
import asyncio
import re
from typing import List

class MasscanWrapper:
    def __init__(self, runner):
        self.runner = runner  # ToolRunner instance

    async def scan_ports(self, ip: str, rate: int = 10000) -> List[dict]:
        """Scan all 65535 ports with high speed."""
        cmd = [self.runner.binaries['masscan'], '-p1-65535', ip, '--rate', str(rate), '-oG', '-']
        output = await self.runner.run_command(cmd)
        ports = []
        for line in output.splitlines():
            if 'open' in line:
                parts = line.split()
                # Format: #1 Ports: 22/open/tcp//ssh///, 443/open/tcp//https///
                match = re.findall(r'(\d+)/open/([^/]+)/([^\s,]+)', line)
                for p in match:
                    ports.append({"port": p[0], "protocol": p[1], "service": p[2]})
        return ports
