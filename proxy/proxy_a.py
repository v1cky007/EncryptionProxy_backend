import asyncio, os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from proxy.tunnel_framing import write_frame, read_frame
from crypto.handshake import generate_keypair, derive_session_key
from crypto.rekey import rekey

PROXY_B_HOST = "127.0.0.1"
PROXY_B_PORT = 1602
REKEY_INTERVAL = 50

class ProxyA:
    def __init__(self):
        self.counter = 0
        self.packet_count = 0

    async def handle_client(self, client_reader, client_writer):
        print("[Proxy A] Legacy client connected")

        b_reader, b_writer = await asyncio.open_connection(
            PROXY_B_HOST, PROXY_B_PORT
        )

        # ---------- HANDSHAKE ----------
        priv, pub = generate_keypair()
        write_frame(b_writer, pub)
        await b_writer.drain()

        peer_pub = await read_frame(b_reader)
        session_key = derive_session_key(priv, peer_pub)
        aes = AESGCM(session_key)

        print("[HANDSHAKE] Proxy A secure session established")

        # ---------- ENCRYPTED + REKEY ----------
        while True:
            data = await client_reader.read(4096)
            if not data:
                break

            self.counter += 1
            self.packet_count += 1

            # ---------- REKEY ----------
            if self.packet_count % REKEY_INTERVAL == 0:
                session_key = rekey(session_key, b"proxy-traffic")
                aes = AESGCM(session_key)
                print("[REKEY] Proxy A rotated session key")

            nonce = os.urandom(12)
            encrypted = aes.encrypt(nonce, data, None)

            payload = (
                self.counter.to_bytes(8, "big") +
                nonce +
                encrypted
            )

            write_frame(b_writer, payload)
            await b_writer.drain()

        client_writer.close()
        b_writer.close()

    async def start(self):
        server = await asyncio.start_server(
            self.handle_client, "0.0.0.0", 1502
        )
        print("[Proxy A] Listening on port 1502")
        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(ProxyA().start())
