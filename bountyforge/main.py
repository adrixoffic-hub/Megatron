
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
# Inside the menu loop, add these choices:
console.print("[13] Masscan (Super-fast port scan)")
console.print("[14] GraphQL Introspection + IDOR Check")
console.print("[15] Cloud Enumeration (AWS S3 / Azure Blob)")
console.print("[16] GitLeaks Scan (GitHub secrets)")
console.print("[17] Log4Shell Deep Scan (Nuclei + AI)")
console.print("[18] Auto-Exploit RCE (Metasploit) - DANGEROUS")
console.print("[19] Regression Testing (Compare previous scans)")
console.print("[20] AI Report Summarization (NLP)")
console.print("[21] Start Scheduler (Auto-scan daily at 2 AM)")
console.print("[22] Burp/ZAP Traffic Analyzer")

# Implement these choices by calling the respective methods from new classes.
