"""
Styles - Modern dark theme stylesheet for PyDM

A sleek, professional dark theme with glassmorphism effects
and smooth animations for a premium feel.
"""



class Styles:
    """Modern dark theme styles for PyDM (Apple Design)"""
    
    # Color Palette (macOS System Colors - Dark Mode)
    COLORS = {
        # Primary colors
        "primary": "#0A84FF",           # System Blue
        "primary_hover": "#409CFF",     # System Blue Light
        "primary_pressed": "#0071F0",   # System Blue Dark
        
        # Background colors
        "bg_dark": "#1C1C1E",           # System Background
        "bg_medium": "#2C2C2E",         # Secondary System Background
        "bg_light": "#3A3A3C",          # Tertiary System Background
        "bg_card": "#2C2C2E",           # Card background
        "bg_hover": "#3A3A3C",          # Hover state
        
        # Text colors
        "text_primary": "#FFFFFF",      # Label Color
        "text_secondary": "#8E8E93",    # Secondary Label Color (System Gray)
        "text_muted": "#636366",        # Tertiary Label Color
        
        # Status colors
        "success": "#30D158",           # System Green
        "warning": "#FF9F0A",           # System Orange
        "error": "#FF453A",             # System Red
        "info": "#0A84FF",              # System Blue
        
        # Border colors
        "border": "#38383A",            # Separator Color
        "border_focus": "#0A84FF",      # Focus Ring
        
        # Progress bar
        "progress_bg": "#3A3A3C",       # Track
        "progress_fill": "#0A84FF",     # Fill
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
                color: {c['text_primary']};
                selection-background-color: {c['primary']};
                selection-color: #FFFFFF;
                outline: none;
            }}
            
            /* Scroll Bars (macOS style invisible track) */
            QScrollBar:vertical {{
                background: transparent;
                width: 12px;
                margin: 0;
            }}
            
            QScrollBar::handle:vertical {{
                background: {c['bg_light']};
                min-height: 40px;
                border-radius: 6px;
                margin: 2px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {c['text_muted']};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            
            QScrollBar:horizontal {{
                background: transparent;
                height: 12px;
            }}
            
            QScrollBar::handle:horizontal {{
                background: {c['bg_light']};
                min-width: 40px;
                border-radius: 6px;
                margin: 2px;
            }}
            
            /* Buttons (Apple Style) */
            QPushButton {{
                background-color: {c['bg_light']};
                color: {c['text_primary']};
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
                font-weight: 500;
            }}
            
            QPushButton:hover {{
                background-color: {c['bg_hover']};
            }}
            
            QPushButton:pressed {{
                background-color: {c['border']};
            }}
            
            QPushButton:disabled {{
                background-color: {c['bg_dark']};
                color: {c['text_muted']};
                border: 1px solid {c['border']};
            }}
            
            /* Primary Button (Blue) */
            QPushButton#primaryButton {{
                background-color: {c['primary']};
                color: #FFFFFF;
            }}
            
            QPushButton#primaryButton:hover {{
                background-color: {c['primary_hover']};
            }}
            
            QPushButton#primaryButton:pressed {{
                background-color: {c['primary_pressed']};
            }}
            
            /* Icon Buttons (Toolbar/List) */
            QPushButton#iconButton {{
                background-color: transparent;
                border-radius: 6px;
                padding: 4px;
                min-width: 28px;
                min-height: 28px;
            }}
            
            QPushButton#iconButton:hover {{
                background-color: {c['bg_light']};
            }}
            
            /* Line Edits (Modern Input) */
            QLineEdit {{
                background-color: {c['bg_medium']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 8px 10px;
                color: {c['text_primary']};
                font-size: 13px;
            }}
            
            QLineEdit:focus {{
                border: 1px solid {c['primary']};
                background-color: {c['bg_dark']};
            }}
            
            QLineEdit::placeholder {{
                color: {c['text_muted']};
            }}
            
            /* Labels */
            QLabel {{
                color: {c['text_primary']};
            }}
            
            QLabel#titleLabel {{
                font-size: 22px;
                font-weight: 700;
                color: {c['text_primary']};
            }}
            
            QLabel#subtitleLabel {{
                font-size: 13px;
                color: {c['text_secondary']};
            }}
            
            QLabel#mutedLabel {{
                color: {c['text_muted']};
                font-size: 11px;
            }}
            
            /* Progress Bar (Slim) */
            QProgressBar {{
                background-color: {c['progress_bg']};
                border: none;
                border-radius: 2px;
                height: 4px;
                text-align: center;
            }}
            
            QProgressBar::chunk {{
                background-color: {c['primary']};
                border-radius: 2px;
            }}
            
            /* List Widget */
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: none;
            }}
            
            QListWidget::item {{
                background-color: transparent;
                border-radius: 8px;
                margin: 4px 8px;
                padding: 0;
            }}
            
            /* Group Box */
            QGroupBox {{
                background-color: transparent;
                border: 1px solid {c['border']};
                border-radius: 8px;
                margin-top: 20px;
                padding: 16px;
                font-weight: 600;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 4px;
                color: {c['text_secondary']};
            }}
            
            /* Combo/Spin Box */
            QComboBox, QSpinBox {{
                background-color: {c['bg_medium']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 6px 10px;
                color: {c['text_primary']};
            }}
            
            QComboBox:hover, QSpinBox:hover {{
                border-color: {c['text_secondary']};
            }}

            /* Menu */
            QMenu {{
                background-color: {c['bg_medium']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 4px;
            }}
            
            QMenu::item {{
                padding: 6px 20px;
                border-radius: 4px;
            }}
            
            QMenu::item:selected {{
                background-color: {c['primary']};
                color: #FFFFFF;
            }}
            
            /* Tool Tip */
            QToolTip {{
                background-color: {c['bg_medium']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }}
            
            /* ToolBar */
            QToolBar {{
                background: {c['bg_dark']};
                border-bottom: 1px solid {c['border']};
                spacing: 12px;
                padding: 8px;
            }}
            
            QToolButton {{
                background-color: transparent;
                border-radius: 6px;
                padding: 6px;
                color: {c['text_primary']};
            }}
            
            QToolButton:hover {{
                background-color: {c['bg_medium']};
            }}
        """
    
    @classmethod
    def get_download_item_style(cls, state: str = "normal") -> str:
        """Get style for download item widget based on state"""
        c = cls.COLORS
        
        # Consistent Card Look
        base_style = f"""
            background-color: {c['bg_card']};
            border-radius: 10px;
            padding: 12px;
        """
        
        # Subtle border hint instead of heavy side border
        if state == "downloading":
            return base_style + f"border: 1px solid {c['border_focus']};"
        elif state == "completed":
            return base_style + f"border: 1px solid {c['border']}; opacity: 0.8;"
        else:
            return base_style + f"border: 1px solid {c['border']};"
    
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
