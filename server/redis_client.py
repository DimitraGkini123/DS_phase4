#responsible for everything related to cache access. Get (hit or miss).
#The server.py calls cache.py whenever he gets a new request.
import os
import redis

cache = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, decode_responses=True)

def make_key(text, keyword):
    return f"{text}:{keyword.lower()}"


def get_result(word, filename):
    #check in redis if the request has already been calculated.
    #If it is found --> hit, else --> miss
    key = make_key(filename, word)
    result = cache.get(key)

    if result is not None:
        print(f"HIT: {key}")
        return int(result)

    print(f"MISS {key}")
    return None
