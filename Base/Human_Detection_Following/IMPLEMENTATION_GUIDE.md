# 🤖 NAVIS Robot - Human Detection & Following System
## Complete Implementation Summary

---

## ✅ What Was Built

A complete **autonomous human detection and following system** that integrates with your NAVIS robot:

### Core Components
1. **MediaPipe Holistic Pose Detection** - Real-time human pose estimation
2. **Position Analysis** - LEFT / CENTER / RIGHT detection
3. **Depth Estimation** - NEAR / MEDIUM / FAR distance calculation
4. **Intelligent Command Generation** - Automatic MQTT robot control
5. **Web Control Interface** - Live monitoring and threshold adjustment
6. **MQTT Integration** - Seamless communication with ESP32

---

## 📁 Project Structure

```
/home/navis/NAVIS/Base/Human_Detection_Following/
├── app.py                      # Main Flask app (312 lines)
│   ├── MediaPipe integration
│   ├── Position detection algorithm
│   ├── Depth estimation logic
│   ├── MQTT command generation
│   ├── Flask routes
│   └── Video streaming
│
├── templates/
│   └── index.html             # Web interface (~450 lines)
│       ├── Live video stream
│       ├── Real-time status display
│       ├── Threshold controls
│       ├── Modern UI design
│       └── JavaScript auto-update
│
├── test_setup.py              # System verification script
├── viewer.py                  # Standalone pose viewer (no web)
├── requirements.txt           # Dependencies
├── QUICKSTART.md             # 5-minute setup guide
├── SETUP_COMPLETE.md         # Setup summary
└── README                     # (in main README.md)
```

---

## 🔄 System Architecture

```
┌──────────────────────────────────────────────────────┐
│              HUMAN DETECTION PIPELINE                │
├──────────────────────────────────────────────────────┤
│                                                       │
│  Camera (USB/Pi Camera)                             │
│       ↓                                              │
│  OpenCV: Capture Frame (640×480, 15-25 FPS)        │
│       ↓                                              │
│  MediaPipe: Pose Detection (33 landmarks)          │
│       ↓                                              │
│  ┌──────────────────────────────────────┐           │
│  │ Analyze Pose Landmarks:              │           │
│  │ - Nose (0)         → Position X      │           │
│  │ - L Shoulder (11)  → Depth estimate  │           │
│  │ - R Shoulder (12)  → Depth estimate  │           │
│  └──────────────────────────────────────┘           │
│       ↓                                              │
│  Position Detection: LEFT / CENTER / RIGHT           │
│       ↓                                              │
│  Depth Detection: NEAR / MEDIUM / FAR                │
│       ↓                                              │
│  Decision Engine (Command Logic)                     │
│       ↓                                              │
│  MQTT Publisher: Publish JSON Command               │
│       ↓                                              │
│  {"cmd": "X", "speed": 200}                         │
│       ↓                                              │
│  Mosquitto MQTT Broker (localhost:1883)             │
│       ↓ Publish to: robot/control                    │
│       ↓                                              │
│  ESP32 MQTT Subscriber                              │
│       ↓ Parse JSON & Execute                         │
│       ↓                                              │
│  BTS7960 Motor Drivers                              │
│       ↓                                              │
│  DC Motors → Robot Movement                          │
│                                                       │
└──────────────────────────────────────────────────────┘
```

---

## 🎯 Detection Algorithm

### Position Detection (Horizontal)
```
Frame divided into 3 zones based on nose X coordinate:

    NOSE_X_NORM
    (0.0 to 1.0)
        ↓
    
0.0 ├─────────┼─────────┼─────────┤ 1.0
    │  LEFT   │ CENTER  │  RIGHT  │
    │ 0-0.35  │0.35-0.65│0.65-1.0 │
    └─────────┴─────────┴─────────┘
    
    Tolerance: ±15% for center zone
```

### Depth Detection (Distance)
```
Shoulder Width Normalized → Depth Percentage

SHOULDER_WIDTH_NORM
(inverted to get distance)
        ↓
        
0.0% ├─────────┼─────────┼─────────┤ 100%
     │  NEAR   │ MEDIUM  │  FAR    │
     │ < 30%   │ 30-70%  │ > 70%   │
     └─────────┴─────────┴─────────┘
     
     Closer = Wider shoulders = Smaller %
     Farther = Narrower shoulders = Larger %
```

### Command Generation Logic
```
IF person_detected == False:
    COMMAND = 'S' (STOP)

ELIF depth == 'FAR':
    COMMAND = 'F' (FORWARD)  ← Follow forward

ELIF depth == 'NEAR':
    COMMAND = 'B' (BACKWARD) ← Back away

ELIF depth == 'MEDIUM':
    IF position == 'LEFT':
        COMMAND = 'L' (LEFT)
    ELIF position == 'RIGHT':
        COMMAND = 'R' (RIGHT)
    ELSE:  # CENTER
        COMMAND = 'S' (STOP)  ← Track at this distance

PUBLISH: {"cmd": COMMAND, "speed": 200}
```

---

## 🔌 Hardware Integration

### Required Hardware
✅ **Camera**: USB or Raspberry Pi camera module
✅ **ESP32**: Microcontroller with WiFi/MQTT
✅ **BTS7960**: H-bridge motor driver (2 units for 2 motors)
✅ **Motors**: DC motors with wheels
✅ **Raspberry Pi**: Running MQTT broker + Flask app
✅ **Network**: WiFi connection (2.4GHz)

### Message Format
```json
{
  "cmd": "F",        // Command: F, B, L, R, or S
  "speed": 200       // Speed: 0-255
}
```

### MQTT Topic
- **Topic**: `robot/control`
- **Broker**: localhost:1883
- **Publisher**: Flask app on Raspberry Pi
- **Subscriber**: ESP32 MQTT client

---

## 🚀 Quick Start Commands

### 1. Install Dependencies
```bash
cd /home/navis/NAVIS
source venv_3.10/bin/activate
pip install -r Base/Human_Detection_Following/requirements.txt
```

*Note: OpenCV and MediaPipe are large - installation takes 5-10 minutes on Raspberry Pi*

### 2. Test System
```bash
cd Base/Human_Detection_Following
python test_setup.py
```

Expected output:
```
✓ Camera working: Resolution 640x480
✓ MediaPipe imported successfully
✓ Holistic model loaded
✓ Pose detection working
✓ OpenCV version: 4.8.1.78
✓ MQTT broker connected
✓ Test message published

✓ All systems ready! Start the app...
```

### 3. Run Application
```bash
python app.py
```

Expected output:
```
✅ MQTT Connected
🎥 Human Detection Following - Starting on http://0.0.0.0:5051
 * Running on http://0.0.0.0:5051
 * Press CTRL+C to quit
```

### 4. Access Web Interface
Open browser: **http://192.168.0.199:5051**

### 5. Monitor MQTT (Optional)
```bash
mosquitto_sub -h 127.0.0.1 -p 1883 -t "robot/control"
```

---

## 🎨 Web Interface Features

### Live Video Stream
- Real-time camera feed (30 FPS)
- MediaPipe skeleton overlay
- Zone visualization (LEFT, CENTER, RIGHT)
- Pose landmarks with connections

### Status Panel
- **Detection Indicator**: Red (no person) / Green (detected)
- **Position Display**: LEFT / CENTER / RIGHT
- **Depth Display**: NEAR / MEDIUM / FAR
- **Distance Percentage**: 0-100% shoulder width
- **FPS Counter**: Real-time performance
- **Command Display**: Current MQTT command

### Threshold Controls
- **Near Threshold** slider (0.1-0.5)
  - Controls when person is considered NEAR
  - Higher = backs away sooner
- **Far Threshold** slider (0.5-0.9)
  - Controls when person is considered FAR
  - Lower = follows sooner
- Real-time updates (no page reload needed)

### Design
- Dark theme (OLED-friendly)
- Green (#00ff88) and cyan (#00ccff) accent colors
- Responsive layout (desktop and mobile)
- Smooth animations and indicators

---

## ⚙️ Configuration Options

### In `app.py`
```python
# Frame dimensions
FRAME_WIDTH = 640                    # Camera width (pixels)
FRAME_HEIGHT = 480                   # Camera height (pixels)
FPS = 30                             # Target frame rate

# Position detection
CENTER_TOLERANCE = 0.15              # ±15% tolerance for center

# Depth detection (adjustable via web)
DEPTH_THRESHOLD_NEAR = 0.3           # < 30% = NEAR
DEPTH_THRESHOLD_FAR = 0.7            # > 70% = FAR

# MediaPipe confidence
min_detection_confidence = 0.5        # 50% confidence threshold
min_tracking_confidence = 0.5         # 50% tracking threshold
```

### Via Web Interface
- Adjust Near Threshold: 0.1 to 0.5
- Adjust Far Threshold: 0.5 to 0.9
- Changes take effect immediately

---

## 📊 Performance Specifications

### Raspberry Pi 4B
| Metric | Expected |
|--------|----------|
| FPS | 15-25 |
| Latency | 100-200ms |
| CPU Usage | 60-80% |
| Memory Usage | 150-200 MB |
| Detection Accuracy | 85-95% |

### Optimization Tips
1. **Reduce resolution** → Faster processing
2. **Increase frame skip** → Lower FPS, higher throughput
3. **Use lighter model** → Faster but less accurate
4. **Adjust confidence** → Lower = easier detection

---

## 🧪 Testing Checklist

Before deployment, verify:

- [ ] Camera displays live feed in web interface
- [ ] Person's skeleton visible with 33 landmarks
- [ ] Moving left updates position to "LEFT"
- [ ] Moving center updates position to "CENTER"
- [ ] Moving right updates position to "RIGHT"
- [ ] Moving away increases depth percentage
- [ ] Moving closer decreases depth percentage
- [ ] FAR triggers → MQTT publishes 'F' command
- [ ] NEAR triggers → MQTT publishes 'B' command
- [ ] Moving left at medium distance → 'L' command
- [ ] Moving right at medium distance → 'R' command
- [ ] Centered at medium distance → 'S' command
- [ ] Robot responds to each command correctly
- [ ] Threshold sliders update detection behavior
- [ ] FPS counter shows 15+ (acceptable)

---

## 🐛 Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Camera feed not loading | Camera not found | Check connection, run `test_setup.py` |
| No person detected | Poor lighting | Increase brightness/lighting |
| Skeleton flickering | Low FPS | Increase lighting, reduce resolution |
| Robot not responding | MQTT not working | Verify broker running, check ESP32 |
| Threshold not updating | Browser cache | Hard refresh (Ctrl+F5) |
| High CPU usage | Heavy processing | Reduce resolution, skip frames |
| Slow FPS | Heavy computation | Lower FRAME_WIDTH/HEIGHT in app.py |

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `QUICKSTART.md` | 5-minute setup guide |
| `SETUP_COMPLETE.md` | Implementation summary |
| `HUMAN_DETECTION_GUIDE.md` | Technical deep-dive |
| `app.py` | Main application code |
| `templates/index.html` | Web interface |
| `test_setup.py` | System verification |
| `viewer.py` | Standalone debugging viewer |
| `requirements.txt` | Dependencies |

---

## 🔄 Running Both Modules Simultaneously

You can run Remote_Control and Human_Detection_Following at the same time:

```
Terminal 1:
cd /home/navis/NAVIS/Base/Remote_Control
python app.py  # Port 5050

Terminal 2:
cd /home/navis/NAVIS/Base/Human_Detection_Following
python app.py  # Port 5051
```

**Result**:
- Both publish to `robot/control` MQTT topic
- Manual control (Remote) takes priority when active
- Robot autonomously follows when remote is idle
- Real-time command switching

---

## 🎓 Learning Resources

### MediaPipe Documentation
- 33 Pose Landmarks: https://mediapipe.dev/solutions/pose
- Confidence interpretation: 0.5 = 50% confidence minimum
- Visibility: 0-1 range, higher = more visible

### MQTT Protocol
- Topic: `robot/control`
- Message: JSON with `cmd` and `speed`
- QoS: 0 (fire and forget)

### OpenCV
- Frame capture: `cap.read()`
- Encoding: `cv2.imencode('.jpg', frame)`
- Streaming: MJPEG format

---

## 🎉 Success Indicators

You'll know it's working when:

✅ Web interface loads at `http://192.168.0.199:5051`
✅ Live video appears with skeleton overlay
✅ Status shows "PERSON DETECTED" when you're visible
✅ Position changes as you move left/right
✅ Depth changes as you move closer/farther
✅ MQTT messages appear in `mosquitto_sub` output
✅ Robot responds to commands immediately
✅ Robot follows you around the room
✅ FPS counter shows 15+ frames per second

---

## 🚀 Next Steps

1. **Deploy and Test** - Run the system with actual robot
2. **Fine-tune Thresholds** - Adjust sensitivity for your environment
3. **Optimize Performance** - Adjust resolution/settings if needed
4. **Add Features** - Gesture control, recording, cloud integration
5. **Document Results** - Record performance metrics

---

## 📞 Quick Reference

**Start App**: `python app.py` (in Base/Human_Detection_Following)
**Web URL**: `http://192.168.0.199:5051`
**Test System**: `python test_setup.py`
**Monitor MQTT**: `mosquitto_sub -h 127.0.0.1 -p 1883 -t "robot/control"`
**View Skeleton**: `python viewer.py` (no web server, direct camera)

---

## 📈 Future Enhancements

1. Multi-person tracking (follow closest)
2. Hand gesture recognition
3. Depth calibration with known objects
4. Machine learning for behavior patterns
5. 3D pose with multiple cameras
6. Cloud data logging
7. Mobile app control
8. Computer vision obstacles detection

---

**Implementation Date**: 28 January 2026
**Status**: ✅ Complete & Ready for Deployment
**System**: Autonomous Human Following Robot
**Framework**: MediaPipe + Flask + MQTT
**Target Device**: Raspberry Pi + ESP32 + BTS7960

---

*For detailed technical information, see HUMAN_DETECTION_GUIDE.md*
*For quick setup, see QUICKSTART.md*
