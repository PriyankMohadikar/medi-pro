"""
FAQ response cache with TTL-based expiration.
"""

import time


class FAQCache:
    """Simple in-memory cache with time-to-live expiration for FAQ responses."""

    def __init__(self, ttl: int = 300):
        self.cache: dict = {}
        self.ttl = ttl

    def get(self, key: str):
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry["time"] < self.ttl:
                return entry["response"]
        return None

    def set(self, key: str, response: str):
        self.cache[key] = {"response": response, "time": time.time()}
