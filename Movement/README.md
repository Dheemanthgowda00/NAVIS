# Movement Control Module - NAVIS Robot

## Overview

This module provides pose detection and movement control using MediaPipe pose landmarks. It detects bicep curls (both arms) and head movement, mapping them to 0-180 degree angles.

**Two implementations available:**
1. **`pose_angle_detector.py`** - MediaPipe pose detection with GUI (no Arduino)
2. **`pose_angle_detector_arduino.py`** - Same as above + Arduino Mega PWM control

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
# Install Python 3.10 (or 3.8+)
# Install pip packages
pip install -r requirements.txt
```

### Dependencies
- **mediapipe**: Pose detection (33 landmarks)
- **opencv-python**: Camera input and visualization
- **numpy**: Angle calculations
- **Pillow**: Image processing for GUI
- **PyMata4**: Arduino communication (arduino version only)
- **pyserial**: Serial communication (arduino version only)

---

## Usage

### 1. Pose Angle Detector (MediaPipe Only)

```bash
python pose_angle_detector.py
```

**GUI Layout:**
- **Left side**: Live camera feed with pose landmarks
- **Right side**: Control panel with:
  - Movement selection buttons (Left Bicep, Right Bicep, Head)
  - Current angle display (0-180°)
  - Angle progress bar
  - Real-time status for all three joints
  - Person detection indicator

**Controls:**
1. Position yourself in front of camera
2. Click desired movement button (Left Bicep, Right Bicep, or Head)
3. Perform the movement
4. Angle updates in real-time (0-180°)

**Output:**
- Real-time angle display in GUI
- Pose landmarks visualization on camera feed
- Angle annotations above detected joints

---

### 2. Pose Angle Detector with Arduino

```bash
python pose_angle_detector_arduino.py
```

**Additional Requirements:**
- Arduino Mega board connected via USB
- PyMata4/StandardFirmata loaded on Arduino
- Servo motors or PWM-controlled actuators wired to pins 3, 5, 6

**Connection Steps:**
1. Connect Arduino Mega via USB
2. Run the script: `python pose_angle_detector_arduino.py`
3. Click **"Connect to Arduino Mega"** button
4. Script auto-detects Arduino on COM3-COM10
5. Select movement (Left/Right Bicep or Head)
6. Perform movement → Servo/actuator moves in real-time

**Arduino Wiring:**
```
Arduino Mega Pin 3  → Left Bicep Servo PWM
Arduino Mega Pin 5  → Right Bicep Servo PWM
Arduino Mega Pin 6  → Head Movement Servo PWM
Arduino GND        → Servo GND
Arduino 5V         → Servo VCC (through voltage regulator)
```

**Angle to PWM Conversion:**
```
Angle (°)  → PWM (0-255)
0°         → 0
90°        → 127
180°       → 255
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
- Small distance = Upright (90°)
- Large distance = Tilted (0° or 180°)

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

## Troubleshooting

### Person Not Detected
- Ensure good lighting
- Position entire body in frame
- Keep at arm's length distance from camera
- Check MediaPipe is installed: `pip install mediapipe`

### Arduino Not Connecting
- Check USB cable connection
- Verify Arduino appears in Device Manager (Windows) or `/dev/ttyUSB*` (Linux)
- Ensure StandardFirmata is uploaded to Arduino
- Try clicking "Connect to Arduino Mega" multiple times
- Check port manually: `python -m serial.tools.list_ports`

### Inaccurate Angles
- Improve lighting conditions
- Ensure clear visibility of arms
- Reduce background clutter
- Increase detection confidence in code if needed

### PyMata4 Import Error
```bash
pip install PyMata4 --no-cache-dir
```

---

## Performance

### Hardware Requirements
- **Processor**: Raspberry Pi 4B or faster
- **RAM**: 2GB minimum
- **Camera**: USB webcam (640×480 @ 30fps)

### Expected Performance
- **FPS**: 25-30 FPS
- **Latency**: 100-150ms (angle detection to PWM output)
- **CPU Usage**: 40-50%

---

## File Structure

```
Movement/
├── pose_angle_detector.py              # MediaPipe-only version
├── pose_angle_detector_arduino.py      # Arduino integration version
├── requirements.txt                     # Dependencies
├── README.md                            # This file
└── SETUP.md                             # Detailed setup guide
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
