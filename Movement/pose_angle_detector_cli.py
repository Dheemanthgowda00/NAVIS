"""
Pose Angle Detector using MediaPipe (CLI Version - No GUI)
Detects bicep curls (both arms) and head movement
Maps movements to 0-180 degree angles
User can select which movement to track via keyboard input
"""

import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import sys

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

class PoseAngleDetectorCLI:
    def __init__(self):
        # Configuration
        self.SMOOTHING_FRAMES = 5
        self.angle_history_left = deque(maxlen=self.SMOOTHING_FRAMES)
        self.angle_history_right = deque(maxlen=self.SMOOTHING_FRAMES)
        self.angle_history_head = deque(maxlen=self.SMOOTHING_FRAMES)
        
        # State
        self.selected_joint = "left_bicep"  # Options: left_bicep, right_bicep, head
        self.current_angle = 0
        self.cap = None
        self.running = True
        
        # Print menu
        self.print_menu()
        
    def print_menu(self):
        """Print control menu"""
        print("\n" + "="*60)
        print("  POSE ANGLE DETECTOR - MediaPipe")
        print("="*60)
        print("\nKEYBOARD CONTROLS:")
        print("  1 = Select LEFT BICEP")
        print("  2 = Select RIGHT BICEP")
        print("  3 = Select HEAD MOVEMENT")
        print("  q = Quit")
        print("\nCURRENT SELECTION: LEFT BICEP")
        print("="*60 + "\n")
        
    def start_camera(self):
        """Start camera capture"""
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        if not self.cap.isOpened():
            print("❌ Error: Could not open camera")
            sys.exit(1)
        
        self.video_loop()
        
    def calculate_angle(self, point1, point2, point3):
        """
        Calculate angle between three points
        """
        a = np.array([point1.x - point2.x, point1.y - point2.y])
        b = np.array([point3.x - point2.x, point3.y - point2.y])
        
        cos_angle = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-6)
        cos_angle = np.clip(cos_angle, -1, 1)
        angle = np.arccos(cos_angle)
        angle_deg = np.degrees(angle)
        
        return angle_deg
    
    def calculate_head_angle(self, landmarks, face_landmarks=None):
        """Calculate head movement angle"""
        # If face landmarks available, use eye landmarks for better accuracy
        if face_landmarks is not None and len(face_landmarks.landmark) > 263:
            left_eye = face_landmarks.landmark[33]
            right_eye = face_landmarks.landmark[263]
            eye_distance = abs(left_eye.y - right_eye.y)
            head_angle = np.clip(eye_distance * 180, 0, 180)
        else:
            # Fallback: Use shoulder landmarks from pose for head estimation
            # Calculate nose position relative to shoulders for head tilt
            nose = landmarks[0]
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            
            shoulder_center_x = (left_shoulder.x + right_shoulder.x) / 2
            shoulder_center_y = (left_shoulder.y + right_shoulder.y) / 2
            
            # Calculate angle from shoulder center to nose
            dx = nose.x - shoulder_center_x
            dy = nose.y - shoulder_center_y
            
            # Map to 0-180 degrees
            head_angle = np.degrees(np.arctan2(dy, dx))
            head_angle = np.clip(abs(head_angle) * 1.0, 0, 180)
        
        return head_angle
    
    def smooth_angle(self, new_angle, history):
        """Smooth angle using moving average"""
        history.append(new_angle)
        return sum(history) / len(history)
    
    def video_loop(self):
        """Main video processing loop"""
        frame_count = 0
        
        print("📹 Camera started. Press keys to select movement...")
        print("   'q' to quit\n")
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            h, w, c = frame.shape
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = holistic.process(frame_rgb)
            
            left_bicep_angle = None
            right_bicep_angle = None
            head_angle = None
            person_detected = False
            
            # Process pose
            if results.pose_landmarks:
                person_detected = True
                landmarks = results.pose_landmarks.landmark
                
                # Left Bicep: shoulder (11) -> elbow (13) -> wrist (15)
                if landmarks[11].visibility > 0.7 and landmarks[13].visibility > 0.7 and landmarks[15].visibility > 0.7:
                    left_bicep_angle = self.calculate_angle(landmarks[11], landmarks[13], landmarks[15])
                    left_bicep_angle = self.smooth_angle(left_bicep_angle, self.angle_history_left)
                
                # Right Bicep: shoulder (12) -> elbow (14) -> wrist (16)
                if landmarks[12].visibility > 0.7 and landmarks[14].visibility > 0.7 and landmarks[16].visibility > 0.7:
                    right_bicep_angle = self.calculate_angle(landmarks[12], landmarks[14], landmarks[16])
                    right_bicep_angle = self.smooth_angle(right_bicep_angle, self.angle_history_right)
                
                # Head movement
                if landmarks[0].visibility > 0.7:
                    head_angle = self.calculate_head_angle(landmarks, results.face_landmarks)
                    head_angle = self.smooth_angle(head_angle, self.angle_history_head)
                
                # Draw pose landmarks
                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_holistic.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=1)
                )
                
                # Draw angle annotations
                if left_bicep_angle is not None:
                    elbow_left = landmarks[13]
                    cv2.putText(frame, f"L: {left_bicep_angle:.1f}°", 
                               (int(elbow_left.x * w) - 50, int(elbow_left.y * h)), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 255), 2)
                
                if right_bicep_angle is not None:
                    elbow_right = landmarks[14]
                    cv2.putText(frame, f"R: {right_bicep_angle:.1f}°", 
                               (int(elbow_right.x * w) + 20, int(elbow_right.y * h)), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 255), 2)
                
                if head_angle is not None:
                    nose = landmarks[0]
                    cv2.putText(frame, f"H: {head_angle:.1f}°", 
                               (int(nose.x * w), int(nose.y * h) - 20), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 100), 2)
            
            # Select current angle based on selection
            if self.selected_joint == "left_bicep" and left_bicep_angle is not None:
                self.current_angle = left_bicep_angle
                color = (100, 100, 255)
                label = "LEFT BICEP"
            elif self.selected_joint == "right_bicep" and right_bicep_angle is not None:
                self.current_angle = right_bicep_angle
                color = (100, 255, 255)
                label = "RIGHT BICEP"
            elif self.selected_joint == "head" and head_angle is not None:
                self.current_angle = head_angle
                color = (255, 255, 100)
                label = "HEAD MOVEMENT"
            else:
                self.current_angle = 0
                color = (200, 200, 200)
                label = self.selected_joint.upper()
            
            # Draw main angle display
            cv2.putText(frame, f"{label}: {self.current_angle:.1f}°", 
                       (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
            
            # Draw status
            status_text = f"Person: {'YES' if person_detected else 'NO'}"
            status_color = (0, 255, 0) if person_detected else (0, 0, 255)
            cv2.putText(frame, status_text, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
            
            # Draw instructions
            cv2.putText(frame, "Press: 1=Left 2=Right 3=Head | q=Quit", 
                       (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            
            # Display frame
            cv2.imshow("Pose Angle Detector", frame)
            
            # Print status
            frame_count += 1
            if frame_count % 30 == 0:  # Print every 30 frames (~1 second at 30fps)
                print(f"\r[Frame {frame_count}] {label}: {self.current_angle:.1f}° | "
                      f"Left: {left_bicep_angle:.1f if left_bicep_angle else 'N/A'}° | "
                      f"Right: {right_bicep_angle:.1f if right_bicep_angle else 'N/A'}° | "
                      f"Head: {head_angle:.1f if head_angle else 'N/A'}°", end="", flush=True)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\n✓ Quitting...")
                self.running = False
            elif key == ord('1'):
                self.selected_joint = "left_bicep"
                print("\n[*] Selected: LEFT BICEP")
            elif key == ord('2'):
                self.selected_joint = "right_bicep"
                print("\n[*] Selected: RIGHT BICEP")
            elif key == ord('3'):
                self.selected_joint = "head"
                print("\n[*] Selected: HEAD MOVEMENT")
        
        self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("\n✓ Camera closed. Goodbye!")

if __name__ == "__main__":
    detector = PoseAngleDetectorCLI()
    detector.start_camera()
