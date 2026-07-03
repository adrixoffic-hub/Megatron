import asyncio
import sys
import os
import json
import yaml

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

from src.core.ai_agent import BugBountyAgent
from src.core.metasploit_rpc import MetasploitRPC
from src.core.regression import RegressionEngine
from src.core.summarizer import Summarizer
from src.core.scheduler import ScanScheduler
from src.core.burp_integration import BurpTrafficCapture
from src.core.database import Database          # <-- added

from src.tools.runner import ToolRunner
from src.tools.masscan import MasscanWrapper
from src.tools.graphql_scanner import GraphQLScanner
from src.tools.cloud_enum import CloudEnumerator
from src.tools.gitleaks import GitLeaksScanner

console = Console()

class BountyForge:
    def __init__(self):
        try:
            with open("config.yaml") as f:
                self.config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            console.print(f"[red]Config error: {e}[/red]")
            sys.exit(1)
        self.ai = BugBountyAgent("config.yaml")
        self.runner = ToolRunner(self.config)
        self.db = Database(self.config)           # <-- instantiate DB
        self.target = None
        self.live_hosts = []

    async def menu(self):
        await self.db.init_db()                   # <-- create tables
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
                try:
                    subs = await self.runner.recon_subdomains(self.target)
                    self.live_hosts = await self.runner.probe_http(subs)
                    console.print(f"[green]Found {len(self.live_hosts)} live hosts[/green]")
                except Exception as e:
                    console.print(f"[red]Recon failed: {e}[/red]")
                await asyncio.sleep(2)

            elif choice == "3":
                if not self.live_hosts:
                    console.print("[red]Run Recon first[/red]")
                    await asyncio.sleep(1)
                    continue
                try:
                    domains = [h.get('host') for h in self.live_hosts if h.get('host')]
                    findings = await self.runner.run_nuclei(domains)
                    report = await self.ai.send_prompt(f"Triage these findings: {json.dumps(findings)[:5000]}")
                    console.print(Panel(report, title="AI Triage"))
                    # Save findings to DB
                    if findings:
                        await self.db.save_scan(self.target, findings)
                        console.print("[green]Scan results saved to database.[/green]")
                except Exception as e:
                    console.print(f"[red]Triage failed: {e}[/red]")
                await asyncio.sleep(2)

            elif choice == "4":
                ip = Prompt.ask("Enter IP")
                try:
                    wrapper = MasscanWrapper(self.runner)
                    ports = await wrapper.scan_ports(ip)
                    console.print(f"[green]Open ports: {ports}[/green]")
                except Exception as e:
                    console.print(f"[red]Masscan failed: {e}[/red]")
                await asyncio.sleep(2)

            elif choice == "5":
                ip = Prompt.ask("Enter IP")
                try:
                    ports = await self.runner.run_nmap(ip)
                    console.print(f"[green]{ports}[/green]")
                except Exception as e:
                    console.print(f"[red]Nmap failed: {e}[/red]")
                await asyncio.sleep(2)

            elif choice == "6":
                url = Prompt.ask("Enter URL with param (e.g., http://x.com?id=1)")
                try:
                    out = await self.runner.run_sqlmap(url)
                    console.print(Panel(out[:1000], title="SQLMap Output"))
                except Exception as e:
                    console.print(f"[red]SQLMap failed: {e}[/red]")
                await asyncio.sleep(2)

            elif choice == "7":
                if not self.live_hosts:
                    console.print("[red]Run Recon first[/red]")
                    await asyncio.sleep(1)
                    continue
                try:
                    urls = [h.get('url') for h in self.live_hosts if h.get('url')]
                    path = await self.runner.run_gowitness(urls)
                    console.print(f"[green]Screenshots saved to {path}[/green]")
                except Exception as e:
                    console.print(f"[red]Gowitness failed: {e}[/red]")
                await asyncio.sleep(2)

            elif choice == "8":
                if not self.target:
                    console.print("[red]Set target first[/red]")
                    await asyncio.sleep(1)
                    continue
                try:
                    emails = await self.runner.run_theharvester(self.target)
                    console.print(f"[green]Emails: {emails}[/green]")
                except Exception as e:
                    console.print(f"[red]TheHarvester failed: {e}[/red]")
                await asyncio.sleep(2)

            elif choice == "9":
                if not self.target:
                    console.print("[red]Set target first[/red]")
                    await asyncio.sleep(1)
                    continue
                try:
                    endpoints = await self.runner.extract_js_endpoints(self.target)
                    console.print(f"[green]Found {len(endpoints)} JS endpoints[/green]")
                except Exception as e:
                    console.print(f"[red]JS extraction failed: {e}[/red]")
                await asyncio.sleep(2)

            elif choice == "10":
                tech = Prompt.ask("Tech stack (comma separated, e.g., react,php)").split(',')
                try:
                    path = await self.runner.generate_wordlist(tech, self.target)
                    console.print(f"[green]Wordlist saved: {path}[/green]")
                except Exception as e:
                    console.print(f"[red]Wordlist generation failed: {e}[/red]")
                await asyncio.sleep(2)

            elif choice == "11":
                token = Prompt.ask("Enter JWT token")
                try:
                    result = await self.ai.analyze_jwt(token)
                    console.print(Panel(str(result), title="JWT Analysis"))
                except Exception as e:
                    console.print(f"[red]JWT analysis failed: {e}[/red]")
                await asyncio.sleep(2)

            elif choice == "12":
                ws_url = Prompt.ask("Enter WS URL (ws://...)")
                msgs = ["test", "<script>alert(1)</script>", "' OR '1'='1"]
                try:
                    findings = await self.ai.websocket_fuzz(ws_url, msgs)
                    console.print(f"[yellow]{findings}[/yellow]")
                except Exception as e:
                    console.print(f"[red]WebSocket fuzzing failed: {e}[/red]")
                await asyncio.sleep(2)

            elif choice == "13":
                url = Prompt.ask("Enter GraphQL endpoint")
                try:
                    scanner = GraphQLScanner()
                    result = await scanner.introspect(url)
                    console.print(Panel(str(result), title="GraphQL"))
                except Exception as e:
                    console.print(f"[red]GraphQL scan failed: {e}[/red]")
                await asyncio.sleep(2)

            elif choice == "14":
                try:
                    cloud_cfg = self.config.get('cloud', {})
                    wordlist_path = cloud_cfg.get('aws_bucket_wordlist', 'wordlists/buckets.txt')
                    enum = CloudEnumerator(wordlist_path)
                    s3 = await enum.enumerate_s3(self.target)
                    az = await enum.enumerate_azure(self.target)
                    console.print(f"[green]S3: {s3}\nAzure: {az}[/green]")
                except Exception as e:
                    console.print(f"[red]Cloud enumeration failed: {e}[/red]")
                await asyncio.sleep(2)

            elif choice == "15":
                repo = Prompt.ask("GitHub repo URL")
                try:
                    gitleaks = GitLeaksScanner(self.runner)
                    result = await gitleaks.scan(repo)
                    console.print(Panel(str(result), title="GitLeaks"))
                except Exception as e:
                    console.print(f"[red]GitLeaks failed: {e}[/red]")
                await asyncio.sleep(2)

            elif choice == "16":
                url = Prompt.ask("Enter URL")
                try:
                    result = await self.ai.log4shell_scan(url)
                    console.print(Panel(result, title="Log4Shell AI"))
                except Exception as e:
                    console.print(f"[red]Log4Shell scan failed: {e}[/red]")
                await asyncio.sleep(2)

            elif choice == "17":                           # <-- indentation fixed (16 spaces)
                target = Prompt.ask("Enter target IP")
                try:
                    msf = MetasploitRPC(self.config.get('metasploit', {}))
                    result = await msf.exploit_rce(target, 80)
                    console.print(f"[red]⚠️ {result}[/red]")
                except Exception as e:
                    console.print(f"[red]Metasploit exploit failed: {e}[/red]")
                await asyncio.sleep(2)

            elif choice == "18":
                try:
                    reg = RegressionEngine("bounty.db")
                    result = await reg.compare_scans(self.target)
                    console.print(Panel(str(result), title="Regression"))
                except Exception as e:
                    console.print(f"[red]Regression failed: {e}[/red]")
                await asyncio.sleep(2)

            elif choice == "19":
                report = Prompt.ask("Paste raw report text")
                try:
                    summ = Summarizer(self.ai)
                    summary = await summ.summarize(raw_report=report)
                    console.print(Panel(summary, title="AI Summary"))
                except Exception as e:
                    console.print(f"[red]Summarization failed: {e}[/red]")
                await asyncio.sleep(2)

            elif choice == "20":
                try:
                    targets = self.config.get('scheduler', {}).get('targets', [])
                    if not targets:
                        console.print("[red]Add targets in config.yaml[/red]")
                        await asyncio.sleep(1)
                        continue
                    scheduler = ScanScheduler(targets, lambda t: self.runner.run_nuclei([t]))
                    scheduler.start()
                    console.print("[green]Scheduler started! Daily 2AM scan active.[/green]")
                except Exception as e:
                    console.print(f"[red]Scheduler failed: {e}[/red]")
                await asyncio.sleep(2)

            elif choice == "21":
                url = Prompt.ask("Enter URL to browse")
                try:
                    burp = BurpTrafficCapture(
                        self.config['burp']['proxy_host'],
                        self.config['burp']['proxy_port']
                    )
                    result = await burp.capture(url, 30)
                    console.print(f"[green]{result}[/green]")
                except Exception as e:
                    console.print(f"[red]Burp capture failed: {e}[/red]")
                await asyncio.sleep(2)

            elif choice == "22":
                if not os.path.exists("src/web/dashboard.py"):
                    console.print("[red]Dashboard file not found![/red]")
                    await asyncio.sleep(1)
                    continue
                try:
                    console.print("[green]Launching Dashboard at http://localhost:8501[/green]")
                    os.system("streamlit run src/web/dashboard.py &")
                except Exception as e:
                    console.print(f"[red]Dashboard launch failed: {e}[/red]")
                await asyncio.sleep(2)

async def main():
    forge = BountyForge()
    await forge.menu()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
