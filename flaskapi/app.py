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

hum_model = joblib.load(r'C:\Users\vhpun\Downloads\sampleapp\flaskapi\hum_model.pkl')
temp_model = joblib.load(r'C:\Users\vhpun\Downloads\sampleapp\flaskapi\temp_model.pkl')

def predict_future(model, current_value):
    predictions = [current_value]
    for i in range(7):
        next_value = model.predict(np.array([[predictions[-1]]]))
        predictions.append(next_value[0])
    return predictions[1:]

@app.route('/')
def home():
    return "🌦️ Flask Weather ML API is Running!"

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

@app.route('/predict', methods=['POST'])
def predict():
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

if __name__ == '__main__':
    app.run(debug=True)
