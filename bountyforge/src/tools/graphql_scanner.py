import httpx
import json

class GraphQLScanner:
    def __init__(self, proxy=None):
        self.proxy = proxy

    async def introspect(self, url):
        async with httpx.AsyncClient(proxies=self.proxy, timeout=15.0) as client:   # added timeout
            query = "{ __schema { types { name fields { name } } } }"
            resp = await client.post(url, json={"query": query})
            if resp.status_code == 200:
                data = resp.json()
                fields = []
                for t in data.get('data',{}).get('__schema',{}).get('types',[]):
                    if t.get('fields'):
                        for f in t['fields']:
                            if f['name'] in ['id','userId','email']:
                                fields.append(f"{t['name']}.{f['name']}")
                return {"schema": data, "idor_potential": list(set(fields))}
            return {"error": "Introspection disabled"}
