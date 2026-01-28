"""
Human Detection and Following Module
Uses MediaPipe to detect person position and depth, sends MQTT commands to ESP32
"""

from flask import Flask, render_template, Response, jsonify, request
import cv2
import mediapipe as mp
import paho.mqtt.client as mqtt
import numpy as np
import json
from threading import Lock
import time

app = Flask(__name__)

# --- Configuration ---
FRAME_WIDTH = 320              # Reduced for faster processing
FRAME_HEIGHT = 240             # Reduced for faster processing
FPS = 30
FRAME_SKIP = 2                 # Process every 2nd frame
JPEG_QUALITY = 50              # Lower quality = faster compression

# --- MQTT Setup ---
MQTT_BROKER = "localhost"
MQTT_TOPIC = "robot/control"
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# --- Position Detection Parameters ---
CENTER_TOLERANCE = 0.15  # 15% tolerance for center detection
DEPTH_THRESHOLD_NEAR = 0.3    # Person closer than 30% frame height
DEPTH_THRESHOLD_FAR = 0.7     # Person farther than 70% frame height

# --- State Management ---
state_lock = Lock()
CURRENT_SPEED = 200  # Default speed (0-255)
current_state = {
    'person_detected': False,
    'position': 'center',  # left, center, right
    'depth': 'medium',     # near, medium, far
    'distance_percent': 0,
    'command': 'S',        # Current MQTT command
    'speed': CURRENT_SPEED,
    'fps': 0,
    'frame_count': 0,
    'person_x': 0,
    'person_y': 0
}

# --- MediaPipe Setup ---
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils
holistic = mp_holistic.Holistic(
    static_image_mode=False,
    model_complexity=0,              # Lighter model for speed
    smooth_landmarks=True,
    min_detection_confidence=0.4,    # Lower threshold for speed
    min_tracking_confidence=0.4
)

def send_mqtt_command(cmd, speed=None):
    """Send command to MQTT broker"""
    global CURRENT_SPEED
    try:
        if speed is None:
            speed = CURRENT_SPEED
        payload = json.dumps({"cmd": cmd, "speed": int(speed)})
        client.publish(MQTT_TOPIC, payload)
        with state_lock:
            current_state['command'] = cmd
            current_state['speed'] = int(speed)
        return True
    except Exception as e:
        print(f"MQTT Error: {e}")
        return False

def analyze_pose(frame, results):
    """
    Analyze person position and depth from pose landmarks
    Returns: (position, depth_percent, person_x, person_y)
    """
    h, w, c = frame.shape
    
    if not results.pose_landmarks:
        return None, None, None, None
    
    # Get key landmarks for position analysis
    landmarks = results.pose_landmarks.landmark
    
    # Use nose (landmark 0) and shoulders for position/depth detection
    nose = landmarks[0]
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]
    
    # Check confidence
    if nose.visibility < 0.5:
        return None, None, None, None
    
    # --- Calculate Horizontal Position (Left/Center/Right) ---
    # Normalize nose x position to frame width
    nose_x_norm = nose.x  # 0 = left, 1 = right
    
    # Determine position based on normalized x coordinate
    if nose_x_norm < (0.5 - CENTER_TOLERANCE):
        position = 'left'
    elif nose_x_norm > (0.5 + CENTER_TOLERANCE):
        position = 'right'
    else:
        position = 'center'
    
    # --- Calculate Depth (Near/Medium/Far) ---
    # Use shoulder width as proxy for distance
    # Closer person = larger shoulder width in frame
    if left_shoulder.visibility > 0.5 and right_shoulder.visibility > 0.5:
        shoulder_width = abs(right_shoulder.x - left_shoulder.x)
        # Normalize shoulder width relative to frame width
        shoulder_width_norm = shoulder_width
    else:
        shoulder_width_norm = 0.3  # Default estimation
    
    # Reverse: larger width = closer (smaller z)
    # Map to 0-1 range where 0 = very close, 1 = very far
    depth_percent = 1.0 - np.clip(shoulder_width_norm, 0, 1)
    
    if depth_percent < DEPTH_THRESHOLD_NEAR:
        depth = 'near'
    elif depth_percent > DEPTH_THRESHOLD_FAR:
        depth = 'far'
    else:
        depth = 'medium'
    
    # --- Calculate Person Center Position in Pixels ---
    person_x = int(nose.x * w)
    person_y = int(nose.y * h)
    
    return position, depth, depth_percent, (person_x, person_y)

def generate_frames():
    """Generate video frames with pose detection"""
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, FPS)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer for lower latency
    
    last_command = None
    frame_count = 0
    frame_skip_count = 0
    start_time = time.time()
    last_position = 'center'
    last_depth = 'medium'
    last_depth_percent = 0.5
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        frame_skip_count += 1
        
        # Flip for webcam (mirror effect)
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        
        # Process detection every N frames
        if frame_skip_count >= FRAME_SKIP:
            frame_skip_count = 0
            
            # Convert to RGB for MediaPipe
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Run pose detection
            results = holistic.process(frame_rgb)
            
            # Analyze pose
            position, depth, depth_percent, person_pos = analyze_pose(frame, results)
            
            # Update state if detection successful
            if position is not None:
                last_position = position
                last_depth = depth
                last_depth_percent = depth_percent
        else:
            # Use previous results for skipped frames
            position = last_position
            depth = last_depth
            depth_percent = last_depth_percent
            person_pos = None
            results = None
        
        # --- Decision Logic for MQTT Commands ---
        if position is not None:
            # Person detected
            with state_lock:
                current_state['person_detected'] = True
                current_state['position'] = position
                current_state['depth'] = depth
                current_state['distance_percent'] = depth_percent
                if person_pos:
                    current_state['person_x'] = person_pos[0]
                    current_state['person_y'] = person_pos[1]
            
            # Send appropriate command based on position and depth
            if depth == 'far':
                command = 'F'
            elif depth == 'near':
                command = 'B'
            else:
                if position == 'left':
                    command = 'L'
                elif position == 'right':
                    command = 'R'
                else:
                    command = 'S'
            
            # Send command if it changed
            if command != last_command:
                send_mqtt_command(command)
                last_command = command
        else:
            # No person detected
            with state_lock:
                current_state['person_detected'] = False
            
            if last_command != 'S':
                send_mqtt_command('S')
                last_command = 'S'
        
        # --- Draw Visualization (only for display) ---
        # Draw pose landmarks only if we processed this frame
        if results and results.pose_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_holistic.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
                mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=1)
            )
        
        # --- Draw Status Information (minimal) ---
        status_text = []
        if position is not None:
            status_text.append(f"Pos: {position.upper()}")
            status_text.append(f"Depth: {depth.upper()}")
            status_text.append(f"Dist: {depth_percent*100:.0f}%")
            status_text.append(f"Cmd: {last_command}")
        else:
            status_text.append("NO PERSON")
        
        # Draw text on frame (smaller font)
        y_offset = 20
        for i, text in enumerate(status_text):
            cv2.putText(frame, text, (5, y_offset + i*15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        # Draw frame info
        fps = frame_count / (time.time() - start_time) if time.time() - start_time > 0 else 0
        cv2.putText(frame, f"FPS: {fps:.1f}", (w-100, 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
        
        # Draw center point and detection zones
        cv2.circle(frame, (w//2, h//2), 3, (0, 255, 255), -1)
        
        # Draw left/center/right zones (thinner lines)
        zone_w = w // 3
        cv2.rectangle(frame, (0, 0), (zone_w, h), (80, 80, 80), 1)
        cv2.rectangle(frame, (zone_w, 0), (2*zone_w, h), (80, 80, 80), 1)
        cv2.rectangle(frame, (2*zone_w, 0), (w, h), (80, 80, 80), 1)
        
        # Encode frame to JPEG with lower quality
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        frame_bytes = buffer.tobytes()
        
        # Update FPS
        with state_lock:
            current_state['fps'] = fps
            current_state['frame_count'] = frame_count
        
        # Yield frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    cap.release()

@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Stream video frames"""
    return Response(generate_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def get_status():
    """Get current detection status"""
    with state_lock:
        return jsonify(current_state)

@app.route('/set_threshold', methods=['POST'])
def set_threshold():
    """Update depth thresholds"""
    global DEPTH_THRESHOLD_NEAR, DEPTH_THRESHOLD_FAR
    try:
        data = request.json
        DEPTH_THRESHOLD_NEAR = data.get('near_threshold', DEPTH_THRESHOLD_NEAR)
        DEPTH_THRESHOLD_FAR = data.get('far_threshold', DEPTH_THRESHOLD_FAR)
        return jsonify({
            'status': 'updated',
            'near': DEPTH_THRESHOLD_NEAR,
            'far': DEPTH_THRESHOLD_FAR
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/set_speed', methods=['POST'])
def set_speed():
    """Update motor speed"""
    global CURRENT_SPEED
    try:
        data = request.json
        speed = data.get('speed', CURRENT_SPEED)
        CURRENT_SPEED = max(0, min(255, int(speed)))  # Clamp to 0-255
        with state_lock:
            current_state['speed'] = CURRENT_SPEED
        return jsonify({
            'status': 'updated',
            'speed': CURRENT_SPEED
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    # Connect to MQTT
    try:
        client.connect(MQTT_BROKER, 1883, 60)
        client.loop_start()
        print("✅ MQTT Connected")
    except Exception as e:
        print(f"❌ MQTT Connection Failed: {e}")
    
    # Start Flask
    print("🎥 Human Detection Following - Starting on http://0.0.0.0:5051")
    app.run(host='0.0.0.0', port=5051, debug=False, threaded=True)
