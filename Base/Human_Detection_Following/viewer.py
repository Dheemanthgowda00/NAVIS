#!/usr/bin/env python3
"""
Real-time pose detection viewer for debugging
Shows skeleton, zones, and depth visualization without web server
"""

import cv2
import mediapipe as mp
import numpy as np

# Configuration
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
CENTER_TOLERANCE = 0.15
DEPTH_THRESHOLD_NEAR = 0.3
DEPTH_THRESHOLD_FAR = 0.7

# MediaPipe
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils
holistic = mp_holistic.Holistic(
    static_image_mode=False,
    model_complexity=1,
    smooth_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def analyze_pose(frame, results):
    """Analyze person position and depth"""
    h, w, c = frame.shape
    
    if not results.pose_landmarks:
        return None, None, None
    
    landmarks = results.pose_landmarks.landmark
    nose = landmarks[0]
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]
    
    if nose.visibility < 0.5:
        return None, None, None
    
    # Position
    nose_x_norm = nose.x
    if nose_x_norm < (0.5 - CENTER_TOLERANCE):
        position = 'LEFT'
    elif nose_x_norm > (0.5 + CENTER_TOLERANCE):
        position = 'RIGHT'
    else:
        position = 'CENTER'
    
    # Depth
    if left_shoulder.visibility > 0.5 and right_shoulder.visibility > 0.5:
        shoulder_width = abs(right_shoulder.x - left_shoulder.x)
        shoulder_width_norm = shoulder_width
    else:
        shoulder_width_norm = 0.3
    
    depth_percent = 1.0 - np.clip(shoulder_width_norm, 0, 1)
    
    if depth_percent < DEPTH_THRESHOLD_NEAR:
        depth = 'NEAR'
    elif depth_percent > DEPTH_THRESHOLD_FAR:
        depth = 'FAR'
    else:
        depth = 'MEDIUM'
    
    return position, depth, depth_percent

def main():
    """Main debugging viewer"""
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    
    print("📷 Human Detection Viewer")
    print("-" * 50)
    print("Press 'q' to quit")
    print("Press 'r' to reset camera")
    print("-" * 50)
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        frame_count += 1
        
        # Process
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(frame_rgb)
        
        # Draw skeleton
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_holistic.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
            )
        
        # Draw zones
        zone_w = w // 3
        cv2.rectangle(frame, (0, 0), (zone_w, h), (100, 100, 100), 2)
        cv2.putText(frame, "LEFT", (zone_w//2 - 30, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)
        
        cv2.rectangle(frame, (zone_w, 0), (2*zone_w, h), (100, 100, 100), 2)
        cv2.putText(frame, "CENTER", (zone_w + zone_w//2 - 50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)
        
        cv2.rectangle(frame, (2*zone_w, 0), (w, h), (100, 100, 100), 2)
        cv2.putText(frame, "RIGHT", (2*zone_w + zone_w//2 - 40, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)
        
        # Center marker
        cv2.circle(frame, (w//2, h//2), 5, (0, 255, 255), -1)
        
        # Analyze
        position, depth, depth_percent = analyze_pose(frame, results)
        
        # Draw info
        if position is not None:
            y = 30
            cv2.putText(frame, f"Position: {position}", (10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Depth: {depth}", (10, y+30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Distance: {depth_percent*100:.1f}%", (10, y+60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Draw depth bar
            bar_x = w - 100
            bar_y = 30
            bar_h = 200
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x+50, bar_y+bar_h), (100, 100, 100), 2)
            
            # Fill percentage
            fill_h = int(bar_h * depth_percent)
            cv2.rectangle(frame, (bar_x, bar_y+bar_h-fill_h), (bar_x+50, bar_y+bar_h), (0, 255, 0), -1)
            
            # Thresholds
            cv2.line(frame, (bar_x, int(bar_y+bar_h*(1-DEPTH_THRESHOLD_NEAR))), 
                    (bar_x+50, int(bar_y+bar_h*(1-DEPTH_THRESHOLD_NEAR))), (0, 0, 255), 2)
            cv2.line(frame, (bar_x, int(bar_y+bar_h*(1-DEPTH_THRESHOLD_FAR))), 
                    (bar_x+50, int(bar_y+bar_h*(1-DEPTH_THRESHOLD_FAR))), (255, 0, 0), 2)
        else:
            cv2.putText(frame, "NO PERSON DETECTED", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.putText(frame, f"Frame: {frame_count}", (w-150, h-20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Show
        cv2.imshow('Human Detection Viewer', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    
    cap.release()
    cv2.destroyAllWindows()
    print("✓ Viewer closed")

if __name__ == "__main__":
    main()
