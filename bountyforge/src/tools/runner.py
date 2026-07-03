import asyncio
import json
import re
import os
import httpx                     # <-- Added for async HTTP
from src.core.proxy_manager import ProxyManager
from src.core.notifier import Notifier

class ToolRunner:
    def __init__(self, config):
        self.binaries = config.get('tools', {})
        self.proxy_manager = ProxyManager(config)
        self.notifier = Notifier(config)

    async def run_command(self, cmd, use_proxy=True):
        if use_proxy:
            proxy = self.proxy_manager.get_random_proxy()
            cmd = self.proxy_manager.apply_to_command(cmd, proxy)
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0 and stderr:
            print(f"⚠️ Cmd error: {stderr.decode()[:200]}")
        return stdout.decode()

    async def recon_subdomains(self, domain):
        cmd = [self.binaries.get('subfinder', 'subfinder'), '-d', domain, '-silent']
        out = await self.run_command(cmd)
        return [l.strip() for l in out.splitlines() if l]

    async def probe_http(self, domains):
        with open('/tmp/domains.txt', 'w') as f:
            f.write('\n'.join(domains))
        cmd = [self.binaries.get('httpx', 'httpx'), '-l', '/tmp/domains.txt', '-status-code', '-title', '-tech-detect', '-json', '-silent']
        out = await self.run_command(cmd)
        results = []
        for line in out.splitlines():
            try:
                results.append(json.loads(line))
            except:
                pass
        return results

    async def run_nuclei(self, domains, severity="critical,high"):
        with open('/tmp/nuclei_targets.txt', 'w') as f:
            f.write('\n'.join(domains))
        cmd = [self.binaries.get('nuclei', 'nuclei'), '-l', '/tmp/nuclei_targets.txt', '-severity', severity, '-json', '-silent']
        out = await self.run_command(cmd)
        findings = []
        for line in out.splitlines():
            try:
                findings.append(json.loads(line))
            except:
                pass
        return findings

    # ---- Masscan ----
    async def run_masscan(self, ip, rate=10000):
        cmd = [self.binaries.get('masscan', 'masscan'), '-p1-65535', ip, '--rate', str(rate), '-oG', '-']
        out = await self.run_command(cmd)
        ports = re.findall(r'(\d+)/open/([^/]+)/([^\s,]+)', out)
        return [{"port": p[0], "protocol": p[1], "service": p[2]} for p in ports]

    # ---- Nmap ----
    async def run_nmap(self, ip):
        cmd = [self.binaries.get('nmap', 'nmap'), '-T4', '-p-', ip, '-oG', '-']
        out = await self.run_command(cmd)
        ports = re.findall(r'(\d+)/open/([^/]+)/([^\s]+)', out)
        return [{"port": p[0], "service": p[1], "version": p[2]} for p in ports]

    # ---- SQLMap ----
    async def run_sqlmap(self, url, params=""):
        cmd = [self.binaries.get('sqlmap', 'sqlmap'), '-u', url, '--batch', '--threads', '5']
        if params:
            cmd.extend(['-p', params])
        return await self.run_command(cmd)

    # ---- Gowitness (FIXED: create directory) ----
    async def run_gowitness(self, urls):
        os.makedirs("./screenshots", exist_ok=True)          # <-- FIX: ensure folder exists
        with open('/tmp/shot.txt', 'w') as f:
            f.write('\n'.join(urls))
        cmd = [self.binaries.get('gowitness', 'gowitness'), 'file', '-f', '/tmp/shot.txt', '--destination', './screenshots/']
        await self.run_command(cmd)
        return "./screenshots/"

    # ---- TheHarvester ----
    async def run_theharvester(self, domain):
        cmd = [self.binaries.get('theharvester', 'theharvester'), '-d', domain, '-b', 'google,linkedin']
        out = await self.run_command(cmd)
        return list(set(re.findall(r'[\w\.-]+@[\w\.-]+', out)))

    # ---- JS Endpoint Extraction (FIXED: use httpx instead of curl) ----
    async def extract_js_endpoints(self, domain):
        cmd = [self.binaries.get('katana', 'katana'), '-u', f"https://{domain}", '-jc', '-silent']
        out = await self.run_command(cmd)
        js_urls = [l for l in out.splitlines() if '.js' in l]
        endpoints = set()
        async with httpx.AsyncClient(timeout=10.0) as client:   # <-- FIX: httpx replaces curl
            for js in js_urls[:30]:
                try:
                    resp = await client.get(js)
                    if resp.status_code == 200:
                        content = resp.text
                        endpoints.update(re.findall(r'["\'](/[a-zA-Z0-9/_.-]+)["\']', content))
                except Exception:
                    continue
        return list(endpoints)

    # ---- Custom Wordlist ----
    async def generate_wordlist(self, tech_stack, domain):
        base = ['admin', 'api', 'v1', 'v2', 'test', 'dev', 'backup', '.env', '.git']
        tech_map = {'react': ['component','state','redux'], 'php': ['wp-admin','plugins'], 'node': ['node_modules','dist']}
        for tech in tech_stack:
            if tech.lower() in tech_map:
                base.extend(tech_map[tech.lower()])
        os.makedirs("wordlists", exist_ok=True)
        with open(f"wordlists/{domain}_custom.txt", 'w') as f:
            f.write('\n'.join(set(base)))
        return f"wordlists/{domain}_custom.txt"
