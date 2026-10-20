import asyncio
import os
import random

from icmplib import async_ping

SERVERS = [
    {"name": "server1", "port": 18861,"resource_port": 19000,"connections": 0, "cpu" : 0.0, "memory" : 0.0, "alive": True},
    {"name": "server2", "port": 18861, "resource_port": 19000, "connections": 0, "cpu" : 0.0, "memory" : 0.0, "alive": True},
    {"name": "server3", "port": 18861, "resource_port": 19000, "connections": 0, "cpu" : 0.0, "memory" : 0.0, "alive": True},
]
PORT = 18861
ALGORITHM = os.getenv("LB_ALGORITHM", "least_connections")
PING_INTERVAL = 1.0 
PING_TIMEOUT = 1.0    #seconds to wait for a ping reply before the server is considered offline

async def pipe(reader, writer):
    try:
        while True:
            data = await reader.read(4096)      # magic number, whatever, determined via google search
            if not data:
                break
            writer.write(data)
            await writer.drain()
    except (ConnectionResetError, BrokenPipeError):
        pass
    finally:
        writer.close()
        await writer.wait_closed()

#define the algorithms
def least_connections(servers):

    min_connections = min(
        server["connections"]
        for server in servers  
    )

    candidates = [
        server
        for server in servers
        if server["connections"] == min_connections
    ]

    return random.choice(candidates)
def resource_based(servers):

    #calculate score for each server.
    #Score is a combination of cpu and memory that shows how heavily loaded is a server
    #for now we define 50/50. Maybe later we have to put more wieght on cpu because our problem affects more the cpu due to the computations rather than the memory 
    for server in servers:
        server["score"] = (
            0.7 * server["cpu"] +
            0.3 * server["memory"]
        )

        print(
                f"{server['name']} | "
                f"CPU={server['cpu']:.1f}% | "
                f"MEM={server['memory']:.1f}% | "
                f"SCORE={server['score']:.1f}"
            )

    min_score = min(
            server["score"]
            for server in servers
        )
    
    candidates = [
            server
            for server in servers
            if server["score"] == min_score
        ]
    
    return random.choice(candidates)

async def get_resources(server):
    try:
        reader, writer = await asyncio.open_connection(   ##LB opens a connection to the resource_agent.py 
            server["name"],
            server["resource_port"]
        )

        data = await reader.read(100)  #waiting for the metrics from the server.

        writer.close()
        await writer.wait_closed()

        cpu, memory = data.decode().split(",")  ##respose is in this format: b"24.5,38.2" ,so the LB decodes it.

        server["cpu"] = float(cpu)
        server["memory"] = float(memory)

    except Exception as e:
        print(
            f"Could not get resources from "
            f"{server['name']}: {e}"
        )

async def check_server(server):
    #send ONE ICMP echo request to the server and update its "alive" flag
    reason = ""
    try:
        host = await async_ping(
            server["name"],
            count=1,
            timeout=PING_TIMEOUT,
            privileged=True
        )
        alive = host.is_alive
        if not alive:
            reason = "no ping reply"
    except Exception as e:
        alive = False
        reason = repr(e)

    if alive != server["alive"]:        #only print when the state changes
        if alive:
            print(f"HEALTH: {server['name']} is back ONLINE")
        else:
            print(f"HEALTH: {server['name']} is OFFLINE ({reason})")

    server["alive"] = alive

async def check_all_servers():
    await asyncio.gather(
        *[
            check_server(server)
            for server in SERVERS
        ]
    )

async def health_check_loop():
    #runs forever in the background, in parallel with handle_client()
    while True:
        await asyncio.sleep(PING_INTERVAL)
        await check_all_servers()


async def connect_to_server():
    # pick a server and open a connection to it.
    # If the picked server is unreachable (it died after the last ping), mark it OFFLINE
    # immediately and pick another one, so the client request is not lost.
    while True:
        selected_server = await choose_server()

        if selected_server is None:     # every server is offline
            return None, None, None

        selected_server["connections"] += 1     # moved here from handle_client (must happen right after choosing)

        try:
            server_reader, server_writer = await asyncio.open_connection(
                selected_server["name"],
                selected_server["port"]
            )
            return selected_server, server_reader, server_writer

        except OSError as e:
            selected_server["connections"] -= 1
            selected_server["alive"] = False
            print(
                f"HEALTH: could not connect to {selected_server['name']} ({e!r}), "
                f"marked OFFLINE, retrying on another server"
            )

async def handle_client(client_reader, client_writer):

    selected_server, server_reader, server_writer = await connect_to_server()

    if selected_server is None: 
        print("No healthy servers available, closing client connection")
        client_writer.close()
        await client_writer.wait_closed()
        return

    if ALGORITHM == "resource_based":
        print(
            f"Selected {selected_server['name']} | "
            f"CPU={selected_server['cpu']:.1f}% | "
            f"MEM={selected_server['memory']:.1f}% | "
            f"SCORE={selected_server['score']:.1f} | "
            f"connections={selected_server['connections']}"
        )
    else:
        print(
            f"Selected {selected_server['name']} | "
            f"connections={selected_server['connections']}"
        )


    try:

        await asyncio.gather(
            pipe(client_reader, server_writer),   # client --> server
            pipe(server_reader, client_writer),   # server --> client
        )

    finally:
        selected_server["connections"] -= 1

        print(
            f"Closed connection on {selected_server['name']} | "
            f"connections = {selected_server['connections']}"
        )


async def choose_server():
    available = [
        server
        for server in SERVERS
        if server["alive"]
    ]

    if not available:
        return None

    if ALGORITHM == "least_connections":
        return least_connections(available)
    
    elif ALGORITHM == "resource_based":
        await asyncio.gather(
            *[
                get_resources(server)
                for server in available
            ]
        )

        return resource_based(available)

    else:
        raise ValueError(f"Unknown algorithm: {ALGORITHM}")

async def main():
    print(f"Load balancing algorithm: {ALGORITHM}")

    await check_all_servers()                                   # know the real state before accepting clients
    health_task = asyncio.create_task(health_check_loop())      # start the heartbeat in the background

    server = await asyncio.start_server(
        handle_client, "0.0.0.0", PORT
    )
    print(f"Load balancer listening on port {PORT}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())