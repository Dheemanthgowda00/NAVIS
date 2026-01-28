# Human Detection & Following - Complete Guide

## 🎯 Overview

The Human_Detection_Following module is an intelligent vision system that:
1. **Detects humans** in real-time using MediaPipe Holistic
2. **Analyzes position** (left, center, right) relative to camera
3. **Estimates depth** (near, medium, far) using shoulder width analysis
4. **Commands robot** via MQTT based on detection results
5. **Provides web interface** for live monitoring and threshold adjustment

## 🏗️ Architecture

```
Camera Feed
    ↓
OpenCV (Capture Frame)
    ↓
MediaPipe Holistic (Pose Detection)
    ↓
Position Analysis (Left/Center/Right)
    ↓
Depth Estimation (Near/Medium/Far)
    ↓
Decision Engine (Determine MQTT Command)
    ↓
MQTT Publisher (Publish to robot/control)
    ↓
ESP32 Motor Control
```

## 📊 Detection Algorithm

### Position Detection (Horizontal Axis)

The frame is divided into three zones based on the person's nose position (normalized 0-1):

```
0.0 ←─────────────→ 1.0 (left to right)
│
0.0-0.35   → LEFT ZONE      → Send 'L' command
0.35-0.65  → CENTER ZONE    → Check depth
0.65-1.0   → RIGHT ZONE     → Send 'R' command
```

**Formula:**
```
nose_x_norm = nose.x (from MediaPipe, 0-1)
center_tolerance = 0.15 (15% tolerance)

if nose_x_norm < 0.35: position = "LEFT"
elif nose_x_norm > 0.65: position = "RIGHT"
else: position = "CENTER"
```

### Depth Detection (Distance Axis)

Uses shoulder width as proxy for distance from camera:

```
Distance Zones:
0% ←─────────────→ 100% (shoulder width normalized)
│
< 30%  → NEAR    → Person too close    → Send 'B' (back)
30-70% → MEDIUM  → Optimal distance    → Analyze position
> 70%  → FAR     → Person too far      → Send 'F' (forward)
```

**Formula:**
```
shoulder_width = |right_shoulder.x - left_shoulder.x|
depth_percent = 1.0 - shoulder_width_norm
(inverted: larger shoulders = closer = smaller %)

if depth_percent < 0.30: depth = "NEAR"
elif depth_percent > 0.70: depth = "FAR"
else: depth = "MEDIUM"
```

## 🎮 Command Decision Tree

```
Person Detected?
├─ YES
│  ├─ Depth = FAR?
│  │  └─ YES → Send 'F' (FORWARD)
│  │
│  ├─ Depth = NEAR?
│  │  └─ YES → Send 'B' (BACKWARD)
│  │
│  └─ Depth = MEDIUM?
│     ├─ Position = LEFT?  → Send 'L' (LEFT)
│     ├─ Position = RIGHT? → Send 'R' (RIGHT)
│     └─ Position = CENTER → Send 'S' (STOP)
│
└─ NO → Send 'S' (STOP)
```

## 📡 MQTT Communication

**Message Format (JSON):**
```json
{
  "cmd": "F",     // Command: F, B, L, R, or S
  "speed": 200    // Speed: 0-255
}
```

**Topic:** `robot/control`
**Broker:** localhost:1883
**Publisher:** Flask app on Raspberry Pi

## 🎛️ Adjustable Thresholds

The web interface allows real-time adjustment of depth detection thresholds:

### Near Threshold (Default: 0.30)
- **Range:** 0.1 to 0.5
- **Meaning:** Person closer than this percentage triggers NEAR detection
- **Effect:** Higher value = triggers sooner (more sensitive)
- **Use case:** Adjust if robot backs away too easily

### Far Threshold (Default: 0.70)
- **Range:** 0.5 to 0.9
- **Meaning:** Person farther than this percentage triggers FAR detection
- **Effect:** Lower value = triggers sooner (more sensitive)
- **Use case:** Adjust if robot doesn't follow far-away people

## 🖥️ Web Interface

**URL:** `http://192.168.0.199:5051`

### Components

1. **Video Stream**
   - Live camera feed with MediaPipe skeleton overlay
   - Zone divisions (LEFT, CENTER, RIGHT)
   - Pose landmarks visualization

2. **Status Display**
   - Person detection indicator
   - Current position (LEFT/CENTER/RIGHT)
   - Current depth (NEAR/MEDIUM/FAR)
   - Distance percentage
   - Frame rate (FPS)

3. **Command Display**
   - Currently active MQTT command
   - Color-coded for visibility

4. **Threshold Controls**
   - Sliders for Near and Far thresholds
   - Real-time update
   - Current values displayed

## 🔧 Configuration Parameters

Edit `app.py` to adjust these constants:

```python
# Frame dimensions
FRAME_WIDTH = 640      # Camera width in pixels
FRAME_HEIGHT = 480     # Camera height in pixels
FPS = 30               # Target frames per second

# Position tolerance
CENTER_TOLERANCE = 0.15  # ±15% tolerance for center detection

# Depth thresholds
DEPTH_THRESHOLD_NEAR = 0.3   # < 30% = NEAR
DEPTH_THRESHOLD_FAR = 0.7    # > 70% = FAR

# Confidence thresholds (MediaPipe)
min_detection_confidence = 0.5   # Person must be 50% confident
min_tracking_confidence = 0.5    # Tracked points must be 50% confident
```

## 📦 Dependencies

All dependencies are specified in `requirements.txt`:

```
Flask==3.1.2              # Web framework
opencv-python==4.8.1.78   # Computer vision
mediapipe==0.10.8         # Pose detection
paho-mqtt==2.1.0          # MQTT client
numpy==1.24.3             # Numerical computing
```

**Installation:**
```bash
source /home/navis/NAVIS/venv_3.10/bin/activate
pip install -r Base/Human_Detection_Following/requirements.txt
```

## 🚀 Running the Module

**1. Activate Virtual Environment:**
```bash
cd /home/navis/NAVIS
source venv_3.10/bin/activate
```

**2. Start the Application:**
```bash
cd Base/Human_Detection_Following
python app.py
```

**3. Access Web Interface:**
```
Open browser: http://192.168.0.199:5051
```

**4. Monitor MQTT (Optional):**
```bash
# In another terminal
mosquitto_sub -h 127.0.0.1 -p 1883 -t "robot/control"
```

## 🧪 Testing

### Test 1: Person Detection
1. Stand in front of camera
2. Observe "PERSON DETECTED" indicator
3. Watch skeleton overlay appear in video

### Test 2: Position Detection
1. Move left → Should see "LEFT" in position
2. Move to center → Should see "CENTER"
3. Move right → Should see "RIGHT"

### Test 3: Depth Detection
1. Stand far away → Should see "FAR"
2. Step closer → Should see "MEDIUM"
3. Very close → Should see "NEAR"

### Test 4: Command Generation
1. Position LEFT + MEDIUM depth → Check MQTT publishes 'L'
2. Position CENTER + FAR depth → Check MQTT publishes 'F'
3. Position CENTER + NEAR depth → Check MQTT publishes 'B'
4. Position CENTER + MEDIUM depth → Check MQTT publishes 'S'

**Monitor commands:**
```bash
mosquitto_sub -h 127.0.0.1 -p 1883 -t "robot/control"
```

## 🐛 Troubleshooting

### Camera Not Found
```
Error: Cannot open camera device
Solution:
- Check if camera is properly connected
- Test with: python3 -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
```

### MediaPipe Not Detecting Person
```
Problem: No skeleton visible, always "NO PERSON DETECTED"
Solutions:
1. Ensure good lighting (MediaPipe needs visible body)
2. Adjust min_detection_confidence in app.py (lower = more sensitive)
3. Make sure full body is visible in frame
4. Person must be clearly visible (not too small in frame)
```

### Depth Threshold Not Working
```
Problem: Depth always shows same value
Solution:
1. Ensure shoulders are visible in frame
2. Check if person is close enough to detect shoulders
3. Adjust confidence thresholds if needed
```

### MQTT Commands Not Publishing
```
Problem: Commands not reaching ESP32
Solutions:
1. Verify Mosquitto is running: sudo systemctl status mosquitto
2. Test MQTT: mosquitto_pub -h 127.0.0.1 -p 1883 -t test -m "hello"
3. Check logs: sudo tail -f /var/log/mosquitto/mosquitto.log
```

### Performance Issues (Low FPS)
```
Problem: FPS drops below 15
Solutions:
1. Reduce FRAME_WIDTH and FRAME_HEIGHT
2. Increase frame skip (process every 2nd frame)
3. Use model_complexity=0 (lighter model)
4. Reduce ESP32 publish frequency
```

## 📈 Performance Metrics

**Expected Performance (Raspberry Pi 4B):**
- Frame Rate: 15-25 FPS
- Latency: 100-200ms end-to-end
- CPU Usage: 60-80%
- Memory Usage: 150-200 MB

**Optimization Tips:**
1. Lower resolution → Faster processing
2. Reduce confidence thresholds → Easier detection
3. Increase frame skip → Lower FPS, higher throughput
4. Use lighter model → Faster but less accurate

## 🔄 Integration with Other Modules

This module works alongside:
- **Remote_Control**: Both publish to same MQTT topic
- **Movement**: Receives commands from both modules
- **MQTT Broker**: Central communication hub

**Priority:** Remote_Control (manual) > Human_Detection_Following (autonomous)
- If both try to control simultaneously, implement command queuing

## 📚 MediaPipe References

- **Holistic Model**: Full-body pose detection (33 pose landmarks)
- **Confidence Values**: 0-1 range (0.5 = 50% confidence)
- **Landmarks Used:**
  - Nose (0): Center face point
  - Left Shoulder (11): Left shoulder joint
  - Right Shoulder (12): Right shoulder joint

## 💡 Future Enhancements

1. **Multi-person Detection**: Track multiple people, follow closest
2. **Hand Gesture Recognition**: Add hand commands (wave to stop, etc.)
3. **Skeleton Tracking**: Store and analyze movement patterns
4. **Distance Calibration**: Use known object sizes for accurate depth
5. **Machine Learning**: Train model for specific behaviors
6. **3D Pose Estimation**: Use two cameras for 3D reconstruction
7. **Recording**: Save video with annotations for analysis
8. **Cloud Integration**: Send data to cloud for analysis

---

**Documentation Created**: 28 January 2026
**Module Status**: Ready for testing
**Tested On**: Raspberry Pi 4B with USB camera
