# Resource agent: runs on each server and reports the container's CPU and memory usage.
import socket
import threading
import time
import psutil

RESOURCE_PORT = 19000
SAMPLE_INTERVAL = 0.2          # seconds between measurements

latest = {"cpu": 0.0, "memory": 0.0}
latest_lock = threading.Lock()


def sampler():
    # Measure only the processes inside this container (the container has its own
    # process list), so each server reports its own load instead of the host's.
    procs = {}
    ncpu = psutil.cpu_count() or 1
    while True:
        cpu = 0.0
        mem = 0.0
        current = {}
        for p in psutil.process_iter():
            try:
                proc = procs.get(p.pid, p)          # reuse object so cpu_percent has a baseline
                cpu += proc.cpu_percent(None)       # non-blocking: usage since last call
                mem += proc.memory_percent()
                current[p.pid] = proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        procs = current
        with latest_lock:
            latest["cpu"] = cpu / ncpu
            latest["memory"] = mem
        time.sleep(SAMPLE_INTERVAL)


def handle_client(conn):
    try:
        with latest_lock:
            message = f"{latest['cpu']:.1f},{latest['memory']:.1f}"
        conn.sendall(message.encode())          # replies instantly, no measuring here
    finally:
        conn.close()


def resource_agent():
    threading.Thread(target=sampler, daemon=True).start()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", RESOURCE_PORT))
    sock.listen()
    print(f"Resource agent listening on port {RESOURCE_PORT}")

    while True:
        conn, addr = sock.accept()
        threading.Thread(target=handle_client, args=(conn,), daemon=True).start()
