import os
import time
import uuid
import asyncio
import threading
from typing import Dict, Optional, List
import yt_dlp
import imageio_ffmpeg
from common.schemas import DownloadTask, TaskStatus, EngineType, MediaMetadata, MediaFormat

def sanitize_filename(name: str) -> str:
    return "".join(c for c in name if c not in r'\/:*?"<>|').strip()

class MediaExtractorEngine:
    def __init__(self, default_download_dir: str = "downloads"):
        self.download_dir = os.path.abspath(default_download_dir)
        os.makedirs(self.download_dir, exist_ok=True)
        self.ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        self.tasks: Dict[str, DownloadTask] = {}
        self._pause_events: Dict[str, threading.Event] = {}
        self._cancelled_tasks: Dict[str, bool] = {}

    def get_task(self, task_id: str) -> Optional[DownloadTask]:
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[DownloadTask]:
        return list(self.tasks.values())

    def extract_info(self, url: str) -> MediaMetadata:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats_list: List[MediaFormat] = []
            
            raw_formats = info.get("formats", [])
            for f in raw_formats:
                fmt_id = str(f.get("format_id", ""))
                ext = f.get("ext", "mp4")
                res = f.get("resolution") or (f"{f.get('width')}x{f.get('height')}" if f.get("width") else "audio only")
                vcodec = f.get("vcodec")
                acodec = f.get("acodec")
                note = f.get("format_note", "")
                filesize = f.get("filesize") or f.get("filesize_approx")

                formats_list.append(MediaFormat(
                    format_id=fmt_id,
                    ext=ext,
                    resolution=res,
                    filesize_approx=filesize,
                    fps=f.get("fps"),
                    vcodec=vcodec,
                    acodec=acodec,
                    format_note=note
                ))

            return MediaMetadata(
                url=url,
                title=info.get("title", "Unknown Video"),
                thumbnail=info.get("thumbnail"),
                duration=info.get("duration"),
                formats=formats_list
            )

    async def start_media_download(
        self,
        url: str,
        save_path: Optional[str] = None,
        file_name: Optional[str] = None,
        format_id: Optional[str] = None
    ) -> DownloadTask:
        task_id = str(uuid.uuid4())[:8]
        now = time.time()
        target_dir = os.path.abspath(save_path) if save_path else self.download_dir
        os.makedirs(target_dir, exist_ok=True)

        initial_name = file_name or "Đang lấy tiêu đề video..."

        task = DownloadTask(
            id=task_id,
            url=url,
            file_name=initial_name,
            save_path=target_dir,
            total_bytes=0,
            downloaded_bytes=0,
            speed_bps=0.0,
            eta_seconds=None,
            progress_percent=0.0,
            status=TaskStatus.QUEUED,
            engine_type=EngineType.MEDIA_STREAM,
            num_threads=16,
            created_at=now,
            updated_at=now
        )
        self.tasks[task_id] = task

        pause_event = threading.Event()
        pause_event.set()
        self._pause_events[task_id] = pause_event
        self._cancelled_tasks[task_id] = False

        asyncio.create_task(
            asyncio.to_thread(self._run_ytdlp_download, task_id, url, target_dir, file_name, format_id)
        )

        return task

    def _run_ytdlp_download(
        self,
        task_id: str,
        url: str,
        target_dir: str,
        file_name: Optional[str],
        format_id: Optional[str]
    ):
        task = self.tasks.get(task_id)
        if not task:
            return

        task.status = TaskStatus.DOWNLOADING
        task.updated_at = time.time()

        if not file_name or file_name == "Đang lấy tiêu đề video...":
            try:
                with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "skip_download": True}) as probe_ydl:
                    info_probe = probe_ydl.extract_info(url, download=False)
                    if info_probe and info_probe.get("title"):
                        real_title = sanitize_filename(info_probe.get("title"))
                        ext = "mp3" if format_id == "audio_only" else (info_probe.get("ext") or "mp4")
                        task.file_name = f"{real_title}.{ext}"
                        task.updated_at = time.time()
            except Exception:
                pass

        pause_event = self._pause_events.get(task_id)

        def progress_hook(d):
            if self._cancelled_tasks.get(task_id):
                raise Exception("Tác vụ đã bị hủy bởi người dùng.")

            if pause_event and not pause_event.is_set():
                task.status = TaskStatus.PAUSED
                task.speed_bps = 0.0
                task.updated_at = time.time()
                while not pause_event.is_set():
                    if self._cancelled_tasks.get(task_id):
                        raise Exception("Tác vụ đã bị hủy bởi người dùng.")
                    time.sleep(0.3)
                task.status = TaskStatus.DOWNLOADING

            if d.get("status") == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                downloaded = d.get("downloaded_bytes") or 0
                speed = d.get("speed") or 0.0
                eta = d.get("eta")

                if total > 0:
                    task.total_bytes = total
                task.downloaded_bytes = downloaded
                task.speed_bps = speed
                task.eta_seconds = eta
                if task.total_bytes > 0:
                    task.progress_percent = min(100.0, round((downloaded / task.total_bytes) * 100, 2))
                task.updated_at = time.time()
            elif d.get("status") == "finished":
                task.status = TaskStatus.MERGING
                task.updated_at = time.time()

        out_template = os.path.join(target_dir, file_name or "%(title)s.%(ext)s")

        is_audio_only = False
        if format_id:
            if format_id in ("audio_only", "bestaudio"):
                selected_format = "bestaudio/best"
                is_audio_only = True
            elif "+" in format_id or "best" in format_id:
                selected_format = format_id
            else:
                selected_format = f"{format_id}+bestaudio/best"
        else:
            selected_format = "bestvideo+bestaudio/best"

        ydl_opts = {
            "ffmpeg_location": self.ffmpeg_path,
            "outtmpl": out_template,
            "format": selected_format,
            "progress_hooks": [progress_hook],
            "quiet": True,
            "no_warnings": True,
            "concurrent_fragment_downloads": 16,
            "http_chunk_size": 10485760,
            "buffersize": 1048576,
            "retries": 10,
            "fragment_retries": 10,
        }

        if is_audio_only:
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        else:
            ydl_opts["merge_output_format"] = "mp4"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                final_filename = ydl.prepare_filename(info)
                base, _ = os.path.splitext(final_filename)
                
                if is_audio_only and os.path.exists(f"{base}.mp3"):
                    final_filename = f"{base}.mp3"
                elif os.path.exists(f"{base}.mp4"):
                    final_filename = f"{base}.mp4"

                task.file_name = os.path.basename(final_filename)
                task.save_path = final_filename

                if os.path.exists(final_filename):
                    real_file_size = os.path.getsize(final_filename)
                    task.total_bytes = real_file_size
                    task.downloaded_bytes = real_file_size

                task.status = TaskStatus.COMPLETED
                task.progress_percent = 100.0
                task.speed_bps = 0.0
                task.eta_seconds = 0
                task.updated_at = time.time()
        except Exception as e:
            if self._cancelled_tasks.get(task_id):
                # Xóa hoàn toàn khỏi tasks nếu người dùng đã hủy
                self.tasks.pop(task_id, None)
            else:
                task.status = TaskStatus.FAILED
                task.error_message = str(e)
                task.updated_at = time.time()

    def pause_task(self, task_id: str) -> bool:
        if task_id in self.tasks and task_id in self._pause_events:
            self._pause_events[task_id].clear()
            self.tasks[task_id].status = TaskStatus.PAUSED
            self.tasks[task_id].speed_bps = 0.0
            return True
        return False

    def resume_task(self, task_id: str) -> bool:
        if task_id in self.tasks and task_id in self._pause_events:
            self._pause_events[task_id].set()
            self.tasks[task_id].status = TaskStatus.DOWNLOADING
            return True
        return False

    def cancel_task(self, task_id: str) -> bool:
        """Hủy tải và xóa vĩnh viễn khỏi bộ nhớ engine"""
        self._cancelled_tasks[task_id] = True
        if task_id in self._pause_events:
            self._pause_events[task_id].set()
            self._pause_events.pop(task_id, None)
        
        # Xóa dứt điểm khỏi tasks để không bao giờ trả về nữa
        self.tasks.pop(task_id, None)
        return True
