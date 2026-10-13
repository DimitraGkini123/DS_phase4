import asyncio
import os
import random

SERVERS = [
    {"name": "server1", "port": 18861,"resource_port": 19000,"connections": 0, "cpu" : 0.0, "memory" : 0.0},
    {"name": "server2", "port": 18861, "resource_port": 19000, "connections": 0, "cpu" : 0.0, "memory" : 0.0},
    {"name": "server3", "port": 18861, "resource_port": 19000, "connections": 0, "cpu" : 0.0, "memory" : 0.0},
]
PORT = 18861
ALGORITHM = os.getenv("LB_ALGORITHM", "least_connections")

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
def least_connections():

    min_connections = min(
        server["connections"]
        for server in SERVERS
    )

    candidates = [
        server
        for server in SERVERS
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

    return min( servers, key=lambda server: server["score"] ) 

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

async def handle_client(client_reader, client_writer):

    selected_server = await choose_server()
    selected_server["connections"] +=1

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

        server_reader, server_writer = await asyncio.open_connection(
            selected_server["name"],
            selected_server["port"]
        )

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
    if ALGORITHM == "least_connections":
        return least_connections()
    
    elif ALGORITHM == "resource_based":
        await asyncio.gather(
            *[
                get_resources(server)
                for server in SERVERS
            ]
        )

        return resource_based(SERVERS)

    else:
        raise ValueError(f"Unknown algorithm: {ALGORITHM}")

async def main():
    print(f"Load balancing algorithm: {ALGORITHM}")
    server = await asyncio.start_server(
        handle_client, "0.0.0.0", PORT
    )
    print(f"Load balancer listening on port {PORT}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())