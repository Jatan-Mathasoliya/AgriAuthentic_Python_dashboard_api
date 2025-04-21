from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import random
import time
from threading import Thread
from collections import deque

app = FastAPI()

# CORS Middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (Change this in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Certification Tracking
valid_time = 0
certification_status = "Not Certified"
certification_reason = "Insufficient data."
farmer_dashboard = {"certification": certification_status, "reason": certification_reason}

# Store sensor readings (last 30 readings)
data_history = deque(maxlen=30)

# Function to generate random sensor data
def generate_sensor_data():
    return {
        "soil_moisture": round(random.uniform(20, 75), 2),
        "soil_temperature": round(random.uniform(10, 25), 2),
        "pH": round(random.uniform(6, 8), 2),
        "ec": round(random.uniform(1, 2.2), 2),
        "nitrogen": round(random.uniform(15, 35), 2),
        "phosphorus": round(random.uniform(8, 32), 2),
        "potassium": round(random.uniform(90, 260), 2),
        "water_tds": round(random.uniform(90, 510), 2)
    }

# Function to validate farming conditions
def validate_farming_conditions(data):
    global valid_time, certification_status, certification_reason
    all_valid = True
    failure_keys = []

    # Validation conditions
    thresholds = {
        "soil_moisture": (30, 70),
        "soil_temperature": (15, 30),
        "pH": (6.5, 7.5),
        "ec": (1.2, 2.0),
        "nitrogen": (20, 40),
        "phosphorus": (10, 30),
        "potassium": (100, 250),
        "water_tds": (100, 500)
    }

    for key, (min_val, max_val) in thresholds.items():
        if not (min_val <= data[key] <= max_val):
            all_valid = False
            failure_keys.append(key)

    # Update certification status
    if all_valid:
        valid_time += 1
        certification_reason = "✅ All conditions met."
    else:
        valid_time = 0
        certification_reason = "❌ Issues detected: " + ", ".join([f"⚠️ {key.replace('_', ' ').title()} out of range." for key in failure_keys])

    # Certification levels
    if valid_time >= 15:
        certification_status = "Level 3 - Full Certification ✅"
    elif valid_time >= 10:
        certification_status = "Level 2 - Intermediate Certification 🟡"
    elif valid_time >= 5:
        certification_status = "Level 1 - Basic Certification ⚪"
    else:
        certification_status = "Not Certified ❌"

    farmer_dashboard["certification"] = certification_status
    farmer_dashboard["reason"] = certification_reason
    return certification_status, failure_keys

# Function to generate AI suggestions
def generate_suggestions(failure_keys):
    suggestions = {
        "soil_moisture": "💧 Adjust irrigation to keep soil moisture within range.",
        "soil_temperature": "🌿 Use shading/mulching to regulate soil temperature.",
        "pH": "🧪 Apply lime (increase pH) or sulfur (decrease pH).",
        "ec": "🌱 Add organic matter to stabilize soil EC.",
        "nitrogen": "🌾 Apply compost or nitrogen-rich fertilizers.",
        "phosphorus": "🔬 Use phosphorus fertilizers like bone meal.",
        "potassium": "🍌 Apply potash-based fertilizers.",
        "water_tds": "💦 Check water source for high TDS levels."
    }

    ai_suggestions = [suggestions[key] for key in failure_keys]
    return ai_suggestions if ai_suggestions else ["✅ Farm conditions are perfect!"]

# Real-time sensor data update thread
def update_sensor_data():
    while True:
        sensor_data = generate_sensor_data()
        certification_status, failure_keys = validate_farming_conditions(sensor_data)
        data_history.append(sensor_data)

        print("\n📡 Sensor Data Update:", sensor_data)
        print("📜 Certification Status:", certification_status)
        print("📌 Reason:", certification_reason)
        print("🤖 AI Suggestions:", generate_suggestions(failure_keys))
        print("-" * 50)

        time.sleep(10)  # Update every 10 sec

# API Route to get the latest sensor data
@app.get('/api/sensor_data')
async def get_sensor_data():
    latest_data = list(data_history)[-1] if data_history else {}
    return JSONResponse(content={
        "sensor_data": latest_data,
        "sensor_history": list(data_history),  # Send full history to frontend for graph
        "certification_status": certification_status,
        "certification_reason": certification_reason,
        "suggestions": generate_suggestions(validate_farming_conditions(latest_data)[1]) if latest_data else []
    })

# Start the background thread
thread = Thread(target=update_sensor_data)
thread.daemon = True
thread.start()

# 🚀 MAIN ENTRY POINT 🚀
if __name__ == "__main__":
    uvicorn.run("farm_verify:app", host="0.0.0.0", port=5000, reload=True)
