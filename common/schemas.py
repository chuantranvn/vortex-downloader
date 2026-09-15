from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    QUEUED = "queued"
    ANALYZING = "analyzing"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    MERGING = "merging"
    COMPLETED = "completed"
    FAILED = "failed"

class EngineType(str, Enum):
    DIRECT_HTTP = "direct_http"
    MEDIA_STREAM = "media_stream"

class DownloadRequest(BaseModel):
    url: str
    save_path: Optional[str] = None
    file_name: Optional[str] = None
    num_threads: int = Field(default=8, ge=1, le=32)
    headers: Optional[Dict[str, str]] = None
    format_id: Optional[str] = None
    cookies: Optional[str] = None

class CookieSyncRequest(BaseModel):
    cookies: str

class ChunkProgress(BaseModel):
    chunk_id: int
    start_byte: int
    end_byte: int
    downloaded_bytes: int
    status: str = "pending"

class DownloadTask(BaseModel):
    id: str
    url: str
    file_name: str
    save_path: str
    total_bytes: int = 0
    downloaded_bytes: int = 0
    speed_bps: float = 0.0
    eta_seconds: Optional[float] = None
    progress_percent: float = 0.0
    status: TaskStatus = TaskStatus.QUEUED
    engine_type: EngineType = EngineType.DIRECT_HTTP
    num_threads: int = 8
    error_message: Optional[str] = None
    chunks: List[ChunkProgress] = []
    created_at: float
    updated_at: float

class ProgressBroadcast(BaseModel):
    task_id: str
    status: TaskStatus
    progress_percent: float
    downloaded_bytes: int
    total_bytes: int
    speed_bps: float
    eta_seconds: Optional[float] = None
    chunks: Optional[List[ChunkProgress]] = None

class MediaFormat(BaseModel):
    format_id: str
    ext: str
    resolution: Optional[str] = None
    filesize_approx: Optional[int] = None
    fps: Optional[float] = None
    vcodec: Optional[str] = None
    acodec: Optional[str] = None
    format_note: Optional[str] = None

class MediaMetadata(BaseModel):
    url: str
    title: str
    thumbnail: Optional[str] = None
    duration: Optional[float] = None
    formats: List[MediaFormat] = []
    ext: Optional[str] = None
