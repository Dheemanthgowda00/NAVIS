#!/usr/bin/env python3
"""
MQTT & ESP32 Connectivity Troubleshooter
Diagnoses and tests MQTT communication setup
"""

import os
import subprocess
import socket
import sys

def run_command(cmd):
    """Run shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.stdout.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "TIMEOUT", 1
    except Exception as e:
        return str(e), 1

def check_mosquitto_service():
    """Check if Mosquitto service is running"""
    print("\n📋 MOSQUITTO SERVICE STATUS")
    print("-" * 50)
    output, code = run_command("sudo systemctl is-active mosquitto")
    
    if "active" in output:
        print("✓ Mosquitto service is RUNNING")
        return True
    else:
        print("✗ Mosquitto service is STOPPED")
        print("  Run: sudo systemctl start mosquitto")
        return False

def check_mqtt_port():
    """Check if MQTT port is listening"""
    print("\n📋 MQTT PORT BINDING")
    print("-" * 50)
    output, code = run_command("netstat -tuln | grep 1883")
    
    if "1883" in output:
        print("✓ Port 1883 is LISTENING")
        print(f"  {output}")
        return True
    else:
        print("✗ Port 1883 is NOT listening")
        return False

def check_mqtt_broker():
    """Test MQTT broker connectivity"""
    print("\n📋 MQTT BROKER CONNECTIVITY")
    print("-" * 50)
    output, code = run_command("mosquitto_pub -h 127.0.0.1 -p 1883 -t 'test/diagnostic' -m 'test' 2>&1")
    
    if code == 0:
        print("✓ MQTT Broker is ACCEPTING connections")
        return True
    else:
        print("✗ MQTT Broker connection FAILED")
        print(f"  Error: {output}")
        return False

def check_mdns():
    """Check mDNS hostname resolution"""
    print("\n📋 mDNS HOSTNAME RESOLUTION")
    print("-" * 50)
    output, code = run_command("avahi-resolve-host-name navis.local 2>&1")
    
    if code == 0 and "navis" in output:
        print("✓ mDNS resolving 'navis.local' successfully")
        print(f"  {output}")
        return True
    else:
        print("✗ mDNS resolution FAILED for 'navis.local'")
        return False

def check_pi_ip():
    """Get Pi's IP address"""
    print("\n📋 RASPBERRY PI NETWORK INFO")
    print("-" * 50)
    output, code = run_command("hostname -I")
    
    if code == 0:
        ips = output.split()
        if ips:
            print(f"✓ Pi IP Address(es): {', '.join(ips)}")
            print(f"\n  Use in ESP32 code:")
            print(f"    - Hostname: navis.local")
            print(f"    - IP: {ips[0]}")
            print(f"    - Port: 1883")
            return True
    
    print("✗ Could not determine Pi IP")
    return False

def check_flask_app():
    """Check if Flask app is configured correctly"""
    print("\n📋 FLASK APP CONFIGURATION")
    print("-" * 50)
    app_path = "/home/navis/NAVIS/Base/Remote_Control/app.py"
    
    try:
        with open(app_path, 'r') as f:
            content = f.read()
            
        checks = {
            "MQTT Broker Address": "127.0.0.1",
            "MQTT Port": "1883",
            "MQTT Topic": "robot/control"
        }
        
        all_good = True
        for check, pattern in checks.items():
            if pattern in content:
                print(f"✓ {check}: FOUND")
            else:
                print(f"✗ {check}: NOT FOUND")
                all_good = False
        
        return all_good
    except FileNotFoundError:
        print(f"✗ Flask app not found at {app_path}")
        return False

def check_mosquitto_config():
    """Check Mosquitto configuration"""
    print("\n📋 MOSQUITTO CONFIGURATION")
    print("-" * 50)
    config_path = "/etc/mosquitto/conf.d/listener.conf"
    
    try:
        with open(config_path, 'r') as f:
            content = f.read()
        
        print("✓ Listener configuration found:")
        for line in content.split('\n'):
            if line.strip() and not line.startswith('#'):
                print(f"  {line}")
        return True
    except FileNotFoundError:
        print(f"✗ Configuration not found at {config_path}")
        return False

def esp32_connection_test():
    """Provide ESP32 connection test code"""
    print("\n📋 ESP32 CONNECTION TEST")
    print("-" * 50)
    print("\nAdd this to your ESP32 code to test MQTT connection:")
    print("""
void testMQTTConnection() {
  Serial.println("Testing MQTT Connection...");
  
  // Option 1: Connect using hostname
  IPAddress serverIP = MDNS.queryHost("navis");
  if (serverIP.toString() == "0.0.0.0") {
    Serial.println("✗ Failed to resolve navis.local via mDNS");
    return;
  }
  Serial.print("✓ Resolved navis.local to: ");
  Serial.println(serverIP);
  
  client.setServer(serverIP, 1883);
  
  if (client.connect("ESP32_Test_Client")) {
    Serial.println("✓ Connected to MQTT broker!");
    client.publish("test/esp32", "Connection successful");
  } else {
    Serial.print("✗ Failed to connect. Code: ");
    Serial.println(client.state());
  }
}
    """)

def main():
    """Run all diagnostics"""
    print("\n" + "=" * 50)
    print("  MQTT & ESP32 CONNECTIVITY TROUBLESHOOTER")
    print("=" * 50)
    
    results = {
        "Mosquitto Service": check_mosquitto_service(),
        "MQTT Port": check_mqtt_port(),
        "MQTT Broker": check_mqtt_broker(),
        "mDNS Resolution": check_mdns(),
        "Pi Network Info": check_pi_ip(),
        "Flask Configuration": check_flask_app(),
        "Mosquitto Config": check_mosquitto_config(),
    }
    
    esp32_connection_test()
    
    # Summary
    print("\n" + "=" * 50)
    print("  SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ ALL CHECKS PASSED - MQTT Ready for ESP32 Connection!")
    else:
        print("\n✗ Some checks failed. See details above.")
    
    print("\nNext Steps:")
    print("1. Deploy your ESP32 code")
    print("2. Run MQTT monitor: python3 mqtt_monitor.py")
    print("3. Check ESP32 Serial Monitor for connection messages")
    print("4. Verify commands in MQTT monitor output")

if __name__ == "__main__":
    main()
