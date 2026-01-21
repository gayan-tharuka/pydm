"""
Download Item Widget - Custom widget for displaying a download in the list

Features a modern card design with nice vector icons and Apple-style layout.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPainter, QColor

from ..core.download_engine import DownloadTask, DownloadState
from .styles import Styles
from .icon_utils import IconUtils


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
        # Main layout (Horizontal)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(16)
        
        # 1. File Icon (Left)
        # We use a button as an icon container for perfect centering
        self.icon_btn = QPushButton()
        self.icon_btn.setObjectName("iconButton")
        self.icon_btn.setFixedSize(48, 48)
        self.icon_btn.setIconSize(QSize(32, 32)) 
        # Disable interaction
        self.icon_btn.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.layout.addWidget(self.icon_btn)
        
        # 2. Info Section (Middle)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)
        info_layout.setContentsMargins(0, 2, 0, 2)
        
        # Top Row: Filename and Status
        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        
        self.filename_label = QLabel(self.task.filename)
        self.filename_label.setObjectName("titleLabel")
        self.filename_label.setStyleSheet("font-size: 15px; font-weight: 600;")
        top_row.addWidget(self.filename_label)
        
        top_row.addStretch()
        
        # Status Badge (Capsule style)
        self.status_label = QLabel(self.task.state.value)
        self.status_label.setObjectName("mutedLabel")
        self.status_label.setStyleSheet(f"color: {Styles.COLORS['text_secondary']};")
        top_row.addWidget(self.status_label)
        
        info_layout.addLayout(top_row)
        
        # Middle: Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(int(self.task.progress))
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(5)  # Simpler, thinner bar
        info_layout.addWidget(self.progress_bar)
        
        # Bottom Row: Stats
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        
        self.size_label = QLabel(self._format_size(self.task.file_size))
        self.size_label.setObjectName("mutedLabel")
        stats_layout.addWidget(self.size_label)
        
        self.speed_label = QLabel("")
        self.speed_label.setObjectName("mutedLabel")
        stats_layout.addWidget(self.speed_label)
        
        self.eta_label = QLabel("")
        self.eta_label.setObjectName("mutedLabel")
        stats_layout.addWidget(self.eta_label)
        
        stats_layout.addStretch()
        info_layout.addLayout(stats_layout)
        
        # Add info layout to main layout
        self.layout.addLayout(info_layout, stretch=1)
        
        # 3. Actions (Right)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        buttons_layout.setContentsMargins(8, 0, 0, 0)
        
        # Action Buttons using Vector Icons
        self.pause_resume_btn = QPushButton()
        self.pause_resume_btn.setObjectName("iconButton")
        self.pause_resume_btn.setFixedSize(32, 32)
        self.pause_resume_btn.setIconSize(QSize(18, 18))
        self.pause_resume_btn.setToolTip("Pause")
        self.pause_resume_btn.clicked.connect(self._on_pause_resume)
        buttons_layout.addWidget(self.pause_resume_btn)
        
        self.cancel_btn = QPushButton()
        self.cancel_btn.setObjectName("iconButton")
        self.cancel_btn.setFixedSize(32, 32)
        self.cancel_btn.setIconSize(QSize(16, 16))
        self.cancel_btn.setToolTip("Cancel")
        self.cancel_btn.clicked.connect(self._on_cancel)
        buttons_layout.addWidget(self.cancel_btn)
        
        self.open_folder_btn = QPushButton()
        self.open_folder_btn.setObjectName("iconButton")
        self.open_folder_btn.setFixedSize(32, 32)
        self.open_folder_btn.setIconSize(QSize(18, 18))
        self.open_folder_btn.setIcon(IconUtils.icon("folder", Styles.COLORS['primary']))
        self.open_folder_btn.setToolTip("Open Folder")
        self.open_folder_btn.clicked.connect(lambda: self.open_folder_clicked.emit(self.task.id))
        self.open_folder_btn.hide()
        
        self.layout.addLayout(buttons_layout)
    
    def _update_file_icon(self):
        """Update file icon based on file type"""
        filename = self.task.filename.lower()
        
        if any(filename.endswith(ext) for ext in ['.mp4', '.mkv', '.avi', '.mov', '.wmv']):
            self.icon_btn.setIcon(IconUtils.icon("video", "#FF2D55")) # System Pink
        elif any(filename.endswith(ext) for ext in ['.mp3', '.wav', '.flac', '.aac', '.m4a']):
            self.icon_btn.setIcon(IconUtils.icon("audio", "#BF5AF2")) # System Purple
        elif any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']):
            self.icon_btn.setIcon(IconUtils.icon("image", "#FF9F0A")) # System Orange
        elif any(filename.endswith(ext) for ext in ['.zip', '.rar', '.7z', '.tar', '.gz']):
            self.icon_btn.setIcon(IconUtils.icon("archive", "#FFCC00")) # System Yellow
        else:
            self.icon_btn.setIcon(IconUtils.icon("file", "#0A84FF")) # System Blue
            
    def update_display(self):
        """Update the display based on current task state"""
        # Update filename
        self.filename_label.setText(self.task.filename or "Unknown")
        
        # Update icon
        self._update_file_icon()
        
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
            DownloadState.DOWNLOADING: f"Downloading {progress}%",
            DownloadState.PAUSED: "Paused",
            DownloadState.MERGING: "Merging...",
            DownloadState.COMPLETED: "Completed",
            DownloadState.FAILED: "Failed",
            DownloadState.CANCELLED: "Cancelled",
        }
        self.status_label.setText(state_labels.get(state, "Unknown"))
        self.status_label.setStyleSheet(
            f"color: {Styles.get_status_color(state.value)}; font-size: 12px;"
        )
        
        # Update speed and ETA
        if state == DownloadState.DOWNLOADING:
            self.speed_label.setText(self.task.formatted_speed)
            self.eta_label.setText(self.task.formatted_eta)
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
            self.pause_resume_btn.setIcon(IconUtils.icon("pause", Styles.COLORS['text_primary']))
            self.pause_resume_btn.setToolTip("Pause")
            self.pause_resume_btn.show()
            
            self.cancel_btn.setIcon(IconUtils.icon("stop", Styles.COLORS['error']))
            self.cancel_btn.setToolTip("Cancel")
            self.cancel_btn.show()
            
            self.open_folder_btn.hide()
            
        elif state == DownloadState.PAUSED:
            self.pause_resume_btn.setIcon(IconUtils.icon("resume", Styles.COLORS['success']))
            self.pause_resume_btn.setToolTip("Resume")
            self.pause_resume_btn.show()
            
            self.cancel_btn.setIcon(IconUtils.icon("stop", Styles.COLORS['error']))
            self.cancel_btn.setToolTip("Cancel")
            self.cancel_btn.show()
            
            self.open_folder_btn.hide()
            
        elif state == DownloadState.COMPLETED:
            self.pause_resume_btn.hide()
            
            self.cancel_btn.setIcon(IconUtils.icon("remove", Styles.COLORS['text_muted']))
            self.cancel_btn.setToolTip("Remove from list")
            self.cancel_btn.show()
            
            self.open_folder_btn.show()
            
        else:  # FAILED, CANCELLED
            self.pause_resume_btn.hide()
            
            self.cancel_btn.setIcon(IconUtils.icon("remove", Styles.COLORS['text_muted']))
            self.cancel_btn.setToolTip("Remove from list")
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
        
    def _format_size(self, size_bytes):
        """Format size in bytes to human readable string"""
        if size_bytes == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        i = 0
        while size_bytes >= 1024 and i < len(units) - 1:
            size_bytes /= 1024
            i += 1
            
        return f"{size_bytes:.1f} {units[i]}"

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
