import yaml
import asyncio
import jwt
import json
import re
import websockets                     # <-- Moved import to top for clarity
from anthropic import Anthropic, RateLimitError
from src.core.capsule import Capsule
from src.core.account_pool import AccountPool
from src.core.bypass_engine import BypassEngine

class BugBountyAgent:
    def __init__(self, config_path="config.yaml"):
        with open(config_path) as f:
            raw = yaml.safe_load(f)
        self.accounts = raw['accounts']
        self.agent_cfg = raw.get('agent', {})
        self.pool = AccountPool(self.accounts)
        self.capsule = Capsule("capsule.json", 80000)
        self.bypass = BypassEngine(raw.get('bypass', {}))
        self.semaphore = asyncio.Semaphore(self.agent_cfg.get('concurrency', 5))
        self.jwt_wordlist = raw.get('jwt', {}).get('wordlist_path', 'wordlists/jwt_secrets.txt')

    async def send_prompt(self, user_prompt, system_override=None):
        async with self.semaphore:
            messages = self.capsule.load()
            for level in range(1, 4):
                enhanced, sys_override = self.bypass.apply(user_prompt, level)
                sys_msg = system_override or sys_override or "You are a security assistant."
                for attempt in range(self.agent_cfg.get('max_retries', 3)):
                    acc = self.pool.acquire()
                    if not acc:
                        await asyncio.sleep(2)
                        continue
                    try:
                        client = Anthropic(api_key=acc.api_key)
                        temp_msgs = messages.copy()
                        if temp_msgs and temp_msgs[-1]['role'] == 'user':
                            temp_msgs[-1]['content'] = enhanced
                        else:
                            temp_msgs.append({"role": "user", "content": enhanced})
                        resp = client.messages.create(
                            model=self.agent_cfg.get('model', 'claude-3-5-sonnet-20241022'),
                            max_tokens=4096,
                            temperature=self.agent_cfg.get('temperature', 0.2),
                            system=sys_msg,
                            messages=temp_msgs
                        )
                        reply = resp.content[0].text
                        if self.bypass.detect_refusal(reply):
                            # <-- FIXED: release account before breaking to next level
                            self.pool.release(acc, 5)
                            break
                        # Success – release account and return reply
                        self.pool.release(acc, 0)          # <-- FIXED: release on success
                        messages.append({"role": "user", "content": user_prompt})
                        messages.append({"role": "assistant", "content": reply})
                        self.capsule.save(messages)
                        return reply
                    except RateLimitError:
                        self.pool.release(acc, 90)
                    except Exception:
                        self.pool.release(acc, 30)
            return "❌ All attempts failed."

    # ---- JWT Bruteforce ----
    async def analyze_jwt(self, token):
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
        except:
            return {"error": "Invalid JWT"}
        try:
            with open(self.jwt_wordlist, 'r') as f:
                secrets = f.read().splitlines()
        except:
            secrets = ["secret","password","123456"]
        for secret in secrets[:100]:
            try:
                decoded = jwt.decode(token, secret, algorithms=['HS256'])
                return {"status": "CRACKED", "secret": secret, "payload": decoded}
            except:
                pass
        return {"status": "UNCRACKED", "payload": payload}

    # ---- WebSocket Fuzzing ----
    async def websocket_fuzz(self, ws_url, messages):
        findings = []
        for msg in messages:
            try:
                async with websockets.connect(ws_url) as ws:
                    await ws.send(msg)
                    resp = await ws.recv()
                    if "error" in resp.lower() or "exception" in resp.lower():
                        findings.append({"payload": msg, "response": resp[:200]})
            except Exception as e:
                findings.append({"payload": msg, "error": str(e)})
        return findings

    # ---- Log4Shell Detection ----
    async def log4shell_scan(self, url):
        prompt = f"Check if {url} is vulnerable to Log4Shell. Provide a detailed analysis."
        return await self.send_prompt(prompt, system_override="You are a Log4Shell expert.")
