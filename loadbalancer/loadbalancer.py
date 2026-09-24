# loadbalancer/loadbalancer.py

import asyncio
import time

# --- Config ---
SERVERS = [
    ("server1", 18861),
    ("server2", 18861),
    ("server3", 18861),
]
PORT = 18861

# --- State ---
server_stats = {
    name: {"connections": 0, "response_time": 0.0, "healthy": True}
    for name, _ in SERVERS
}

# --- Algorithms ---
def pick_least_connections():
    ...

def pick_least_response_time():
    ...

# --- Forwarding ---
async def pipe(reader, writer):
    ...

async def handle_client(client_reader, client_writer):
    ...

# --- Health checks ---
async def health_check():
    ...

# --- Entry point ---
async def main():
    server = await asyncio.start_server(
        handle_client, "0.0.0.0", PORT
    )
    asyncio.create_task(health_check())
    print(f"Load balancer listening on port {PORT}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())