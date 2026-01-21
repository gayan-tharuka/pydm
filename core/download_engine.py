"""
Download Engine - High-performance async download engine

This is the main engine that orchestrates downloads, managing speed calculation,
progress tracking, and coordinating the chunk manager.
"""

import asyncio
import aiohttp
import os
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional, Callable, Any
from enum import Enum
from urllib.parse import urlparse, unquote
from datetime import datetime

from .chunk_manager import ChunkManager, ChunkState


class DownloadState(Enum):
    """State of a download task"""
    QUEUED = "queued"
    FETCHING_INFO = "fetching_info"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    MERGING = "merging"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DownloadInfo:
    """Information about a download"""
    url: str
    filename: str
    file_size: int
    resumable: bool
    content_type: str
    
    @classmethod
    async def fetch(cls, url: str, timeout: int = 10) -> "DownloadInfo":
        """Fetch download information from URL"""
        async with aiohttp.ClientSession() as session:
            async with session.head(
                url,
                allow_redirects=True,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                response.raise_for_status()
                
                # Get file size
                file_size = int(response.headers.get("Content-Length", 0))
                
                # Check if resumable
                accept_ranges = response.headers.get("Accept-Ranges", "none")
                resumable = accept_ranges.lower() == "bytes"
                
                # Get content type
                content_type = response.headers.get("Content-Type", "application/octet-stream")
                
                # Try to get filename from Content-Disposition
                filename = None
                content_disp = response.headers.get("Content-Disposition", "")
                if "filename=" in content_disp:
                    try:
                        filename = content_disp.split("filename=")[1].split(";")[0].strip('"\'')
                    except Exception:
                        pass
                
                # Fallback to URL path
                if not filename:
                    parsed = urlparse(str(response.url))
                    filename = unquote(os.path.basename(parsed.path)) or "download"
                
                return cls(
                    url=str(response.url),  # Use final URL after redirects
                    filename=filename,
                    file_size=file_size,
                    resumable=resumable,
                    content_type=content_type
                )


@dataclass
class DownloadTask:
    """Represents a single download task"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    url: str = ""
    save_path: str = ""
    filename: str = ""
    file_size: int = 0
    downloaded_bytes: int = 0
    state: DownloadState = DownloadState.QUEUED
    speed: float = 0.0  # bytes per second
    eta: int = 0  # seconds remaining
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    resumable: bool = False
    num_chunks: int = 8
    
    # Internal tracking
    _chunk_manager: Optional[ChunkManager] = field(default=None, repr=False)
    _speed_samples: list = field(default_factory=list, repr=False)
    _last_speed_update: float = field(default=0, repr=False)
    _last_downloaded: int = field(default=0, repr=False)
    saved_chunk_states: Optional[list] = field(default=None, repr=False)  # For restoring from DB

    @property
    def progress(self) -> float:
        """Download progress percentage"""
        if self.file_size == 0:
            return 0.0
        return (self.downloaded_bytes / self.file_size) * 100

    @property
    def formatted_speed(self) -> str:
        """Human-readable download speed"""
        return self._format_size(self.speed) + "/s"
    
    @property
    def formatted_size(self) -> str:
        """Human-readable file size"""
        return self._format_size(self.file_size)
    
    @property
    def formatted_downloaded(self) -> str:
        """Human-readable downloaded size"""
        return self._format_size(self.downloaded_bytes)
    
    @property
    def formatted_eta(self) -> str:
        """Human-readable ETA"""
        if self.eta <= 0:
            return "--"
        
        hours, remainder = divmod(self.eta, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{int(hours)}h {int(minutes)}m"
        elif minutes > 0:
            return f"{int(minutes)}m {int(seconds)}s"
        else:
            return f"{int(seconds)}s"
    
    @staticmethod
    def _format_size(size: float) -> str:
        """Format bytes to human-readable string"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if abs(size) < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def update_speed(self):
        """Update download speed calculation"""
        now = time.time()
        
        if self._last_speed_update == 0:
            self._last_speed_update = now
            self._last_downloaded = self.downloaded_bytes
            return
        
        elapsed = now - self._last_speed_update
        
        if elapsed >= 0.5:  # Update every 500ms
            bytes_diff = self.downloaded_bytes - self._last_downloaded
            current_speed = bytes_diff / elapsed
            
            # Keep last 5 samples for smoothing
            self._speed_samples.append(current_speed)
            if len(self._speed_samples) > 5:
                self._speed_samples.pop(0)
            
            # Average speed
            self.speed = sum(self._speed_samples) / len(self._speed_samples)
            
            # Calculate ETA
            remaining = self.file_size - self.downloaded_bytes
            if self.speed > 0:
                self.eta = int(remaining / self.speed)
            else:
                self.eta = 0
            
            self._last_speed_update = now
            self._last_downloaded = self.downloaded_bytes





class DownloadEngine:
    """
    High-performance download engine with chunked parallel downloads.
    
    Features:
    - Multi-threaded chunked downloads
    - Speed calculation and ETA
    - Pause/resume support
    - Progress callbacks
    """
    
    def __init__(
        self,
        temp_dir: str = "/tmp/pydm",
        default_chunks: int = 8,
        progress_callback: Optional[Callable[[DownloadTask], None]] = None,
        completion_callback: Optional[Callable[[DownloadTask], None]] = None
    ):
        """
        Initialize the download engine.
        
        Args:
            temp_dir: Directory for temporary chunk files
            default_chunks: Default number of chunks for downloads
            progress_callback: Called on progress updates
            completion_callback: Called when download completes
        """
        self.temp_dir = temp_dir
        self.default_chunks = default_chunks
        self.progress_callback = progress_callback
        self.completion_callback = completion_callback
        
        self._active_downloads: dict[str, DownloadTask] = {}
        self._download_tasks: dict[str, asyncio.Task] = {}
    
    async def fetch_info(self, url: str) -> DownloadInfo:
        """Fetch information about a download URL"""
        return await DownloadInfo.fetch(url)
    
    async def start_download(
        self,
        task: DownloadTask
    ) -> bool:
        """
        Start a download task.
        
        Args:
            task: The download task to start
            
        Returns:
            True if download started successfully
        """
        try:
            # Fetch download info if not already set
            if task.file_size == 0:
                task.state = DownloadState.FETCHING_INFO
                self._notify_progress(task)
                
                info = await self.fetch_info(task.url)
                task.url = info.url  # Update with final URL
                task.filename = task.filename or info.filename
                task.file_size = info.file_size
                task.resumable = info.resumable
            
            # Ensure save directory exists
            os.makedirs(os.path.dirname(task.save_path), exist_ok=True)
            
            # Create temp directory for this download
            download_temp_dir = os.path.join(self.temp_dir, task.id)
            os.makedirs(download_temp_dir, exist_ok=True)
            
            # Determine number of chunks
            num_chunks = task.num_chunks if task.resumable else 1
            
            # Create chunk manager only if it doesn't exist
            if task._chunk_manager is None:
                task._chunk_manager = ChunkManager(
                    url=task.url,
                    file_size=task.file_size,
                    temp_dir=download_temp_dir,
                    num_chunks=num_chunks,
                    progress_callback=lambda cid, dl, total: self._on_chunk_progress(task, cid, dl, total)
                )
                
                # Restore chunk states if available (e.g. from DB)
                if task.saved_chunk_states:
                    try:
                        task._chunk_manager.restore_state({"chunks": task.saved_chunk_states})
                    except Exception as e:
                        print(f"Failed to restore chunk states for {task.id}: {e}")
            else:
                # Ensure callback is re-attached if needed (e.g. after serialization restore)
                task._chunk_manager.progress_callback = lambda cid, dl, total: self._on_chunk_progress(task, cid, dl, total)
            
            # Start download
            task.state = DownloadState.DOWNLOADING
            self._active_downloads[task.id] = task
            
            # Run download in background
            download_task = asyncio.create_task(self._run_download(task))
            self._download_tasks[task.id] = download_task
            
            return True
            
        except Exception as e:
            task.state = DownloadState.FAILED
            task.error = str(e)
            self._notify_progress(task)
            return False
    
    async def _run_download(self, task: DownloadTask):
        """Run the actual download process"""
        try:
            # Download all chunks
            success = await task._chunk_manager.download_all()
            
            if not success:
                if task.state != DownloadState.PAUSED:
                    task.state = DownloadState.FAILED
                    task.error = "Download failed"
                self._notify_progress(task)
                return
            
            # Merge chunks
            task.state = DownloadState.MERGING
            self._notify_progress(task)
            
            merge_success = await task._chunk_manager.merge_chunks(task.save_path)
            
            if merge_success:
                task.state = DownloadState.COMPLETED
                task.completed_at = datetime.now()
                task.downloaded_bytes = task.file_size
            else:
                task.state = DownloadState.FAILED
                task.error = "Failed to merge chunks"
            
            self._notify_progress(task)
            
            if self.completion_callback:
                self.completion_callback(task)
                
        except asyncio.CancelledError:
            task.state = DownloadState.CANCELLED
            self._notify_progress(task)
        except Exception as e:
            task.state = DownloadState.FAILED
            task.error = str(e)
            self._notify_progress(task)
        finally:
            # Cleanup
            if task.id in self._active_downloads:
                del self._active_downloads[task.id]
            if task.id in self._download_tasks:
                del self._download_tasks[task.id]
    
    def _on_chunk_progress(self, task: DownloadTask, chunk_id: int, downloaded: int, total: int):
        """Handle progress updates from chunk manager"""
        if task._chunk_manager:
            task.downloaded_bytes = task._chunk_manager.total_downloaded
            task.update_speed()
            self._notify_progress(task)
    
    def _notify_progress(self, task: DownloadTask):
        """Notify progress callback"""
        if self.progress_callback:
            self.progress_callback(task)
    
    def pause_download(self, task_id: str):
        """Pause a download"""
        if task_id in self._active_downloads:
            task = self._active_downloads[task_id]
            if task._chunk_manager:
                task._chunk_manager.pause()
            task.state = DownloadState.PAUSED
            self._notify_progress(task)
    
    async def resume_download(self, task: DownloadTask) -> bool:
        """Resume a paused download"""
        if task.state != DownloadState.PAUSED:
            return False
        
        if task._chunk_manager:
            task._chunk_manager.resume()
        
        return await self.start_download(task)
    
    def cancel_download(self, task_id: str):
        """Cancel a download"""
        if task_id in self._active_downloads:
            task = self._active_downloads[task_id]
            if task._chunk_manager:
                task._chunk_manager.cancel()
            task.state = DownloadState.CANCELLED
            self._notify_progress(task)
        
        if task_id in self._download_tasks:
            self._download_tasks[task_id].cancel()
    
    async def cleanup(self):
        """Cleanup all downloads and temporary files"""
        for task_id in list(self._download_tasks.keys()):
            self.cancel_download(task_id)
        
        # Wait for all tasks to complete
        if self._download_tasks:
            await asyncio.gather(*self._download_tasks.values(), return_exceptions=True)
