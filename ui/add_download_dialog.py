"""
Add Download Dialog - Dialog for adding new downloads

Features URL input with validation, filename detection, and download options.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFileDialog, QCheckBox,
    QSpinBox, QGroupBox, QFormLayout, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

import os
from pathlib import Path

from .styles import Styles


class AddDownloadDialog(QDialog):
    """Dialog for adding a new download"""
    
    # Signal emitted when download is confirmed
    download_requested = pyqtSignal(str, str, str, bool)  # url, save_dir, filename, start_immediately
    
    def __init__(self, parent=None, default_dir: str = None, clipboard_url: str = None):
        super().__init__(parent)
        self.default_dir = default_dir or str(Path.home() / "Downloads")
        self.clipboard_url = clipboard_url
        
        self._setup_ui()
        self._connect_signals()
        
        # Auto-fill URL from clipboard if available
        if clipboard_url:
            self.url_input.setText(clipboard_url)
            self._on_url_changed()
    
    def _setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle("Add New Download")
        self.setMinimumWidth(550)
        self.setModal(True)
        
        # Apply stylesheet
        self.setStyleSheet(Styles.get_main_stylesheet())
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title = QLabel("Add New Download")
        title.setObjectName("titleLabel")
        font = title.font()
        font.setPointSize(20)
        font.setWeight(QFont.Weight.Bold)
        title.setFont(font)
        layout.addWidget(title)
        
        # URL Section
        url_group = QGroupBox("Download URL")
        url_layout = QVBoxLayout(url_group)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste URL here (http:// or https://)")
        self.url_input.setMinimumHeight(44)
        url_layout.addWidget(self.url_input)
        
        # URL status
        self.url_status = QLabel("")
        self.url_status.setObjectName("mutedLabel")
        url_layout.addWidget(self.url_status)
        
        layout.addWidget(url_group)
        
        # Save Location Section
        save_group = QGroupBox("Save Location")
        save_layout = QVBoxLayout(save_group)
        
        # Directory row
        dir_layout = QHBoxLayout()
        
        self.dir_input = QLineEdit()
        self.dir_input.setText(self.default_dir)
        self.dir_input.setMinimumHeight(44)
        dir_layout.addWidget(self.dir_input)
        
        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("secondaryButton")
        browse_btn.clicked.connect(self._browse_directory)
        dir_layout.addWidget(browse_btn)
        
        save_layout.addLayout(dir_layout)
        
        # Filename row
        filename_layout = QFormLayout()
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("Auto-detected from URL")
        self.filename_input.setMinimumHeight(44)
        filename_layout.addRow("Filename:", self.filename_input)
        
        save_layout.addLayout(filename_layout)
        
        layout.addWidget(save_group)
        
        # Options Section
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        
        # Start immediately checkbox
        self.start_immediately_check = QCheckBox("Start download immediately")
        self.start_immediately_check.setChecked(True)
        options_layout.addWidget(self.start_immediately_check)
        
        # Number of chunks
        chunks_layout = QHBoxLayout()
        chunks_label = QLabel("Download chunks:")
        self.chunks_spin = QSpinBox()
        self.chunks_spin.setRange(1, 16)
        self.chunks_spin.setValue(8)
        self.chunks_spin.setToolTip("More chunks = faster download (for large files)")
        chunks_layout.addWidget(chunks_label)
        chunks_layout.addWidget(self.chunks_spin)
        chunks_layout.addStretch()
        options_layout.addLayout(chunks_layout)
        
        layout.addWidget(options_group)
        
        # Spacer
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.setMinimumHeight(44)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        self.download_btn = QPushButton("Download")
        self.download_btn.setMinimumHeight(44)
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self._on_download)
        btn_layout.addWidget(self.download_btn)
        
        layout.addLayout(btn_layout)
    
    def _connect_signals(self):
        """Connect signals"""
        self.url_input.textChanged.connect(self._on_url_changed)
    
    def _on_url_changed(self):
        """Handle URL input change"""
        url = self.url_input.text().strip()
        
        if not url:
            self.url_status.setText("")
            self.download_btn.setEnabled(False)
            return
        
        # Basic URL validation
        if url.startswith(("http://", "https://")):
            self.url_status.setText("Valid URL")
            self.url_status.setStyleSheet(f"color: {Styles.COLORS['success']}; font-size: 12px;")
            self.download_btn.setEnabled(True)
            
            # Try to extract filename from URL
            try:
                from urllib.parse import urlparse, unquote
                parsed = urlparse(url)
                filename = unquote(os.path.basename(parsed.path))
                if filename and not self.filename_input.text():
                    self.filename_input.setPlaceholderText(filename)
            except Exception:
                pass
        else:
            self.url_status.setText("Invalid URL (must start with http:// or https://)")
            self.url_status.setStyleSheet(f"color: {Styles.COLORS['error']}; font-size: 12px;")
            self.download_btn.setEnabled(False)
    
    def _browse_directory(self):
        """Open directory browser"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Download Directory",
            self.dir_input.text()
        )
        
        if directory:
            self.dir_input.setText(directory)
    
    def _on_download(self):
        """Handle download button click"""
        url = self.url_input.text().strip()
        save_dir = self.dir_input.text().strip()
        filename = self.filename_input.text().strip()
        start_immediately = self.start_immediately_check.isChecked()
        
        self.download_requested.emit(url, save_dir, filename, start_immediately)
        self.accept()
    
    def get_values(self) -> tuple:
        """Get dialog values"""
        return (
            self.url_input.text().strip(),
            self.dir_input.text().strip(),
            self.filename_input.text().strip() or None,
            self.start_immediately_check.isChecked(),
            self.chunks_spin.value()
        )
