"""
Download Manager - High-level manager for all downloads

Manages the download queue, concurrent downloads, and persistence.
"""

import asyncio
import os
from typing import Optional, Callable, List
from datetime import datetime

from .download_engine import DownloadEngine, DownloadTask, DownloadState
from ..data.database import Database
from ..data.config import Config


class DownloadManager:
    """
    High-level download manager that coordinates all downloads.
    
    Features:
    - Download queue management
    - Concurrent download limiting
    - Persistence and recovery
    - Progress callbacks for UI
    """
    
    def __init__(
        self,
        config: Optional[Config] = None,
        database: Optional[Database] = None,
        progress_callback: Optional[Callable[[DownloadTask], None]] = None,
        completion_callback: Optional[Callable[[DownloadTask], None]] = None
    ):
        """
        Initialize the download manager.
        
        Args:
            config: Configuration object
            database: Database for persistence
            progress_callback: Called on download progress
            completion_callback: Called on download completion
        """
        self.config = config or Config()
        self.database = database
        self.progress_callback = progress_callback
        self.completion_callback = completion_callback
        
        # Initialize download engine
        self.engine = DownloadEngine(
            temp_dir=self.config.temp_dir,
            default_chunks=self.config.default_chunks,
            progress_callback=self._on_progress,
            completion_callback=self._on_completion
        )
        
        # Download tracking
        self.downloads: dict[str, DownloadTask] = {}
        self.queue: List[str] = []  # Queue of task IDs
        self._active_count = 0
        self._is_running = False
        self._queue_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the download manager"""
        self._is_running = True
        
        # Load pending downloads from database
        if self.database:
            saved_downloads = self.database.get_all_downloads()
            for dl in saved_downloads:
                if dl.state in (DownloadState.QUEUED, DownloadState.DOWNLOADING, DownloadState.PAUSED):
                    # Restore chunk states if available
                    try:
                        chunk_states = self.database.get_chunk_states(dl.id)
                        if chunk_states:
                            dl.saved_chunk_states = chunk_states
                    except Exception as e:
                        print(f"Error loading chunks for {dl.id}: {e}")
                        
                    self.downloads[dl.id] = dl
                    if dl.state == DownloadState.QUEUED:
                        self.queue.append(dl.id)
        
        # Start queue processor
        self._queue_task = asyncio.create_task(self._process_queue())
    
    async def stop(self):
        """Stop the download manager"""
        self._is_running = False
        
        # Save state of all active downloads
        if self.database:
            for task in self.downloads.values():
                if task.state in (DownloadState.DOWNLOADING, DownloadState.PAUSED):
                    self._save_task_state(task)
        
        if self._queue_task:
            self._queue_task.cancel()
            try:
                await self._queue_task
            except asyncio.CancelledError:
                pass
        
        await self.engine.cleanup()
    
    def _save_task_state(self, task: DownloadTask):
        """Save task state including chunks"""
        if self.database:
            try:
                self.database.update_download(task)
                
                # Save chunks if manager exists
                if task._chunk_manager:
                    state = task._chunk_manager.get_state()
                    # Pass dicts directly; database now supports both formats
                    self.database.save_chunk_state(task.id, state['chunks'])
            except Exception as e:
                print(f"Failed to save chunk state for {task.id}: {e}")

    async def add_download(
        self,
        url: str,
        save_dir: Optional[str] = None,
        filename: Optional[str] = None,
        start_immediately: bool = True
    ) -> DownloadTask:
        """
        Add a new download.
        
        Args:
            url: URL to download
            save_dir: Directory to save file (uses default if None)
            filename: Filename override (auto-detected if None)
            start_immediately: Start download immediately if queue allows
            
        Returns:
            The created download task
        """
        # Fetch info first to get filename if needed
        info = await self.engine.fetch_info(url)
        
        final_filename = filename or info.filename
        final_save_dir = save_dir or self.config.default_download_dir
        save_path = os.path.join(final_save_dir, final_filename)
        
        # Handle duplicate filenames
        save_path = self._get_unique_path(save_path)
        
        # Create task
        task = DownloadTask(
            url=info.url,
            save_path=save_path,
            filename=os.path.basename(save_path),
            file_size=info.file_size,
            resumable=info.resumable,
            num_chunks=self.config.default_chunks,
            state=DownloadState.QUEUED
        )
        
        # Add to tracking
        self.downloads[task.id] = task
        
        # Save to database
        if self.database:
            self.database.save_download(task)
        
        if start_immediately:
            self.queue.append(task.id)
        
        return task
    
    def _get_unique_path(self, path: str) -> str:
        """Get a unique file path by adding number suffix if needed"""
        if not os.path.exists(path):
            return path
        
        base, ext = os.path.splitext(path)
        counter = 1
        
        while os.path.exists(f"{base} ({counter}){ext}"):
            counter += 1
        
        return f"{base} ({counter}){ext}"
    
    async def _process_queue(self):
        """Process the download queue"""
        while self._is_running:
            try:
                # Check if we can start more downloads
                while (
                    self._active_count < self.config.max_concurrent_downloads
                    and self.queue
                ):
                    task_id = self.queue.pop(0)
                    task = self.downloads.get(task_id)
                    
                    if task and task.state == DownloadState.QUEUED:
                        self._active_count += 1
                        await self.engine.start_download(task)
                
                await asyncio.sleep(0.5)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Queue processing error: {e}")
                await asyncio.sleep(1)
    
    def _on_progress(self, task: DownloadTask):
        """Handle progress updates"""
        # Update database
        if self.database:
            self.database.update_download(task)
        
        # Notify UI
        if self.progress_callback:
            self.progress_callback(task)
    
    def _on_completion(self, task: DownloadTask):
        """Handle download completion"""
        self._active_count = max(0, self._active_count - 1)
        
        # Update database
        if self.database:
            self.database.update_download(task)
        
        # Notify UI
        if self.completion_callback:
            self.completion_callback(task)
    
    def pause_download(self, task_id: str):
        """Pause a download"""
        self.engine.pause_download(task_id)
        self._active_count = max(0, self._active_count - 1)
        
        # Save state
        task = self.downloads.get(task_id)
        if task:
            self._save_task_state(task)
    
    async def resume_download(self, task_id: str):
        """Resume a paused download"""
        task = self.downloads.get(task_id)
        if task and task.state == DownloadState.PAUSED:
            self._active_count += 1
            await self.engine.resume_download(task)
    
    def cancel_download(self, task_id: str):
        """Cancel a download"""
        self.engine.cancel_download(task_id)
        self._active_count = max(0, self._active_count - 1)
        
        # Remove from queue if present
        if task_id in self.queue:
            self.queue.remove(task_id)
    
    def remove_download(self, task_id: str, delete_file: bool = False):
        """Remove a download from the list"""
        task = self.downloads.get(task_id)
        
        if task:
            # Cancel if active
            if task.state in (DownloadState.DOWNLOADING, DownloadState.QUEUED):
                self.cancel_download(task_id)
            
            # Delete file if requested
            if delete_file and os.path.exists(task.save_path):
                try:
                    os.remove(task.save_path)
                except Exception:
                    pass
            
            # Remove from tracking
            del self.downloads[task_id]
            
            # Remove from database
            if self.database:
                self.database.delete_download(task_id)
    
    def get_all_downloads(self) -> List[DownloadTask]:
        """Get all downloads"""
        return list(self.downloads.values())
    
    def get_active_downloads(self) -> List[DownloadTask]:
        """Get currently active downloads"""
        return [
            d for d in self.downloads.values()
            if d.state in (DownloadState.DOWNLOADING, DownloadState.FETCHING_INFO)
        ]
    
    def get_completed_downloads(self) -> List[DownloadTask]:
        """Get completed downloads"""
        return [
            d for d in self.downloads.values()
            if d.state == DownloadState.COMPLETED
        ]
