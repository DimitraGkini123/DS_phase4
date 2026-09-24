import os
import re
from server.redis_client import cache, make_key

TEXTS_DIR = os.getenv("TEXTS_DIR", os.path.join(os.path.dirname(__file__), "..", "SampleTexts"))

def calculate_occurrences(text, keyword):
    with open(os.path.join(TEXTS_DIR, text + ".txt"), encoding="utf-8") as f:
        content = f.read()
    pattern = r"\b" + re.escape(keyword) + r"\b"
    count = len(re.findall(pattern, content, flags=re.IGNORECASE))
    cache.set(make_key(text, keyword), count)  #store newly calculated result in server 
    return count