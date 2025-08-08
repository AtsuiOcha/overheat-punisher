# 🎮 Overheat Punisher

> Hispanic parenting simulator when I do stupid plays in Valorant

A real-time computer vision tool that analyzes Valorant gameplay footage to detect game events, track player statistics, and identify agent compositions. Built with OpenCV, EasyOCR, and Python.

## ✨ Features

- **📸 Real-time Screen Capture**: Captures gameplay frames from your primary monitor
- **💀 Kill Feed Detection**: Extracts kill events and player deaths using OCR
- **👥 Agent Detection**: Identifies all 10 agents in the match using template matching
- **📊 Round Information**: Tracks current round, score, and round timer
- **🎯 Player Death Detection**: Detects when you've been eliminated
- **🔄 Automated Asset Processing**: Converts and mirrors agent icons for detection

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Windows, macOS, or Linux
- Valorant running in windowed or fullscreen mode

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/overheat-punisher.git
   cd overheat-punisher
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the package:**
   ```bash
   pip install -e .
   ```

4. **Install development dependencies (optional):**
   ```bash
   pip install -e .[dev]
   ```

## 📖 Usage

### Basic Screen Capture
```python
from src.capture.screen_capture import show_screen_capture

# Display live screen capture (press '~' to exit)
show_screen_capture()
```

### Game Event Detection
```python
from src.capture.screen_capture import capture_screen
from src.detection.hud_detection import detect_kill_feed, is_player_dead, detect_agent_icons

# Capture current frame
frame = capture_screen()

# Detect kill events
kill_events = detect_kill_feed(frame)
print(f"Recent kills: {kill_events}")

# Check if player is dead
if is_player_dead(frame):
    print("You got punished! 💀")

# Detect team compositions
team1, team2 = detect_agent_icons(frame)
print(f"Your team: {team1}")
print(f"Enemy team: {team2}")
```

### Asset Processing
```python
from src.utility.clean_agents_and_flip import process_agent_icons

# Process raw agent icons (grayscale, resize, mirror for team detection)
process_agent_icons()
```

## 🏗️ Project Structure

```
overheat-punisher/
├── src/
│   ├── analysis/          # Game analysis and statistics
│   ├── assets/           # Agent icons and test scenarios
│   │   ├── agent_icons_raw/      # Original agent icons
│   │   ├── agent_icons_clean/    # Processed icons for detection
│   │   └── game_scenarios/       # Test images
│   ├── capture/          # Screen capture functionality
│   ├── detection/        # Computer vision and OCR detection
│   ├── utility/          # Helper scripts and tools
│   └── main.py          # Entry point
├── tests/               # Unit tests
├── pyproject.toml       # Project configuration
└── README.md           # This file
```

## 🔧 Configuration

The detection system uses several configurable parameters:

- **VARIANCE_THRESHOLD** (`800`): Minimum variance for valid agent icon regions
- **MATCH_THRESHOLD** (`0.9`): Template matching confidence threshold
- **KILL_FEED_TRIGGER** (`"KILLED BY"`): Text trigger for death detection

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run only unit tests
pytest -m unit
```

## 📚 API Reference

### Screen Capture (`src.capture.screen_capture`)

- `capture_screen()` → `MatLike`: Captures a single frame from the primary monitor
- `show_screen_capture()` → `None`: Displays live screen capture until '~' is pressed

### HUD Detection (`src.detection.hud_detection`)

- `detect_kill_feed(frame)` → `list[tuple[str, str]]`: Extracts kill events from kill feed
- `is_player_dead(frame)` → `bool`: Checks if player is currently dead
- `detect_round_info(frame)` → `tuple[int, int, str] | None`: Gets round number, time, and score
- `detect_agent_icons(frame)` → `tuple[list[str], list[str]]`: Identifies all 10 agents by team

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Dependencies

### Core Dependencies
- **OpenCV** (`opencv-python`): Computer vision and image processing
- **EasyOCR** (`easyocr`): Text recognition for kill feed and UI elements
- **MSS** (`mss`): Fast cross-platform screen capture
- **NumPy** (`numpy`): Numerical computing for image arrays
- **Loguru** (`loguru`): Structured logging

### Development Dependencies
- **pytest**: Testing framework

## 🐛 Known Issues

- OCR accuracy may vary with different display resolutions
- Agent detection requires specific game UI scaling
- Performance may be impacted with GPU-disabled EasyOCR

## 📄 License

This project is for educational and personal use only. Valorant is a trademark of Riot Games, Inc.

## 🎯 Future Enhancements

- [ ] Real-time performance analytics
- [ ] Match history tracking
- [ ] Web dashboard for statistics
- [ ] Multiple resolution support
- [ ] GPU acceleration for OCR
- [ ] Round outcome prediction

---

**⚠️ Disclaimer**: This tool is designed for personal gameplay analysis and educational purposes. Use responsibly and in accordance with Riot Games' Terms of Service.