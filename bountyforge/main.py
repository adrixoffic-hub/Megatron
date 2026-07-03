import asyncio
import sys
import os
import json
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from src.core.ai_agent import BugBountyAgent
from src.tools.runner import ToolRunner
from src.tools.masscan import MasscanWrapper
from src.tools.graphql_scanner import GraphQLScanner
from src.tools.cloud_enum import CloudEnumerator
from src.tools.gitleaks import GitLeaksScanner
from src.core.metasploit_rpc import MetasploitRPC
from src.core.regression import RegressionEngine
from src.core.summarizer import Summarizer
from src.core.scheduler import ScanScheduler
from src.core.burp_integration import BurpTraffic
import yaml

console = Console()

class BountyForge:
    def __init__(self):
        with open("config.yaml") as f:
            self.config = yaml.safe_load(f)
        self.ai = BugBountyAgent("config.yaml")
        self.runner = ToolRunner(self.config)
        self.target = None
        self.live_hosts = []

    async def menu(self):
        while True:
            console.clear()
            console.print(Panel.fit("[bold cyan]🔮 BOUNTYFORGE ZENITH (All 22 Features)[/bold cyan]", border_style="cyan"))
            console.print("[1] Set Target")
            console.print("[2] Full Recon (Subfinder + httpx)")
            console.print("[3] Nuclei + AI Triage")
            console.print("[4] Masscan (Super-fast Ports)")
            console.print("[5] Nmap Scan")
            console.print("[6] SQLMap Auto-Exploit")
            console.print("[7] Gowitness Screenshots")
            console.print("[8] TheHarvester OSINT")
            console.print("[9] Extract JS Endpoints")
            console.print("[10] Generate Custom Wordlist")
            console.print("[11] JWT Bruteforce")
            console.print("[12] WebSocket Fuzzing")
            console.print("[13] GraphQL Introspection + IDOR")
            console.print("[14] Cloud Enum (AWS/Azure)")
            console.print("[15] GitLeaks Scan")
            console.print("[16] Log4Shell AI Scan")
            console.print("[17] Metasploit Auto-Exploit (DANGER)")
            console.print("[18] Regression Testing")
            console.print("[19] AI Report Summarization")
            console.print("[20] Start Scheduler (Daily 2AM)")
            console.print("[21] Burp/ZAP Traffic Capture")
            console.print("[22] Launch Dashboard (Streamlit)")
            console.print("[0] Exit")

            choice = Prompt.ask("\n[bold yellow]Select Option[/bold yellow]")
            if choice == "0":
                sys.exit()

            if choice == "1":
                self.target = Prompt.ask("Enter domain")
                console.print(f"[green]Target set: {self.target}[/green]")
                await asyncio.sleep(1)

            elif choice == "2":
                if not self.target:
                    console.print("[red]Set target first[/red]")
                    await asyncio.sleep(1)
                    continue
                subs = await self.runner.recon_subdomains(self.target)
                self.live_hosts = await self.runner.probe_http(subs)
                console.print(f"[green]Found {len(self.live_hosts)} live hosts[/green]")
                await asyncio.sleep(2)

            elif choice == "3":
                if not self.live_hosts:
                    console.print("[red]Run Recon first[/red]")
                    await asyncio.sleep(1)
                    continue
                domains = [h.get('host') for h in self.live_hosts if h.get('host')]
                findings = await self.runner.run_nuclei(domains)
                report = await self.ai.send_prompt(f"Triage these findings: {json.dumps(findings)[:5000]}")
                console.print(Panel(report, title="AI Triage"))
                await asyncio.sleep(2)

            elif choice == "4":
                ip = Prompt.ask("Enter IP")
                wrapper = MasscanWrapper(self.runner)
                ports = await wrapper.scan_ports(ip)
                console.print(f"[green]Open ports: {ports}[/green]")
                await asyncio.sleep(2)

            elif choice == "5":
                ip = Prompt.ask("Enter IP")
                ports = await self.runner.run_nmap(ip)
                console.print(f"[green]{ports}[/green]")
                await asyncio.sleep(2)

            elif choice == "6":
                url = Prompt.ask("Enter URL with param (e.g., http://x.com?id=1)")
                out = await self.runner.run_sqlmap(url)
                console.print(Panel(out[:1000], title="SQLMap Output"))
                await asyncio.sleep(2)

            elif choice == "7":
                if not self.live_hosts:
                    console.print("[red]Run Recon first[/red]")
                    await asyncio.sleep(1)
                    continue
                urls = [h.get('url') for h in self.live_hosts if h.get('url')]
                path = await self.runner.run_gowitness(urls)
                console.print(f"[green]Screenshots saved to {path}[/green]")
                await asyncio.sleep(2)

            elif choice == "8":
                if not self.target:
                    console.print("[red]Set target first[/red]")
                    await asyncio.sleep(1)
                    continue
                emails = await self.runner.run_theharvester(self.target)
                console.print(f"[green]Emails: {emails}[/green]")
                await asyncio.sleep(2)

            elif choice == "9":
                if not self.target:
                    console.print("[red]Set target first[/red]")
                    await asyncio.sleep(1)
                    continue
                endpoints = await self.runner.extract_js_endpoints(self.target)
                console.print(f"[green]Found {len(endpoints)} JS endpoints[/green]")
                await asyncio.sleep(2)

            elif choice == "10":
                tech = Prompt.ask("Tech stack (comma separated, e.g., react,php)").split(',')
                path = await self.runner.generate_wordlist(tech, self.target)
                console.print(f"[green]Wordlist saved: {path}[/green]")
                await asyncio.sleep(2)

            elif choice == "11":
                token = Prompt.ask("Enter JWT token")
                result = await self.ai.analyze_jwt(token)
                console.print(Panel(str(result), title="JWT Analysis"))
                await asyncio.sleep(2)

            elif choice == "12":
                ws_url = Prompt.ask("Enter WS URL (ws://...)")
                msgs = ["test", "<script>alert(1)</script>", "' OR '1'='1"]
                findings = await self.ai.websocket_fuzz(ws_url, msgs)
                console.print(f"[yellow]{findings}[/yellow]")
                await asyncio.sleep(2)

            elif choice == "13":
                url = Prompt.ask("Enter GraphQL endpoint")
                scanner = GraphQLScanner()
                result = await scanner.introspect(url)
                console.print(Panel(str(result), title="GraphQL"))
                await asyncio.sleep(2)

            elif choice == "14":
                enum = CloudEnumerator(["test", "dev"])
                s3 = await enum.enumerate_s3(self.target)
                az = await enum.enumerate_azure(self.target)
                console.print(f"[green]S3: {s3}\nAzure: {az}[/green]")
                await asyncio.sleep(2)

            elif choice == "15":
                repo = Prompt.ask("GitHub repo URL")
                gitleaks = GitLeaksScanner(self.runner)
                result = await gitleaks.scan(repo)
                console.print(Panel(str(result), title="GitLeaks"))
                await asyncio.sleep(2)

            elif choice == "16":
                url = Prompt.ask("Enter URL")
                result = await self.ai.log4shell_scan(url)
                console.print(Panel(result, title="Log4Shell AI"))
                await asyncio.sleep(2)

            elif choice == "17":
                target = Prompt.ask("Enter target IP")
                msf = MetasploitRPC(self.config.get('metasploit', {}))
                result = msf.exploit(target, 80)
                console.print(f"[red]⚠️ {result}[/red]")
                await asyncio.sleep(2)

            elif choice == "18":
                reg = RegressionEngine("bounty.db")
                result = reg.compare(self.target)
                console.print(Panel(str(result), title="Regression"))
                await asyncio.sleep(2)

            elif choice == "19":
                report = Prompt.ask("Paste raw report text")
                summ = Summarizer(self.ai)
                summary = await summ.summarize(report)
                console.print(Panel(summary, title="AI Summary"))
                await asyncio.sleep(2)

            elif choice == "20":
                targets = self.config.get('scheduler', {}).get('targets', [])
                if not targets:
                    console.print("[red]Add targets in config.yaml[/red]")
                    await asyncio.sleep(1)
                    continue
                scheduler = ScanScheduler(targets, self.runner.run_nuclei)
                scheduler.start()
                console.print("[green]Scheduler started! Daily 2AM scan active.[/green]")
                await asyncio.sleep(2)

            elif choice == "21":
                url = Prompt.ask("Enter URL to browse")
                burp = BurpTraffic(
                    self.config['burp']['proxy_host'],
                    self.config['burp']['proxy_port']
                )
                result = await burp.capture(url, 30)
                console.print(f"[green]{result}[/green]")
                await asyncio.sleep(2)

            elif choice == "22":
                console.print("[green]Launching Dashboard at http://localhost:8501[/green]")
                os.system("streamlit run src/web/dashboard.py &")
                await asyncio.sleep(2)

async def main():
    forge = BountyForge()
    await forge.menu()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
