import os
import time

import rpyc

# In docker-compose, containers address each other by service name,
# not "localhost". These defaults match the docker-compose.yml below.
SERVER_HOST = os.environ.get("SERVER_HOST", "server")
SERVER_PORT = int(os.environ.get("SERVER_PORT", 18861))

startTimer = 0


def connect_with_retry(host, port, retries=10, delay=2):
    """
    Containers can start in any order, so the server socket might not be
    open yet when the client container boots. Retry instead of failing.
    """
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            return rpyc.connect(host, port)
        except (ConnectionRefusedError, OSError) as e:
            last_error = e
            print(f"[client] server not ready (attempt {attempt}/{retries}), "
                  f"retrying in {delay}s...")
            time.sleep(delay)
    raise ConnectionError(
        f"Could not connect to {host}:{port} after {retries} attempts"
    ) from last_error

def timerStart():
    startTimer = time.perf_counter()

def timerStop():
    elapsed_ms = (time.perf_counter() - startTimer) * 1000
    print(f"[client] E2E latency: {elapsed_ms:.2f} ms")


def main():
    print(f"[client] connecting to {SERVER_HOST}:{SERVER_PORT} ...")
    conn = connect_with_retry(SERVER_HOST, SERVER_PORT)
    print("[client] connected")

    # This is a placeholder remote call. Once the real word-count service
    # is implemented, swap this for something like:
    #   conn.root.count_keyword(keyword="the", text_ref="hamlet.txt")
    timerStart()
    result = conn.root.hello("world")
    timerStop()

    conn.close()


if __name__ == "__main__":
    main()