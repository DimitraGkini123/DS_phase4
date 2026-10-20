##Gets the request from client and talks with cache.py

import rpyc
from rpyc.utils.server import ThreadedServer

import threading
import socket
from server.resource_agent import resource_agent

from server.redis_client import get_result
from server.occurrences import calculate_occurrences


PORT = 18861  ##RPyC port, as defined in the client
HEARTBEAT_PORT = 19001    # UDP health-check port

class CountService(rpyc.Service):

    def exposed_count(self, reqID, keyword, text):

        # 1. Check cache
        result = get_result(keyword, text)

        # 2. Cache miss -> calculate
        if result is None:
            result = calculate_occurrences(text, keyword) ##this function will directly save the result into the cache

        # 4. Return response to client
        return reqID, result
def udp_health_responder():
    """
    Listens for UDP health-check messages from the load balancer.
    If it receives b"HEALTH?", it checks whether the local RPyC
    service is reachable and replies accordingly.
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) ##create the udp socket

    sock.bind(("0.0.0.0", HEARTBEAT_PORT))

    print(
        f"UDP health responder listening on port {HEARTBEAT_PORT}"
    )

    while True:

        data, addr = sock.recvfrom(1024)  ##wait for health datagram from load balancer

        if data == b"HEALTH?":  ##if Health? is received

            try:
                # Check whether the actual RPyC service is reachable
                test_socket = socket.create_connection(
                    ("127.0.0.1", PORT),  ##tries to open a tcp connection to see if the application works
                    timeout=0.2
                )

                test_socket.close()

                sock.sendto(
                    b"ALIVE",
                    addr
                )

            except OSError:  ##is the tcp fails--> not ready

                sock.sendto(
                    b"NOT_READY",
                    addr
                )
##starts the server
## the server listens on port 18861 and 1900 at the same time.
## 18861 --> client requests 
## 19000 --> resource metrics 
if __name__ == "__main__":

    threading.Thread(
        target=resource_agent,
        daemon=True
    ).start()

    threading.Thread(
        target=udp_health_responder,
        daemon=True
    ).start()

    print(f"Server listening on port {PORT}")


    server = ThreadedServer(
        CountService,
        hostname="0.0.0.0",
        port=PORT
    )

    server.start()