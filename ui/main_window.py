"""
Main Window - The primary application window for PyDM

Features a modern, sleek interface with download list, toolbar, and status bar.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QFrame,
    QStatusBar, QToolBar, QMessageBox, QApplication,
    QSizePolicy, QScrollArea, QSpacerItem, QSystemTrayIcon
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, QSize
from PyQt6.QtGui import QFont, QAction, QCloseEvent, QIcon

import asyncio
import os
import subprocess
from typing import Optional, Dict

from ..core.download_manager import DownloadManager
from ..core.download_engine import DownloadTask, DownloadState
from ..data.config import Config
from ..data.database import Database
from .styles import Styles
from .add_download_dialog import AddDownloadDialog
from .download_item_widget import DownloadItemWidget
from .system_tray import SystemTrayIcon
from .icon_utils import IconUtils


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(
        self,
        download_manager: DownloadManager,
        config: Config,
        parent=None
    ):
        super().__init__(parent)
        
        self.download_manager = download_manager
        self.config = config
        
        # Widget tracking
        self._download_widgets: Dict[str, DownloadItemWidget] = {}
        self._list_items: Dict[str, QListWidgetItem] = {}
        
        # Setup UI
        self._setup_window()
        self._setup_toolbar()
        self._setup_central_widget()
        self._setup_status_bar()
        self._setup_system_tray()
        
        # Apply styles
        self.setStyleSheet(Styles.get_main_stylesheet())
        
        # Setup update timer
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._update_status)
        self._update_timer.start(1000)  # Update every second
        
        # Connect to download manager callbacks
        self.download_manager.progress_callback = self._on_download_progress
        self.download_manager.completion_callback = self._on_download_complete
        
        # Load existing downloads
        self._load_downloads()
    
    def _setup_window(self):
        """Setup window properties"""
        self.setWindowTitle("PyDM")
        self.setMinimumSize(800, 600)
        self.resize(900, 650)
        
        # Center on screen
        screen = QApplication.primaryScreen()
        if screen:
            screen_geo = screen.availableGeometry()
            x = (screen_geo.width() - self.width()) // 2
            y = (screen_geo.height() - self.height()) // 2
            self.move(x, y)
    
    def _setup_toolbar(self):
        """Setup the toolbar"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        # Add Download Action
        add_action = QAction(IconUtils.icon("add", Styles.COLORS['primary']), "Add Download", self)
        add_action.setToolTip("Add a new download (Cmd+N)")
        add_action.setShortcut("Ctrl+N")
        add_action.triggered.connect(self._show_add_dialog)
        toolbar.addAction(add_action)
        
        toolbar.addSeparator()
        
        # Pause All Action
        pause_all_action = QAction(IconUtils.icon("pause", Styles.COLORS['text_secondary']), "Pause All", self)
        pause_all_action.setToolTip("Pause all active downloads")
        pause_all_action.triggered.connect(self._pause_all)
        toolbar.addAction(pause_all_action)
        
        # Resume All Action
        resume_all_action = QAction(IconUtils.icon("resume", Styles.COLORS['text_secondary']), "Resume All", self)
        resume_all_action.setToolTip("Resume all paused downloads")
        resume_all_action.triggered.connect(self._resume_all)
        toolbar.addAction(resume_all_action)
        
        toolbar.addSeparator()
        
        # Clear Completed Action
        clear_action = QAction(IconUtils.icon("clear", Styles.COLORS['text_secondary']), "Clear Completed", self)
        clear_action.setToolTip("Remove completed downloads from list")
        clear_action.triggered.connect(self._clear_completed)
        toolbar.addAction(clear_action)
        
        # Add spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        
        # Settings Action
        settings_action = QAction(IconUtils.icon("settings", Styles.COLORS['text_secondary']), "Settings", self)
        settings_action.setToolTip("Open settings")
        settings_action.triggered.connect(self._show_settings)
        toolbar.addAction(settings_action)
        
        self.addToolBar(toolbar)
    
    def _setup_central_widget(self):
        """Setup the central widget"""
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Downloads")
        title.setObjectName("titleLabel")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Stats labels
        self.active_label = QLabel("0 active")
        self.active_label.setObjectName("subtitleLabel")
        self.active_label.setStyleSheet(f"""
            padding: 4px 8px;
            background-color: {Styles.COLORS['bg_medium']};
            border-radius: 4px;
        """)
        header_layout.addWidget(self.active_label)
        
        self.speed_label = QLabel("0 B/s")
        self.speed_label.setObjectName("subtitleLabel")
        self.speed_label.setStyleSheet(f"""
            color: {Styles.COLORS['primary']};
            font-weight: 600;
            padding: 4px 8px;
            background-color: {Styles.COLORS['bg_medium']};
            border-radius: 4px;
        """)
        header_layout.addWidget(self.speed_label)
        
        layout.addLayout(header_layout)
        
        # Download list
        self.download_list = QListWidget()
        self.download_list.setSpacing(10)
        self.download_list.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.download_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        layout.addWidget(self.download_list)
        
        # Empty state (shown when no downloads)
        self.empty_widget = QWidget()
        empty_layout = QVBoxLayout(self.empty_widget)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.setSpacing(10)
        
        # Large empty icon
        empty_icon = QLabel()
        empty_icon.setFixedSize(80, 80)
        empty_icon.setPixmap(IconUtils.icon("archive", Styles.COLORS['border'], 80).pixmap(80, 80))
        empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_icon)
        
        empty_text = QLabel("No Downloads Yet")
        empty_text.setObjectName("subtitleLabel")
        empty_text.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {Styles.COLORS['text_muted']};")
        empty_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_text)
        
        empty_hint = QLabel("Click '+' to add a new download")
        empty_hint.setObjectName("mutedLabel")
        empty_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_hint)
        
        add_btn = QPushButton("Start Download", cursor=Qt.CursorShape.PointingHandCursor)
        add_btn.setObjectName("primaryButton")
        add_btn.setFixedSize(140, 36)
        add_btn.clicked.connect(self._show_add_dialog)
        empty_layout.addWidget(add_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.empty_widget)
        
        self.setCentralWidget(central)
        
        # Initial visibility
        self._update_empty_state()
    
    def _setup_status_bar(self):
        """Setup the status bar"""
        status_bar = QStatusBar()
        status_bar.setSizeGripEnabled(False)
        self.status_message = QLabel("Ready")
        self.status_message.setObjectName("mutedLabel")
        status_bar.addWidget(self.status_message)
        self.setStatusBar(status_bar)
    
    def _setup_system_tray(self):
        """Setup system tray icon"""
        self.tray = SystemTrayIcon(self)
        
        # Connect signals
        self.tray.show_window_requested.connect(self._show_from_tray)
        self.tray.add_download_requested.connect(self._show_add_dialog)
        self.tray.pause_all_requested.connect(self._pause_all)
        self.tray.resume_all_requested.connect(self._resume_all)
        self.tray.quit_requested.connect(self._quit_app)
        
        self.tray.show()
    
    def _load_downloads(self):
        """Load existing downloads into the UI"""
        for task in self.download_manager.get_all_downloads():
            self._add_download_widget(task)
        
        self._update_empty_state()
    
    def _add_download_widget(self, task: DownloadTask):
        """Add a download widget to the list"""
        widget = DownloadItemWidget(task)
        
        # Connect signals
        widget.pause_clicked.connect(self._on_pause_clicked)
        widget.resume_clicked.connect(self._on_resume_clicked)
        widget.cancel_clicked.connect(self._on_cancel_clicked)
        widget.remove_clicked.connect(self._on_remove_clicked)
        widget.open_folder_clicked.connect(self._on_open_folder)
        
        # Create list item
        item = QListWidgetItem()
        item.setSizeHint(widget.sizeHint())
        
        self.download_list.addItem(item)
        self.download_list.setItemWidget(item, widget)
        
        # Track widgets
        self._download_widgets[task.id] = widget
        self._list_items[task.id] = item
        
        self._update_empty_state()
    
    def _update_download_widget(self, task: DownloadTask):
        """Update an existing download widget"""
        widget = self._download_widgets.get(task.id)
        if widget:
            widget.task = task
            widget.update_display()
    
    def _remove_download_widget(self, task_id: str):
        """Remove a download widget from the list"""
        item = self._list_items.get(task_id)
        if item:
            row = self.download_list.row(item)
            self.download_list.takeItem(row)
            
            del self._download_widgets[task_id]
            del self._list_items[task_id]
        
        self._update_empty_state()
    
    def _update_empty_state(self):
        """Update empty state visibility"""
        has_downloads = len(self._download_widgets) > 0
        self.download_list.setVisible(has_downloads)
        self.empty_widget.setVisible(not has_downloads)
    
    def _update_status(self):
        """Update status bar and tray"""
        active = self.download_manager.get_active_downloads()
        active_count = len(active)
        
        # Calculate total speed
        total_speed = sum(d.speed for d in active)
        speed_str = DownloadTask._format_size(total_speed) + "/s"
        
        # Update UI
        self.active_label.setText(f"{active_count} active")
        self.speed_label.setText(speed_str)
        
        # Update tray
        self.tray.update_status(active_count, speed_str)
    
    # ============ Dialog Methods ============
    
    def _show_add_dialog(self):
        """Show add download dialog"""
        # Check clipboard for URL
        clipboard = QApplication.clipboard()
        clipboard_text = clipboard.text().strip() if clipboard else ""
        
        clipboard_url = None
        if clipboard_text.startswith(("http://", "https://")):
            clipboard_url = clipboard_text
        
        dialog = AddDownloadDialog(
            self,
            default_dir=self.config.default_download_dir,
            clipboard_url=clipboard_url
        )
        
        if dialog.exec():
            url, save_dir, filename, start_immediately, chunks = dialog.get_values()
            
            # Add download
            loop = asyncio.get_event_loop()
            loop.create_task(self._add_download(url, save_dir, filename, start_immediately))
    
    async def _add_download(self, url: str, save_dir: str, filename: str, start_immediately: bool):
        """Add a new download"""
        try:
            task = await self.download_manager.add_download(
                url=url,
                save_dir=save_dir,
                filename=filename,
                start_immediately=start_immediately
            )
            
            # Add to UI
            self._add_download_widget(task)
            self.status_message.setText(f"Added: {task.filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add download: {e}")
    
    def _show_settings(self):
        """Show settings dialog"""
        QMessageBox.information(self, "Settings", "Settings dialog coming soon!")
    
    # ============ Download Action Handlers ============
    
    @pyqtSlot(str)
    def _on_pause_clicked(self, task_id: str):
        """Handle pause button click"""
        self.download_manager.pause_download(task_id)
    
    @pyqtSlot(str)
    def _on_resume_clicked(self, task_id: str):
        """Handle resume button click"""
        loop = asyncio.get_event_loop()
        loop.create_task(self.download_manager.resume_download(task_id))
    
    @pyqtSlot(str)
    def _on_cancel_clicked(self, task_id: str):
        """Handle cancel button click"""
        self.download_manager.cancel_download(task_id)
    
    @pyqtSlot(str)
    def _on_remove_clicked(self, task_id: str):
        """Handle remove button click"""
        self.download_manager.remove_download(task_id)
        self._remove_download_widget(task_id)
    
    @pyqtSlot(str)
    def _on_open_folder(self, task_id: str):
        """Handle open folder button click"""
        task = self.download_manager.downloads.get(task_id)
        if task and os.path.exists(task.save_path):
            folder = os.path.dirname(task.save_path)
            subprocess.run(["open", folder])
    
    def _pause_all(self):
        """Pause all active downloads"""
        for task in self.download_manager.get_active_downloads():
            self.download_manager.pause_download(task.id)
    
    def _resume_all(self):
        """Resume all paused downloads"""
        loop = asyncio.get_event_loop()
        for task in self.download_manager.downloads.values():
            if task.state == DownloadState.PAUSED:
                loop.create_task(self.download_manager.resume_download(task.id))
    
    def _clear_completed(self):
        """Clear completed downloads"""
        completed = self.download_manager.get_completed_downloads()
        for task in completed:
            self.download_manager.remove_download(task.id)
            self._remove_download_widget(task.id)
    
    # ============ Callbacks ============
    
    def _on_download_progress(self, task: DownloadTask):
        """Handle download progress update"""
        self._update_download_widget(task)
    
    def _on_download_complete(self, task: DownloadTask):
        """Handle download completion"""
        self._update_download_widget(task)
        
        if task.state == DownloadState.COMPLETED:
            self.tray.show_download_complete(task.filename)
            self.status_message.setText(f"Completed: {task.filename}")
        elif task.state == DownloadState.FAILED:
            self.tray.show_download_failed(task.filename, task.error or "Unknown error")
            self.status_message.setText(f"Failed: {task.filename}")
    
    # ============ Window Methods ============
    
    def _show_from_tray(self):
        """Show window from tray"""
        self.show()
        self.activateWindow()
        self.raise_()
    
    def _quit_app(self):
        """Quit the application"""
        # Confirm if downloads are active
        active = self.download_manager.get_active_downloads()
        if active and self.config.confirm_on_exit:
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                f"There are {len(active)} active downloads. Are you sure you want to quit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Cleanup and quit
        loop = asyncio.get_event_loop()
        loop.create_task(self._cleanup_and_quit())
    
    async def _cleanup_and_quit(self):
        """Cleanup and quit"""
        self.tray.cleanup()
        await self.download_manager.stop()
        QApplication.quit()
    
    def closeEvent(self, event: QCloseEvent):
        """Handle window close"""
        if self.config.minimize_to_tray:
            event.ignore()
            self.hide()
            # Avoid showing notification on minimize as it can cause crashes on macOS
            # self.tray.show_notification("PyDM Minimized", "PyDM is still running in the background.")
        else:
            # Cleanup synchronously before accepting the event
            self.tray.cleanup()
            event.accept()
            asyncio.create_task(self._cleanup_and_quit())
