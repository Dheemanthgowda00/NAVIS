# NAVIS Face Recognition - Auto-Start Setup

## Overview
The Face Recognition service is now configured to:
- ✅ Auto-start automatically when Raspberry Pi boots
- ✅ Accessible via http://navis.local:5000 on any device on the same network
- ✅ Run as a systemd service with auto-restart on failure

## Access Information

### From Mobile/Computer on Same Network:
```
http://navis.local:5000
```

### Direct IP Access (if mDNS doesn't work):
```
http://192.168.0.199:5000
```

## System Service Details

### Service File Location:
```
/etc/systemd/system/navis-face-recognition.service
```

### Service Commands:

**Check Status:**
```bash
sudo systemctl status navis-face-recognition.service
```

**Start Service:**
```bash
sudo systemctl start navis-face-recognition.service
```

**Stop Service:**
```bash
sudo systemctl stop navis-face-recognition.service
```

**Restart Service:**
```bash
sudo systemctl restart navis-face-recognition.service
```

**View Logs:**
```bash
sudo journalctl -u navis-face-recognition.service -n 50 -f
```

**Enable on Boot:**
```bash
sudo systemctl enable navis-face-recognition.service
```

**Disable Auto-Start:**
```bash
sudo systemctl disable navis-face-recognition.service
```

## Web Interface

### Home Page (http://navis.local:5000)
- Upload a reference image
- Enter the person's name
- Click "Start Recognition" to begin live detection

### Live Stream (http://navis.local:5000/live)
- Shows real-time video with face detection
- Green boxes = Recognized faces
- Red boxes = Unknown faces
- Click "Stop" to return to upload page

## Testing Procedure

1. **Reboot Raspberry Pi:**
   ```bash
   sudo reboot
   ```

2. **Wait 30-60 seconds for the service to start**

3. **On Your Mobile/Computer:**
   - Connect to the same WiFi network as Raspberry Pi
   - Open browser
   - Navigate to `http://navis.local:5000`
   - You should see the Face Recognition upload interface

4. **Upload a Test Image:**
   - Take a photo of someone
   - Upload with their name
   - Click "Start Recognition"

5. **View Live Stream:**
   - Face will be detected and labeled
   - Green box = Recognized
   - Red box = Unknown

## Performance

- Frame Width: 640px (from 1280px)
- Frame Height: 480px (from 720px)
- Processing: Every 2nd frame (frame skipping)
- Detection Model: HOG (fast)
- Tolerance: 0.6 (confidence threshold)
- JPEG Quality: 60 (optimized)
- Latency: ~200-300ms (optimized for Raspberry Pi 4B)

## Network Settings

### mDNS (Bonjour/Avahi)
- Service: avahi-daemon
- Status: ✅ Running
- Hostname: navis.local
- The Raspberry Pi broadcasts itself as "navis.local" on the network

### Application Server
- Framework: Flask
- Port: 5000
- Bind: 0.0.0.0 (accessible from all network interfaces)
- Debug: Disabled (production mode)

## Troubleshooting

### Service Won't Start
```bash
# Check if port 5000 is in use
lsof -i :5000

# Kill any existing process
sudo pkill -f "python app.py"

# Restart service
sudo systemctl restart navis-face-recognition.service
```

### Can't Access navis.local
```bash
# Try direct IP instead
http://192.168.0.199:5000

# Check if host can be resolved
ping navis.local

# Restart avahi-daemon
sudo systemctl restart avahi-daemon.service
```

### Slow Performance
- Check CPU usage: `top`
- Check system logs: `sudo journalctl -u navis-face-recognition.service -f`
- Reduce JPEG_QUALITY further if needed
- Increase FRAME_SKIP to process fewer frames

### No Faces Being Detected
- Ensure good lighting
- Upload clearer reference images
- Check tolerance value (currently 0.6)
- Try adjusting confidence thresholds in app.py

## Production Notes

- ⚠️ Flask debug mode is DISABLED for security
- Auto-restart is enabled (restarts on failure)
- Service runs with proper permissions
- Logs are stored in journalctl (system logs)
- No data is persisted except uploaded images in static/

## Next Steps

1. Test by rebooting the Raspberry Pi
2. Access from mobile at http://navis.local:5000
3. Upload test images and verify recognition
4. Monitor logs with: `sudo journalctl -u navis-face-recognition.service -f`
