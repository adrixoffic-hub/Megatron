import json

class GitLeaksScanner:
    def __init__(self, runner):
        self.runner = runner

    async def scan(self, repo_url):
        repo = repo_url.split('/')[-1].replace('.git', '')
        clone_cmd = ['git', 'clone', repo_url, f'/tmp/{repo}']
        clone_out = await self.runner.run_command(clone_cmd)
        if "fatal" in clone_out.lower() or "error" in clone_out.lower():
            return [{"error": f"Git clone failed: {clone_out[:200]}"}]
        cmd = [self.runner.binaries.get('gitleaks', 'gitleaks'), 'detect', '--source', f'/tmp/{repo}', '--report-format', 'json']
        out = await self.runner.run_command(cmd)
        try:
            data = json.loads(out)
            return [{"file": f['file'], "rule": f['rule'], "secret": f['secret'][:20]+"..."} for f in data.get('leaks',[])]
        except:
            return [{"error": "No leaks found or invalid output"}]
