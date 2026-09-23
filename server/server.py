import os
import rpyc
from rpyc.utils.server import ThreadedServer
import time
from server.redis_client import cache, make_key
from server.occurrences import calculate_occurrences, TEXTS_DIR

PORT = 18861

def stub_cache_check(text, keyword):
    t0 = time.perf_counter()
    cached = cache.get(make_key(text, keyword))
    if cached is not None:
        print(f"[HIT ] {text}:{keyword} -> {cached}  {(time.perf_counter()-t0)*1000:.2f}ms")
        return int(cached)
    result = calculate_occurrences(text, keyword)
    print(f"[MISS] {text}:{keyword} -> {result}  {(time.perf_counter()-t0)*1000:.2f}ms")
    return result


class CountService(rpyc.Service):
    def exposed_count(self, reqID, keyword, text):
        return reqID, stub_cache_check(text, keyword)

    def exposed_list_texts(self):
        return [n[:-4] for n in os.listdir(TEXTS_DIR) if n.endswith(".txt")]


if __name__ == "__main__":
    cache.ping()                                   # fail fast if redis isn't reachable
    print(f"Connected to redis, server listening on port {PORT}")
    ThreadedServer(CountService, port=PORT, hostname="0.0.0.0").start()