import os
import time
import uuid
import asyncio
import threading
from typing import Dict, Optional, List
import yt_dlp
import imageio_ffmpeg
from common.schemas import DownloadTask, TaskStatus, EngineType, MediaMetadata, MediaFormat
from common.utils import sanitize_filename, get_unique_filepath, clean_video_url

class MediaExtractorEngine:
    def __init__(self, default_download_dir: str = "downloads"):
        self.download_dir = os.path.abspath(default_download_dir)
        os.makedirs(self.download_dir, exist_ok=True)
        self.data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
        os.makedirs(self.data_dir, exist_ok=True)
        self.cookie_file_path = os.path.join(self.data_dir, "cookies.txt")
        self.ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        self.tasks: Dict[str, DownloadTask] = {}
        self._pause_events: Dict[str, threading.Event] = {}
        self._cancelled_tasks: Dict[str, bool] = {}

    def save_cookies(self, cookies_content: str):
        if cookies_content and len(cookies_content.strip()) > 0:
            try:
                with open(self.cookie_file_path, "w", encoding="utf-8") as f:
                    f.write(cookies_content)
            except Exception as e:
                print(f"[MediaExtractor] Failed to save cookies: {e}")

    def get_task(self, task_id: str) -> Optional[DownloadTask]:
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[DownloadTask]:
        return list(self.tasks.values())

    def extract_info(self, url: str, cookies: Optional[str] = None) -> MediaMetadata:
        url = clean_video_url(url)
        if cookies:
            self.save_cookies(cookies)

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "noplaylist": True,
            "extract_flat": False,
            "js_runtimes": {"node": {}},
            "remote_components": ["ejs:github"],
        }
        if os.path.exists(self.cookie_file_path) and os.path.getsize(self.cookie_file_path) > 0:
            ydl_opts["cookiefile"] = self.cookie_file_path

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
        format_id: Optional[str] = None,
        cookies: Optional[str] = None
    ) -> DownloadTask:
        if cookies:
            self.save_cookies(cookies)

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
            asyncio.to_thread(self._run_ytdlp_download, task_id, url, target_dir, file_name, format_id, cookies)
        )

        return task

    def _run_ytdlp_download(
        self,
        task_id: str,
        url: str,
        target_dir: str,
        file_name: Optional[str],
        format_id: Optional[str],
        cookies: Optional[str] = None
    ):
        task = self.tasks.get(task_id)
        if not task:
            return

        url = clean_video_url(url)
        if cookies:
            self.save_cookies(cookies)

        task.status = TaskStatus.DOWNLOADING
        task.updated_at = time.time()

        probe_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "js_runtimes": {"node": {}},
            "remote_components": ["ejs:github"],
        }
        if os.path.exists(self.cookie_file_path) and os.path.getsize(self.cookie_file_path) > 0:
            probe_opts["cookiefile"] = self.cookie_file_path

        is_audio_only = (format_id in ("audio_only", "bestaudio")) if format_id else False
        reserved_paths = [
            t.save_path for tid, t in self.tasks.items()
            if tid != task_id and t.status in (TaskStatus.DOWNLOADING, TaskStatus.QUEUED) and t.save_path
        ]

        # 1. Tối ưu lựa chọn Format để ghép file siêu tốc:
        # Ưu tiên ghép các luồng cùng chuẩn MP4 container (video mp4 + audio m4a) -> chỉ cần stream copy (-c copy), ghép xong trong 1 giây!
        if is_audio_only:
            selected_format = "bestaudio[ext=m4a]/bestaudio/best"
        elif format_id:
            if "+" in format_id or "best" in format_id:
                selected_format = format_id
            else:
                selected_format = f"{format_id}+bestaudio[ext=m4a]/{format_id}+bestaudio/best"
        else:
            selected_format = (
                "bestvideo[ext=mp4]+bestaudio[ext=m4a]/"
                "bestvideo+bestaudio[ext=m4a]/"
                "bestvideo[ext=mp4]+bestaudio/"
                "bestvideo+bestaudio/best"
            )

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
                    task.progress_percent = min(99.0, round((downloaded / task.total_bytes) * 100, 2))
                task.updated_at = time.time()
            elif d.get("status") == "finished":
                task.status = TaskStatus.MERGING
                task.progress_percent = 99.0
                task.speed_bps = 0.0
                task.updated_at = time.time()

        # 2. Cấu hình FFmpeg & yt-dlp tối đa hóa hiệu năng (Multithreaded + Stream Copy + Node.js)
        ydl_opts = {
            "ffmpeg_location": self.ffmpeg_path,
            "format": selected_format,
            "progress_hooks": [progress_hook],
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "concurrent_fragment_downloads": 16,  # Tải song song 16 phân mảnh
            "buffersize": 4194304,                 # Bộ đệm 4MB giảm 75% I/O ghi đĩa
            "retries": 10,
            "fragment_retries": 10,
            "file_access_retries": 5,
            "js_runtimes": {"node": {}},           # V8 engine từ Node.js cực nhanh
            "remote_components": ["ejs:github"],
            "overwrites": True,
            "nooverwrites": False,
            "nocheckcertificate": True,
            # Tối ưu hóa Merger bằng toàn bộ luồng CPU và stream copy thuần túy
            "postprocessor_args": {
                "Merger": ["-c", "copy", "-threads", "0"],
                "FFmpegExtractAudio": ["-threads", "0", "-preset", "ultrafast"]
            }
        }
        if os.path.exists(self.cookie_file_path) and os.path.getsize(self.cookie_file_path) > 0:
            ydl_opts["cookiefile"] = self.cookie_file_path

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
                # 🚀 TỐI ƯU 1-PASS: Trích xuất thông tin 1 lần duy nhất, tránh gọi 2 lần mạng mất 5-10s
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise Exception("Không thể lấy thông tin video từ đường dẫn này.")

                real_title = sanitize_filename(info.get("title") or f"video_{int(time.time())}")
                ext = ".mp3" if is_audio_only else ".mp4"

                target_filename = file_name if (file_name and file_name != "Đang lấy tiêu đề video...") else f"{real_title}{ext}"
                unique_path = get_unique_filepath(target_dir, target_filename, reserved_paths)

                final_file_name = os.path.basename(unique_path)
                base_no_ext, _ = os.path.splitext(final_file_name)

                task.file_name = final_file_name
                task.save_path = unique_path
                task.updated_at = time.time()

                out_template = os.path.join(target_dir, base_no_ext + ".%(ext)s")
                ydl.params["outtmpl"] = {"default": out_template}

                # Bắt đầu tải và ghép nối ngay lập tức bằng info đã trích xuất
                ydl.process_ie_result(info, download=True)

                final_filename = ydl.prepare_filename(info)
                base, _ = os.path.splitext(final_filename)

                if is_audio_only and os.path.exists(f"{base}.mp3"):
                    final_filename = f"{base}.mp3"
                elif os.path.exists(f"{base}.mp4"):
                    final_filename = f"{base}.mp4"
                elif os.path.exists(f"{base}.mkv"):
                    final_filename = f"{base}.mkv"
                elif os.path.exists(f"{base}.webm"):
                    final_filename = f"{base}.webm"

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
                err_str = str(e)
                if "Sign in to confirm you're not a bot" in err_str:
                    task.error_message = "YouTube chặn bot. Hãy mở video và bấm nút tải từ Extension Chrome để tự động gửi Cookie xác minh!"
                else:
                    task.error_message = err_str
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
