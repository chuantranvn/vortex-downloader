import asyncio
import os
import time
import uuid
import urllib.parse
from typing import Dict, Optional, List
import aiohttp
from common.schemas import DownloadTask, TaskStatus, EngineType, ChunkProgress
from common.utils import get_unique_filepath, sanitize_filename

class HttpRangeDownloadEngine:
    def __init__(self, default_download_dir: str = "downloads"):
        self.download_dir = os.path.abspath(default_download_dir)
        os.makedirs(self.download_dir, exist_ok=True)
        self.tasks: Dict[str, DownloadTask] = {}
        self._pause_events: Dict[str, asyncio.Event] = {}
        self._active_async_tasks: Dict[str, asyncio.Task] = {}

    def get_task(self, task_id: str) -> Optional[DownloadTask]:
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[DownloadTask]:
        return list(self.tasks.values())

    async def probe_url(self, url: str, headers: Optional[Dict[str, str]] = None) -> dict:
        req_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        if headers:
            req_headers.update(headers)

        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.head(url, headers=req_headers, allow_redirects=True) as resp:
                    if resp.status < 400:
                        content_length = int(resp.headers.get("Content-Length", 0))
                        accept_ranges = resp.headers.get("Accept-Ranges", "").lower()
                        supports_range = (accept_ranges == "bytes") or ("bytes" in resp.headers.get("Content-Range", ""))
                        filename = self._extract_filename(url, resp.headers.get("Content-Disposition"))
                        return {
                            "content_length": content_length,
                            "supports_range": supports_range,
                            "filename": filename,
                            "final_url": str(resp.url)
                        }
            except Exception:
                pass

            test_headers = req_headers.copy()
            test_headers["Range"] = "bytes=0-0"
            async with session.get(url, headers=test_headers, allow_redirects=True) as resp:
                content_length = 0
                content_range = resp.headers.get("Content-Range")
                supports_range = resp.status == 206 and content_range is not None

                if content_range and "/" in content_range:
                    try:
                        content_length = int(content_range.split("/")[-1])
                    except ValueError:
                        content_length = int(resp.headers.get("Content-Length", 0))
                else:
                    content_length = int(resp.headers.get("Content-Length", 0))

                filename = self._extract_filename(url, resp.headers.get("Content-Disposition"))
                return {
                    "content_length": content_length,
                    "supports_range": supports_range,
                    "filename": filename,
                    "final_url": str(resp.url)
                }

    def _extract_filename(self, url: str, content_disposition: Optional[str]) -> str:
        if content_disposition:
            import re
            match = re.search(r'filename\*?=(?:UTF-8\'\')?["\']?([^"\';\r\n]+)', content_disposition, re.IGNORECASE)
            if match:
                return urllib.parse.unquote(match.group(1).strip())

        parsed = urllib.parse.urlparse(url)
        path = parsed.path
        filename = os.path.basename(path)
        if filename and "." in filename:
            return urllib.parse.unquote(filename)
        return f"download_{int(time.time())}.bin"

    async def create_download_task(
        self,
        url: str,
        save_path: Optional[str] = None,
        file_name: Optional[str] = None,
        num_threads: int = 16,
        headers: Optional[Dict[str, str]] = None
    ) -> DownloadTask:
        probe = await self.probe_url(url, headers)
        total_bytes = probe["content_length"]
        supports_range = probe["supports_range"]
        raw_filename = file_name or probe["filename"]

        target_dir = os.path.abspath(save_path) if save_path else self.download_dir
        os.makedirs(target_dir, exist_ok=True)

        reserved_paths = [t.save_path for t in self.tasks.values() if t.status in (TaskStatus.DOWNLOADING, TaskStatus.QUEUED) and t.save_path]
        final_path = get_unique_filepath(target_dir, raw_filename, reserved_paths)
        final_filename = os.path.basename(final_path)

        task_id = str(uuid.uuid4())[:8]
        now = time.time()

        actual_threads = num_threads if (supports_range and total_bytes > 0) else 1

        chunks: List[ChunkProgress] = []
        if actual_threads > 1 and total_bytes > 0:
            chunk_size = total_bytes // actual_threads
            for i in range(actual_threads):
                start_byte = i * chunk_size
                end_byte = (i + 1) * chunk_size - 1 if i < actual_threads - 1 else total_bytes - 1
                chunks.append(ChunkProgress(
                    chunk_id=i,
                    start_byte=start_byte,
                    end_byte=end_byte,
                    downloaded_bytes=0,
                    status="pending"
                ))
        else:
            chunks.append(ChunkProgress(
                chunk_id=0,
                start_byte=0,
                end_byte=max(0, total_bytes - 1),
                downloaded_bytes=0,
                status="pending"
            ))

        task = DownloadTask(
            id=task_id,
            url=url,
            file_name=final_filename,
            save_path=final_path,
            total_bytes=total_bytes,
            downloaded_bytes=0,
            speed_bps=0.0,
            eta_seconds=None,
            progress_percent=0.0,
            status=TaskStatus.QUEUED,
            engine_type=EngineType.DIRECT_HTTP,
            num_threads=actual_threads,
            chunks=chunks,
            created_at=now,
            updated_at=now
        )
        self.tasks[task_id] = task
        self._pause_events[task_id] = asyncio.Event()
        self._pause_events[task_id].set()

        worker_task = asyncio.create_task(self._run_download_task(task_id, headers))
        self._active_async_tasks[task_id] = worker_task

        return task

    async def _run_download_task(self, task_id: str, custom_headers: Optional[Dict[str, str]] = None):
        task = self.tasks.get(task_id)
        if not task:
            return

        task.status = TaskStatus.DOWNLOADING
        task.updated_at = time.time()

        # Cấu hình TCP Connector tối đa hóa thông lượng
        connector = aiohttp.TCPConnector(limit=128, limit_per_host=64, ttl_dns_cache=300)
        timeout = aiohttp.ClientTimeout(total=None, sock_connect=30, sock_read=60)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            chunk_tasks = []
            for chunk in task.chunks:
                chunk_tasks.append(
                    asyncio.create_task(
                        self._download_chunk(session, task, chunk, custom_headers)
                    )
                )

            monitor_task = asyncio.create_task(self._monitor_progress(task_id))

            try:
                results = await asyncio.gather(*chunk_tasks, return_exceptions=True)
                for res in results:
                    if isinstance(res, Exception):
                        raise res

                if task.status == TaskStatus.DOWNLOADING:
                    task.status = TaskStatus.MERGING
                    task.updated_at = time.time()
                    await self._merge_chunks(task)
                    task.status = TaskStatus.COMPLETED
                    task.progress_percent = 100.0
                    task.speed_bps = 0.0
                    task.eta_seconds = 0
                    task.updated_at = time.time()
            except asyncio.CancelledError:
                pass
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error_message = str(e)
                task.updated_at = time.time()
            finally:
                monitor_task.cancel()

    async def _download_chunk(
        self,
        session: aiohttp.ClientSession,
        task: DownloadTask,
        chunk: ChunkProgress,
        custom_headers: Optional[Dict[str, str]]
    ):
        chunk_file = f"{task.save_path}.part.chunk_{chunk.chunk_id}"
        
        if os.path.exists(chunk_file):
            chunk.downloaded_bytes = os.path.getsize(chunk_file)

        target_bytes = (chunk.end_byte - chunk.start_byte + 1) if chunk.end_byte > 0 else 0
        if target_bytes > 0 and chunk.downloaded_bytes >= target_bytes:
            chunk.status = "completed"
            return

        req_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        if custom_headers:
            req_headers.update(custom_headers)

        current_start = chunk.start_byte + chunk.downloaded_bytes
        if chunk.end_byte > 0:
            req_headers["Range"] = f"bytes={current_start}-{chunk.end_byte}"

        chunk.status = "downloading"
        
        async with session.get(task.url, headers=req_headers) as resp:
            if resp.status not in (200, 206):
                raise Exception(f"HTTP Error {resp.status} on chunk {chunk.chunk_id}")

            mode = "ab" if chunk.downloaded_bytes > 0 else "wb"
            with open(chunk_file, mode) as f:
                # Nâng buffer lên 256KB để tăng tốc độ ghi đĩa
                async for data in resp.content.iter_chunked(262144):
                    pause_event = self._pause_events.get(task.id)
                    if pause_event and not pause_event.is_set():
                        await pause_event.wait()

                    f.write(data)
                    chunk.downloaded_bytes += len(data)
                    task.downloaded_bytes += len(data)

        chunk.status = "completed"

    async def _merge_chunks(self, task: DownloadTask):
        with open(task.save_path, "wb") as outfile:
            for chunk in task.chunks:
                chunk_file = f"{task.save_path}.part.chunk_{chunk.chunk_id}"
                if os.path.exists(chunk_file):
                    with open(chunk_file, "rb") as infile:
                        while True:
                            buf = infile.read(16777216)  # 16MB buffer ghép file siêu tốc
                            if not buf:
                                break
                            outfile.write(buf)
                    try:
                        os.remove(chunk_file)
                    except OSError:
                        pass

    async def _monitor_progress(self, task_id: str):
        task = self.tasks.get(task_id)
        if not task:
            return

        last_bytes = task.downloaded_bytes
        last_time = time.time()

        while task.status in (TaskStatus.DOWNLOADING, TaskStatus.QUEUED):
            await asyncio.sleep(0.5)
            now = time.time()
            elapsed = now - last_time
            if elapsed >= 0.5:
                total_dl = sum(c.downloaded_bytes for c in task.chunks)
                task.downloaded_bytes = total_dl
                
                bytes_diff = total_dl - last_bytes
                speed = max(0.0, bytes_diff / elapsed)
                task.speed_bps = speed

                if task.total_bytes > 0:
                    task.progress_percent = min(100.0, round((total_dl / task.total_bytes) * 100, 2))
                    remaining_bytes = max(0, task.total_bytes - total_dl)
                    task.eta_seconds = round(remaining_bytes / speed, 1) if speed > 100 else None
                else:
                    task.progress_percent = 0.0

                task.updated_at = now
                last_bytes = total_dl
                last_time = now

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
        if task_id in self._active_async_tasks:
            self._active_async_tasks[task_id].cancel()
            self._active_async_tasks.pop(task_id, None)
        if task_id in self._pause_events:
            self._pause_events[task_id].set()
            self._pause_events.pop(task_id, None)
        self.tasks.pop(task_id, None)
        return True

