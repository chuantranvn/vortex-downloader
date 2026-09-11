import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import asyncio
import re
from typing import List, Dict, Any, Optional
import httpx
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from common.schemas import DownloadRequest, DownloadTask, TaskStatus, EngineType, MediaMetadata
from common.database import HistoryDatabase

app = FastAPI(
    title="Vortex Downloader - API Gateway",
    description="Gateway trung tâm điều phối tải đa luồng & quản lý lịch sử SQLite",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CORE_ENGINE_URL = os.getenv("CORE_ENGINE_URL", "http://127.0.0.1:8001")
MEDIA_EXTRACTOR_URL = os.getenv("MEDIA_EXTRACTOR_URL", "http://127.0.0.1:8002")

db = HistoryDatabase()

class WebSocketHub:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        for dead in disconnected:
            self.disconnect(dead)

hub = WebSocketHub()
task_engine_map: Dict[str, str] = {}

def is_streaming_media_url(url: str) -> bool:
    media_patterns = [
        r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)",
        r"(?:https?:\/\/)?(?:www\.)?tiktok\.com",
        r"(?:https?:\/\/)?(?:www\.)?(?:facebook\.com|fb\.watch)",
        r"(?:https?:\/\/)?(?:www\.)?instagram\.com",
        r"(?:https?:\/\/)?(?:www\.)?(?:twitter\.com|x\.com)",
        r"(?:https?:\/\/)?(?:www\.)?vimeo\.com",
        r"(?:https?:\/\/)?(?:www\.)?twitch\.tv",
        r"(?:https?:\/\/)?(?:www\.)?soundcloud\.com",
        r"\.m3u8(?:\?.*)?$",
        r"\.mpd(?:\?.*)?$"
    ]
    for pattern in media_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return True
    return False

@app.on_event("startup")
async def start_background_broadcaster():
    asyncio.create_task(_periodic_broadcast_loop())

async def _periodic_broadcast_loop():
    async with httpx.AsyncClient(timeout=3.0) as client:
        while True:
            await asyncio.sleep(0.5)

            active_tasks = []
            # Core Engine
            try:
                res = await client.get(f"{CORE_ENGINE_URL}/api/v1/download")
                if res.status_code == 200:
                    for t in res.json():
                        task_engine_map[t["id"]] = CORE_ENGINE_URL
                        active_tasks.append(t)
                        # Lưu/Cập nhật vào SQLite
                        try:
                            task_obj = DownloadTask(**t)
                            db.upsert_task(task_obj)
                        except Exception:
                            pass
            except Exception:
                pass

            # Media Extractor
            try:
                res = await client.get(f"{MEDIA_EXTRACTOR_URL}/api/v1/download")
                if res.status_code == 200:
                    for t in res.json():
                        task_engine_map[t["id"]] = MEDIA_EXTRACTOR_URL
                        active_tasks.append(t)
                        # Lưu/Cập nhật vào SQLite
                        try:
                            task_obj = DownloadTask(**t)
                            db.upsert_task(task_obj)
                        except Exception:
                            pass
            except Exception:
                pass

            if hub.active_connections and active_tasks:
                await hub.broadcast({"type": "progress_update", "tasks": active_tasks})

@app.get("/health")
async def health_check():
    core_ok = False
    media_ok = False
    async with httpx.AsyncClient(timeout=2.0) as client:
        try:
            r1 = await client.get(f"{CORE_ENGINE_URL}/health")
            core_ok = r1.status_code == 200
        except Exception:
            pass
        try:
            r2 = await client.get(f"{MEDIA_EXTRACTOR_URL}/health")
            media_ok = r2.status_code == 200
        except Exception:
            pass

    return {
        "gateway": "healthy",
        "services": {
            "core_engine": "online" if core_ok else "offline",
            "media_extractor": "online" if media_ok else "offline"
        }
    }

@app.post("/api/v1/extract", response_model=MediaMetadata)
async def extract_media(req: DownloadRequest):
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            res = await client.post(f"{MEDIA_EXTRACTOR_URL}/api/v1/extract", json=req.dict())
            if res.status_code != 200:
                raise HTTPException(status_code=res.status_code, detail=res.text)
            return res.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Media Extractor service offline: {str(e)}")

@app.post("/api/v1/probe")
async def probe_direct_file(req: DownloadRequest):
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            res = await client.post(f"{CORE_ENGINE_URL}/api/v1/probe", json=req.dict())
            return res.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Core Engine service offline: {str(e)}")

@app.post("/api/v1/download", response_model=DownloadTask)
async def create_download(req: DownloadRequest):
    is_media = is_streaming_media_url(req.url) or (req.format_id is not None)
    target_engine = MEDIA_EXTRACTOR_URL if is_media else CORE_ENGINE_URL

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            res = await client.post(f"{target_engine}/api/v1/download", json=req.dict())
            if res.status_code != 200:
                raise HTTPException(status_code=res.status_code, detail=res.text)
            task_data = res.json()
            task_engine_map[task_data["id"]] = target_engine
            # Lưu ngay vào lịch sử SQLite
            try:
                task_obj = DownloadTask(**task_data)
                db.upsert_task(task_obj)
            except Exception:
                pass
            return task_data
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Backend engine offline: {str(e)}")

@app.get("/api/v1/tasks")
async def list_all_tasks(filter: Optional[str] = None):
    # Lấy toàn bộ từ database SQLite (vĩnh viễn không mất)
    history_tasks = db.get_all_tasks(filter)
    history_map = {t["id"]: t for t in history_tasks}

    # Cập nhật tốc độ thời gian thực cho các task đang tải
    async with httpx.AsyncClient(timeout=2.0) as client:
        for engine_url in [CORE_ENGINE_URL, MEDIA_EXTRACTOR_URL]:
            try:
                r = await client.get(f"{engine_url}/api/v1/download")
                if r.status_code == 200:
                    for active_t in r.json():
                        tid = active_t["id"]
                        task_engine_map[tid] = engine_url
                        if tid in history_map:
                            history_map[tid].update({
                                "speed_bps": active_t.get("speed_bps", 0.0),
                                "downloaded_bytes": active_t.get("downloaded_bytes", 0),
                                "status": active_t.get("status", "downloading"),
                                "eta_seconds": active_t.get("eta_seconds"),
                                "progress_percent": active_t.get("progress_percent", 0.0)
                            })
                        else:
                            history_map[tid] = active_t
            except Exception:
                pass

    return list(history_map.values())

@app.get("/api/v1/tasks/{task_id}")
async def get_task_details(task_id: str):
    engine_url = task_engine_map.get(task_id)
    target_urls = [engine_url] if engine_url else [CORE_ENGINE_URL, MEDIA_EXTRACTOR_URL]
    
    async with httpx.AsyncClient(timeout=3.0) as client:
        for base in target_urls:
            try:
                res = await client.get(f"{base}/api/v1/download/{task_id}")
                if res.status_code == 200:
                    task_engine_map[task_id] = base
                    return res.json()
            except Exception:
                pass

    # Nếu không còn trên bộ nhớ engine, lấy từ SQLite
    for t in db.get_all_tasks():
        if t["id"] == task_id:
            return t
    raise HTTPException(status_code=404, detail="Task not found")

@app.post("/api/v1/tasks/{task_id}/pause")
async def pause_task(task_id: str):
    engine_url = task_engine_map.get(task_id, CORE_ENGINE_URL)
    async with httpx.AsyncClient(timeout=5.0) as client:
        res = await client.post(f"{engine_url}/api/v1/download/{task_id}/pause")
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=res.text)
        return res.json()

@app.post("/api/v1/tasks/{task_id}/resume")
async def resume_task(task_id: str):
    engine_url = task_engine_map.get(task_id, CORE_ENGINE_URL)
    async with httpx.AsyncClient(timeout=5.0) as client:
        res = await client.post(f"{engine_url}/api/v1/download/{task_id}/resume")
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=res.text)
        return res.json()

@app.post("/api/v1/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    engine_url = task_engine_map.get(task_id, CORE_ENGINE_URL)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(f"{engine_url}/api/v1/download/{task_id}/cancel")
    except Exception:
        pass
    
    # Xóa khỏi database SQLite
    db.delete_task(task_id)
    return {"status": "deleted", "task_id": task_id}

@app.websocket("/ws/progress")
async def websocket_progress_endpoint(websocket: WebSocket):
    await hub.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        hub.disconnect(websocket)
    except Exception:
        hub.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
