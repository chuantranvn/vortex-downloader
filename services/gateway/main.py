import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import asyncio
import time
import re
from typing import List, Dict, Any, Optional
import httpx
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from common.schemas import DownloadRequest, DownloadTask, TaskStatus, EngineType, MediaMetadata, MediaFormat, CookieSyncRequest
from common.database import HistoryDatabase
from common.utils import clean_video_url, get_default_download_dir

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

@app.middleware("http")
async def add_cors_and_pna_headers(request, call_next):
    if request.method == "OPTIONS":
        from starlette.responses import Response
        res = Response()
        res.headers["Access-Control-Allow-Origin"] = "*"
        res.headers["Access-Control-Allow-Methods"] = "*"
        res.headers["Access-Control-Allow-Headers"] = "*"
        res.headers["Access-Control-Allow-Private-Network"] = "true"
        return res
    response = await call_next(request)
    response.headers["Access-Control-Allow-Private-Network"] = "true"
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.options("/{full_path:path}")
async def options_preflight(full_path: str):
    from fastapi.responses import Response
    res = Response(status_code=204)
    res.headers["Access-Control-Allow-Origin"] = "*"
    res.headers["Access-Control-Allow-Methods"] = "*"
    res.headers["Access-Control-Allow-Headers"] = "*"
    res.headers["Access-Control-Allow-Private-Network"] = "true"
    return res

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

def is_direct_file_url(url: str) -> bool:
    clean = url.split("?")[0].split("#")[0].lower()
    direct_exts = (
        ".ts", ".mp4", ".mkv", ".webm", ".avi", ".mov", ".flv",
        ".mp3", ".m4a", ".aac", ".flac", ".wav",
        ".zip", ".rar", ".7z", ".tar", ".gz", ".iso", ".exe", ".bin"
    )
    return any(clean.endswith(ext) for ext in direct_exts)

def is_streaming_media_url(url: str) -> bool:
    # 1. HLS Playlist hoặc DASH manifest
    if re.search(r"\.(?:m3u8|mpd)(?:\?.*)?$", url, re.IGNORECASE) or ".m3u8" in url.lower():
        return True

    # 2. Các nền tảng streaming chuyên biệt
    media_patterns = [
        r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)",
        r"(?:https?:\/\/)?(?:www\.)?tiktok\.com",
        r"(?:https?:\/\/)?(?:www\.)?(?:facebook\.com|fb\.watch)",
        r"(?:https?:\/\/)?(?:www\.)?instagram\.com",
        r"(?:https?:\/\/)?(?:www\.)?(?:twitter\.com|x\.com)",
        r"(?:https?:\/\/)?(?:www\.)?vimeo\.com",
        r"(?:https?:\/\/)?(?:www\.)?twitch\.tv",
        r"(?:https?:\/\/)?(?:www\.)?soundcloud\.com",
    ]
    for pattern in media_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return True
    return False

@app.on_event("startup")
async def start_background_broadcaster():
    asyncio.create_task(_periodic_broadcast_loop())

async def _periodic_broadcast_loop():
    last_db_sync = time.time()
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
            except Exception:
                pass

            # Media Extractor
            try:
                res = await client.get(f"{MEDIA_EXTRACTOR_URL}/api/v1/download")
                if res.status_code == 200:
                    for t in res.json():
                        task_engine_map[t["id"]] = MEDIA_EXTRACTOR_URL
                        active_tasks.append(t)
            except Exception:
                pass

            # Tối ưu lưu trữ DB: Chỉ ghi đĩa khi đổi trạng thái hoặc định kỳ mỗi 4s để loại bỏ lag I/O
            now = time.time()
            sync_db = (now - last_db_sync >= 4.0)
            if sync_db:
                last_db_sync = now

            for t in active_tasks:
                status_str = str(t.get("status", "")).lower()
                is_terminal = status_str in ("completed", "failed", "paused")
                if sync_db or is_terminal:
                    try:
                        task_obj = DownloadTask(**t)
                        db.upsert_task(task_obj)
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
    req.url = clean_video_url(req.url)

    # Nếu là link file trực tiếp (.mp4, .zip,...), tự động gọi probe thay vì ép qua yt-dlp
    if is_direct_file_url(req.url):
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                res = await client.post(f"{CORE_ENGINE_URL}/api/v1/probe", json=req.dict())
                if res.status_code == 200:
                    probe_data = res.json()
                    filename = probe_data.get("filename") or os.path.basename(req.url.split("?")[0]) or "video.mp4"
                    size = probe_data.get("content_length", 0)
                    ext = os.path.splitext(filename)[1].lstrip(".") or "mp4"
                    return MediaMetadata(
                        url=req.url,
                        title=filename,
                        thumbnail=None,
                        duration=None,
                        formats=[
                            MediaFormat(
                                format_id="direct_file",
                                ext=ext,
                                resolution="Direct File",
                                filesize_approx=size,
                                fps=None,
                                vcodec=None,
                                acodec=None,
                                format_note="Tải trực tiếp đa luồng siêu tốc (16 threads)"
                            )
                        ]
                    )
            except Exception:
                pass

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

@app.post("/api/v1/cookies/sync")
async def sync_cookies(req: CookieSyncRequest):
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            res = await client.post(f"{MEDIA_EXTRACTOR_URL}/api/v1/cookies/sync", json=req.dict())
            return res.json()
        except Exception as e:
            return {"status": "error", "detail": str(e)}

def _show_folder_dialog(initial_dir: Optional[str] = None) -> Optional[str]:
    import tkinter as tk
    from tkinter import filedialog
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        start_dir = initial_dir or db.get_setting("default_download_dir") or os.path.abspath("downloads")
        selected = filedialog.askdirectory(
            master=root,
            title="Chọn Thư Mục Lưu Video - Vortex Downloader",
            initialdir=start_dir
        )
        root.destroy()
        if selected:
            return os.path.normpath(selected)
    except Exception as e:
        print(f"[Gateway] Folder picker error: {e}")
    return None

class SettingsUpdate(BaseModel):
    default_download_dir: Optional[str] = None

@app.get("/api/v1/system/settings")
async def get_system_settings():
    saved_dir = db.get_setting("default_download_dir", get_default_download_dir())
    return {"default_download_dir": saved_dir}

@app.post("/api/v1/system/settings")
async def update_system_settings(settings: SettingsUpdate):
    if settings.default_download_dir:
        norm = os.path.normpath(settings.default_download_dir)
        os.makedirs(norm, exist_ok=True)
        db.set_setting("default_download_dir", norm)
        return {"status": "ok", "default_download_dir": norm}
    return {"status": "noop"}

class OpenDialogRequest(BaseModel):
    url: str
    format_id: Optional[str] = None
    cookies: Optional[str] = None
    save_path: Optional[str] = None
    title: Optional[str] = None

pending_open_dialog: Optional[dict] = None

@app.post("/api/v1/system/open_add_dialog")
async def open_add_dialog_api(req: OpenDialogRequest):
    global pending_open_dialog
    clean_url = clean_video_url(req.url)
    msg = {
        "type": "open_add_dialog",
        "url": clean_url,
        "format_id": req.format_id,
        "cookies": req.cookies,
        "save_path": req.save_path or db.get_setting("default_download_dir", os.path.abspath("downloads")),
        "title": req.title
    }
    
    if hub.active_connections:
        await hub.broadcast(msg)
        return {"status": "ok", "delivered": True}
    else:
        pending_open_dialog = msg
        try:
            import subprocess
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
            venv_py = os.path.join(base_dir, ".venv", "Scripts", "python.exe")
            py_exe = venv_py if os.path.exists(venv_py) else sys.executable
            subprocess.Popen([py_exe, "run_app.py"], cwd=base_dir)
        except Exception as e:
            print(f"[Gateway] Error launching GUI: {e}")
        return {"status": "ok", "delivered": False, "launched": True}

@app.get("/api/v1/system/browse_folder")
@app.post("/api/v1/system/browse_folder")
async def browse_folder(initial_dir: Optional[str] = None):
    chosen = await asyncio.to_thread(_show_folder_dialog, initial_dir)
    return {
        "status": "ok" if chosen else "cancelled",
        "folder": chosen
    }

@app.post("/api/v1/download", response_model=DownloadTask)
async def create_download(req: DownloadRequest):
    req.url = clean_video_url(req.url)
    if not req.save_path:
        req.save_path = db.get_setting("default_download_dir", os.path.abspath("downloads"))

    # Định tuyến thông minh:
    # 1. File trực tiếp (.mp4, .zip, .mkv) -> Chuyển Core Engine (16 luồng phân mảnh)
    # 2. Luồng HLS (.m3u8), .ts segment hoặc nền tảng (YouTube, TikTok) -> Chuyển Media Extractor (FFmpeg merge)
    if is_direct_file_url(req.url):
        target_engine = CORE_ENGINE_URL
    elif is_streaming_media_url(req.url) or (req.format_id is not None):
        target_engine = MEDIA_EXTRACTOR_URL
    else:
        target_engine = CORE_ENGINE_URL

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

class BatchDeleteRequest(BaseModel):
    task_ids: List[str]

@app.post("/api/v1/tasks/batch_delete")
async def batch_delete_tasks(req: BatchDeleteRequest):
    if not req.task_ids:
        return {"status": "ok", "deleted_count": 0}

    # 1. Song song gửi lệnh hủy tới các engines đang chạy task
    async with httpx.AsyncClient(timeout=1.0) as client:
        cancel_coros = []
        for tid in req.task_ids:
            engine_url = task_engine_map.get(tid)
            if engine_url:
                cancel_coros.append(client.post(f"{engine_url}/api/v1/download/{tid}/cancel"))
        if cancel_coros:
            await asyncio.gather(*cancel_coros, return_exceptions=True)

    # 2. Xóa hàng loạt khỏi database SQLite trong 1 lệnh duy nhất (<2ms)
    db.delete_tasks_batch(req.task_ids)

    # 3. Phát thông báo xóa qua WebSocket
    for tid in req.task_ids:
        await hub.broadcast({"type": "task_deleted", "task_id": tid})

    return {"status": "ok", "deleted_count": len(req.task_ids)}

@app.post("/api/v1/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    engine_url = task_engine_map.get(task_id)
    if engine_url:
        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                await client.post(f"{engine_url}/api/v1/download/{task_id}/cancel")
        except Exception:
            pass
    
    # Xóa khỏi database SQLite
    db.delete_task(task_id)
    await hub.broadcast({"type": "task_deleted", "task_id": task_id})
    return {"status": "deleted", "task_id": task_id}

@app.websocket("/ws/progress")
async def websocket_progress_endpoint(websocket: WebSocket):
    global pending_open_dialog
    await hub.connect(websocket)
    if pending_open_dialog:
        msg = pending_open_dialog
        pending_open_dialog = None
        try:
            await websocket.send_json(msg)
        except Exception:
            pass
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
