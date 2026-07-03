import httpx
import os

class CloudEnumerator:
    def __init__(self, wordlist):
        if isinstance(wordlist, list):
            self.wordlist = wordlist
        elif isinstance(wordlist, str) and os.path.exists(wordlist):
            with open(wordlist, 'r') as f:
                self.wordlist = [line.strip() for line in f if line.strip()]
        else:
            self.wordlist = ["test", "dev", "prod", "backup"]

    async def enumerate_s3(self, domain):
        found = []
        parts = domain.split('.')
        base_names = [domain, domain.replace('.', '-')]
        if len(parts) >= 2:
            base_names.append('.'.join(parts[-2:]))  # main domain
            base_names.append(parts[0])              # first subdomain
        for name in set(base_names):
            for suffix in self.wordlist[:20]:
                url = f"https://{name}-{suffix}.s3.amazonaws.com"
                try:
                    resp = await httpx.head(url, timeout=5)
                    if resp.status_code in [200, 403]:
                        found.append(f"{url} ({resp.status_code})")
                except:
                    pass
        return found

    async def enumerate_azure(self, domain):
        found = []
        containers = ['web', 'static', 'backup', 'assets', 'images']
        parts = domain.split('.')
        account_name = parts[-2] if len(parts) >= 2 else parts[0]
        for cont in containers:
            url = f"https://{account_name}.blob.core.windows.net/{cont}"
            try:
                resp = await httpx.get(url, timeout=5)
                if resp.status_code == 200:
                    found.append(f"{url} (accessible)")
            except:
                pass
        return found
