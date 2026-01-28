#!/usr/bin/env python3
"""
MQTT Message Monitor
Monitor messages on the robot/control topic to verify ESP32 communication
Run this alongside Flask app to see real-time commands
"""

import paho.mqtt.client as mqtt
import json

# MQTT Configuration
BROKER = "127.0.0.1"
PORT = 1883
TOPIC = "robot/control"

# Callback when client connects
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✓ Connected to MQTT Broker at {BROKER}:{PORT}")
        client.subscribe(TOPIC)
        print(f"✓ Subscribed to topic: {TOPIC}")
    else:
        print(f"✗ Connection failed with code {rc}")

# Callback when message is received
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8')
        data = json.loads(payload)
        
        cmd = data.get('cmd', 'UNKNOWN')
        speed = data.get('speed', 'N/A')
        
        commands = {
            'F': 'FORWARD',
            'B': 'BACKWARD',
            'L': 'LEFT',
            'R': 'RIGHT',
            'S': 'STOP'
        }
        
        cmd_name = commands.get(cmd, cmd)
        print(f"[{msg.topic}] CMD: {cmd_name:10} | SPEED: {speed}")
    except json.JSONDecodeError:
        print(f"[{msg.topic}] RAW: {payload}")
    except Exception as e:
        print(f"[ERROR] {e}")

# Callback on disconnect
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"✗ Unexpected disconnection. Code: {rc}")

# Main
if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    try:
        print(f"Connecting to MQTT Broker at {BROKER}:{PORT}...")
        client.connect(BROKER, PORT, keepalive=60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n✓ Monitoring stopped")
        client.disconnect()
    except Exception as e:
        print(f"✗ Error: {e}")
