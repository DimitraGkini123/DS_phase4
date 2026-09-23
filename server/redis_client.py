import os
import redis

cache = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, decode_responses=True)

def make_key(text, keyword):
    return f"{text}:{keyword.lower()}"