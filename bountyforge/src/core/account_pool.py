import time
import heapq
import threading

class AccountPool:
    def __init__(self, accounts):
        self.accounts = accounts
        self.heap = []
        self.lock = threading.Lock()
        for idx, acc in enumerate(accounts):
            heapq.heappush(self.heap, (0, idx, acc))

    def acquire(self):
        with self.lock:
            now = time.time()
            if self.heap and self.heap[0][0] <= now:
                return heapq.heappop(self.heap)[2]
            return None

    def release(self, account, cooldown=60):
        with self.lock:
            heapq.heappush(self.heap, (time.time() + cooldown, self.accounts.index(account), account))
