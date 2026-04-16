from flask import Flask, request, jsonify
import requests
from datetime import datetime
import json

app = Flask(__name__)

# ======================================
# CLOUD API
# ======================================
CLOUD_API_URL = "https://52quckwnz6.execute-api.us-east-1.amazonaws.com/dev/data"

# ======================================
# FOG PROCESSING FUNCTION
# ======================================
def process_data(data):
    # Add fog timestamp
    data['fog_timestamp'] = datetime.utcnow().isoformat()

    # ==========================
    # Example Processing Logic
    # ==========================

    alerts = []

    # Temperature check
    if data.get('temperature', 0) > 30:
        alerts.append("HIGH_TEMPERATURE")

    # Humidity check
    if data.get('humidity', 100) < 40:
        alerts.append("LOW_HUMIDITY")

    # Air quality check
    if data.get('air_quality', 0) > 120:
        alerts.append("POOR_AIR_QUALITY")

    # Motion detection
    if data.get('motion', 0) == 1:
        alerts.append("MOTION_DETECTED")

    # Light level check
    if data.get('light', 1000) < 200:
        alerts.append("LOW_LIGHT")

    # Add alerts to payload
    if alerts:
        data['fog_alerts'] = alerts
    else:
        data['fog_alerts'] = ["NORMAL"]

    return data

# ======================================
# FOG ENDPOINT
# ======================================
@app.route('/fog', methods=['POST'])
def fog_handler():
    try:
        incoming_data = request.json

        print("\nReceived at Fog:")
        print(json.dumps(incoming_data, indent=2))

        # Process data at fog
        processed_data = process_data(incoming_data)

        print("\nAfter Fog Processing:")
        print(json.dumps(processed_data, indent=2))

        # Send to cloud
        response = requests.post(CLOUD_API_URL, json=processed_data, timeout=5)

        print("\nSent to Cloud → Status:", response.status_code)

        return jsonify({
            "status": "success",
            "cloud_status": response.status_code
        })

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

# ======================================
# RUN FOG SERVER
# ======================================
if __name__ == "__main__":
    print("Fog Node Started at http://localhost:5000")
    app.run(host="0.0.0.0", port=5000)