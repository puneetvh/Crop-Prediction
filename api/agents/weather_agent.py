import os
import joblib
import numpy as np
import requests
import xgboost as xgb
import pandas as pd
from datetime import datetime, timedelta

class WeatherAgent:
    def __init__(self):
        self.api_key = 'f898f0ddd0357d85d49c79f1b4b16763'  # OpenWeather API
        self.base_url = 'https://api.openweathermap.org/data/2.5/'
        self.resources = self._load_resources()

    def _load_resources(self):
        try:
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            temp_model_path = os.path.join(current_dir, 'weather_xgb_temp.json')
            hum_model_path = os.path.join(current_dir, 'weather_xgb_hum.json')
            rain_model_path = os.path.join(current_dir, 'weather_xgb_rain.json')
            city_enc_path = os.path.join(current_dir, 'city_encoder.pkl')
            
            resources = {'temp': None, 'hum': None, 'rain': None, 'city_le': None}

            if os.path.exists(temp_model_path):
                resources['temp'] = xgb.XGBRegressor()
                resources['temp'].load_model(temp_model_path)
            
            if os.path.exists(hum_model_path):
                resources['hum'] = xgb.XGBRegressor()
                resources['hum'].load_model(hum_model_path)
                
            if os.path.exists(rain_model_path):
                resources['rain'] = xgb.XGBRegressor()
                resources['rain'].load_model(rain_model_path)
                
            if os.path.exists(city_enc_path):
                resources['city_le'] = joblib.load(city_enc_path)
                print("✅ WeatherAgent: Models & City Encoder Loaded.")

            return resources
        except Exception as e:
            print(f"WeatherAgent Error: Failed to load resources: {e}")
            return {'temp': None, 'hum': None, 'rain': None, 'city_le': None}

    def _predict_future(self, start_temp, start_hum, start_rain, city_name):
        # Predict 30 days
        # Features: ['temperature_2m', 'relative_humidity_2m', 'precipitation', 'sin_day', 'cos_day', 'city_encoded']
        
        preds_temp = []
        preds_hum = []
        preds_rain = []
        
        curr_temp = start_temp
        curr_hum = start_hum
        curr_rain = start_rain
        
        # Encode City
        city_encoded = 0
        if self.resources['city_le']:
            try:
                # Handle case mismatch
                available_cities = [c.lower() for c in self.resources['city_le'].classes_]
                if city_name.lower() in available_cities:
                    idx = available_cities.index(city_name.lower())
                    city_encoded = idx # self.resources['city_le'].transform([self.resources['city_le'].classes_[idx]])[0] 
                    # Wait, transform expects original casing. Let's find original casing.
                    real_name = self.resources['city_le'].classes_[idx]
                    city_encoded = self.resources['city_le'].transform([real_name])[0]
                else:
                    # Default to Chennai or 0 if unknown
                    # print(f"⚠️ City {city_name} not in training data. Using generic.")
                    city_encoded = 0 
            except:
                city_encoded = 0
        
        # Start from tomorrow
        current_date = datetime.now() + timedelta(days=1)
        
        for _ in range(30):
            # Calculate Seasonality
            day_of_year = current_date.timetuple().tm_yday
            sin_day = np.sin(2 * np.pi * day_of_year / 365.0)
            cos_day = np.cos(2 * np.pi * day_of_year / 365.0)
            
            if self.resources['temp'] and self.resources['hum'] and self.resources['rain']:
                # Input Vector: [Temp, Hum, Rain, Sin, Cos, City]
                input_feat = np.array([[curr_temp, curr_hum, curr_rain, sin_day, cos_day, city_encoded]])
                
                try:
                    next_temp = float(self.resources['temp'].predict(input_feat)[0])
                    next_hum = float(self.resources['hum'].predict(input_feat)[0])
                    next_rain = float(self.resources['rain'].predict(input_feat)[0])
                    
                    # Enforce realistic bounds
                    next_rain = max(0.0, next_rain) # Rain can't be negative
                    next_hum = min(100.0, max(0.0, next_hum))
                    
                    curr_temp = next_temp
                    curr_hum = next_hum
                    curr_rain = next_rain
                except:
                    curr_temp += np.random.uniform(-0.5, 0.5)
            else:
                curr_temp += 0.1
                curr_rain = 0.0
            
            preds_temp.append(curr_temp)
            preds_hum.append(curr_hum)
            preds_rain.append(curr_rain)
            
            current_date += timedelta(days=1)
            
        return preds_temp, preds_hum, preds_rain

    def get_weather_data(self, city):
        try:
            url = f"{self.base_url}weather?q={city}&appid={self.api_key}&units=metric"
            response = requests.get(url)
            data = response.json()
            
            if response.status_code != 200:
                print(f"Weather API Error: {data}")
                return None

            # Check for rain (mm/1h or mm/3h)
            rain_val = 0.0
            if 'rain' in data:
                if '1h' in data['rain']: rain_val = data['rain']['1h']
                elif '3h' in data['rain']: rain_val = data['rain']['3h']

            return {
                'city': data['name'],
                'current_temp': round(data['main']['temp']),
                'humidity': round(data['main']['humidity']),
                'temp_min': round(data['main']['temp_min']),
                'temp_max': round(data['main']['temp_max']),
                'description': data['weather'][0]['description'],
                'rain_val': rain_val
            }
        except Exception as e:
            print(f"Weather Fetch Error: {e}")
            return None

    def analyze(self, city):
        print(f"🌍 WeatherAgent: Analyzing {city}...")
        current_weather = self.get_weather_data(city)
        
        if not current_weather:
            return {"error": "Could not fetch weather data"}

        # Forecast
        pred_temps, pred_hums, pred_rains = self._predict_future(
            current_weather['current_temp'], 
            current_weather['humidity'],
            current_weather['rain_val'],
            city
        )

        return {
            "city": current_weather['city'],
            "current": current_weather,
            "forecast": {
                "temperature_30_days": [round(x, 2) for x in pred_temps],
                "humidity_30_days": [round(x, 2) for x in pred_hums],
                "rainfall_30_days": [round(x, 2) for x in pred_rains]
            },
            "will_rain_next_30_days": any(r > 5.0 for r in pred_rains) # Heuristic
        }
