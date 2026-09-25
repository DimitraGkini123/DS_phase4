import asyncio

SERVERS = [
    ("server1", 18861),
    ("server2", 18861),
    ("server3", 18861),
]
PORT = 18861


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


async def handle_client(client_reader, client_writer):
    name, port = SERVERS[0]  # TODO fill in algorithm

    server_reader, server_writer = await asyncio.open_connection(name, port)

    await asyncio.gather(
        pipe(client_reader, server_writer),   # client --> server
        pipe(server_reader, client_writer),   # server --> client
    )


async def main():
    server = await asyncio.start_server(
        handle_client, "0.0.0.0", PORT
    )
    print(f"Load balancer listening on port {PORT}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())