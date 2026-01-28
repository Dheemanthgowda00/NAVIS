# Movement Control Module - NAVIS Robot

## Overview

This module provides pose detection and movement control using MediaPipe pose landmarks. It detects bicep curls (both arms) and head movement, mapping them to 0-180 degree angles.

**Three implementations available:**
1. **`pose_angle_detector_cli.py`** - Command-line version (NO GUI, recommended for Raspberry Pi)
2. **`pose_angle_detector.py`** - GUI version (requires tkinter)
3. **`pose_angle_detector_arduino.py`** - GUI version with Arduino Mega integration

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

### Arduino Integration (arduino version)
- PWM signal generation (0-255)
- Angle-to-PWM conversion: `PWM = (Angle / 180) × 255`
- Auto-detection of Arduino Mega on COM3-COM10
- Support for 3 servo/actuator channels:
  - **Pin 3**: Left Bicep PWM
  - **Pin 5**: Right Bicep PWM
  - **Pin 6**: Head Movement PWM

---

## Installation

### Prerequisites
```bash
pip install -r requirements.txt
```

### Dependencies
- **mediapipe**: Pose detection (33 landmarks)
- **opencv-python**: Camera input and visualization
- **numpy**: Angle calculations
- **Pillow**: Image processing (optional)
- **PyMata4**: Arduino communication (optional)
- **pyserial**: Serial communication (optional)

---

## Usage - Quick Start

### 🎯 RECOMMENDED: CLI Version (No GUI needed)

```bash
python pose_angle_detector_cli.py
```

**Keyboard Controls:**
- **1** = Select LEFT BICEP
- **2** = Select RIGHT BICEP  
- **3** = Select HEAD MOVEMENT
- **q** = Quit

**Output:**
```
[Frame 30] LEFT BICEP: 45.3° | Left: 45.3° | Right: 78.2° | Head: 92.1°
[Frame 60] LEFT BICEP: 52.1° | Left: 52.1° | Right: 81.5° | Head: 90.8°
```

✅ Works on all systems (including Raspberry Pi without display)
✅ Real-time angle detection
✅ No tkinter dependency

---

### GUI Version (requires tkinter)

```bash
python pose_angle_detector.py
```

**GUI Features:**
- Movement selection buttons (Left Bicep, Right Bicep, Head)
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

### Arduino Integration (requires tkinter + Arduino)

```bash
python pose_angle_detector_arduino.py
```

**Additional Requirements:**
- Arduino Mega board connected via USB
- StandardFirmata loaded on Arduino
- Servo motors or PWM actuators wired to pins 3, 5, 6

**Connection Steps:**
1. Connect Arduino Mega via USB
2. Run: `python pose_angle_detector_arduino.py`
3. Click **"Connect to Arduino Mega"** button
4. Select movement (Left/Right Bicep or Head)
5. Perform movement → Servo moves in real-time

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
- Uses eye landmarks (33, 263) for tilt detection
- Vertical distance between eyes mapped to 0-180°

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

### Angle to PWM Conversion (Arduino)

```
Angle (°)  → PWM (0-255)
0°         → 0
90°        → 127
180°       → 255
```

---

## Troubleshooting

### "No module named '_tkinter'" Error
**Problem**: tkinter not installed for your Python version

**Solution**: Use the CLI version (recommended)
```bash
python pose_angle_detector_cli.py
```

### Person Not Detected
- Ensure good lighting
- Position entire body in frame
- Keep camera at arm's length distance
- Check MediaPipe: `pip install mediapipe`

### Arduino Not Connecting
- Check USB cable connection
- Verify Arduino in Device Manager or `/dev/ttyUSB*`
- Upload StandardFirmata to Arduino
- Try "Connect to Arduino Mega" button again

### Inaccurate Angles
- Improve lighting conditions
- Reduce background clutter
- Move closer to camera

---

## Performance

### Hardware Requirements
- **Processor**: Raspberry Pi 4B+ recommended
- **RAM**: 2GB minimum
- **Camera**: USB webcam (640×480 @ 30fps)

### Expected Performance
- **FPS**: 25-30 FPS
- **Latency**: 100-150ms with Arduino
- **CPU Usage**: 40-50%

---

## File Structure

```
Movement/
├── pose_angle_detector_cli.py          # CLI version (RECOMMENDED)
├── pose_angle_detector.py              # GUI version
├── pose_angle_detector_arduino.py      # GUI + Arduino
├── requirements.txt                     # Dependencies
└── README.md                            # This file
```

---

## Future Enhancements

- [ ] Full body angle detection (elbow, knee, hip)
- [ ] Multiple servo control (sequential movement)
- [ ] Gesture recognition (thumbs up, wave, etc.)
- [ ] Recording and playback of movements
- [ ] Web interface for remote control
- [ ] Mobile app integration

---

## License

Part of NAVIS Robot Project

---

## Support

For issues or questions, refer to the main NAVIS README.md
