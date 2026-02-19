from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import requests
import joblib
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)

# Enable CORS for your frontend
CORS(app, resources={r"/*": {"origins": "*"}})

API_KEY = 'f898f0ddd0357d85d49c79f1b4b16763'  # OpenWeather API
BASE_URL = 'https://api.openweathermap.org/data/2.5/'  # Base URL for API request

import os

# Get the directory where the current file is located
current_dir = os.path.dirname(os.path.abspath(__file__))


# Load models using absolute paths with error handling
try:
    hum_model = joblib.load(os.path.join(current_dir, 'hum_model.pkl'))
    temp_model = joblib.load(os.path.join(current_dir, 'temp_model.pkl'))
    model_load_error = None
except Exception as e:
    print(f"Error loading models: {e}")
    hum_model = None
    temp_model = None
    model_load_error = str(e)


from agents.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()

@app.route('/')
def home():
    return "<h1>AgriGenius Backend is Running!</h1><p>Use the frontend at localhost:5173 to interact.</p>"

@app.route('/api/workflow', methods=['POST'])
def workflow():
    data = request.get_json()
    city = data.get('city', '').strip()

    if not city:
        return jsonify({'error': 'City not provided'}), 400

    print(f"🌍 Received request for city: {city}")
    
    try:
        result = orchestrator.run_workflow(city)
        if "error" in result:
             return jsonify(result), 500
        return jsonify(result)
    except Exception as e:
        print(f"Workflow Error: {e}")
        return jsonify({'error': str(e)}), 500


# Vercel requires the app object to be available as a variable named 'app'
# No app.run() needed for Vercel

if __name__ == '__main__':
    app.run(debug=True, port=5000)

895