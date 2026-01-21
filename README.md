# PyDM - Python Download Manager

<div align="center">

![PyDM Logo](https://img.shields.io/badge/PyDM-Download%20Manager-4A90D9?style=for-the-badge&logo=python&logoColor=white)

**A high-speed, open-source download manager for macOS**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-41CD52?style=flat-square&logo=qt&logoColor=white)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

</div>

---

## ✨ Features

- **🚀 Full-Speed Downloads** - Multi-threaded chunked downloads (8-16 parallel connections) for maximum speed
- **⏸️ Pause & Resume** - Stop and continue downloads anytime without losing progress
- **🎨 Modern Dark UI** - Sleek, professional interface with glassmorphism effects
- **📊 Real-time Stats** - Live speed, ETA, and progress tracking
- **🔔 System Tray** - Runs in background with notifications
- **💾 Auto-Resume** - Automatically resume interrupted downloads
- **📁 Smart Organization** - Automatic file type detection and icons

## 📸 Screenshots

*Coming soon*

## 🚀 Quick Start

### Prerequisites

- macOS 10.15 or later
- Python 3.10 or later

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/pydm.git
   cd pydm
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run PyDM**
   ```bash
   python main.py
   ```

## 🎯 Usage

### Adding a Download

1. Click the **"Add Download"** button or press `Cmd+N`
2. Paste the URL of the file you want to download
3. Choose the save location (defaults to Downloads folder)
4. Click **"Download"** to start

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd+N` | Add new download |
| `Cmd+Q` | Quit application |

### System Tray

PyDM runs in the system tray, allowing you to:
- Monitor active downloads
- Quickly add new downloads
- Pause/Resume all downloads
- Access the main window

## 🔧 Configuration

Configuration is stored in `~/.pydm/config.json`:

```json
{
  "default_download_dir": "~/Downloads",
  "max_concurrent_downloads": 3,
  "default_chunks": 8,
  "theme": "dark",
  "minimize_to_tray": true,
  "show_notifications": true
}
```

## 🏗️ Architecture

```
pydm/
├── core/
│   ├── download_engine.py   # Async download orchestration
│   ├── chunk_manager.py     # Parallel chunk downloads
│   └── download_manager.py  # Queue & state management
├── data/
│   ├── database.py          # SQLite persistence
│   └── config.py            # Configuration management
├── ui/
│   ├── main_window.py       # Main application window
│   ├── add_download_dialog.py
│   ├── download_item_widget.py
│   ├── system_tray.py
│   └── styles.py            # Modern dark theme
└── main.py                  # Application entry point
```

## 🛠️ Development

### Running Tests

```bash
python -m pytest tests/ -v
```

### Code Style

This project follows PEP 8 style guidelines.

```bash
# Format code
black pydm/

# Check types
mypy pydm/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by Internet Download Manager (IDM)
- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- Uses [aiohttp](https://docs.aiohttp.org/) for async HTTP

---

<div align="center">
Made with ❤️ for the open-source community
</div>
