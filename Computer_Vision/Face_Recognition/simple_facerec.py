import face_recognition
import cv2
import os
import glob

class SimpleFacerec:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.tolerance = 0.6  # Confidence threshold for matching (higher = more lenient)

    def load_encoding_images(self, images_path):
        # Check if path exists
        if not os.path.exists(images_path):
            print(f"⚠️ Path '{images_path}' does not exist. No known faces loaded.")
            return
            
        images_path = glob.glob(os.path.join(images_path, "*.*"))
        print(f"📸 Found {len(images_path)} images for encoding")

        for img_path in images_path:
            img = cv2.imread(img_path)
            if img is None:
                continue
                
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            basename = os.path.basename(img_path)
            filename, _ = os.path.splitext(basename)

            # Use smaller image for faster encoding
            small_img = cv2.resize(rgb_img, (0, 0), fx=0.5, fy=0.5)
            encodings = face_recognition.face_encodings(small_img, model="hog")  # Faster model

            if len(encodings) > 0:
                self.known_face_encodings.append(encodings[0])
                self.known_face_names.append(filename)
                print(f"✓ Encoded: {filename}")
            else:
                print(f"⚠️ No face found in: {filename}")

    def detect_known_faces(self, frame):
        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Use HOG model (faster) instead of CNN (more accurate)
        face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # Use tolerance threshold for matching
            matches = face_recognition.compare_faces(
                self.known_face_encodings, 
                face_encoding, 
                tolerance=self.tolerance
            )
            name = "Unknown"

            # Calculate distances for more accurate matching
            face_distances = face_recognition.face_distance(
                self.known_face_encodings, 
                face_encoding
            )
            if len(face_distances) > 0:
                best_match_index = face_distances.argmin()
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]

            face_names.append(name)

        # Scale locations back to original frame size
        face_locations = [(top*2, right*2, bottom*2, left*2) for (top, right, bottom, left) in face_locations]
        
        return face_locations, face_names