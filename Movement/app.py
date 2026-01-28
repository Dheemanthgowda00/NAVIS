"""
Pose Angle Detector with Flask Web Interface
Detects bicep curls (both arms) and head movement
Maps movements to 0-180 degree angles
Accessible via web browser - no display needed
"""

from flask import Flask, render_template, Response, jsonify
import cv2
import mediapipe as mp
import numpy as np
from collections import deque
from threading import Lock
import json

app = Flask(__name__)

# MediaPipe setup
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils
holistic = mp_holistic.Holistic(
    static_image_mode=False,
    model_complexity=1,
    smooth_landmarks=True,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Configuration
FRAME_WIDTH = 320
FRAME_HEIGHT = 240
FPS = 30
FRAME_SKIP = 2
JPEG_QUALITY = 50
SMOOTHING_FRAMES = 5

# State
state_lock = Lock()
SELECTED_JOINT = "left_bicep"  # left_bicep, right_bicep, head
current_state = {
    'person_detected': False,
    'left_bicep_angle': 0,
    'right_bicep_angle': 0,
    'head_angle': 0,
    'selected_joint': 'left_bicep',
    'current_angle': 0,
    'fps': 0,
    'frame_count': 0
}

# Angle histories
angle_history_left = deque(maxlen=SMOOTHING_FRAMES)
angle_history_right = deque(maxlen=SMOOTHING_FRAMES)
angle_history_head = deque(maxlen=SMOOTHING_FRAMES)

def calculate_angle(point1, point2, point3):
    """Calculate angle between three points"""
    a = np.array([point1.x - point2.x, point1.y - point2.y])
    b = np.array([point3.x - point2.x, point3.y - point2.y])
    
    cos_angle = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-6)
    cos_angle = np.clip(cos_angle, -1, 1)
    angle = np.arccos(cos_angle)
    angle_deg = np.degrees(angle)
    
    return angle_deg

def calculate_head_angle(landmarks, face_landmarks=None):
    """Calculate head movement angle"""
    # If face landmarks available, use eye landmarks
    if face_landmarks is not None and len(face_landmarks.landmark) > 263:
        left_eye = face_landmarks.landmark[33]
        right_eye = face_landmarks.landmark[263]
        eye_distance = abs(left_eye.y - right_eye.y)
        head_angle = np.clip(eye_distance * 180, 0, 180)
    else:
        # Fallback: Use shoulder landmarks from pose
        nose = landmarks[0]
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        
        shoulder_center_x = (left_shoulder.x + right_shoulder.x) / 2
        shoulder_center_y = (left_shoulder.y + right_shoulder.y) / 2
        
        dx = nose.x - shoulder_center_x
        dy = nose.y - shoulder_center_y
        
        head_angle = np.degrees(np.arctan2(dy, dx))
        head_angle = np.clip(abs(head_angle) * 1.0, 0, 180)
    
    return head_angle

def smooth_angle(new_angle, history):
    """Smooth angle using moving average"""
    history.append(new_angle)
    return sum(history) / len(history)

def generate_frames():
    """Generate video frames with pose detection"""
    global SELECTED_JOINT
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, FPS)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    frame_count = 0
    frame_skip_count = 0
    import time
    start_time = time.time()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        frame_skip_count += 1
        
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        
        left_bicep_angle = None
        right_bicep_angle = None
        head_angle = None
        person_detected = False
        
        # Process detection every N frames
        if frame_skip_count >= FRAME_SKIP:
            frame_skip_count = 0
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = holistic.process(frame_rgb)
            
            if results.pose_landmarks:
                person_detected = True
                landmarks = results.pose_landmarks.landmark
                
                # Left Bicep
                if landmarks[11].visibility > 0.7 and landmarks[13].visibility > 0.7 and landmarks[15].visibility > 0.7:
                    left_bicep_angle = calculate_angle(landmarks[11], landmarks[13], landmarks[15])
                    left_bicep_angle = smooth_angle(left_bicep_angle, angle_history_left)
                
                # Right Bicep
                if landmarks[12].visibility > 0.7 and landmarks[14].visibility > 0.7 and landmarks[16].visibility > 0.7:
                    right_bicep_angle = calculate_angle(landmarks[12], landmarks[14], landmarks[16])
                    right_bicep_angle = smooth_angle(right_bicep_angle, angle_history_right)
                
                # Head
                if landmarks[0].visibility > 0.7:
                    head_angle = calculate_head_angle(landmarks, results.face_landmarks)
                    head_angle = smooth_angle(head_angle, angle_history_head)
                
                # Draw landmarks
                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_holistic.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=1)
                )
        
        # Draw current angle
        current_angle = 0
        label = "—"
        color = (200, 200, 200)
        
        if SELECTED_JOINT == "left_bicep" and left_bicep_angle is not None:
            current_angle = left_bicep_angle
            label = "LEFT BICEP"
            color = (100, 100, 255)
        elif SELECTED_JOINT == "right_bicep" and right_bicep_angle is not None:
            current_angle = right_bicep_angle
            label = "RIGHT BICEP"
            color = (100, 255, 255)
        elif SELECTED_JOINT == "head" and head_angle is not None:
            current_angle = head_angle
            label = "HEAD"
            color = (255, 255, 100)
        
        cv2.putText(frame, f"{label}: {current_angle:.1f}°", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Draw status
        status_text = f"Person: {'YES' if person_detected else 'NO'}"
        status_color = (0, 255, 0) if person_detected else (0, 0, 255)
        cv2.putText(frame, status_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        # Update state
        with state_lock:
            current_state['person_detected'] = person_detected
            current_state['left_bicep_angle'] = left_bicep_angle if left_bicep_angle else 0
            current_state['right_bicep_angle'] = right_bicep_angle if right_bicep_angle else 0
            current_state['head_angle'] = head_angle if head_angle else 0
            current_state['current_angle'] = current_angle
            current_state['selected_joint'] = SELECTED_JOINT
            current_state['fps'] = frame_count / (time.time() - start_time) if time.time() - start_time > 0 else 0
            current_state['frame_count'] = frame_count
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    cap.release()

@app.route('/')
def index():
    """Serve main page"""
    return render_template('index_movement.html')

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

@app.route('/select_joint/<joint>')
def select_joint(joint):
    """Select joint to track"""
    global SELECTED_JOINT
    if joint in ['left_bicep', 'right_bicep', 'head']:
        SELECTED_JOINT = joint
        with state_lock:
            current_state['selected_joint'] = joint
        return jsonify({'status': 'ok', 'selected': joint})
    return jsonify({'status': 'error', 'message': 'Invalid joint'})

if __name__ == '__main__':
    print("🎥 Movement Angle Detector - Starting on http://0.0.0.0:5052")
    app.run(host='0.0.0.0', port=5052, debug=False, threaded=True)
