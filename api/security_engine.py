import time
from collections import defaultdict

# ---------- ALERT BUILDER ----------
def build_alert(category, severity, message):
    return {
        "type": "alert",
        "category": category,
        "severity": severity,
        "message": message,
        "timestamp": time.strftime("%H:%M:%S")
    }

# ---------- REPLAY ATTACK ----------
seen_transactions = set()

def detect_replay(transaction_id):
    if transaction_id in seen_transactions:
        return build_alert(
            "REPLAY_ATTACK",
            "CRITICAL",
            "Replay attack detected (duplicate transaction ID)"
        )
    seen_transactions.add(transaction_id)
    return None

# ---------- FLOODING ATTACK ----------
packet_counter = defaultdict(int)
WINDOW_SECONDS = 1
FLOOD_THRESHOLD = 50

def detect_flooding(client_id):
    now = int(time.time())
    key = (client_id, now)

    packet_counter[key] += 1
    if packet_counter[key] > FLOOD_THRESHOLD:
        return build_alert(
            "FLOODING_ATTACK",
            "HIGH",
            "Packet flooding detected"
        )
    return None
