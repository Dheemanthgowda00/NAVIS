from flask import Flask, render_template, request, jsonify
import paho.mqtt.client as mqtt
import json
import os

app = Flask(__name__)

# --- MQTT Setup ---
MQTT_BROKER = "localhost"
MQTT_TOPIC = "robot/control"
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

try:
    client.connect(MQTT_BROKER, 1883, 60)
    client.loop_start()
    print("✅ MQTT Connected")
except:
    print("❌ MQTT Connection Failed")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_command', methods=['POST'])
def send_command():
    data = request.json
    cmd = data.get('cmd')
    speed = data.get('speed', 200)
    
    payload = json.dumps({"cmd": cmd, "speed": int(speed)})
    client.publish(MQTT_TOPIC, payload)
    
    return jsonify({"status": "sent", "command": cmd, "speed": speed})

if __name__ == '__main__':
    # Use port 5050 as 5000 was occupied
    app.run(host='0.0.0.0', port=5050, debug=False)