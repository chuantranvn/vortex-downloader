import sqlite3
import os
import time
from typing import List, Optional, Dict, Any
from common.schemas import DownloadTask, TaskStatus, EngineType

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "vortex_history.db")

class HistoryDatabase:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS download_history (
                    id TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    save_path TEXT NOT NULL,
                    total_bytes INTEGER DEFAULT 0,
                    downloaded_bytes INTEGER DEFAULT 0,
                    status TEXT NOT NULL,
                    engine_type TEXT NOT NULL,
                    num_threads INTEGER DEFAULT 8,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    completed_at REAL,
                    error_message TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            conn.commit()

    def upsert_task(self, task: DownloadTask):
        now = time.time()
        completed_at = now if task.status == TaskStatus.COMPLETED else None
        
        # Nếu đã hoàn tất, đảm bảo lấy dung lượng thực tế của file trên đĩa
        total_b = task.total_bytes
        downloaded_b = task.downloaded_bytes
        if total_b <= 0 and task.save_path and os.path.exists(task.save_path) and os.path.isfile(task.save_path):
            try:
                real_sz = os.path.getsize(task.save_path)
                total_b = real_sz
                downloaded_b = real_sz
            except Exception:
                pass

        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO download_history (
                    id, url, file_name, save_path, total_bytes, downloaded_bytes,
                    status, engine_type, num_threads, created_at, updated_at,
                    completed_at, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    file_name = excluded.file_name,
                    save_path = excluded.save_path,
                    total_bytes = excluded.total_bytes,
                    downloaded_bytes = excluded.downloaded_bytes,
                    status = excluded.status,
                    updated_at = excluded.updated_at,
                    completed_at = COALESCE(download_history.completed_at, excluded.completed_at),
                    error_message = excluded.error_message
            """, (
                task.id, task.url, task.file_name, task.save_path,
                total_b, downloaded_b,
                task.status.value if hasattr(task.status, 'value') else task.status,
                task.engine_type.value if hasattr(task.engine_type, 'value') else task.engine_type,
                task.num_threads, task.created_at, task.updated_at,
                completed_at, task.error_message
            ))
            conn.commit()

    def get_all_tasks(self, status_filter: Optional[str] = None) -> List[dict]:
        with self._get_connection() as conn:
            if status_filter and status_filter.lower() != "all":
                cur = conn.execute(
                    "SELECT * FROM download_history WHERE LOWER(status) = ? ORDER BY created_at DESC",
                    (status_filter.lower(),)
                )
            else:
                cur = conn.execute("SELECT * FROM download_history ORDER BY created_at DESC")
            
            rows = cur.fetchall()
            results = []
            updates_to_fix = []

            for r in rows:
                tot = r["total_bytes"]
                dl = r["downloaded_bytes"]
                save_path = r["save_path"]

                # Tự động khắc phục các file đã tải xong nhưng lưu 0B
                if tot <= 0 and save_path and os.path.exists(save_path) and os.path.isfile(save_path):
                    try:
                        real_size = os.path.getsize(save_path)
                        tot = real_size
                        dl = real_size
                        updates_to_fix.append((real_size, real_size, r["id"]))
                    except Exception:
                        pass

                results.append({
                    "id": r["id"],
                    "url": r["url"],
                    "file_name": r["file_name"],
                    "save_path": save_path,
                    "total_bytes": tot,
                    "downloaded_bytes": dl,
                    "status": r["status"],
                    "engine_type": r["engine_type"],
                    "num_threads": r["num_threads"],
                    "created_at": r["created_at"],
                    "updated_at": r["updated_at"],
                    "completed_at": r["completed_at"],
                    "error_message": r["error_message"],
                    "speed_bps": 0.0,
                    "progress_percent": 100.0 if r["status"] == "completed" else (round((dl / tot * 100), 1) if tot > 0 else 0.0)
                })

            if updates_to_fix:
                for real_tot, real_dl, tid in updates_to_fix:
                    conn.execute("UPDATE download_history SET total_bytes = ?, downloaded_bytes = ? WHERE id = ?", (real_tot, real_dl, tid))
                conn.commit()

            return results

    def delete_task(self, task_id: str):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM download_history WHERE id = ?", (task_id,))
            conn.commit()

    def delete_tasks_batch(self, task_ids: List[str]):
        if not task_ids:
            return
        placeholders = ",".join("?" for _ in task_ids)
        with self._get_connection() as conn:
            conn.execute(f"DELETE FROM download_history WHERE id IN ({placeholders})", task_ids)
            conn.commit()

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        with self._get_connection() as conn:
            cur = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cur.fetchone()
            return row["value"] if row else default

    def set_setting(self, key: str, value: str):
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """, (key, value))
            conn.commit()
