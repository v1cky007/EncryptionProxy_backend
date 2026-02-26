from datetime import datetime

logs = []

stats = {
    "total_packets": 0,
    "modbus_packets": 0,
    "errors": 0,
    "avg_latency": 0.0,
    "start_time": datetime.now()
}

def add_log(message, level="info"):
    logs.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "level": level,
        "message": message
    })
    if len(logs) > 500:
        logs.pop(0)

def get_logs():
    return logs

def update_stats(packet=False, modbus=False, error=False, latency=0):
    if packet:
        stats["total_packets"] += 1
    if modbus:
        stats["modbus_packets"] += 1
    if error:
        stats["errors"] += 1
    if latency > 0:
        stats["avg_latency"] = round(
            (stats["avg_latency"] * 0.9) + (latency * 0.1), 3
        )

def get_stats():
    uptime = (datetime.now() - stats["start_time"]).seconds
    return {
        "total_packets": stats["total_packets"],
        "modbus_packets": stats["modbus_packets"],
        "errors": stats["errors"],
        "avg_latency": stats["avg_latency"],
        "uptime": uptime
    }
