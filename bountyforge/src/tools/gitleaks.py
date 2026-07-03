
import asyncio
import json
from typing import List, Dict

class GitLeaksScanner:
    def __init__(self, runner):
        self.runner = runner

    async def scan_repo(self, repo_url: str) -> List[Dict]:
        """Clone and run gitleaks on a GitHub repo."""
        # Extract repo name
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        clone_cmd = ['git', 'clone', repo_url, f'/tmp/{repo_name}']
        await self.runner.run_command(clone_cmd)
        
        # Run gitleaks
        cmd = [self.runner.binaries['gitleaks'], 'detect', '--source', f'/tmp/{repo_name}', '--report-format', 'json']
        output = await self.runner.run_command(cmd)
        
        # Parse JSON output
        try:
            data = json.loads(output)
            findings = []
            for finding in data.get('leaks', []):
                findings.append({
                    "file": finding.get('file'),
                    "line": finding.get('line'),
                    "rule": finding.get('rule'),
                    "secret": finding.get('secret')[:20] + "..."  # Mask secret
                })
            return findings
        except:
            # Fallback regex scan if gitleaks not installed
            return [{"error": "Gitleaks not installed or no JSON output"}]
