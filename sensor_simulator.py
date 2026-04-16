import random
import time
import requests
import json
from datetime import datetime, UTC

# ======================================
# CONFIGURATION
# ======================================

API_URL = "http://localhost:5000/fog"
SEND_INTERVAL = 5  # seconds between requests
DEVICE_IDS = ["device_001", "device_002", "device_003"]

# Enable/Disable sensors (optional)
ENABLE_SENSORS = {
    "temperature": True,
    "humidity": True,
    "air_quality": True,
    "motion": True,
    "light": True
}

# ======================================
# SENSOR GENERATORS
# ======================================

def generate_temperature():
    return round(random.uniform(20, 40), 2)

def generate_humidity():
    return round(random.uniform(30, 80), 2)

def generate_air_quality():
    return random.randint(50, 150)

def generate_motion():
    return random.choice([0, 1])

def generate_light():
    return random.randint(100, 1000)

# ======================================
# GENERATE SENSOR PAYLOAD
# ======================================

def generate_sensor_data():
    data = {
        "device_id": random.choice(DEVICE_IDS),
        "timestamp": datetime.now(UTC).isoformat()
    }

    if ENABLE_SENSORS["temperature"]:
        data["temperature"] = generate_temperature()

    if ENABLE_SENSORS["humidity"]:
        data["humidity"] = generate_humidity()

    if ENABLE_SENSORS["air_quality"]:
        data["air_quality"] = generate_air_quality()

    if ENABLE_SENSORS["motion"]:
        data["motion"] = generate_motion()

    if ENABLE_SENSORS["light"]:
        data["light"] = generate_light()

    return data

# ======================================
# SEND DATA TO AWS API
# ======================================

def send_data(payload):
    try:
        response = requests.post(API_URL, json=payload, timeout=5)

        print("\n📡 Data Sent:")
        print(json.dumps(payload, indent=2))

        print("Status Code:", response.status_code)
        print("Response:", response.text)

    except requests.exceptions.RequestException as e:
        print("Error sending data:", e)

# ======================================
# MAIN LOOP
# ======================================

def run_simulator():
    print("Starting IoT Sensor Simulator...\n")

    while True:
        sensor_data = generate_sensor_data()
        send_data(sensor_data)
        time.sleep(SEND_INTERVAL)

# ======================================
# ENTRY POINT
# ======================================

if __name__ == "__main__":
    run_simulator()