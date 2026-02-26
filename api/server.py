from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import sys
import os
import asyncio

from api.store import add_log, get_stats

app = FastAPI(title="Encryption Proxy API")

# ==================================================
# CORS
# ==================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================================================
# WebSocket Manager
# ==================================================
class WSManager:
    def __init__(self):
        self.clients = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.clients.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.clients:
            self.clients.remove(ws)

    async def broadcast(self, data):
        dead = []
        for ws in self.clients:
            try:
                await ws.send_json(data)
            except:
                dead.append(ws)
        for d in dead:
            self.disconnect(d)

ws_manager = WSManager()

# ==================================================
# GLOBALS
# ==================================================
proxy_a_process = None
proxy_b_process = None

BASE_DIR = os.getcwd()

# ==================================================
# START PROXY  ▶
# ==================================================
@app.post("/proxy/start")
async def start_proxy():
    global proxy_a_process, proxy_b_process

    if proxy_a_process or proxy_b_process:
        return {"status": "already running"}

    # Ensure proxy package is found
    env = os.environ.copy()
    env["PYTHONPATH"] = BASE_DIR

    # Start Proxy B FIRST
    proxy_b_process = subprocess.Popen(
        [sys.executable, os.path.join("proxy", "proxy_b.py")],
        cwd=BASE_DIR,
        env=env
    )

    # Start Proxy A
    proxy_a_process = subprocess.Popen(
        [sys.executable, os.path.join("proxy", "proxy_a.py")],
        cwd=BASE_DIR,
        env=env
    )

    add_log("Proxy A and Proxy B started", "system")

    await ws_manager.broadcast({
        "type": "proxy_status",
        "running": True
    })

    return {"status": "proxy started"}

# ==================================================
# STOP PROXY  ■
# ==================================================
@app.post("/proxy/stop")
async def stop_proxy():
    global proxy_a_process, proxy_b_process

    if proxy_a_process:
        proxy_a_process.terminate()
        proxy_a_process = None

    if proxy_b_process:
        proxy_b_process.terminate()
        proxy_b_process = None

    add_log("Proxy A and Proxy B stopped", "system")

    await ws_manager.broadcast({
        "type": "proxy_status",
        "running": False
    })

    return {"status": "proxy stopped"}

# ==================================================
# WEBSOCKET ENDPOINT
# ==================================================
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws_manager.connect(ws)
    try:
        while True:
            # keep connection alive, ignore payload
            await ws.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(ws)

# ==================================================
# STATS BROADCAST LOOP
# ==================================================
@app.on_event("startup")
async def start_background_tasks():
    async def stats_loop():
        while True:
            await ws_manager.broadcast({
                "type": "stats",
                "payload": get_stats()
            })
            await asyncio.sleep(1)

    asyncio.create_task(stats_loop())
