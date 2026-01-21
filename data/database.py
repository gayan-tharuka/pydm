"""
Database - SQLite storage for download history and state
"""

import sqlite3
import os
from typing import Optional, List
from datetime import datetime
from contextlib import contextmanager

from ..core.download_engine import DownloadTask, DownloadState


class Database:
    """SQLite database for persistent storage"""
    
    def __init__(self, db_path: str):
        """
        Initialize database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._create_tables()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Downloads table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS downloads (
                    id TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    save_path TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    file_size INTEGER DEFAULT 0,
                    downloaded_bytes INTEGER DEFAULT 0,
                    state TEXT DEFAULT 'queued',
                    error TEXT,
                    resumable INTEGER DEFAULT 0,
                    num_chunks INTEGER DEFAULT 8,
                    created_at TEXT,
                    completed_at TEXT
                )
            """)
            
            # Chunks table for resume support
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    download_id TEXT NOT NULL,
                    chunk_id INTEGER NOT NULL,
                    start_byte INTEGER NOT NULL,
                    end_byte INTEGER NOT NULL,
                    downloaded_bytes INTEGER DEFAULT 0,
                    state TEXT DEFAULT 'pending',
                    temp_file TEXT,
                    FOREIGN KEY (download_id) REFERENCES downloads(id)
                )
            """)
            
            # Settings table for key-value storage
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            
            conn.commit()
    
    def save_download(self, task: DownloadTask):
        """Save a new download task"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO downloads (
                    id, url, save_path, filename, file_size, downloaded_bytes,
                    state, error, resumable, num_chunks, created_at, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.id,
                task.url,
                task.save_path,
                task.filename,
                task.file_size,
                task.downloaded_bytes,
                task.state.value,
                task.error,
                1 if task.resumable else 0,
                task.num_chunks,
                task.created_at.isoformat() if task.created_at else None,
                task.completed_at.isoformat() if task.completed_at else None
            ))
            
            conn.commit()
    
    def update_download(self, task: DownloadTask):
        """Update an existing download task"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE downloads SET
                    downloaded_bytes = ?,
                    state = ?,
                    error = ?,
                    completed_at = ?
                WHERE id = ?
            """, (
                task.downloaded_bytes,
                task.state.value,
                task.error,
                task.completed_at.isoformat() if task.completed_at else None,
                task.id
            ))
            
            conn.commit()
    
    def get_download(self, download_id: str) -> Optional[DownloadTask]:
        """Get a download by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM downloads WHERE id = ?", (download_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_task(row)
            return None
    
    def get_all_downloads(self) -> List[DownloadTask]:
        """Get all downloads"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM downloads ORDER BY created_at DESC")
            rows = cursor.fetchall()
            
            return [self._row_to_task(row) for row in rows]
    
    def delete_download(self, download_id: str):
        """Delete a download"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Delete chunks first
            cursor.execute("DELETE FROM chunks WHERE download_id = ?", (download_id,))
            
            # Delete download
            cursor.execute("DELETE FROM downloads WHERE id = ?", (download_id,))
            
            conn.commit()
    
    def clear_completed(self):
        """Clear all completed downloads"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get completed download IDs
            cursor.execute("SELECT id FROM downloads WHERE state = 'completed'")
            ids = [row['id'] for row in cursor.fetchall()]
            
            # Delete chunks
            for dl_id in ids:
                cursor.execute("DELETE FROM chunks WHERE download_id = ?", (dl_id,))
            
            # Delete downloads
            cursor.execute("DELETE FROM downloads WHERE state = 'completed'")
            
            conn.commit()
    
    def save_chunk_state(self, download_id: str, chunks: list):
        """Save chunk states for resume support"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Clear existing chunks
            cursor.execute("DELETE FROM chunks WHERE download_id = ?", (download_id,))
            
            # Insert new chunk states
            for chunk in chunks:
                cursor.execute("""
                    INSERT INTO chunks (
                        download_id, chunk_id, start_byte, end_byte,
                        downloaded_bytes, state, temp_file
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    download_id,
                    chunk.chunk_id,
                    chunk.start_byte,
                    chunk.end_byte,
                    chunk.downloaded_bytes,
                    chunk.state.value,
                    chunk.temp_file
                ))
            
            conn.commit()
    
    def get_chunk_states(self, download_id: str) -> list:
        """Get chunk states for a download"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM chunks WHERE download_id = ? ORDER BY chunk_id",
                (download_id,)
            )
            
            return [dict(row) for row in cursor.fetchall()]
    
    def _row_to_task(self, row: sqlite3.Row) -> DownloadTask:
        """Convert database row to DownloadTask"""
        task = DownloadTask(
            id=row['id'],
            url=row['url'],
            save_path=row['save_path'],
            filename=row['filename'],
            file_size=row['file_size'],
            downloaded_bytes=row['downloaded_bytes'],
            state=DownloadState(row['state']),
            error=row['error'],
            resumable=bool(row['resumable']),
            num_chunks=row['num_chunks']
        )
        
        if row['created_at']:
            task.created_at = datetime.fromisoformat(row['created_at'])
        if row['completed_at']:
            task.completed_at = datetime.fromisoformat(row['completed_at'])
        
        return task
    
    def get_setting(self, key: str, default: str = "") -> str:
        """Get a setting value"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row['value'] if row else default
    
    def set_setting(self, key: str, value: str):
        """Set a setting value"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value)
            )
            conn.commit()
