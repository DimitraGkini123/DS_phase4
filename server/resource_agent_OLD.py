#The agent runs on each server and calculates usage of server resources, such as its computing capacity and memory. 
import socket
import psutil
import threading

RESOURCE_PORT = 19000


def get_resources():
    cpu = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory().percent

    return cpu, memory


def handle_client(conn):
    try:
        cpu, memory = get_resources()

        message = f"{cpu},{memory}"
        conn.sendall(message.encode())

    finally:
        conn.close()


def resource_agent():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    sock.bind(("0.0.0.0", RESOURCE_PORT))
    sock.listen()

    print(f"Resource agent listening on port {RESOURCE_PORT}")

    while True:
        conn, addr = sock.accept()

        threading.Thread(
            target=handle_client,
            args=(conn,),
            daemon=True
        ).start()