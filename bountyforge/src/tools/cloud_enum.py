import httpx
import xmltodict

class CloudEnumerator:
    def __init__(self, wordlist):
        self.wordlist = wordlist

    async def enumerate_s3(self, domain):
        found = []
        for name in [domain, domain.replace('.','-')]:
            for suffix in self.wordlist[:10]:
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
        containers = ['web','static','backup']
        for acc in [domain.split('.')[0]]:
            for cont in containers:
                url = f"https://{acc}.blob.core.windows.net/{cont}"
                try:
                    resp = await httpx.get(url, timeout=5)
                    if resp.status_code == 200:
                        found.append(f"{url} (accessible)")
                except:
                    pass
        return found
