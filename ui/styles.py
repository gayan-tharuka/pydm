"""
Styles - Modern dark theme stylesheet for PyDM

A sleek, professional dark theme with glassmorphism effects
and smooth animations for a premium feel.
"""


class Styles:
    """Modern dark theme styles for PyDM"""
    
    # Color Palette
    COLORS = {
        # Primary colors
        "primary": "#4A90D9",           # Main accent blue
        "primary_hover": "#5BA0E9",     # Hover state
        "primary_pressed": "#3A80C9",   # Pressed state
        
        # Background colors
        "bg_dark": "#1A1A2E",           # Darkest background
        "bg_medium": "#16213E",         # Medium background
        "bg_light": "#1F2B4A",          # Lighter background
        "bg_card": "#232D4D",           # Card background
        "bg_hover": "#2A3656",          # Hover background
        
        # Text colors
        "text_primary": "#FFFFFF",      # Primary text
        "text_secondary": "#A0A8C0",    # Secondary text
        "text_muted": "#6B7280",        # Muted text
        
        # Status colors
        "success": "#10B981",           # Success green
        "warning": "#F59E0B",           # Warning amber
        "error": "#EF4444",             # Error red
        "info": "#3B82F6",              # Info blue
        
        # Border colors
        "border": "#2D3A5C",            # Default border
        "border_focus": "#4A90D9",      # Focus border
        
        # Progress bar
        "progress_bg": "#2D3A5C",       # Progress background
        "progress_fill": "#4A90D9",     # Progress fill
    }
    
    @classmethod
    def get_main_stylesheet(cls) -> str:
        """Get the main application stylesheet"""
        c = cls.COLORS
        
        return f"""
            /* Global Styles */
            QMainWindow, QDialog {{
                background-color: {c['bg_dark']};
                color: {c['text_primary']};
            }}
            
            QWidget {{
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', Roboto, sans-serif;
                font-size: 13px;
                color: {c['text_primary']};
            }}
            
            /* Scroll Bars */
            QScrollBar:vertical {{
                background: {c['bg_medium']};
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }}
            
            QScrollBar::handle:vertical {{
                background: {c['bg_hover']};
                min-height: 30px;
                border-radius: 6px;
                margin: 2px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {c['primary']};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            
            QScrollBar:horizontal {{
                background: {c['bg_medium']};
                height: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:horizontal {{
                background: {c['bg_hover']};
                min-width: 30px;
                border-radius: 6px;
                margin: 2px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background: {c['primary']};
            }}
            
            /* Buttons */
            QPushButton {{
                background-color: {c['primary']};
                color: {c['text_primary']};
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }}
            
            QPushButton:hover {{
                background-color: {c['primary_hover']};
            }}
            
            QPushButton:pressed {{
                background-color: {c['primary_pressed']};
            }}
            
            QPushButton:disabled {{
                background-color: {c['bg_hover']};
                color: {c['text_muted']};
            }}
            
            QPushButton#secondaryButton {{
                background-color: {c['bg_light']};
                border: 1px solid {c['border']};
            }}
            
            QPushButton#secondaryButton:hover {{
                background-color: {c['bg_hover']};
                border-color: {c['primary']};
            }}
            
            QPushButton#dangerButton {{
                background-color: {c['error']};
            }}
            
            QPushButton#dangerButton:hover {{
                background-color: #DC2626;
            }}
            
            /* Icon Buttons (Toolbar) */
            QPushButton#iconButton {{
                background-color: transparent;
                border-radius: 8px;
                padding: 8px;
                min-width: 40px;
                min-height: 40px;
            }}
            
            QPushButton#iconButton:hover {{
                background-color: {c['bg_hover']};
            }}
            
            /* Line Edits */
            QLineEdit {{
                background-color: {c['bg_light']};
                border: 2px solid {c['border']};
                border-radius: 8px;
                padding: 12px 16px;
                color: {c['text_primary']};
                font-size: 14px;
                selection-background-color: {c['primary']};
            }}
            
            QLineEdit:focus {{
                border-color: {c['primary']};
            }}
            
            QLineEdit:disabled {{
                background-color: {c['bg_medium']};
                color: {c['text_muted']};
            }}
            
            QLineEdit::placeholder {{
                color: {c['text_muted']};
            }}
            
            /* Labels */
            QLabel {{
                color: {c['text_primary']};
            }}
            
            QLabel#titleLabel {{
                font-size: 24px;
                font-weight: 700;
                color: {c['text_primary']};
            }}
            
            QLabel#subtitleLabel {{
                font-size: 14px;
                color: {c['text_secondary']};
            }}
            
            QLabel#mutedLabel {{
                color: {c['text_muted']};
                font-size: 12px;
            }}
            
            /* Progress Bar */
            QProgressBar {{
                background-color: {c['progress_bg']};
                border: none;
                border-radius: 6px;
                height: 12px;
                text-align: center;
                font-size: 10px;
                color: {c['text_primary']};
            }}
            
            QProgressBar::chunk {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {c['primary']},
                    stop:1 {c['primary_hover']}
                );
                border-radius: 6px;
            }}
            
            /* List Widget */
            QListWidget {{
                background-color: {c['bg_medium']};
                border: none;
                border-radius: 12px;
                padding: 8px;
                outline: none;
            }}
            
            QListWidget::item {{
                background-color: {c['bg_card']};
                border-radius: 10px;
                margin: 4px 0;
                padding: 0;
            }}
            
            QListWidget::item:selected {{
                background-color: {c['bg_hover']};
                border: 1px solid {c['primary']};
            }}
            
            QListWidget::item:hover {{
                background-color: {c['bg_hover']};
            }}
            
            /* Group Box */
            QGroupBox {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 12px;
                margin-top: 16px;
                padding: 20px;
                font-weight: 600;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 16px;
                padding: 0 8px;
                color: {c['text_secondary']};
            }}
            
            /* Combo Box */
            QComboBox {{
                background-color: {c['bg_light']};
                border: 2px solid {c['border']};
                border-radius: 8px;
                padding: 10px 16px;
                color: {c['text_primary']};
                min-width: 120px;
            }}
            
            QComboBox:hover {{
                border-color: {c['primary']};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {c['text_secondary']};
                margin-right: 10px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                selection-background-color: {c['primary']};
                outline: none;
            }}
            
            /* Spin Box */
            QSpinBox {{
                background-color: {c['bg_light']};
                border: 2px solid {c['border']};
                border-radius: 8px;
                padding: 10px 16px;
                color: {c['text_primary']};
            }}
            
            QSpinBox:focus {{
                border-color: {c['primary']};
            }}
            
            /* Check Box */
            QCheckBox {{
                spacing: 10px;
                color: {c['text_primary']};
            }}
            
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid {c['border']};
                background-color: {c['bg_light']};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {c['primary']};
                border-color: {c['primary']};
            }}
            
            QCheckBox::indicator:hover {{
                border-color: {c['primary']};
            }}
            
            /* Tab Widget */
            QTabWidget::pane {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 12px;
                padding: 16px;
            }}
            
            QTabBar::tab {{
                background-color: {c['bg_medium']};
                color: {c['text_secondary']};
                border: none;
                padding: 12px 24px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {c['bg_card']};
                color: {c['text_primary']};
            }}
            
            QTabBar::tab:hover {{
                background-color: {c['bg_hover']};
            }}
            
            /* Menu */
            QMenu {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                padding: 8px;
            }}
            
            QMenu::item {{
                padding: 10px 24px;
                border-radius: 6px;
            }}
            
            QMenu::item:selected {{
                background-color: {c['primary']};
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: {c['border']};
                margin: 8px 16px;
            }}
            
            /* Tool Tip */
            QToolTip {{
                background-color: {c['bg_card']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 8px 12px;
            }}
            
            /* Splitter */
            QSplitter::handle {{
                background-color: {c['border']};
            }}
            
            QSplitter::handle:horizontal {{
                width: 2px;
            }}
            
            QSplitter::handle:vertical {{
                height: 2px;
            }}
        """
    
    @classmethod
    def get_download_item_style(cls, state: str = "normal") -> str:
        """Get style for download item widget based on state"""
        c = cls.COLORS
        
        base_style = f"""
            background-color: {c['bg_card']};
            border-radius: 12px;
            padding: 16px;
        """
        
        if state == "downloading":
            return base_style + f"border-left: 4px solid {c['primary']};"
        elif state == "completed":
            return base_style + f"border-left: 4px solid {c['success']};"
        elif state == "paused":
            return base_style + f"border-left: 4px solid {c['warning']};"
        elif state == "failed":
            return base_style + f"border-left: 4px solid {c['error']};"
        else:
            return base_style
    
    @classmethod
    def get_status_color(cls, state: str) -> str:
        """Get color for status indicator"""
        c = cls.COLORS
        
        status_colors = {
            "queued": c['text_muted'],
            "fetching_info": c['info'],
            "downloading": c['primary'],
            "paused": c['warning'],
            "merging": c['info'],
            "completed": c['success'],
            "failed": c['error'],
            "cancelled": c['text_muted'],
        }
        
        return status_colors.get(state, c['text_secondary'])
