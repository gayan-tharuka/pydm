"""
Configuration Manager - Application settings and preferences
"""

import os
import json
from dataclasses import dataclass, field, asdict
from typing import Optional
from pathlib import Path


@dataclass
class Config:
    """Application configuration"""
    
    # Download settings
    default_download_dir: str = field(default_factory=lambda: str(Path.home() / "Downloads"))
    temp_dir: str = field(default_factory=lambda: "/tmp/pydm")
    max_concurrent_downloads: int = 3
    default_chunks: int = 8
    max_chunks: int = 16
    
    # Speed settings
    speed_limit_enabled: bool = False
    speed_limit_kbps: int = 0  # 0 = unlimited
    
    # UI settings
    theme: str = "dark"  # "dark" or "light"
    minimize_to_tray: bool = True
    show_notifications: bool = True
    start_minimized: bool = False
    
    # Behavior settings
    auto_start_downloads: bool = True
    clipboard_monitoring: bool = True
    confirm_on_exit: bool = True
    
    # File paths
    _config_dir: str = field(default_factory=lambda: str(Path.home() / ".pydm"))
    _config_file: str = ""
    
    def __post_init__(self):
        self._config_file = os.path.join(self._config_dir, "config.json")
        
        # Create config directory if needed
        os.makedirs(self._config_dir, exist_ok=True)
        
        # Create download directory if needed
        os.makedirs(self.default_download_dir, exist_ok=True)
        
        # Create temp directory if needed
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def save(self):
        """Save configuration to file"""
        data = {
            "default_download_dir": self.default_download_dir,
            "temp_dir": self.temp_dir,
            "max_concurrent_downloads": self.max_concurrent_downloads,
            "default_chunks": self.default_chunks,
            "max_chunks": self.max_chunks,
            "speed_limit_enabled": self.speed_limit_enabled,
            "speed_limit_kbps": self.speed_limit_kbps,
            "theme": self.theme,
            "minimize_to_tray": self.minimize_to_tray,
            "show_notifications": self.show_notifications,
            "start_minimized": self.start_minimized,
            "auto_start_downloads": self.auto_start_downloads,
            "clipboard_monitoring": self.clipboard_monitoring,
            "confirm_on_exit": self.confirm_on_exit,
        }
        
        with open(self._config_file, "w") as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load(cls) -> "Config":
        """Load configuration from file"""
        config = cls()
        
        if os.path.exists(config._config_file):
            try:
                with open(config._config_file, "r") as f:
                    data = json.load(f)
                
                # Apply loaded values
                for key, value in data.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
                        
            except Exception as e:
                print(f"Error loading config: {e}")
        
        return config
    
    @property
    def database_path(self) -> str:
        """Path to the SQLite database"""
        return os.path.join(self._config_dir, "pydm.db")
