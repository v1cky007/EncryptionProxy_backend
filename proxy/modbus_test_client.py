import socket
import binascii

def send_modbus_hex(hex_data):
    # Convert hex string → bytes
    data = binascii.unhexlify(hex_data.replace(" ", ""))

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 1502))  # Connect to your proxy

    print(f"\nSending Modbus Packet: {hex_data}")
    s.sendall(data + b"\r\n")   # newline triggers send

    response = s.recv(2048)
    print(f"Response: {response}")

    s.close()


if __name__ == "__main__":
    # Read Holding Registers — Function Code 03
    send_modbus_hex("00 01 00 00 00 06 01 03 00 10 00 01")

    # Read Coils — Function Code 01
    send_modbus_hex("00 02 00 00 00 06 01 01 00 13 00 25")
