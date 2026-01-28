# NAVIS Project

## Project Overview
NAVIS is a project running on a Raspberry Pi with Python development environment.

## System Information
- **OS**: Linux (Debian Bookworm)
- **Architecture**: ARM64 (aarch64)
- **System Python Version**: Python 3.11.2
- **Default Python**: Points to Python 3.11.2

## Python Environment Setup

### Available Python Versions
1. **System Python 3.11.2** - Default system Python
   - Location: `/usr/bin/python3`
   
2. **Python 3.10.0** - Compiled from source
   - Location: `/usr/local/bin/python3.10`
   - Installation Date: 28 January 2026
   - Method: Compiled from source

### Virtual Environment (venv_3.10)
- **Path**: `/home/navis/NAVIS/venv_3.10`
- **Python Version**: 3.10.0
- **Status**: ✅ Working & Verified
- **Created**: 28 January 2026

#### Activation Instructions
```bash
# To activate the virtual environment
source /home/navis/NAVIS/venv_3.10/bin/activate

# To verify it's active
python --version  # Should show Python 3.10.0

# To deactivate
deactivate
```

## Installation Details

### Python 3.10 Compilation
- **Source**: https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz
- **Configuration**: `./configure --prefix=/usr/local`
- **Build Method**: Multi-threaded compilation using `make -j$(nproc)`
- **Installation**: `sudo make install`

### Dependencies Installed
```
build-essential
zlib1g-dev
libncurses5-dev
libgdbm-dev
libnss3-dev
libssl-dev
libreadline-dev
libffi-dev
wget
```

## Project Structure
```
NAVIS/
├── README.md                          # This file
├── venv_3.10/                         # Python 3.10 Virtual Environment
│   ├── bin/                           # Executable scripts
│   ├── lib/                           # Python packages
│   ├── include/                       # Header files
│   └── pyvenv.cfg                    # Virtual environment configuration
├── Computer_Vision/                   # Computer vision and image processing module
├── Gemini_Assistant/                  # Gemini AI assistant integration
├── Local_Assistant/                   # Local assistant (offline capabilities)
├── Movement/                          # Robot movement and control module
└── Base/                              # Base configurations and utilities
```

## Quick Start Guide

### 1. Activate Virtual Environment
```bash
cd /home/navis/NAVIS
source venv_3.10/bin/activate
```

### 2. Verify Setup
```bash
python --version
python -c "import sys; print(sys.prefix)"
```

### 3. Install Packages (if needed)
```bash
pip install <package-name>
```

### 4. Deactivate Virtual Environment
```bash
deactivate
```

## Verification Status

### Last Verification: 28 January 2026
- ✅ System Python (3.11.2) confirmed
- ✅ Python 3.10.0 installed from source
- ✅ Virtual environment created successfully
- ✅ Virtual environment activation tested
- ✅ Python version correct inside venv (3.10.0)
- ✅ Prefix correctly set to `/home/navis/NAVIS/venv_3.10`

## Additional Information

### Optional Python Modules Not Built
The following optional modules were not built due to missing dependencies:
- `_bz2`
- `_dbm`
- `_lzma`
- `_sqlite3`
- `_tkinter`
- `_uuid`

These can be installed later if needed by installing the respective development packages.

### Useful Commands

#### Check Python info
```bash
source venv_3.10/bin/activate
python -c "import sys; print(f'Version: {sys.version}'); print(f'Prefix: {sys.prefix}')"
deactivate
```

#### List installed packages
```bash
source venv_3.10/bin/activate
pip list
deactivate
```

#### Check virtual environment status
```bash
ls -la /home/navis/NAVIS/venv_3.10/bin/ | grep python
```

## Notes
- The virtual environment is isolated from the system Python
- All packages installed in this venv will not affect the system Python
- This setup ensures Python 3.10 compatibility for the project

## Project Modules

### 1. Computer_Vision
- Computer vision algorithms and image processing
- Camera/sensor integration
- Object detection and recognition

### 2. Gemini_Assistant
- Integration with Google's Gemini AI
- API communication and handling
- AI-powered features and responses

### 3. Local_Assistant
- Offline/local AI assistant capabilities
- Local processing without external dependencies
- Lightweight model implementations

### 4. Movement
- Robot movement control
- Motor/actuator management
- Navigation algorithms

### 5. Base
- Base configurations
- Utility functions and helpers
- Common modules and dependencies
- **Remote_Control**: Flask + MQTT-based remote control application for robot
- **Human_Detection_Following**: MediaPipe pose detection with automatic robot following

---

## Module: Base/Human_Detection_Following

A sophisticated human detection and following system using MediaPipe pose detection with real-time MQTT robot control.

**Features:**
- Real-time person detection using MediaPipe Holistic
- Position detection: LEFT, CENTER, RIGHT
- Depth estimation: NEAR, MEDIUM, FAR
- Automatic MQTT command generation based on position and distance
- Adjustable depth thresholds
- Web interface with live video feed
- Frame-by-frame analysis with visual overlays

**Detection Logic:**
```
Position Detection (Horizontal):
- LEFT ZONE    → Person on left side → Send 'L' command (Turn Left)
- CENTER ZONE  → Person in center → Check depth
- RIGHT ZONE   → Person on right side → Send 'R' command (Turn Right)

Depth Detection (Distance):
- NEAR (< 30%)    → Person too close → Send 'B' command (Move Backward)
- MEDIUM (30-70%) → Optimal distance → Analyze position
- FAR (> 70%)     → Person too far → Send 'F' command (Move Forward)

Combined Logic:
- FAR + ANY POSITION       → 'F' (Follow forward)
- NEAR + ANY POSITION      → 'B' (Back away)
- MEDIUM + CENTER          → 'S' (Stop and track)
- MEDIUM + LEFT            → 'L' (Turn left)
- MEDIUM + RIGHT           → 'R' (Turn right)
- NO PERSON DETECTED       → 'S' (Stop)
```

**Files:**
- `app.py` - Flask app with MediaPipe integration and MQTT publishing
- `templates/index.html` - Web interface with video stream and controls
- `requirements.txt` - Python dependencies

**Installation:**
```bash
source /home/navis/NAVIS/venv_3.10/bin/activate
cd /home/navis/NAVIS/Base/Human_Detection_Following
pip install -r requirements.txt
```

**Run:**
```bash
source /home/navis/NAVIS/venv_3.10/bin/activate
cd /home/navis/NAVIS/Base/Human_Detection_Following
python app.py
```

Access at: http://your-pi-ip:5051

**Configuration:**
- **Port**: 5051 (different from Remote_Control's 5050)
- **MQTT Topic**: `robot/control` (same as Remote_Control)
- **Message Format**: JSON with `cmd` and `speed` fields
- **Adjustable Thresholds**: Near and Far depth thresholds via web interface

**Requirements (Auto-installed):**
- Flask 3.1.2 - Web framework
- opencv-python 4.8.1.78 - Computer vision
- mediapipe 0.10.8 - Pose detection
- paho-mqtt 2.1.0 - MQTT communication
- numpy 1.24.3 - Numerical computing

---

## Installed Libraries (in venv_3.10)

### Core Dependencies for Remote_Control
- **Flask** (3.1.2) - Web framework for remote control interface
- **paho-mqtt** (2.1.0) - MQTT client for robot communication

### Flask Dependencies (automatically installed)
- Werkzeug (3.1.5) - WSGI utility library
- Jinja2 (3.1.6) - Template engine
- Click (8.3.1) - Command-line interface utilities
- ItsDangerous (2.2.0) - Data signing utilities
- Blinker (1.9.0) - Signal support for Flask
- MarkupSafe (3.0.3) - String escaping utilities

### Installation Summary
- **Installation Date**: 28 January 2026
- **Installation Environment**: venv_3.10 (Python 3.10.0)
- **Installation Method**: `pip install flask paho-mqtt`
- **Installation Status**: ✅ VERIFIED AND WORKING
- **Total Packages Installed**: 10

### How to Install in a New Environment
```bash
# Activate virtual environment
source /home/navis/NAVIS/venv_3.10/bin/activate

# Install from requirements.txt
cd /home/navis/NAVIS/Base/Remote_Control
pip install -r requirements.txt
```

### Module: Base/Remote_Control
A Flask-based web application with MQTT integration for remote robot control.

**Features:**
- Web-based remote control interface (port 5050)
- MQTT communication for robot commands
- Speed control capability
- Real-time command transmission

**Files:**
- `app.py` - Main Flask application with MQTT client
- `requirements.txt` - Dependency specifications
- `templates/index.html` - Web interface
- Running MQTT Broker required on localhost:1883

**To Run:**
```bash
source /home/navis/NAVIS/venv_3.10/bin/activate
cd /home/navis/NAVIS/Base/Remote_Control
python app.py
```
Then access at: http://your-pi-ip:5050

---

## MQTT Broker Setup (Mosquitto)

### Installation
The Mosquitto MQTT broker is installed and configured to handle communication between the Flask Remote_Control app and ESP32 robot.

**Installed Components:**
- **mosquitto** (2.0.11) - MQTT broker server
- **mosquitto-clients** (2.0.11) - Command-line MQTT tools
- **libmosquitto1** (2.0.11) - MQTT client library

**Installation Date**: 28 January 2026
**Installation Status**: ✅ INSTALLED AND RUNNING

### Configuration

**Listening Address**: 0.0.0.0 (all interfaces)
**Port**: 1883 (standard MQTT port)
**Authentication**: Anonymous connections allowed (for development)

**Configuration File**: `/etc/mosquitto/conf.d/listener.conf`
```
listener 1883 0.0.0.0
allow_anonymous true
max_connections -1
```

### Service Management

**Check Status:**
```bash
sudo systemctl status mosquitto
```

**Start/Stop/Restart:**
```bash
sudo systemctl start mosquitto      # Start the broker
sudo systemctl stop mosquitto       # Stop the broker
sudo systemctl restart mosquitto    # Restart the broker
sudo systemctl enable mosquitto     # Enable auto-start on boot
```

### Verify MQTT Connectivity

**Test Broker from Pi:**
```bash
# Publish a test message
mosquitto_pub -h 127.0.0.1 -p 1883 -t "test/connection" -m "Test Message"

# Subscribe to messages in real-time
mosquitto_sub -h 127.0.0.1 -p 1883 -t "robot/control"
```

**Network Information:**
- **Pi Hostname**: `navis` (resolves to `navis.local`)
- **Pi IP Address**: 192.168.0.199
- **MQTT Broker Address**: `navis.local:1883` (or `192.168.0.199:1883`)

### Remote Control Integration

The Flask Remote_Control app publishes commands to:
- **Topic**: `robot/control`
- **Message Format**: JSON with `cmd` and `speed` fields
  ```json
  {
    "cmd": "F",
    "speed": 200
  }
  ```

### ESP32 Connection

Your ESP32 should:
1. Connect to WiFi network (e.g., `ACT_2.4G`)
2. Resolve Pi hostname via mDNS: `navis.local` or use IP `192.168.0.199`
3. Connect to MQTT broker on port 1883
4. Subscribe to topic `robot/control`
5. Parse JSON commands and control motors accordingly

**Example ESP32 MQTT Setup:**
```cpp
// Find Pi via mDNS
IPAddress serverIP = MDNS.queryHost("navis");  // Returns 192.168.0.199
client.setServer(serverIP, 1883);
client.subscribe("robot/control");
```

### Message Flow

```
Flask Remote_Control (Pi:5050)
    ↓ (sends JSON command)
Mosquitto MQTT Broker (Pi:1883)
    ↓ (publishes to "robot/control")
ESP32 MQTT Client
    ↓ (receives and parses JSON)
Motor Control (BTS7960 drivers)
```

---

**Last Updated**: 28 January 2026 14:45 - Human Detection & Following module created with MediaPipe integration
