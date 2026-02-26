from loguru import logger

# =========================================================
# 1️⃣ BASIC MODBUS TCP DETECTION
# =========================================================
def is_modbus_packet(data: bytes) -> bool:
    """
    Checks whether the packet is Modbus TCP by validating:
    - Minimum length
    - Protocol ID == 0
    """
    if len(data) < 8:
        return False

    # Protocol ID must be 0 for Modbus TCP
    protocol_id = int.from_bytes(data[2:4], "big")
    return protocol_id == 0


# =========================================================
# 2️⃣ PARSE MODBUS MBAP HEADER
# =========================================================
def parse_modbus_header(data: bytes):
    """
    Parses the Modbus TCP MBAP header and returns a dictionary
    """
    if len(data) < 8:
        return None

    transaction_id = int.from_bytes(data[0:2], "big")
    protocol_id = int.from_bytes(data[2:4], "big")
    length = int.from_bytes(data[4:6], "big")
    unit_id = data[6]
    function_code = data[7]

    return {
        "transaction_id": transaction_id,
        "protocol_id": protocol_id,
        "length": length,
        "unit_id": unit_id,
        "function_code": function_code
    }


# =========================================================
# 3️⃣ MODBUS PACKET VALIDATION
# =========================================================
def validate_modbus_packet(data: bytes) -> bool:
    """
    Validates Modbus TCP packet by checking:
    - Header correctness
    - Payload length consistency
    """
    header = parse_modbus_header(data)
    if not header:
        logger.warning("[MODBUS] Packet too short to be valid")
        return False

    expected_len = header["length"]
    actual_payload = len(data) - 6  # MBAP header excludes first 6 bytes

    if expected_len != actual_payload:
        logger.warning(
            f"[MODBUS] Length mismatch: expected {expected_len}, got {actual_payload}"
        )
        return False

    return True


# =========================================================
# 4️⃣ MODBUS SUMMARY (🔥 NEW – FOR GUI & LOGGING)
# =========================================================
def get_modbus_summary(data: bytes) -> str:
    """
    Returns a human-readable Modbus summary string
    (Used for dashboard & logs)
    """
    header = parse_modbus_header(data)
    if not header:
        return "Invalid Modbus packet"

    return (
        f"TID={header['transaction_id']} | "
        f"Unit={header['unit_id']} | "
        f"Function={header['function_code']} | "
        f"Length={header['length']}"
    )


# =========================================================
# 5️⃣ FUNCTION CODE CLASSIFICATION (🔥 NEW – SECURITY AWARE)
# =========================================================
def get_function_name(function_code: int) -> str:
    """
    Maps Modbus function codes to human-readable names
    """
    function_map = {
        1: "Read Coils",
        2: "Read Discrete Inputs",
        3: "Read Holding Registers",
        4: "Read Input Registers",
        5: "Write Single Coil",
        6: "Write Single Register",
        15: "Write Multiple Coils",
        16: "Write Multiple Registers",
    }
    return function_map.get(function_code, "Unknown Function")


# =========================================================
# 6️⃣ SECURITY HELPER (🔥 NEW – FUTURE ATTACK DETECTION)
# =========================================================
def is_suspicious_function(function_code: int) -> bool:
    """
    Flags potentially dangerous Modbus function codes
    (Write operations)
    """
    return function_code in {5, 6, 15, 16}
