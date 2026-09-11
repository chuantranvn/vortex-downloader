import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from common.schemas import DownloadRequest, DownloadTask, MediaMetadata
from services.media_extractor.extractor import MediaExtractorEngine

app = FastAPI(title="Vortex Media Extractor Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = MediaExtractorEngine()

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "media_extractor"}

@app.post("/api/v1/extract", response_model=MediaMetadata)
async def extract_media_info(req: DownloadRequest):
    try:
        import asyncio
        return await asyncio.to_thread(engine.extract_info, req.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot extract media info: {str(e)}")

@app.post("/api/v1/download", response_model=DownloadTask)
async def start_download(req: DownloadRequest):
    try:
        return await engine.start_media_download(
            url=req.url,
            save_path=req.save_path,
            file_name=req.file_name,
            format_id=req.format_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        raise HTTPException(status_code=400, detail="Cannot pause media task")
    return {"status": "paused", "task_id": task_id}

@app.post("/api/v1/download/{task_id}/resume")
def resume_download(task_id: str):
    if not engine.resume_task(task_id):
        raise HTTPException(status_code=400, detail="Cannot resume media task")
    return {"status": "resumed", "task_id": task_id}

@app.post("/api/v1/download/{task_id}/cancel")
def cancel_download(task_id: str):
    if not engine.cancel_task(task_id):
        raise HTTPException(status_code=400, detail="Cannot cancel media task")
    return {"status": "cancelled", "task_id": task_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=False)
