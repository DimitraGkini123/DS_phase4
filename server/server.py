##Gets the request from client and talks with cache.py

import rpyc
from rpyc.utils.server import ThreadedServer

from server.redis_client import get_result
from server.occurrences import calculate_occurrences


PORT = 18861  ##RPyC port, as defined in the client


class CountService(rpyc.Service):

    def exposed_count(self, reqID, keyword, text):

        # 1. Check cache
        result = get_result(keyword, text)

        # 2. Cache miss -> calculate
        if result is None:
            result = calculate_occurrences(text, keyword) ##this function will directly save the result into the cache

        # 4. Return response to client
        return reqID, result

##starts the server
if __name__ == "__main__":
    print(f"Server listening on port {PORT}")

    server = ThreadedServer(
        CountService,
        hostname="0.0.0.0",
        port=PORT
    )

    server.start()