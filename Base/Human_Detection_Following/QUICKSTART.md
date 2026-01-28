# Human Detection & Following - Quick Start

## ⚡ 5-Minute Setup

### 1. Install Dependencies
```bash
cd /home/navis/NAVIS
source venv_3.10/bin/activate
pip install -r Base/Human_Detection_Following/requirements.txt
```

### 2. Test Setup
```bash
cd Base/Human_Detection_Following
python test_setup.py
```

You should see:
```
✓ Camera working
✓ MediaPipe imported successfully
✓ Holistic model loaded
✓ Pose detection working
✓ OpenCV version: 4.8.1.78
✓ MQTT broker connected
✓ Test message published to robot/control

✓ All systems ready!
```

### 3. Start the Application
```bash
python app.py
```

Expected output:
```
 * Running on http://0.0.0.0:5051
 * Press CTRL+C to quit
```

### 4. Open Web Interface
Open browser: `http://192.168.0.199:5051`

## 🎯 Expected Behavior

### No Person
- Detection status: "NO PERSON DETECTED" (red)
- Command: "S" (Stop)
- Robot: Stationary

### Person Far Away
- Detection status: "PERSON DETECTED" (green)
- Position: LEFT/CENTER/RIGHT
- Depth: FAR
- Command: "F" (Forward)
- Robot: Moves forward to follow

### Person Too Close
- Detection status: "PERSON DETECTED" (green)
- Position: LEFT/CENTER/RIGHT
- Depth: NEAR
- Command: "B" (Backward)
- Robot: Backs away

### Person at Optimal Distance (Center)
- Detection status: "PERSON DETECTED" (green)
- Position: CENTER
- Depth: MEDIUM
- Command: "S" (Stop)
- Robot: Stops and tracks

### Person at Optimal Distance (Left)
- Detection status: "PERSON DETECTED" (green)
- Position: LEFT
- Depth: MEDIUM
- Command: "L" (Left)
- Robot: Turns left

### Person at Optimal Distance (Right)
- Detection status: "PERSON DETECTED" (green)
- Position: RIGHT
- Depth: MEDIUM
- Command: "R" (Right)
- Robot: Turns right

## 🔧 Adjusting Thresholds

1. Open web interface: `http://192.168.0.199:5051`
2. Scroll down to "Depth Thresholds" section
3. Adjust sliders:
   - **Near Threshold**: When person should be considered NEAR
   - **Far Threshold**: When person should be considered FAR

**Tips:**
- Higher Near value → Robot backs away sooner
- Lower Far value → Robot follows sooner

## 📊 Real-Time Monitoring

**Watch MQTT messages:**
```bash
mosquitto_sub -h 127.0.0.1 -p 1883 -t "robot/control"
```

You'll see JSON messages like:
```json
{"cmd": "F", "speed": 200}
{"cmd": "L", "speed": 200}
{"cmd": "S", "speed": 0}
```

## 🚀 Running Both Modules

You can run Remote_Control and Human_Detection_Following simultaneously:

**Terminal 1 - Remote Control:**
```bash
cd /home/navis/NAVIS/Base/Remote_Control
python app.py  # Port 5050
```

**Terminal 2 - Human Detection:**
```bash
cd /home/navis/NAVIS/Base/Human_Detection_Following
python app.py  # Port 5051
```

Both publish to same MQTT topic (`robot/control`), so:
- Manual remote control takes priority when active
- Robot autonomously follows when remote is idle

## 🧪 Testing Checklist

- [ ] Camera works (video feed appears)
- [ ] Person visible in frame appears with skeleton overlay
- [ ] Zones (LEFT/CENTER/RIGHT) are visible
- [ ] Moving left updates "LEFT" indicator
- [ ] Moving center updates "CENTER" indicator
- [ ] Moving right updates "RIGHT" indicator
- [ ] Moving away updates "FAR" and sends "F" command
- [ ] Moving closer updates "NEAR" and sends "B" command
- [ ] Standing center at medium distance sends "S" command
- [ ] Robot responds to MQTT commands correctly
- [ ] FPS is 15+ (acceptable for real-time)

## 📱 Web Interface Features

**Top Section:**
- Live video feed with pose skeleton
- Zone dividers (LEFT, CENTER, RIGHT)
- Real-time skeleton with joints and connections

**Right Panel:**
- Detection status indicator (red/green)
- Position display (LEFT/CENTER/RIGHT)
- Depth display (NEAR/MEDIUM/FAR)
- Distance percentage (0-100%)
- FPS counter
- Current MQTT command display
- Threshold adjustment sliders
- Information box with behavior guide

## 🔄 Message Flow

```
Person in front of camera
        ↓
MediaPipe detects pose landmarks
        ↓
App analyzes position & depth
        ↓
Decision engine selects command
        ↓
MQTT publishes: {"cmd": "X", "speed": 200}
        ↓
ESP32 receives MQTT message
        ↓
Motor drivers move robot
        ↓
Robot follows person!
```

## 🐛 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| No video stream | Check camera connection, try `python test_setup.py` |
| No person detected | Ensure good lighting, full body visible, move closer |
| Skeleton flickering | Normal at low FPS, increase lighting or reduce frame skip |
| Robot not responding | Check MQTT broker running, verify ESP32 connected |
| High CPU usage | Reduce resolution, increase frame skip, use lighter model |
| Slow FPS | Reduce FRAME_WIDTH/HEIGHT in app.py |

## 📚 More Information

- **Full Guide**: See `HUMAN_DETECTION_GUIDE.md`
- **Configuration**: Edit `app.py` for advanced settings
- **Dependencies**: See `requirements.txt`

---

**Status**: ✅ Ready to use
**Last Updated**: 28 January 2026
