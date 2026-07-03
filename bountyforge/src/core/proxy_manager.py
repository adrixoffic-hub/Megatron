import random

class ProxyManager:
    def __init__(self, config):
        self.proxies = config.get('proxies', [])
        self.idx = 0

    def get_random_proxy(self):
        return random.choice(self.proxies) if self.proxies else None

    def get_round_robin(self):
        if not self.proxies:
            return None
        p = self.proxies[self.idx % len(self.proxies)]
        self.idx += 1
        return p

    def apply_to_command(self, cmd, proxy):
        if proxy and any(x in cmd[0] for x in ['httpx', 'nuclei', 'ffuf']):
            cmd.extend(['-proxy', proxy])
        return cmd
