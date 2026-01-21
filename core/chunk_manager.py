"""
Chunk Manager - Handles individual download chunks for parallel downloading

This module manages the splitting of files into chunks and downloading them
simultaneously for maximum speed.
"""

import asyncio
import aiohttp
import aiofiles
import os
from dataclasses import dataclass, field
from typing import Optional, Callable
from enum import Enum


class ChunkState(Enum):
    """State of a download chunk"""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Chunk:
    """Represents a single download chunk"""
    chunk_id: int
    start_byte: int
    end_byte: int
    downloaded_bytes: int = 0
    state: ChunkState = ChunkState.PENDING
    temp_file: str = ""
    error: Optional[str] = None
    
    @property
    def total_bytes(self) -> int:
        """Total bytes this chunk needs to download"""
        return self.end_byte - self.start_byte + 1
    
    @property
    def progress(self) -> float:
        """Progress percentage of this chunk"""
        if self.total_bytes == 0:
            return 100.0
        return (self.downloaded_bytes / self.total_bytes) * 100
    
    @property
    def is_complete(self) -> bool:
        """Check if chunk download is complete"""
        return self.downloaded_bytes >= self.total_bytes


class ChunkManager:
    """
    Manages chunked downloads for a single file.
    
    Splits files into multiple chunks and downloads them in parallel
    to maximize download speed.
    """
    
    # Configuration
    MIN_CHUNK_SIZE = 1024 * 1024  # 1 MB minimum chunk size
    MAX_CHUNKS = 16  # Maximum number of parallel chunks
    DEFAULT_CHUNKS = 8  # Default number of chunks
    BUFFER_SIZE = 1024 * 64  # 64 KB buffer for reading/writing
    
    def __init__(
        self,
        url: str,
        file_size: int,
        temp_dir: str,
        num_chunks: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int, int], None]] = None
    ):
        """
        Initialize the chunk manager.
        
        Args:
            url: Download URL
            file_size: Total file size in bytes
            temp_dir: Directory for temporary chunk files
            num_chunks: Number of chunks (auto-calculated if None)
            progress_callback: Callback(chunk_id, downloaded, total) for progress updates
        """
        self.url = url
        self.file_size = file_size
        self.temp_dir = temp_dir
        self.progress_callback = progress_callback
        
        # Calculate optimal number of chunks
        self.num_chunks = self._calculate_chunks(num_chunks)
        
        # Create chunks
        self.chunks: list[Chunk] = []
        self._create_chunks()
        
        # Tracking
        self._is_paused = False
        self._is_cancelled = False
        self._active_tasks: list[asyncio.Task] = []
    
    def _calculate_chunks(self, requested_chunks: Optional[int]) -> int:
        """Calculate optimal number of chunks based on file size"""
        if self.file_size == 0:
            return 1
        
        # Calculate based on file size
        max_by_size = max(1, self.file_size // self.MIN_CHUNK_SIZE)
        
        if requested_chunks:
            return min(requested_chunks, max_by_size, self.MAX_CHUNKS)
        
        # Auto-calculate: more chunks for larger files
        if self.file_size < 10 * 1024 * 1024:  # < 10 MB
            return min(4, max_by_size)
        elif self.file_size < 100 * 1024 * 1024:  # < 100 MB
            return min(8, max_by_size)
        else:  # >= 100 MB
            return min(self.DEFAULT_CHUNKS, max_by_size, self.MAX_CHUNKS)
    
    def _create_chunks(self):
        """Create chunk definitions with byte ranges"""
        if self.file_size == 0:
            # Empty file or unknown size - single chunk
            self.chunks = [Chunk(
                chunk_id=0,
                start_byte=0,
                end_byte=0,
                temp_file=os.path.join(self.temp_dir, "chunk_0.tmp")
            )]
            return
        
        chunk_size = self.file_size // self.num_chunks
        
        for i in range(self.num_chunks):
            start = i * chunk_size
            # Last chunk gets any remaining bytes
            end = self.file_size - 1 if i == self.num_chunks - 1 else (i + 1) * chunk_size - 1
            
            self.chunks.append(Chunk(
                chunk_id=i,
                start_byte=start,
                end_byte=end,
                temp_file=os.path.join(self.temp_dir, f"chunk_{i}.tmp")
            ))
    
    async def download_chunk(
        self,
        chunk: Chunk,
        session: aiohttp.ClientSession,
        timeout: int = 30
    ) -> bool:
        """
        Download a single chunk.
        
        Args:
            chunk: The chunk to download
            session: aiohttp session to use
            timeout: Request timeout in seconds
            
        Returns:
            True if successful, False otherwise
        """
        if self._is_cancelled:
            return False
        
        chunk.state = ChunkState.DOWNLOADING
        
        # Calculate resume position
        resume_from = chunk.start_byte + chunk.downloaded_bytes
        
        headers = {
            "Range": f"bytes={resume_from}-{chunk.end_byte}",
            "User-Agent": "PyDM/1.0"
        }
        
        try:
            async with session.get(
                self.url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout, connect=10)
            ) as response:
                
                if response.status not in (200, 206):
                    chunk.error = f"HTTP {response.status}"
                    chunk.state = ChunkState.FAILED
                    return False
                
                # Open file for writing (append mode for resume)
                mode = "ab" if chunk.downloaded_bytes > 0 else "wb"
                
                async with aiofiles.open(chunk.temp_file, mode) as f:
                    async for data in response.content.iter_chunked(self.BUFFER_SIZE):
                        if self._is_cancelled:
                            chunk.state = ChunkState.PAUSED
                            return False
                        
                        if self._is_paused:
                            chunk.state = ChunkState.PAUSED
                            return False
                        
                        await f.write(data)
                        chunk.downloaded_bytes += len(data)
                        
                        # Report progress
                        if self.progress_callback:
                            self.progress_callback(
                                chunk.chunk_id,
                                chunk.downloaded_bytes,
                                chunk.total_bytes
                            )
                
                chunk.state = ChunkState.COMPLETED
                return True
                
        except asyncio.TimeoutError:
            chunk.error = "Timeout"
            chunk.state = ChunkState.FAILED
            return False
        except aiohttp.ClientError as e:
            chunk.error = str(e)
            chunk.state = ChunkState.FAILED
            return False
        except Exception as e:
            chunk.error = str(e)
            chunk.state = ChunkState.FAILED
            return False
    
    async def download_all(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> bool:
        """
        Download all chunks in parallel.
        
        Args:
            max_retries: Maximum retry attempts per chunk
            retry_delay: Delay between retries in seconds
            
        Returns:
            True if all chunks downloaded successfully
        """
        # Ensure temp directory exists
        os.makedirs(self.temp_dir, exist_ok=True)
        
        connector = aiohttp.TCPConnector(
            limit=self.num_chunks,
            limit_per_host=self.num_chunks,
            force_close=False,
            enable_cleanup_closed=True
        )
        
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            
            for chunk in self.chunks:
                if chunk.state != ChunkState.COMPLETED:
                    task = asyncio.create_task(
                        self._download_with_retry(chunk, session, max_retries, retry_delay)
                    )
                    tasks.append(task)
                    self._active_tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check results
            success = all(
                r is True for r in results 
                if not isinstance(r, Exception)
            )
            
            return success and not self._is_cancelled
    
    async def _download_with_retry(
        self,
        chunk: Chunk,
        session: aiohttp.ClientSession,
        max_retries: int,
        retry_delay: float
    ) -> bool:
        """Download a chunk with retry logic"""
        for attempt in range(max_retries):
            if self._is_cancelled or self._is_paused:
                return False
            
            success = await self.download_chunk(chunk, session)
            
            if success:
                return True
            
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay * (attempt + 1))
        
        return False
    
    async def merge_chunks(self, output_path: str) -> bool:
        """
        Merge all chunks into the final file.
        
        Args:
            output_path: Path for the final merged file
            
        Returns:
            True if merge was successful
        """
        try:
            async with aiofiles.open(output_path, "wb") as output_file:
                for chunk in sorted(self.chunks, key=lambda c: c.chunk_id):
                    if not os.path.exists(chunk.temp_file):
                        return False
                    
                    async with aiofiles.open(chunk.temp_file, "rb") as chunk_file:
                        while True:
                            data = await chunk_file.read(self.BUFFER_SIZE)
                            if not data:
                                break
                            await output_file.write(data)
            
            # Clean up temp files
            await self.cleanup()
            return True
            
        except Exception as e:
            print(f"Merge error: {e}")
            return False
    
    async def cleanup(self):
        """Remove temporary chunk files"""
        for chunk in self.chunks:
            try:
                if os.path.exists(chunk.temp_file):
                    os.remove(chunk.temp_file)
            except Exception:
                pass
        
        # Try to remove temp directory if empty
        try:
            if os.path.exists(self.temp_dir) and not os.listdir(self.temp_dir):
                os.rmdir(self.temp_dir)
        except Exception:
            pass
    
    def pause(self):
        """Pause all chunk downloads"""
        self._is_paused = True
    
    def resume(self):
        """Resume paused downloads"""
        self._is_paused = False
    
    def cancel(self):
        """Cancel all downloads"""
        self._is_cancelled = True
        for task in self._active_tasks:
            if not task.done():
                task.cancel()
    
    @property
    def total_downloaded(self) -> int:
        """Total bytes downloaded across all chunks"""
        return sum(c.downloaded_bytes for c in self.chunks)
    
    @property
    def progress(self) -> float:
        """Overall download progress percentage"""
        if self.file_size == 0:
            return 100.0
        return (self.total_downloaded / self.file_size) * 100
    
    @property
    def is_complete(self) -> bool:
        """Check if all chunks are complete"""
        return all(c.is_complete for c in self.chunks)
    
    def get_state(self) -> dict:
        """Get serializable state for persistence"""
        return {
            "url": self.url,
            "file_size": self.file_size,
            "num_chunks": self.num_chunks,
            "chunks": [
                {
                    "chunk_id": c.chunk_id,
                    "start_byte": c.start_byte,
                    "end_byte": c.end_byte,
                    "downloaded_bytes": c.downloaded_bytes,
                    "state": c.state.value,
                    "temp_file": c.temp_file
                }
                for c in self.chunks
            ]
        }
    
    def restore_state(self, state: dict):
        """Restore state from persistence"""
        for chunk_state in state.get("chunks", []):
            chunk_id = chunk_state["chunk_id"]
            if chunk_id < len(self.chunks):
                chunk = self.chunks[chunk_id]
                chunk.downloaded_bytes = chunk_state["downloaded_bytes"]
                chunk.state = ChunkState(chunk_state["state"])
                chunk.temp_file = chunk_state["temp_file"]
