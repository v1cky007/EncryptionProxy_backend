async def read_frame(reader):
    header = await reader.readexactly(4)
    length = int.from_bytes(header, "big")
    return await reader.readexactly(length)

def write_frame(writer, data: bytes):
    writer.write(len(data).to_bytes(4, "big") + data)
