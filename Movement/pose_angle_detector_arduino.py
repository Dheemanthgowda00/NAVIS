"""
Pose Angle Detector with Arduino PyFirmata Integration
Detects bicep curls (both arms) and head movement
Maps movements to 0-180 degree angles and sends to Arduino Mega via PWM
User can select which movement to track via GUI buttons
"""

import cv2
import mediapipe as mp
import numpy as np
import sys
from collections import deque
import serial
import time

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    from PIL import Image, ImageTk
    import threading
    TKINTER_AVAILABLE = True
except ImportError:
    print("❌ Error: tkinter not installed on this system")
    print("   On Raspberry Pi/Linux, tkinter must be installed separately.")
    print("\n   Solution 1: Use CLI version without Arduino")
    print("   $ python pose_angle_detector_cli.py")
    print("\n   Solution 2: Install tkinter")
    print("   $ sudo apt-get install python3-tk")
    sys.exit(1)
    TKINTER_AVAILABLE = False

try:
    from PyMata4.pymata4 import PyMata4
except ImportError:
    print("PyMata4 not installed. Run: pip install PyMata4")
    PyMata4 = None

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

class PoseAngleDetectorArduino:
    def __init__(self, root):
        self.root = root
        self.root.title("Pose Angle Detector - Arduino Control")
        self.root.geometry("1400x900")
        
        # Configuration
        self.SMOOTHING_FRAMES = 5
        self.angle_history_left = deque(maxlen=self.SMOOTHING_FRAMES)
        self.angle_history_right = deque(maxlen=self.SMOOTHING_FRAMES)
        self.angle_history_head = deque(maxlen=self.SMOOTHING_FRAMES)
        
        # Arduino setup
        self.board = None
        self.pwm_pin_left = 3    # Arduino Mega PWM pin for left bicep
        self.pwm_pin_right = 5   # Arduino Mega PWM pin for right bicep
        self.pwm_pin_head = 6    # Arduino Mega PWM pin for head
        self.arduino_connected = False
        
        # State
        self.selected_joint = "left_bicep"
        self.current_angle = 0
        self.cap = None
        self.running = False
        
        # UI Setup
        self.setup_ui()
        self.start_camera()
        
    def setup_ui(self):
        """Setup tkinter UI"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Video display area
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(left_frame, text="Live Camera Feed", font=("Arial", 14, "bold")).pack()
        
        self.canvas = tk.Canvas(left_frame, bg="black", width=640, height=480)
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Right panel
        right_frame = ttk.Frame(main_frame, width=450)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        
        # Arduino Connection Section
        arduino_frame = ttk.LabelFrame(right_frame, text="Arduino Connection", padding=15)
        arduino_frame.pack(fill=tk.X, pady=10)
        
        self.connect_btn = tk.Button(
            arduino_frame,
            text="Connect to Arduino Mega",
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            command=self.connect_arduino,
            cursor="hand2",
            height=2
        )
        self.connect_btn.pack(fill=tk.X, pady=5)
        
        self.arduino_status = tk.Label(
            arduino_frame,
            text="Status: Disconnected",
            font=("Arial", 10),
            fg="#FF0000"
        )
        self.arduino_status.pack(anchor=tk.W)
        
        self.port_label = tk.Label(
            arduino_frame,
            text="Port: Auto-detect (COM3-COM10)",
            font=("Arial", 9),
            fg="#666"
        )
        self.port_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Movement Selection
        button_frame = ttk.LabelFrame(right_frame, text="Select Movement", padding=15)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.btn_left = tk.Button(
            button_frame,
            text="LEFT BICEP (PWM Pin 3)",
            font=("Arial", 11, "bold"),
            bg="#FF6B6B" if self.selected_joint == "left_bicep" else "#CCCCCC",
            fg="white",
            command=lambda: self.select_joint("left_bicep"),
            height=2,
            cursor="hand2"
        )
        self.btn_left.pack(fill=tk.X, pady=8)
        
        self.btn_right = tk.Button(
            button_frame,
            text="RIGHT BICEP (PWM Pin 5)",
            font=("Arial", 11, "bold"),
            bg="#4ECDC4" if self.selected_joint == "right_bicep" else "#CCCCCC",
            fg="white",
            command=lambda: self.select_joint("right_bicep"),
            height=2,
            cursor="hand2"
        )
        self.btn_right.pack(fill=tk.X, pady=8)
        
        self.btn_head = tk.Button(
            button_frame,
            text="HEAD MOVEMENT (PWM Pin 6)",
            font=("Arial", 11, "bold"),
            bg="#FFD93D" if self.selected_joint == "head" else "#CCCCCC",
            fg="black",
            command=lambda: self.select_joint("head"),
            height=2,
            cursor="hand2"
        )
        self.btn_head.pack(fill=tk.X, pady=8)
        
        # Angle Display
        display_frame = ttk.LabelFrame(right_frame, text="Current Angle", padding=20)
        display_frame.pack(fill=tk.X, pady=10)
        
        self.angle_label = tk.Label(
            display_frame,
            text="0°",
            font=("Arial", 48, "bold"),
            fg="#00FF00",
            bg="black"
        )
        self.angle_label.pack(pady=10)
        
        self.angle_range_label = tk.Label(
            display_frame,
            text="Range: 0° - 180°",
            font=("Arial", 10),
            fg="#666"
        )
        self.angle_range_label.pack()
        
        # PWM Signal Display
        self.pwm_label = tk.Label(
            display_frame,
            text="PWM Signal: 0/255",
            font=("Arial", 12, "bold"),
            fg="#00FFFF"
        )
        self.pwm_label.pack()
        
        self.progress = ttk.Progressbar(
            display_frame,
            orient=tk.HORIZONTAL,
            length=300,
            mode='determinate',
            maximum=180
        )
        self.progress.pack(fill=tk.X, pady=10)
        
        # Status Frame
        status_frame = ttk.LabelFrame(right_frame, text="Status Information", padding=15)
        status_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.left_label = tk.Label(status_frame, text="Left Bicep: —", font=("Arial", 10), fg="#FF6B6B")
        self.left_label.pack(anchor=tk.W, pady=5)
        
        self.right_label = tk.Label(status_frame, text="Right Bicep: —", font=("Arial", 10), fg="#4ECDC4")
        self.right_label.pack(anchor=tk.W, pady=5)
        
        self.head_label = tk.Label(status_frame, text="Head Movement: —", font=("Arial", 10), fg="#FFD93D")
        self.head_label.pack(anchor=tk.W, pady=5)
        
        self.detection_label = tk.Label(status_frame, text="Person Detected: No", font=("Arial", 10), fg="#999")
        self.detection_label.pack(anchor=tk.W, pady=5)
        
        self.pwm_sent_label = tk.Label(status_frame, text="Last PWM Sent: None", font=("Arial", 10, "bold"), fg="#00FFFF")
        self.pwm_sent_label.pack(anchor=tk.W, pady=5)
        
        # Guide
        guide_frame = ttk.LabelFrame(right_frame, text="Guide", padding=10)
        guide_frame.pack(fill=tk.BOTH)
        
        guide_text = """
1. Click "Connect to Arduino Mega"
2. Select movement (Left/Right Bicep)
3. Angles mapped to PWM (0-255)
   • 0° → PWM 0
   • 180° → PWM 255

Wire servo/actuator to selected pin.
Refresh position immediately.
        """
        
        tk.Label(guide_frame, text=guide_text, font=("Arial", 9), justify=tk.LEFT, fg="#666").pack(anchor=tk.W)
        
    def connect_arduino(self):
        """Connect to Arduino Mega"""
        if self.arduino_connected:
            messagebox.showinfo("Info", "Already connected to Arduino!")
            return
        
        if PyMata4 is None:
            messagebox.showerror("Error", "PyMata4 not installed!\nRun: pip install PyMata4")
            return
        
        try:
            # Try to auto-detect Arduino port
            ports_to_try = [f"COM{i}" for i in range(3, 11)]  # COM3 to COM10
            
            for port in ports_to_try:
                try:
                    self.board = PyMata4(port, autoplay=False)
                    self.arduino_connected = True
                    
                    # Set pins as PWM outputs
                    self.board.set_pin_mode_pwm_output(self.pwm_pin_left)
                    self.board.set_pin_mode_pwm_output(self.pwm_pin_right)
                    self.board.set_pin_mode_pwm_output(self.pwm_pin_head)
                    
                    self.arduino_status.config(text="Status: Connected ✓", fg="#00FF00")
                    self.port_label.config(text=f"Port: {port}")
                    self.connect_btn.config(text="✓ Connected", state=tk.DISABLED, bg="#4CAF50")
                    messagebox.showinfo("Success", f"Connected to Arduino on {port}")
                    print(f"✅ Arduino Mega connected on {port}")
                    return
                except Exception as e:
                    continue
            
            messagebox.showerror("Error", "Could not find Arduino Mega on any COM port")
            self.arduino_status.config(text="Status: Connection Failed", fg="#FF0000")
            
        except Exception as e:
            messagebox.showerror("Error", f"Connection Error: {str(e)}")
            self.arduino_status.config(text="Status: Error", fg="#FF0000")
    
    def send_pwm(self, pin, angle):
        """Convert angle (0-180) to PWM (0-255) and send to Arduino"""
        if not self.arduino_connected:
            return
        
        try:
            # Map angle to PWM (0-180 degrees → 0-255 PWM)
            pwm_value = int((angle / 180.0) * 255)
            pwm_value = max(0, min(255, pwm_value))  # Clamp to 0-255
            
            self.board.pwm_write(pin, pwm_value)
            
            self.root.after(0, self.update_pwm_label, angle, pwm_value)
            
        except Exception as e:
            print(f"PWM Error: {e}")
    
    def select_joint(self, joint):
        """Change selected joint"""
        self.selected_joint = joint
        self.btn_left.config(bg="#FF6B6B" if joint == "left_bicep" else "#CCCCCC")
        self.btn_right.config(bg="#4ECDC4" if joint == "right_bicep" else "#CCCCCC")
        self.btn_head.config(bg="#FFD93D" if joint == "head" else "#CCCCCC")
        print(f"Selected: {joint}")
        
    def start_camera(self):
        """Start camera capture"""
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.running = True
        self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
        self.video_thread.start()
        
    def calculate_angle(self, point1, point2, point3):
        """
        Calculate bicep curl angle at elbow
        point1: shoulder
        point2: elbow (pivot point)
        point3: wrist
        
        Mapping:
        - 0 degrees = straight arms down (fully extended)
        - 180 degrees = bent arms (L-shape, like bicep curl)
        """
        a = np.array([point1.x - point2.x, point1.y - point2.y])
        b = np.array([point3.x - point2.x, point3.y - point2.y])
        
        cos_angle = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-6)
        cos_angle = np.clip(cos_angle, -1, 1)
        angle = np.arccos(cos_angle)
        angle_deg = np.degrees(angle)
        
        # Invert: straight (180 degrees) becomes 0, bent (0) becomes 180
        angle_deg = 180 - angle_deg
        angle_deg = np.clip(angle_deg, 0, 180)
        
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
    
    def smooth_angle(self, new_angle, history):
        """Smooth angle using moving average"""
        history.append(new_angle)
        return sum(history) / len(history)
    
    def video_loop(self):
        """Main video processing loop"""
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
            
            if results.pose_landmarks:
                person_detected = True
                landmarks = results.pose_landmarks.landmark
                
                # Left Bicep
                if landmarks[11].visibility > 0.7 and landmarks[13].visibility > 0.7 and landmarks[15].visibility > 0.7:
                    left_bicep_angle = self.calculate_angle(landmarks[11], landmarks[13], landmarks[15])
                    left_bicep_angle = self.smooth_angle(left_bicep_angle, self.angle_history_left)
                
                # Right Bicep
                if landmarks[12].visibility > 0.7 and landmarks[14].visibility > 0.7 and landmarks[16].visibility > 0.7:
                    right_bicep_angle = self.calculate_angle(landmarks[12], landmarks[14], landmarks[16])
                    right_bicep_angle = self.smooth_angle(right_bicep_angle, self.angle_history_right)
                
                # Head
                if landmarks[0].visibility > 0.7:
                    head_angle = self.calculate_head_angle(landmarks, results.face_landmarks)
                    head_angle = self.smooth_angle(head_angle, self.angle_history_head)
                
                # Draw landmarks
                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_holistic.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
                )
                
                # Draw annotations
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
            
            self.root.after(0, self.update_labels, left_bicep_angle, right_bicep_angle, head_angle, person_detected)
            
            # Select and send angle
            if self.selected_joint == "left_bicep" and left_bicep_angle is not None:
                self.current_angle = left_bicep_angle
                self.send_pwm(self.pwm_pin_left, left_bicep_angle)
            elif self.selected_joint == "right_bicep" and right_bicep_angle is not None:
                self.current_angle = right_bicep_angle
                self.send_pwm(self.pwm_pin_right, right_bicep_angle)
            elif self.selected_joint == "head" and head_angle is not None:
                self.current_angle = head_angle
                self.send_pwm(self.pwm_pin_head, head_angle)
            
            self.root.after(0, self.update_angle_display)
            
            # Update canvas
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            image.thumbnail((640, 480))
            photo = ImageTk.PhotoImage(image)
            
            self.root.after(0, lambda img=photo: self.update_canvas(img))
    
    def update_labels(self, left_angle, right_angle, head_angle, detected):
        """Update status labels"""
        self.left_label.config(
            text=f"Left Bicep: {left_angle:.1f}°" if left_angle else "Left Bicep: —",
            fg="#FF6B6B"
        )
        self.right_label.config(
            text=f"Right Bicep: {right_angle:.1f}°" if right_angle else "Right Bicep: —",
            fg="#4ECDC4"
        )
        self.head_label.config(
            text=f"Head Movement: {head_angle:.1f}°" if head_angle else "Head Movement: —",
            fg="#FFD93D"
        )
        self.detection_label.config(
            text=f"Person Detected: {'Yes' if detected else 'No'}",
            fg="#00FF00" if detected else "#999"
        )
    
    def update_angle_display(self):
        """Update main angle display"""
        self.angle_label.config(text=f"{self.current_angle:.1f}°")
        self.progress.config(value=self.current_angle)
    
    def update_pwm_label(self, angle, pwm):
        """Update PWM display"""
        self.pwm_label.config(text=f"PWM Signal: {pwm}/255")
        self.pwm_sent_label.config(text=f"Last PWM Sent: {pwm}/255 (at {angle:.1f}°)")
    
    def update_canvas(self, photo):
        """Update canvas with new frame"""
        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas.image = photo
    
    def on_closing(self):
        """Cleanup on window close"""
        self.running = False
        if self.cap:
            self.cap.release()
        if self.arduino_connected and self.board:
            self.board.shutdown()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PoseAngleDetectorArduino(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
