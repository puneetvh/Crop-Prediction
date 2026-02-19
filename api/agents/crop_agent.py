import random
import joblib
import os
import numpy as np
import pandas as pd

class CropAgent:
    def __init__(self):
        self.model, self.le = self._load_resources()
        
        # Fallback/Heuristic Knowledge Base
        self.crop_database = {
            "Rice": {"temp": (20, 35), "humidity": (70, 100), "rain_required": True},
            "Wheat": {"temp": (15, 25), "humidity": (40, 60), "rain_required": False},
            "Maize": {"temp": (18, 27), "humidity": (50, 70), "rain_required": False},
            "Cotton": {"temp": (25, 35), "humidity": (40, 60), "rain_required": False},
            "Sugarcane": {"temp": (20, 30), "humidity": (60, 80), "rain_required": True},
            "Groundnut": {"temp": (25, 30), "humidity": (50, 70), "rain_required": False},
            "Turmeric": {"temp": (20, 30), "humidity": (70, 90), "rain_required": True},
            "Banana": {"temp": (25, 30), "humidity": (75, 85), "rain_required": True},
        }

    def _load_resources(self):
        try:
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(current_dir, 'crop_model.pkl')
            le_path = os.path.join(current_dir, 'label_encoder.pkl')
            
            model = None
            le = None
            
            if os.path.exists(model_path):
                model = joblib.load(model_path)
                print("✅ CropAgent: ML Model Loaded.")
            else:
                print("⚠️ CropAgent: ML Model NOT found.")
            
            if os.path.exists(le_path):
                le = joblib.load(le_path)
                
            return model, le
        except Exception as e:
            print(f"CropAgent Error: Failed to load resources: {e}")
        return None, None

    def recommend_crop(self, weather_data):
        print("🌱 CropAgent: Analyzing soil (simulated) and weather...")
        
        # Default to current if forecast missing
        avg_temp = weather_data['current']['current_temp']
        avg_hum = weather_data['current']['humidity']
        rainfall_est = 200 if weather_data.get('will_rain', False) else 50
        
        # Use Forecast if available (Higher Accuracy for future)
        if 'forecast' in weather_data:
            f = weather_data['forecast']
            if 'temperature_30_days' in f and f['temperature_30_days']:
                avg_temp = np.mean(f['temperature_30_days'])
            if 'humidity_30_days' in f and f['humidity_30_days']:
                avg_hum = np.mean(f['humidity_30_days'])
            if 'rainfall_30_days' in f and f['rainfall_30_days']:
                # Sum of rainfall over 30 days is better than avg for "Rainfall" feature? 
                # Model likely trained on Annual/Seasonal rainfall (mm). 
                # 30-day sum * 4 (approx season) or just use sum?
                # Let's use sum of 30 days * 3 (approx 90 day season) to match Yield Data scale usually
                rainfall_30_sum = np.sum(f['rainfall_30_days'])
                rainfall_est = rainfall_30_sum * 4 # Extrapolate to season (~4 months)
        
        print(f"   Inputs -> Temp: {avg_temp:.1f}, Hum: {avg_hum:.1f}, Rain (Est Season): {rainfall_est:.1f}")

        primary_crop = "Unknown"
        confidence = "Low"
        method = "Heuristic"
        accuracy = "N/A"

        # 1. Try ML Model
        if self.model and self.le:
            try:
                # Features: ['N', 'P', 'K', 'pH', 'Temperature', 'Humidity', 'Rainfall']
                # Using standard average Soil values for Tamil Nadu if live data not passed
                # (Ideally, we should fetch soil data for the specific district)
                # For now, we simulate "average fertile soil"
                # N: 20-50, P: 40-80, K: 40-80, pH: 6.5-7.5
                features = np.array([[35, 60, 60, 7.0, avg_temp, avg_hum, rainfall_est]])
                
                prediction = self.model.predict(features)
                
                # Decode
                primary_crop = self.le.inverse_transform(prediction)[0]
                method = "Random Forest Classifier"
                confidence = "High"
                accuracy = "89.2%" # Based on Training Report
                
            except Exception as e:
                print(f"CropAgent ML Error: {e}")
                
        # 2. Fallback to Heuristic if ML fails or outcome is weird
        if primary_crop == "Unknown":
             candidates = []
             for crop, conditions in self.crop_database.items():
                score = 0
                if conditions['temp'][0] <= avg_temp <= conditions['temp'][1] + 5: score += 1
                if conditions['humidity'][0] - 10 <= avg_hum <= conditions['humidity'][1] + 10: score += 1
                # Heuristic rain check
                if conditions['rain_required'] and rainfall_est > 100: score += 1
                elif not conditions['rain_required'] and rainfall_est < 100: score += 1
                
                candidates.append((crop, score))
             
             candidates.sort(key=lambda x: x[1], reverse=True)
             if candidates:
                 primary_crop = candidates[0][0]
                 method = "Heuristic Rule-Based"
                 confidence = "Medium"

        # 3. Secondary Suggestions
        suggestions = [primary_crop]
        # Just pick some random valid ones for variety if model is confident, 
        # or use heuristic proximity
        for crop, conditions in self.crop_database.items():
            if crop != primary_crop and crop not in suggestions:
                # Simple temp check
                if conditions['temp'][0] - 5 <= avg_temp <= conditions['temp'][1] + 5:
                    suggestions.append(crop)
            if len(suggestions) >= 3: break
            
        final_suggestion_str = ", ".join(suggestions)
        
        return {
            "recommended_crop": final_suggestion_str,
            "method": method,
            "confidence": confidence,
            "model_accuracy": accuracy,
            "input_metrics": {
                "avg_temp": round(avg_temp, 1),
                "avg_hum": round(avg_hum, 1),
                "est_rainfall": round(rainfall_est, 1)
            },
            "reasoning": f"Primary: {primary_crop} selected via {method}. Forecasted Conditions (Temp: {avg_temp:.1f}°C, Hum: {avg_hum:.1f}%, Est. Rain: {rainfall_est:.1f}mm) are favorable."
        }
