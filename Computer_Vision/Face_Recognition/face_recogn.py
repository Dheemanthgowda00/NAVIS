import cv2
import face_recognition
import os
from tkinter import Tk, filedialog

# Disable tkinter root window
Tk().withdraw()

# Prompt user to select an image file
image_path = filedialog.askopenfilename(title="Select Image for Face Recognition",
                                        filetypes=[("Image files", "*.jpg *.png *.jpeg")])

if not image_path:
    print("❌ No image selected. Exiting.")
    exit()

# Load the selected image and encode
image = face_recognition.load_image_file(image_path)
encodings = face_recognition.face_encodings(image)

if len(encodings) == 0:
    print("❌ No face detected in the selected image.")
    exit()

# Store the encoding and name
known_encodings = [encodings[0]]
known_names = [os.path.basename(image_path).split('.')[0]]  # Use filename as name

print(f"✅ Loaded encoding for: {known_names[0]}")

# Start webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("🎥 Starting webcam. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        name = "Unknown"
        color = (0, 0, 255)

        if True in matches:
            match_index = matches.index(True)
            name = known_names[match_index]
            color = (0, 255, 0)

        # Scale back to original frame size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    cv2.imshow("Face Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("👋 Quitting...")
        break

cap.release()
cv2.destroyAllWindows()
