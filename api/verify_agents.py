import sys
import os

# Add api directory to path
sys.path.append(os.path.join(os.getcwd(), 'api'))

from agents.crop_agent import CropAgent
from agents.weather_agent import WeatherAgent
from agents.disease_agent import DiseaseAgent

def test_weather_agent():
    print("\n--- Testing Weather Agent ---")
    agent = WeatherAgent()
    # Mock analysis for a city
    result = agent.analyze("Chennai")
    if "error" in result:
        print(f"❌ Weather Agent Failed: {result['error']}")
    else:
        print(f"✅ Weather Agent Success for {result['city']}")
        print(f"   Current Temp: {result['current']['current_temp']}°C")
        print(f"   Forecast (Next 5 days):")
        print(f"     Temp: {result['forecast']['temperature_30_days'][:5]}")
        print(f"     Rain: {result['forecast']['rainfall_30_days'][:5]}")
        
def test_crop_agent():
    print("\n--- Testing Crop Agent ---")
    agent = CropAgent()
    # Mock Weather Data
    weather_data = {
        'current': {'current_temp': 30, 'humidity': 80},
        'will_rain': True
    }
    result = agent.recommend_crop(weather_data)
    print(f"✅ Crop Agent Recommendation: {result['recommended_crop']}")
    print(f"   Method: {result['method']}")
    print(f"   Confidence: {result['confidence']}")
    print(f"   Model Accuracy: {result.get('model_accuracy', 'N/A')}")

def test_disease_agent():
    print("\n--- Testing Disease Agent ---")
    agent = DiseaseAgent()
    # Mock Data
    crop = "Rice"
    weather_data_high_risk = {
        'current': {'current_temp': 32, 'humidity': 90}
    }
    
    result = agent.predict_disease(crop, weather_data_high_risk)
    print(f"✅ Disease Prediction for {crop} (High Risk Inputs):")
    print(f"   Status: {result['status']}")
    print(f"   Risk Level: {result['risk_level']}")
    print(f"   Message: {result['message']}")
    print(f"   Method: {result.get('method', 'N/A')}")
    print(f"   Model Accuracy: {result.get('model_accuracy', 'N/A')}")

    # Healthy Case
    weather_data_low_risk = {
        'current': {'current_temp': 25, 'humidity': 50}
    }
    result_healthy = agent.predict_disease("Wheat", weather_data_low_risk)
    print(f"✅ Disease Prediction for Wheat (Low Risk Inputs):")
    print(f"   Status: {result_healthy['status']}")

if __name__ == "__main__":
    test_weather_agent()
    test_crop_agent()
    test_disease_agent()
