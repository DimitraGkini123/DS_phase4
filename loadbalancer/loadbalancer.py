import asyncio

SERVERS = [
    {"name": "server1", "port": 18861, "connections": 0, "response_time": 0.0},
    {"name": "server2", "port": 18861, "connections": 0, "response_time": 0.0},
    {"name": "server3", "port": 18861, "connections": 0, "response_time": 0.0},
]
PORT = 18861
ALGORITHM = "least_connections" 
#ALGORITHM = "least_response_time"


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
    return min(
        SERVERS,
        key=lambda server: server["connections"]
    )

def least_response_time(servers):
    return min(
        servers,
        key=lambda server: server["response_time"]
    )

async def handle_client(client_reader, client_writer):

    selected_server = choose_server()
    selected_server["connections"] +=1

    print(
        f"Selected {selected_server['name']} | "
        f"connections = {selected_server['connections']}"
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


def choose_server():
    if ALGORITHM == "least_connections":
        return least_connections()
    
    elif ALGORITHM == "least_response_time":
        return least_response_time()

    else:
        raise ValueError(f"Unknown algorithm: {ALGORITHM}")

async def main():
    server = await asyncio.start_server(
        handle_client, "0.0.0.0", PORT
    )
    print(f"Load balancer listening on port {PORT}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())