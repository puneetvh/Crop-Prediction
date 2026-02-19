import joblib
import os
import numpy as np

class DiseaseAgent:
    def __init__(self):
        self.model, self.le_disease, self.le_crop = self._load_resources()
        
        # Knowledge Base: Rule-based fallback
        self.disease_database = {
            "Rice": [
                {"name": "Blast Disease", "desc": "Fungal infection causing lesions.", "condition": lambda w: w['current']['humidity'] > 85},
                {"name": "Bacterial Blight", "desc": "Water-soaked streaks on leaves.", "condition": lambda w: w['current']['current_temp'] > 30 and w['current']['humidity'] > 70}
            ],
            "Wheat": [
                {"name": "Rust", "desc": "Reddish-orange pustules.", "condition": lambda w: w['current']['humidity'] > 70},
                {"name": "Smut", "desc": "Black powdery spores.", "condition": lambda w: w['current']['current_temp'] < 20}
            ],
            "Maize": [
                {"name": "Leaf Blight", "desc": "Grayish-green lesions.", "condition": lambda w: w['current']['humidity'] > 80}
            ],
             "Cotton": [
                {"name": "Root Rot", "desc": "Decay of roots.", "condition": lambda w: w['current']['current_temp'] > 30},
                {"name": "Boll Rot", "desc": "Rotting of bolls.", "condition": lambda w: w['current']['humidity'] > 90}
            ],
            "Sugarcane": [
                {"name": "Red Rot", "desc": "Reddish discoloration inside stalk.", "condition": lambda w: w['current']['humidity'] > 90},
                {"name": "Wilt", "desc": "Drying of leaves.", "condition": lambda w: w['current']['current_temp'] > 30}
            ],
            "Groundnut": [
                {"name": "Tikka Disease", "desc": "Dark spots on leaves.", "condition": lambda w: w['current']['humidity'] > 80},
                {"name": "Rust", "desc": "Orange pustules on leaf underside.", "condition": lambda w: w['current']['humidity'] > 75}
            ],
            "Turmeric": [
                {"name": "Leaf Spot", "desc": "Brown spots with yellow halos.", "condition": lambda w: w['current']['humidity'] > 80},
                {"name": "Rhizome Rot", "desc": "Rotting of rhizomes.", "condition": lambda w: w['current']['humidity'] > 90}
            ],
            "Banana": [
                {"name": "Panama Wilt", "desc": "Yellowing of leaves.", "condition": lambda w: w['current']['current_temp'] > 28},
                {"name": "Sigatoka", "desc": "Black streaks on leaves.", "condition": lambda w: w['current']['humidity'] > 80}
            ]
        }

    def _load_resources(self):
        try:
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(current_dir, 'disease_model.pkl')
            le_path = os.path.join(current_dir, 'disease_label_encoder.pkl')
            crop_le_path = os.path.join(current_dir, 'crop_name_encoder.pkl')
            
            model = None
            le = None
            le_crop = None
            
            if os.path.exists(model_path):
                model = joblib.load(model_path)
                print("✅ DiseaseAgent: ML Model Loaded.")
            
            if os.path.exists(le_path):
                le = joblib.load(le_path)
                
            if os.path.exists(crop_le_path):
                le_crop = joblib.load(crop_le_path)
                
            return model, le, le_crop
        except Exception as e:
            print(f"DiseaseAgent Error: Failed to load resources: {e}")
        return None, None, None

    def predict_disease(self, crop, weather_data):
        print(f"🦠 DiseaseAgent: Checking risks for {crop}...")
        
        # Split multiple crops check (e.g. "Rice, Cotton") - check primary first
        primary_crop = crop.split(',')[0].strip()
        
        # Default to Current
        temp = weather_data['current']['current_temp']
        hum = weather_data['current']['humidity']
        is_forecast = False
        
        # Use Forecast if available
        if 'forecast' in weather_data:
            f = weather_data['forecast']
            if 'temperature_30_days' in f and f['temperature_30_days']:
                temp = np.mean(f['temperature_30_days'])
                is_forecast = True
            if 'humidity_30_days' in f and f['humidity_30_days']:
                hum = np.mean(f['humidity_30_days'])
                is_forecast = True
                
        if is_forecast:
            print(f"   Using Forecast -> Avg Temp: {temp:.1f}, Avg Hum: {hum:.1f}")
        
        predicted_disease = "None"
        risk_level = "Low"
        method = "Heuristic"
        accuracy = "N/A"
        
        # 1. Try ML Model
        if self.model and self.le_disease and self.le_crop:
            try:
                # Encode crop
                # Check if known
                if primary_crop in self.le_crop.classes_:
                    crop_encoded = self.le_crop.transform([primary_crop])[0]
                    # Features: [Crop_Encoded, Temp, Hum]
                    features = np.array([[crop_encoded, temp, hum]])
                    prediction = self.model.predict(features)
                    
                    predicted_disease = self.le_disease.inverse_transform(prediction)[0]
                    
                    if predicted_disease != "Healthy":
                        risk_level = "High"
                    
                    method = "Random Forest Classifier"
                    accuracy = "97.7%" # From training logs
                else:
                    print(f"⚠️ DiseaseAgent: Crop '{primary_crop}' not in ML training data. Using Fallback.")
                    
            except Exception as e:
                print(f"DiseaseAgent ML Error: {e}")

        # 2. Fallback Rule-Based (if ML failed or crop unknown or predicted Healthy but heuristic suggests risk?)
        # Let's say ML is authority. Only fallback if ML didn't run.
        
        risks = []
        descriptions = []
        
        if method == "Heuristic":
            if primary_crop in self.disease_database:
                potential_diseases = self.disease_database[primary_crop]
                for disease in potential_diseases:
                    if disease["condition"](weather_data):
                        risks.append(disease["name"])
                        descriptions.append(f"{disease['name']}: {disease['desc']}")
            
            if risks:
                predicted_disease = risks[0]
                risk_level = "High" if len(risks) > 1 else "Moderate"
        else:
            # If ML predicted a disease, add description if known
            if predicted_disease != "Healthy":
                risks.append(predicted_disease)
                # Try to find description in DB
                desc = "Detected via ML analysis."
                if primary_crop in self.disease_database:
                    for d in self.disease_database[primary_crop]:
                        if d['name'] == predicted_disease:
                            desc = d['desc']
                descriptions.append(f"{predicted_disease}: {desc}")

        if not risks and predicted_disease == "Healthy":
            return {
                "status": "Healthy",
                "risk_level": "Low",
                "message": f"No immediate disease risks detected for {primary_crop} based on forecast (Avg Temp: {temp:.1f}°C, Hum: {hum:.1f}%).",
                "method": method,
                "model_accuracy": accuracy
            }
        else:
            return {
                "status": "Warning",
                "risk_level": risk_level,
                "diseases_detected": risks,
                "message": f"Risks for {primary_crop}: {', '.join(descriptions)}",
                "method": method,
                "model_accuracy": accuracy
            }
