#!/usr/bin/env python3
"""
PyDM - Python Download Manager

A high-speed, open-source download manager for macOS.
Features multi-threaded chunked downloads for maximum speed.
"""

import sys
import asyncio
import signal
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from pydm.core.download_manager import DownloadManager
from pydm.data.config import Config
from pydm.data.database import Database
from pydm.ui.main_window import MainWindow
from pydm.ui.styles import Styles


class AsyncHelper:
    """Helper to run asyncio event loop with Qt"""
    
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
        self._timer = QTimer()
        self._timer.timeout.connect(self._process_events)
        self._timer.start(10)  # Process every 10ms
    
    def _process_events(self):
        """Process pending asyncio events"""
        self.loop.run_until_complete(asyncio.sleep(0))


def main():
    """Main application entry point"""
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("PyDM")
    app.setApplicationDisplayName("PyDM - Download Manager")
    app.setOrganizationName("PyDM")
    app.setOrganizationDomain("pydm.app")
    
    # Apply global stylesheet
    app.setStyleSheet(Styles.get_main_stylesheet())
    
    # Don't quit when last window closes (we have system tray)
    app.setQuitOnLastWindowClosed(False)
    
    # Load configuration
    config = Config.load()
    
    # Initialize database
    database = Database(config.database_path)
    
    # Create asyncio event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Create async helper for Qt integration
    async_helper = AsyncHelper(loop)
    
    # Create download manager
    download_manager = DownloadManager(
        config=config,
        database=database
    )
    
    # Start download manager
    loop.run_until_complete(download_manager.start())
    
    # Create main window
    window = MainWindow(
        download_manager=download_manager,
        config=config
    )
    
    # Show window (unless start minimized)
    if not config.start_minimized:
        window.show()
    
    # Handle signals
    def signal_handler(sig, frame):
        print("\nShutting down PyDM...")
        loop.run_until_complete(download_manager.stop())
        app.quit()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run application
    exit_code = app.exec()
    
    # Cleanup
    loop.run_until_complete(download_manager.stop())
    loop.close()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
