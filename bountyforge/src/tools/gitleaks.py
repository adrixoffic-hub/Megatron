import json

class GitLeaksScanner:
    def __init__(self, runner):
        self.runner = runner

    async def scan(self, repo_url):
    repo = repo_url.split('/')[-1].replace('.git', '')
    clone_result = await self.runner.run_command(['git', 'clone', repo_url, f'/tmp/{repo}'])
    if "fatal" in clone_result.lower() or "error" in clone_result.lower():
        return [{"error": f"Git clone failed: {clone_result[:200]}"}]
    out = await self.runner.run_command([self.runner.binaries.get('gitleaks','gitleaks'), 'detect', '--source', f'/tmp/{repo}', '--report-format', 'json'])
        try:
            data = json.loads(out)
            return [{"file": f['file'], "rule": f['rule'], "secret": f['secret'][:20]+"..."} for f in data.get('leaks',[])]
        except:
            return [{"error": "No leaks found"}]
