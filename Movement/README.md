# Movement Control Module - NAVIS Robot

## Overview

This module provides pose detection and movement control using MediaPipe pose landmarks. It detects bicep curls (both arms) and head movement, mapping them to 0-180 degree angles.

**Available implementations:**
1. **`app.py`** - Flask web interface (RECOMMENDED for Raspberry Pi)
2. **`pose_angle_detector_cli.py`** - Command-line version (terminal-based)
3. **`pose_angle_detector.py`** - Desktop GUI version (requires tkinter & display)
4. **`pose_angle_detector_arduino.py`** - GUI + Arduino integration

---

## Features

### Movement Detection
- **Left Bicep**: Detects left arm bend angle (shoulder → elbow → wrist)
- **Right Bicep**: Detects right arm bend angle (shoulder → elbow → wrist)
- **Head Movement**: Detects vertical head rotation/tilt

### Angle Mapping
- All movements mapped to **0-180 degrees**
- 0° = Straight/Neutral
- 180° = Fully bent/Maximum rotation
- Real-time angle smoothing (5-frame moving average)

---

## Installation

### Prerequisites
```bash
pip install -r requirements.txt
```

### Dependencies
- **mediapipe**: Pose detection (33 landmarks)
- **opencv-python**: Camera input and video processing
- **numpy**: Angle calculations
- **Flask**: Web interface (for web version)
- **Pillow**: Image processing (optional)
- **PyMata4**: Arduino communication (optional)

---

## Usage - Quick Start

### 🌟 RECOMMENDED: Flask Web Interface

```bash
python app.py
```

**Features:**
- ✅ Accessible via web browser (http://navis.local:5052)
- ✅ Works on Raspberry Pi headless mode
- ✅ No tkinter or display required
- ✅ Real-time video streaming
- ✅ Beautiful responsive web UI
- ✅ Can access from any computer on network
- ✅ Perfect for remote operation

**How to Use:**
1. Start the server:
   ```bash
   cd /home/navis/NAVIS/Movement
   python app.py
   ```

2. Open in web browser:
   ```
   http://navis.local:5052
   or
   http://192.168.0.199:5052
   ```

3. Click buttons to select movement:
   - **LEFT BICEP** - Track left arm bend angle
   - **RIGHT BICEP** - Track right arm bend angle
   - **HEAD** - Track head movement angle

4. Watch real-time angle display and video stream

---

### CLI Version (Terminal-based)

```bash
python pose_angle_detector_cli.py
```

**Keyboard Controls:**
- **1** = Select LEFT BICEP
- **2** = Select RIGHT BICEP  
- **3** = Select HEAD MOVEMENT
- **q** = Quit

**Advantages:**
- ✅ Works on SSH (no display needed)
- ✅ Lowest latency
- ✅ Smallest memory footprint
- ✅ Real-time terminal output
- ✅ Perfect for headless Raspberry Pi

**Output:**
```
[Frame 30] LEFT BICEP: 45.3° | Left: 45.3° | Right: 78.2° | Head: 92.1°
[Frame 60] LEFT BICEP: 52.1° | Left: 52.1° | Right: 81.5° | Head: 90.8°
```

---

### Desktop GUI Version (requires tkinter)

```bash
python pose_angle_detector.py
```

**GUI Features:**
- Movement selection buttons
- Real-time angle display (0-180°)
- Angle progress bar
- Status display for all three joints
- Person detection indicator
- Live camera feed with pose overlay

**Installation (if needed):**
```bash
sudo apt-get install python3-tk
```

---

### Arduino Integration (requires tkinter + Arduino Mega)

```bash
python pose_angle_detector_arduino.py
```

**Additional Requirements:**
- Arduino Mega board connected via USB
- StandardFirmata loaded on Arduino
- Servo motors or PWM actuators wired to pins 3, 5, 6

**Arduino Wiring:**
```
Arduino Mega Pin 3  → Left Bicep Servo PWM
Arduino Mega Pin 5  → Right Bicep Servo PWM
Arduino Mega Pin 6  → Head Movement Servo PWM
Arduino GND        → Servo GND
Arduino 5V         → Servo VCC
```

---

## Technical Details

### Pose Landmarks Used

**Left Bicep Calculation:**
- Point 1: Left Shoulder (landmark 11)
- Point 2: Left Elbow (landmark 13)
- Point 3: Left Wrist (landmark 15)
- Angle = Arc cos of normalized vectors

**Right Bicep Calculation:**
- Point 1: Right Shoulder (landmark 12)
- Point 2: Right Elbow (landmark 14)
- Point 3: Right Wrist (landmark 16)

**Head Movement Calculation:**
- Uses eye landmarks from face_landmarks (indices 33, 263)
- Fallback: Uses nose-to-shoulder angle if face not detected
- Vertical eye distance mapped to 0-180°

### Smoothing Algorithm

All angles use 5-frame moving average:
```python
smoothed_angle = (angle_frame1 + angle_frame2 + ... + angle_frame5) / 5
```

### MediaPipe Configuration

```python
model_complexity = 1        # Medium accuracy/speed balance
smooth_landmarks = True     # Temporal smoothing
min_detection_confidence = 0.7
min_tracking_confidence = 0.7
```

---

## File Structure

```
Movement/
├── app.py                              # Flask web interface ⭐ RECOMMENDED
├── templates/
│   └── index_movement.html             # Web UI template
├── pose_angle_detector_cli.py          # CLI version
├── pose_angle_detector.py              # Desktop GUI version
├── pose_angle_detector_arduino.py      # GUI + Arduino version
├── requirements.txt                     # Dependencies
└── README.md                            # This file
```

---

## Performance Comparison

| Feature | Web | CLI | GUI | Arduino |
|---------|-----|-----|-----|---------|
| Display needed | ❌ No | ❌ No | ✅ Yes | ✅ Yes |
| Tkinter needed | ❌ No | ❌ No | ✅ Yes | ✅ Yes |
| Browser access | ✅ Yes | ❌ No | ❌ No | ❌ No |
| Remote access | ✅ Yes | ❌ No | ❌ No | ❌ No |
| Arduino support | ❌ No | ❌ No | ❌ No | ✅ Yes |
| Latency | Low | Very low | Low | Medium |
| Ease of use | Easy | Easy | Medium | Medium |
| Network ports | 5052 | None | None | None |
| Best for | Remote Raspberry Pi | SSH/Terminal | Development | Hardware control |

---

## Troubleshooting

### "No display" error with CLI version
The CLI version doesn't show a display window - it runs completely headless. This is normal and expected.

### "Could not connect to display" error with Qt
This error occurs when trying to run GUI version without a display. Use `app.py` instead:
```bash
python app.py
```

### Person Not Detected
- Ensure good lighting
- Position entire body in frame
- Keep camera at arm's length distance
- Check MediaPipe: `pip install mediapipe`

### Web interface not accessible
- Verify Flask is running: Look for "Running on http://0.0.0.0:5052"
- Check firewall: Port 5052 should be open
- Try direct IP: http://192.168.0.199:5052 (replace with your Pi's IP)
- Verify on same network: Computer and Pi must be on same network

### Arduino Not Connecting
- Check USB cable connection
- Verify Arduino in Device Manager or `/dev/ttyUSB*`
- Upload StandardFirmata to Arduino
- Try "Connect to Arduino" button again

### Inaccurate Angles
- Improve lighting conditions
- Reduce background clutter
- Move closer to camera
- Ensure full body visibility

---

## Performance Specs

### Hardware Requirements
- **Processor**: Raspberry Pi 4B+ recommended
- **RAM**: 2GB minimum
- **Camera**: USB webcam (640×480 @ 30fps)
- **Network**: Ethernet or WiFi for web interface

### Expected Performance
- **FPS**: 25-30 FPS
- **Latency**: 100-150ms (web), <50ms (CLI)
- **CPU Usage**: 40-50%
- **Memory Usage**: 150-200MB

---

## FAQ

**Q: What's the best version for Raspberry Pi?**
A: Use `app.py` (Flask web interface). It requires no display, works remotely, and has a nice UI.

**Q: Can I access from my phone?**
A: Yes! With `app.py`, just open http://navis.local:5052 on your phone's browser.

**Q: Does it work over SSH?**
A: CLI version works perfectly over SSH. Web version works via browser on any device.

**Q: What's the difference between GUI and web versions?**
A: GUI runs on the Raspberry Pi with a display. Web version is a server you access via browser - more flexible.

**Q: Can I use this with motors/servos?**
A: Yes! Use the Arduino version to control PWM servos (0-255 based on angle).

---

## Future Enhancements

- [ ] Full body angle detection (elbow, knee, hip, ankle)
- [ ] Multiple servo/motor control with sequences
- [ ] Gesture recognition (thumbs up, wave, point, etc.)
- [ ] Recording and playback of movements
- [ ] Mobile app for iOS/Android
- [ ] Bluetooth servo control
- [ ] Machine learning-based movement classification

---

## License

Part of NAVIS Robot Project

---

## Support

For issues or questions, refer to the main NAVIS README.md or create an issue on GitHub.
