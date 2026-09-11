import sys
import os
# Thêm root vào sys.path để import common
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from common.schemas import DownloadRequest, DownloadTask
from services.core_engine.engine import HttpRangeDownloadEngine

app = FastAPI(title="Vortex Core Engine (IDM Multi-threaded)", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = HttpRangeDownloadEngine()

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "core_engine"}

@app.post("/api/v1/probe")
async def probe_url(req: DownloadRequest):
    return await engine.probe_url(req.url, req.headers)

@app.post("/api/v1/download", response_model=DownloadTask)
async def start_download(req: DownloadRequest):
    return await engine.create_download_task(
        url=req.url,
        save_path=req.save_path,
        file_name=req.file_name,
        num_threads=req.num_threads,
        headers=req.headers
    )

@app.get("/api/v1/download/{task_id}", response_model=DownloadTask)
def get_task(task_id: str):
    task = engine.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.get("/api/v1/download", response_model=list[DownloadTask])
def list_tasks():
    return engine.get_all_tasks()

@app.post("/api/v1/download/{task_id}/pause")
def pause_download(task_id: str):
    if not engine.pause_task(task_id):
        raise HTTPException(status_code=400, detail="Cannot pause task")
    return {"status": "paused", "task_id": task_id}

@app.post("/api/v1/download/{task_id}/resume")
def resume_download(task_id: str):
    if not engine.resume_task(task_id):
        raise HTTPException(status_code=400, detail="Cannot resume task")
    return {"status": "resumed", "task_id": task_id}

@app.post("/api/v1/download/{task_id}/cancel")
def cancel_download(task_id: str):
    if not engine.cancel_task(task_id):
        raise HTTPException(status_code=400, detail="Cannot cancel task")
    return {"status": "cancelled", "task_id": task_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=False)
