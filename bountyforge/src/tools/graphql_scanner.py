
import requests
import json
from typing import Dict, List

class GraphQLScanner:
    def __init__(self, proxy=None):
        self.proxy = proxy
        self.session = requests.Session()

    async def introspect(self, url: str) -> Dict:
        """Dump entire GraphQL schema."""
        query = """
        query IntrospectionQuery {
            __schema {
                types {
                    name
                    kind
                    description
                    fields {
                        name
                        type {
                            name
                            kind
                        }
                    }
                }
            }
        }
        """
        payload = {"query": query}
        proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
        response = self.session.post(url, json=payload, proxies=proxies, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            # Check for IDOR potential (fields like "id", "user", "email")
            fields = data.get('data', {}).get('__schema', {}).get('types', [])
            idor_fields = []
            for t in fields:
                if t.get('fields'):
                    for f in t['fields']:
                        if f['name'] in ['id', 'userId', 'accountId', 'email', 'phone']:
                            idor_fields.append(f"{t['name']}.{f['name']}")
            return {
                "schema": data,
                "idor_potential": list(set(idor_fields)),
                "total_types": len(fields)
            }
        return {"error": "Introspection disabled or invalid endpoint."}

    async def test_idor(self, url: str, field: str, base_id: int = 1) -> List[Dict]:
        """Try to brute force sequential IDs."""
        findings = []
        for i in range(base_id, base_id + 10):
            test_query = f"{{ {field}(id: {i}) {{ id name email }} }}"
            payload = {"query": test_query}
            resp = self.session.post(url, json=payload)
            if resp.status_code == 200 and '"data"' in resp.text:
                findings.append({"attempt": i, "response": resp.json()})
        return findings
