import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("127.0.0.1", 1502))

print("[*] Sending malformed packet...")
sock.sendall(b"\x00\x01\x00")  # Invalid / truncated Modbus packet

sock.close()
print("[✓] Malformed packet sent")
