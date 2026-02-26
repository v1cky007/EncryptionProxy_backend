import asyncio
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from proxy.tunnel_framing import read_frame, write_frame
from crypto.handshake import generate_keypair, derive_session_key
from crypto.rekey import rekey

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 502
REKEY_INTERVAL = 50

class ProxyB:
    def __init__(self):
        self.last_counter = 0
        self.packet_count = 0

    async def handle_proxy_a(self, reader, writer):
        print("[Proxy B] Connected to Proxy A")

        # ---------- HANDSHAKE ----------
        peer_pub = await read_frame(reader)
        priv, pub = generate_keypair()
        write_frame(writer, pub)
        await writer.drain()

        session_key = derive_session_key(priv, peer_pub)
        aes = AESGCM(session_key)

        print("[HANDSHAKE] Proxy B secure session established")

        server_reader, server_writer = await asyncio.open_connection(
            SERVER_HOST, SERVER_PORT
        )

        # ---------- DECRYPT + REKEY ----------
        while True:
            payload = await read_frame(reader)

            counter = int.from_bytes(payload[:8], "big")
            nonce = payload[8:20]
            ciphertext = payload[20:]

            if counter <= self.last_counter:
                print("[SECURITY] Replay detected — dropped")
                continue

            self.last_counter = counter
            self.packet_count += 1

            # ---------- REKEY ----------
            if self.packet_count % REKEY_INTERVAL == 0:
                session_key = rekey(session_key, b"proxy-traffic")
                aes = AESGCM(session_key)
                print("[REKEY] Proxy B rotated session key")

            plaintext = aes.decrypt(nonce, ciphertext, None)
            server_writer.write(plaintext)
            await server_writer.drain()

    async def start(self):
        server = await asyncio.start_server(
            self.handle_proxy_a, "0.0.0.0", 1602
        )
        print("[Proxy B] Listening on port 1602")
        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(ProxyB().start())
