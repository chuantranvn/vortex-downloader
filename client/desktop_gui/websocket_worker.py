import asyncio
import json
import websockets
from PySide6.QtCore import QThread, Signal

class WebSocketProgressWorker(QThread):
    progress_received = Signal(dict)
    connection_status = Signal(bool)

    def __init__(self, ws_url: str = "ws://localhost:8000/ws/progress"):
        super().__init__()
        self.ws_url = ws_url
        self.running = True

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._listen_loop())

    async def _listen_loop(self):
        while self.running:
            try:
                async with websockets.connect(self.ws_url) as ws:
                    self.connection_status.emit(True)
                    while self.running:
                        msg = await ws.recv()
                        data = json.loads(msg)
                        self.progress_received.emit(data)
            except Exception:
                self.connection_status.emit(False)
                await asyncio.sleep(2)

    def stop(self):
        self.running = False
        self.wait(1000)
