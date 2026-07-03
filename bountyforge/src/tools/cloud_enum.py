
import requests
import xmltodict
from typing import List

class CloudEnumerator:
    def __init__(self, wordlist_path: str):
        self.wordlist = self._load_wordlist(wordlist_path)

    def _load_wordlist(self, path):
        try:
            with open(path, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except:
            return ["test", "dev", "prod", "backup", "assets"]

    async def enumerate_aws_s3(self, domain: str) -> List[str]:
        """Check for public readable S3 buckets."""
        # Common patterns: bucket = domain, subdomain.domain, etc.
        names = [domain, domain.replace('.', '-'), domain.split('.')[0]]
        found = []
        for name in names:
            for suffix in self.wordlist[:10]:
                bucket_name = f"{name}-{suffix}"
                url = f"https://{bucket_name}.s3.amazonaws.com"
                try:
                    resp = requests.head(url, timeout=5)
                    if resp.status_code == 200:
                        found.append(f"{url} (public read access)")
                    elif resp.status_code == 403:
                        found.append(f"{url} (exists, but private)")
                except:
                    pass
        return found

    async def enumerate_azure_blob(self, domain: str) -> List[str]:
        """Check for Azure Blob containers."""
        # Azure format: https://<account>.blob.core.windows.net/<container>
        names = [domain.split('.')[0], domain.replace('.', '')]
        found = []
        containers = ["web", "static", "images", "backup", "config"]
        for account in names:
            for container in containers:
                url = f"https://{account}.blob.core.windows.net/{container}"
                try:
                    resp = requests.get(url, timeout=5)
                    if resp.status_code == 200:
                        # Parse XML if exists
                        try:
                            data = xmltodict.parse(resp.text)
                            found.append(f"{url} (accessible: {data})")
                        except:
                            found.append(f"{url} (accessible)")
                except:
                    pass
        return found
