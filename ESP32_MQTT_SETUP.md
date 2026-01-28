# MQTT Setup & ESP32 Connection Guide

## ✅ Raspberry Pi Setup Complete

Your Raspberry Pi is now fully configured for MQTT communication:

### Installed Services
- **Mosquitto MQTT Broker** (2.0.11) - Running on port 1883
- **avahi-daemon** (mDNS) - Hostname registration for `navis.local`
- **Flask Remote Control App** - Published to localhost:1883

### Network Configuration
```
Raspberry Pi IP:       192.168.0.199
Hostname:              navis
mDNS Address:          navis.local:1883
MQTT Broker Port:      1883
Flask Web Interface:   http://192.168.0.199:5050
```

---

## 🔧 ESP32 Setup

### 1. Update Your WiFi Credentials
In your ESP32 code, update:
```cpp
WiFi.begin("ACT_2.4G", "18001723");  // Your WiFi SSID and password
```

### 2. Verify mDNS Resolution
Your code already includes this, but verify it works:
```cpp
// This finds the Pi
IPAddress serverIP = MDNS.queryHost("navis");  // Returns 192.168.0.199
```

### 3. MQTT Connection
The code correctly attempts:
```cpp
client.setServer(serverIP, 1883);
client.subscribe("robot/control");
```

### 4. Expected JSON Message Format
Flask sends commands like:
```json
{
  "cmd": "F",      // F, B, L, R, or S
  "speed": 200     // 0-255
}
```

Your callback should handle it exactly as you have:
```cpp
void callback(char* topic, byte* payload, unsigned int length) {
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, payload, length);
  
  const char* cmd = doc["cmd"];
  int speed = doc["speed"];
  // ... process command
}
```

---

## 📡 Testing Connection

### On Raspberry Pi

**1. Start Flask Remote Control:**
```bash
cd /home/navis/NAVIS
source venv_3.10/bin/activate
cd Base/Remote_Control
python app.py
```

**2. Monitor MQTT Messages** (in another terminal):
```bash
cd /home/navis/NAVIS
source venv_3.10/bin/activate
python3 Base/Remote_Control/mqtt_monitor.py
```

**3. Test Manually:**
```bash
# In another terminal, publish a test command
mosquitto_pub -h 127.0.0.1 -p 1883 -t "robot/control" -m '{"cmd":"F","speed":200}'
```

### On ESP32

1. **Upload the code** to your ESP32
2. **Open Serial Monitor** (115200 baud)
3. **Watch for these messages:**
   ```
   Connecting to WiFi...
   WiFi Connected!
   Searching for navis.local...
   SUCCESS! Pi IP found: 192.168.0.199
   Connecting to MQTT Broker...
   Connected!
   RAW RECEIVED: {"cmd":"F","speed":200}
   >> EXECUTING: F | SPEED: 200
   ```

---

## 🔍 Troubleshooting

### ESP32 Can't Connect to WiFi
- Check SSID and password
- Ensure 2.4GHz WiFi (not 5GHz)
- Check signal strength

### ESP32 Can't Find navis.local
- Verify avahi-daemon is running: `sudo systemctl status avahi-daemon`
- Restart avahi: `sudo systemctl restart avahi-daemon`
- Try using IP directly: `client.setServer(IPAddress(192, 168, 0, 199), 1883);`

### MQTT Connection Fails
- Verify Mosquitto is running: `sudo systemctl status mosquitto`
- Check port 1883: `netstat -tuln | grep 1883`
- Restart broker: `sudo systemctl restart mosquitto`

### Run Full Diagnostics
```bash
cd /home/navis/NAVIS
python3 mqtt_troubleshooter.py
```

---

## 📋 Quick Commands

```bash
# Check MQTT broker status
sudo systemctl status mosquitto

# Restart MQTT broker
sudo systemctl restart mosquitto

# Monitor all MQTT messages
mosquitto_sub -h 127.0.0.1 -p 1883 -t "robot/control"

# Test MQTT connection
mosquitto_pub -h 127.0.0.1 -p 1883 -t "test/ping" -m "hello"

# Check mDNS resolution
avahi-resolve-host-name navis.local

# Get Pi IP address
hostname -I
```

---

## Message Flow

```
┌─────────────────────────────────────────────────────────┐
│                    COMMUNICATION FLOW                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Browser (Port 5050)                                     │
│       ↓ HTTP POST /send_command                          │
│       ↓                                                   │
│  Flask App (app.py)                                      │
│       ↓ MQTT Publish                                     │
│       ↓                                                   │
│  Mosquitto Broker (Port 1883)                            │
│       ↓ Publish to topic: "robot/control"               │
│       ↓                                                   │
│  ESP32 MQTT Client                                       │
│       ↓ Callback receives JSON                           │
│       ↓ Parse command & speed                            │
│       ↓                                                   │
│  BTS7960 Motor Driver                                    │
│       ↓ analogWrite() PWM control                        │
│       ↓                                                   │
│  DC Motors (wheels)                                      │
│       ↓ Physical movement                                │
│       ↓                                                   │
│  Robot moves!                                             │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## Files Created

1. **mqtt_monitor.py** - Monitor MQTT messages in real-time
   - Location: `/home/navis/NAVIS/Base/Remote_Control/mqtt_monitor.py`
   - Usage: `python3 mqtt_monitor.py`

2. **mqtt_troubleshooter.py** - Diagnose connectivity issues
   - Location: `/home/navis/NAVIS/mqtt_troubleshooter.py`
   - Usage: `python3 mqtt_troubleshooter.py`

3. **README.md** - Updated with MQTT configuration details

---

**Setup completed**: 28 January 2026 14:25 IST

All systems ready for ESP32 connection!
