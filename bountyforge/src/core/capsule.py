import json
import os
import tiktoken

class Capsule:
    def __init__(self, path: str, max_tokens: int = 80000):
        self.path = path
        self.max_tokens = max_tokens
        try:
            self.encoder = tiktoken.encoding_for_model("gpt-4")
        except:
            self.encoder = None

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                return json.load(f).get("messages", [])
        return []

    def save(self, messages):
        pruned = self._prune(messages)
        with open(self.path, 'w') as f:
            json.dump({"messages": pruned}, f, indent=2)

    def _prune(self, messages):
        if not self.encoder:
            return messages
        while True:
            total = sum(len(self.encoder.encode(m.get("content", ""))) for m in messages)
            if total <= self.max_tokens or len(messages) <= 2:
                return messages
            messages.pop(1)
