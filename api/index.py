from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import requests
import joblib
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)

# Enable CORS for your frontend
CORS(app, supports_credentials=True, origins=["http://localhost:5173"])

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


def predict_future(model, current_value):
    predictions = [current_value]
    for i in range(7):
        next_value = model.predict(np.array([[predictions[-1]]]))
        predictions.append(next_value[0])
    return predictions[1:]

@app.route('/api/')
def home():
    if model_load_error:
        return f"🌦️ Flask Weather ML API is Running! WARNING: Models failed to load: {model_load_error}"
    return "🌦️ Flask Weather ML API is Running! Models loaded successfully."


def get_current_weather(city):
    url = f"{BASE_URL}weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    return {
        'city': data['name'],
        'current_temp': round(data['main']['temp']),
        'feels_like': round(data['main']['feels_like']),
        'temp_min': round(data['main']['temp_min']),
        'temp_max': round(data['main']['temp_max']),
        'humidity': round(data['main']['humidity']),
        'description': data['weather'][0]['description'],
        'country': data['sys']['country'],
        'Wind_Gust_Dir': data['wind']['deg'],
        'Wind_Gust_Speed': data['wind']['speed'],
        'pressure': data['main']['pressure']
    }

@app.route('/api/predict', methods=['POST'])
def predict():
    if not hum_model or not temp_model:
        return jsonify({'error': f'Models not loaded. Server Error: {model_load_error}'}), 500

    data = request.get_json()
    city = data.get('city', '').strip()

    if not city:
        return jsonify({'error': 'City not provided'}), 400

    print(f"🌍 Received city: {city}")
    
    curr_weather = get_current_weather(city)
    predicted_temps = predict_future(temp_model, curr_weather['temp_min'])
    predicted_humidity = predict_future(hum_model, curr_weather['humidity'])

    print(curr_weather['humidity'], curr_weather['temp_min'])
    print(f"the predicted temperatures is {predicted_temps}, the predicted humidity is {predicted_humidity}")

    # Attach predictions to response
    curr_weather['predicted_temperatures'] = [round(float(val), 2) for val in predicted_temps]
    curr_weather['predicted_humidity'] = [round(float(val), 2) for val in predicted_humidity]

    return jsonify(curr_weather)

# Vercel requires the app object to be available as a variable named 'app'
# No app.run() needed for Vercel

895