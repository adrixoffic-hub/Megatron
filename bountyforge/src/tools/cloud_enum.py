import httpx
import os

class CloudEnumerator:
    def __init__(self, wordlist):
        """
        wordlist can be a list of strings or a file path (string).
        If it's a file path, we load it and strip lines.
        """
        if isinstance(wordlist, list):
            self.wordlist = wordlist
        elif isinstance(wordlist, str) and os.path.exists(wordlist):
            with open(wordlist, 'r') as f:
                self.wordlist = [line.strip() for line in f if line.strip()]
        else:
            # Fallback default
            self.wordlist = ["test", "dev", "prod", "backup"]

    async def enumerate_s3(self, domain):
        found = []
        # Try variations: domain, domain-with-dashes, and main domain
        base_names = [domain, domain.replace('.', '-')]
        # Also add the main domain (e.g., from sub.example.com -> example)
        parts = domain.split('.')
        if len(parts) >= 2:
            main_domain = '.'.join(parts[-2:])  # e.g., example.com
            base_names.append(main_domain)
        # Also add the first part (for subdomain specific buckets)
        if len(parts) >= 2:
            base_names.append(parts[0])

        for name in set(base_names):  # Remove duplicates
            for suffix in self.wordlist[:20]:  # Limit to first 20 for speed
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

        # Extract main account name (e.g., from sub.example.com -> example)
        parts = domain.split('.')
        if len(parts) >= 2:
            # Use the second-level domain as the account name (e.g., example in example.com)
            account_name = parts[-2] if len(parts) >= 2 else parts[0]
        else:
            account_name = domain

        for cont in containers:
            url = f"https://{account_name}.blob.core.windows.net/{cont}"
            try:
                resp = await httpx.get(url, timeout=5)
                if resp.status_code == 200:
                    found.append(f"{url} (accessible)")
            except:
                pass
        return found
