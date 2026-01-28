import cv2
import face_recognition
import os

# This module provides face recognition utilities for the Flask web app
# It is imported by simple_facerec.py

def load_image_and_encode(image_path):
    """Load image and encode face"""
    try:
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        if len(encodings) > 0:
            return encodings[0], True
        return None, False
    except Exception as e:
        print(f"Error loading image: {e}")
        return None, False

def get_face_name(image_path):
    """Extract name from image filename"""
    return os.path.basename(image_path).split('.')[0]

def compare_faces(known_encodings, face_encoding):
    """Compare face with known encodings"""
    matches = face_recognition.compare_faces(known_encodings, face_encoding)
    return matches

