"""
System Tray - macOS system tray integration

Provides quick access to PyDM from the menu bar with status and controls.
"""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import pyqtSignal, QObject

from .styles import Styles


class SystemTrayIcon(QSystemTrayIcon):
    """System tray icon for PyDM"""
    
    # Signals
    show_window_requested = pyqtSignal()
    add_download_requested = pyqtSignal()
    pause_all_requested = pyqtSignal()
    resume_all_requested = pyqtSignal()
    quit_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._setup_icon()
        self._setup_menu()
        self._connect_signals()
        
        # State tracking
        self._active_count = 0
        self._download_speed = ""
    
    def _setup_icon(self):
        """Setup tray icon"""
        # Create a simple icon programmatically
        icon = self._create_icon()
        self.setIcon(icon)
        self.setToolTip("PyDM - Download Manager")
    
    def _create_icon(self, active: bool = False) -> QIcon:
        """Create tray icon programmatically"""
        size = 22  # macOS tray icon size
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw simple download arrow icon using lines
        color = QColor(Styles.COLORS['primary'] if active else "#FFFFFF")
        from PyQt6.QtGui import QPen
        pen = QPen(color)
        pen.setWidth(2)
        painter.setPen(pen)
        
        # Vertical line
        painter.drawLine(11, 4, 11, 14)
        
        # Arrow head
        painter.drawLine(7, 10, 11, 14)
        painter.drawLine(15, 10, 11, 14)
        
        # Base line
        painter.drawLine(4, 18, 18, 18)
        
        painter.end()
        
        return QIcon(pixmap)
    
    def _setup_menu(self):
        """Setup context menu"""
        menu = QMenu()
        
        # Show/Hide window
        self.show_action = menu.addAction("Show PyDM")
        self.show_action.triggered.connect(self.show_window_requested.emit)
        
        menu.addSeparator()
        
        # Add download
        add_action = menu.addAction("Add Download...")
        add_action.triggered.connect(self.add_download_requested.emit)
        
        menu.addSeparator()
        
        # Pause/Resume all
        self.pause_action = menu.addAction("Pause All")
        self.pause_action.triggered.connect(self.pause_all_requested.emit)
        
        self.resume_action = menu.addAction("Resume All")
        self.resume_action.triggered.connect(self.resume_all_requested.emit)
        
        menu.addSeparator()
        
        # Status section
        self.status_action = menu.addAction("No active downloads")
        self.status_action.setEnabled(False)
        
        menu.addSeparator()
        
        # Quit
        quit_action = menu.addAction("Quit PyDM")
        quit_action.triggered.connect(self.quit_requested.emit)
        
        self.setContextMenu(menu)
    
    def _connect_signals(self):
        """Connect signals"""
        self.activated.connect(self._on_activated)
    
    def _on_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Single click - show window
            self.show_window_requested.emit()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Double click - show window
            self.show_window_requested.emit()
    
    def update_status(self, active_count: int, total_speed: str = ""):
        """Update tray status"""
        self._active_count = active_count
        self._download_speed = total_speed
        
        # Update icon
        icon = self._create_icon(active=active_count > 0)
        self.setIcon(icon)
        
        # Update tooltip
        if active_count > 0:
            self.setToolTip(f"PyDM - {active_count} active download(s)\n{total_speed}")
        else:
            self.setToolTip("PyDM - Download Manager")
        
        # Update status action
        if active_count > 0:
            self.status_action.setText(f"{active_count} active download(s) - {total_speed}")
        else:
            self.status_action.setText("No active downloads")
    
    def show_notification(self, title: str, message: str, icon_type=None):
        """Show a system notification"""
        # On macOS, using MessageIcon.Information/Warning etc can cause SIGBUS in ImageIO
        # when Qt tries to create a notification image. Safer to use NoIcon.
        if icon_type is None:
            icon_type = QSystemTrayIcon.MessageIcon.NoIcon
        
        if self.isVisible():
            self.showMessage(title, message, icon_type, 3000)

    def cleanup(self):
        """Cleanup system tray resources"""
        self.hide()
        self.setParent(None)
    
    def show_download_complete(self, filename: str):
        """Show download complete notification"""
        self.show_notification(
            "Download Complete",
            f"{filename} has finished downloading.",
            QSystemTrayIcon.MessageIcon.Information
        )
    
    def show_download_failed(self, filename: str, error: str):
        """Show download failed notification"""
        self.show_notification(
            "Download Failed",
            f"{filename}: {error}",
            QSystemTrayIcon.MessageIcon.Warning
        )
