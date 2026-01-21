"""
Download Item Widget - Custom widget for displaying a download in the list

Features a modern card design with progress bar, speed display, and action buttons.
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
    QProgressBar, QPushButton, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon

from ..core.download_engine import DownloadTask, DownloadState
from .styles import Styles


class DownloadItemWidget(QWidget):
    """Widget displaying a single download item"""
    
    # Signals
    pause_clicked = pyqtSignal(str)  # download_id
    resume_clicked = pyqtSignal(str)  # download_id
    cancel_clicked = pyqtSignal(str)  # download_id
    remove_clicked = pyqtSignal(str)  # download_id
    open_file_clicked = pyqtSignal(str)  # download_id
    open_folder_clicked = pyqtSignal(str)  # download_id
    
    def __init__(self, task: DownloadTask, parent=None):
        super().__init__(parent)
        self.task = task
        self._setup_ui()
        self.update_display()
    
    def _setup_ui(self):
        """Setup the widget UI"""
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)
        
        # File icon placeholder (left side)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(48, 48)
        self.icon_label.setStyleSheet(f"""
            background-color: {Styles.COLORS['bg_hover']};
            border-radius: 10px;
            font-size: 20px;
        """)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setText(self._get_file_icon())
        layout.addWidget(self.icon_label)
        
        # Info section (middle)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)
        
        # Filename
        self.filename_label = QLabel(self.task.filename)
        self.filename_label.setFont(QFont("SF Pro Text", 14, QFont.Weight.DemiBold))
        self.filename_label.setStyleSheet(f"color: {Styles.COLORS['text_primary']};")
        info_layout.addWidget(self.filename_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        info_layout.addWidget(self.progress_bar)
        
        # Status row
        status_layout = QHBoxLayout()
        status_layout.setSpacing(16)
        
        # Status label
        self.status_label = QLabel("Queued")
        self.status_label.setStyleSheet(f"color: {Styles.COLORS['text_secondary']}; font-size: 12px;")
        status_layout.addWidget(self.status_label)
        
        # Size info
        self.size_label = QLabel("0 B / 0 B")
        self.size_label.setStyleSheet(f"color: {Styles.COLORS['text_muted']}; font-size: 12px;")
        status_layout.addWidget(self.size_label)
        
        # Speed
        self.speed_label = QLabel("")
        self.speed_label.setStyleSheet(f"color: {Styles.COLORS['primary']}; font-size: 12px; font-weight: 600;")
        status_layout.addWidget(self.speed_label)
        
        # ETA
        self.eta_label = QLabel("")
        self.eta_label.setStyleSheet(f"color: {Styles.COLORS['text_muted']}; font-size: 12px;")
        status_layout.addWidget(self.eta_label)
        
        status_layout.addStretch()
        info_layout.addLayout(status_layout)
        
        layout.addLayout(info_layout, 1)
        
        # Action buttons (right side)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        
        # Pause/Resume button
        self.pause_resume_btn = QPushButton()
        self.pause_resume_btn.setObjectName("iconButton")
        self.pause_resume_btn.setFixedSize(36, 36)
        self.pause_resume_btn.setText("⏸")
        self.pause_resume_btn.setToolTip("Pause")
        self.pause_resume_btn.clicked.connect(self._on_pause_resume)
        buttons_layout.addWidget(self.pause_resume_btn)
        
        # Cancel/Remove button
        self.cancel_btn = QPushButton()
        self.cancel_btn.setObjectName("iconButton")
        self.cancel_btn.setFixedSize(36, 36)
        self.cancel_btn.setText("✕")
        self.cancel_btn.setToolTip("Cancel")
        self.cancel_btn.clicked.connect(self._on_cancel)
        buttons_layout.addWidget(self.cancel_btn)
        
        # Open folder button (shown when completed)
        self.open_folder_btn = QPushButton()
        self.open_folder_btn.setObjectName("iconButton")
        self.open_folder_btn.setFixedSize(36, 36)
        self.open_folder_btn.setText("📂")
        self.open_folder_btn.setToolTip("Open Folder")
        self.open_folder_btn.clicked.connect(lambda: self.open_folder_clicked.emit(self.task.id))
        self.open_folder_btn.hide()
        buttons_layout.addWidget(self.open_folder_btn)
        
        layout.addLayout(buttons_layout)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(90)
    
    def _get_file_icon(self) -> str:
        """Get emoji icon based on file type"""
        filename = self.task.filename.lower()
        
        if any(filename.endswith(ext) for ext in ['.mp4', '.mkv', '.avi', '.mov', '.wmv']):
            return "🎬"
        elif any(filename.endswith(ext) for ext in ['.mp3', '.wav', '.flac', '.aac', '.m4a']):
            return "🎵"
        elif any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']):
            return "🖼"
        elif any(filename.endswith(ext) for ext in ['.pdf']):
            return "📄"
        elif any(filename.endswith(ext) for ext in ['.zip', '.rar', '.7z', '.tar', '.gz']):
            return "📦"
        elif any(filename.endswith(ext) for ext in ['.exe', '.dmg', '.app', '.pkg']):
            return "💿"
        elif any(filename.endswith(ext) for ext in ['.doc', '.docx', '.txt', '.rtf']):
            return "📝"
        else:
            return "📁"
    
    def update_display(self):
        """Update the display based on current task state"""
        # Update filename
        self.filename_label.setText(self.task.filename or "Unknown")
        
        # Update icon
        self.icon_label.setText(self._get_file_icon())
        
        # Update progress
        progress = int(self.task.progress)
        self.progress_bar.setValue(progress)
        
        # Update size info
        self.size_label.setText(
            f"{self.task.formatted_downloaded} / {self.task.formatted_size}"
        )
        
        # Update status
        state = self.task.state
        state_labels = {
            DownloadState.QUEUED: "Queued",
            DownloadState.FETCHING_INFO: "Getting info...",
            DownloadState.DOWNLOADING: f"Downloading ({progress}%)",
            DownloadState.PAUSED: "Paused",
            DownloadState.MERGING: "Merging chunks...",
            DownloadState.COMPLETED: "Completed",
            DownloadState.FAILED: f"Failed: {self.task.error or 'Unknown error'}",
            DownloadState.CANCELLED: "Cancelled",
        }
        self.status_label.setText(state_labels.get(state, "Unknown"))
        self.status_label.setStyleSheet(
            f"color: {Styles.get_status_color(state.value)}; font-size: 12px;"
        )
        
        # Update speed and ETA
        if state == DownloadState.DOWNLOADING:
            self.speed_label.setText(self.task.formatted_speed)
            self.eta_label.setText(f"ETA: {self.task.formatted_eta}")
            self.speed_label.show()
            self.eta_label.show()
        else:
            self.speed_label.hide()
            self.eta_label.hide()
        
        # Update buttons based on state
        self._update_buttons()
        
        # Update widget style based on state
        self._update_style()
    
    def _update_buttons(self):
        """Update button visibility and state"""
        state = self.task.state
        
        if state in (DownloadState.DOWNLOADING, DownloadState.FETCHING_INFO):
            self.pause_resume_btn.setText("⏸")
            self.pause_resume_btn.setToolTip("Pause")
            self.pause_resume_btn.show()
            self.cancel_btn.show()
            self.open_folder_btn.hide()
        elif state == DownloadState.PAUSED:
            self.pause_resume_btn.setText("▶")
            self.pause_resume_btn.setToolTip("Resume")
            self.pause_resume_btn.show()
            self.cancel_btn.show()
            self.open_folder_btn.hide()
        elif state == DownloadState.QUEUED:
            self.pause_resume_btn.hide()
            self.cancel_btn.show()
            self.open_folder_btn.hide()
        elif state == DownloadState.COMPLETED:
            self.pause_resume_btn.hide()
            self.cancel_btn.setText("🗑")
            self.cancel_btn.setToolTip("Remove")
            self.cancel_btn.show()
            self.open_folder_btn.show()
        else:  # FAILED, CANCELLED
            self.pause_resume_btn.hide()
            self.cancel_btn.setText("🗑")
            self.cancel_btn.setToolTip("Remove")
            self.cancel_btn.show()
            self.open_folder_btn.hide()
    
    def _update_style(self):
        """Update widget style based on state"""
        state_map = {
            DownloadState.DOWNLOADING: "downloading",
            DownloadState.COMPLETED: "completed",
            DownloadState.PAUSED: "paused",
            DownloadState.FAILED: "failed",
            DownloadState.CANCELLED: "failed",
        }
        style_state = state_map.get(self.task.state, "normal")
        self.setStyleSheet(Styles.get_download_item_style(style_state))
    
    def _on_pause_resume(self):
        """Handle pause/resume button click"""
        if self.task.state == DownloadState.PAUSED:
            self.resume_clicked.emit(self.task.id)
        else:
            self.pause_clicked.emit(self.task.id)
    
    def _on_cancel(self):
        """Handle cancel/remove button click"""
        if self.task.state in (DownloadState.COMPLETED, DownloadState.FAILED, DownloadState.CANCELLED):
            self.remove_clicked.emit(self.task.id)
        else:
            self.cancel_clicked.emit(self.task.id)
