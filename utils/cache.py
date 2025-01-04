from functools import lru_cache
from typing import List, Dict, Any
import time

CACHE_TTL = 300  # 5分钟缓存

class Cache:
    def __init__(self):
        self._cache = {}
        self._timestamps = {}

    def get(self, key: str) -> Any:
        if key in self._cache:
            if time.time() - self._timestamps[key] < CACHE_TTL:
                return self._cache[key]
            else:
                del self._cache[key]
                del self._timestamps[key]
        return None

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = value
        self._timestamps[key] = time.time()

cache = Cache() 