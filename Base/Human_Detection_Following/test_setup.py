#!/usr/bin/env python3
"""
Quick Test Script for Human Detection & Following
Tests camera, MediaPipe, and MQTT connectivity
"""

import cv2
import mediapipe as mp
import paho.mqtt.client as mqtt
import json
import sys

def test_camera():
    """Test camera connectivity"""
    print("\n📷 TESTING CAMERA")
    print("-" * 50)
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                h, w = frame.shape[:2]
                print(f"✓ Camera working")
                print(f"  Resolution: {w}x{h}")
                cap.release()
                return True
        else:
            print("✗ Camera not found")
            return False
    except Exception as e:
        print(f"✗ Camera error: {e}")
        return False

def test_mediapipe():
    """Test MediaPipe installation and functionality"""
    print("\n🧠 TESTING MEDIAPIPE")
    print("-" * 50)
    try:
        import mediapipe as mp
        print(f"✓ MediaPipe imported successfully")
        
        # Try creating a holistic instance
        mp_holistic = mp.solutions.holistic
        holistic = mp_holistic.Holistic()
        print(f"✓ Holistic model loaded")
        
        # Test with dummy frame
        import numpy as np
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        results = holistic.process(dummy_frame)
        print(f"✓ Pose detection working")
        
        holistic.close()
        return True
    except Exception as e:
        print(f"✗ MediaPipe error: {e}")
        return False

def test_mqtt():
    """Test MQTT broker connectivity"""
    print("\n📡 TESTING MQTT")
    print("-" * 50)
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.connect("127.0.0.1", 1883, 60)
        client.loop_start()
        
        # Publish test message
        payload = json.dumps({"cmd": "S", "speed": 0})
        client.publish("robot/control", payload)
        print(f"✓ MQTT broker connected")
        print(f"✓ Test message published to robot/control")
        
        client.loop_stop()
        client.disconnect()
        return True
    except Exception as e:
        print(f"✗ MQTT error: {e}")
        return False

def test_opengl():
    """Test OpenCV"""
    print("\n🎨 TESTING OPENCV")
    print("-" * 50)
    try:
        import cv2
        print(f"✓ OpenCV version: {cv2.__version__}")
        return True
    except Exception as e:
        print(f"✗ OpenCV error: {e}")
        return False

def main():
    print("\n" + "=" * 50)
    print("  HUMAN DETECTION & FOLLOWING - TEST SUITE")
    print("=" * 50)
    
    results = {
        "Camera": test_camera(),
        "OpenCV": test_opengl(),
        "MediaPipe": test_mediapipe(),
        "MQTT": test_mqtt(),
    }
    
    # Summary
    print("\n" + "=" * 50)
    print("  SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All systems ready! Start the app with:")
        print("  cd /home/navis/NAVIS/Base/Human_Detection_Following")
        print("  python app.py")
    else:
        print("\n✗ Some tests failed. Install missing dependencies:")
        print("  pip install -r requirements.txt")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
