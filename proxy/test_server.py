import asyncio

async def handle_client(reader, writer):
    try:
        while True:
            header = await reader.readexactly(4)
            length = int.from_bytes(header, "big")
            data = await reader.readexactly(length)
            print("[SERVER] Received encrypted frame")
            writer.write(b"OK\r\n")
            await writer.drain()
    except:
        writer.close()

async def main():
    server = await asyncio.start_server(handle_client, "127.0.0.1", 502)
    print("[SERVER] Test server running on 127.0.0.1:502")
    async with server:
        await server.serve_forever()

asyncio.run(main())
