import json

class GitLeaksScanner:
    def __init__(self, runner):
        self.runner = runner

    async def scan(self, repo_url):
        repo = repo_url.split('/')[-1].replace('.git','')
        await self.runner.run_command(['git', 'clone', repo_url, f'/tmp/{repo}'])
        out = await self.runner.run_command([self.runner.binaries.get('gitleaks','gitleaks'), 'detect', '--source', f'/tmp/{repo}', '--report-format', 'json'])
        try:
            data = json.loads(out)
            return [{"file": f['file'], "rule": f['rule'], "secret": f['secret'][:20]+"..."} for f in data.get('leaks',[])]
        except:
            return [{"error": "No leaks found"}]
