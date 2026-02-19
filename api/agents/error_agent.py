
class ErrorAgent:
    def check_weather_data(self, weather_data):
        """
        Validates weather data ranges.
        """
        print("🛡️ ErrorAgent: Checking weather data integrity...")
        if not weather_data:
            return {"error": "Weather data is empty."}
            
        current = weather_data.get('current', {})
        temp = current.get('current_temp')
        humidity = current.get('humidity')

        if temp is None or not (-50 <= temp <= 60):
             return {"error": f"Detected unrealistic temperature: {temp}°C"}
             
        if humidity is None or not (0 <= humidity <= 100):
            return {"error": f"Detected unrealistic humidity: {humidity}%"}

        return {"status": "valid"}

    def check_crop_recommendation(self, crop_data):
        """
        Validates crop recommendation.
        """
        print("🛡️ ErrorAgent: Checking crop recommendation...")
        if not crop_data:
             return {"error": "Crop data is empty."}
             
        if "recommended_crop" not in crop_data:
            return {"error": "No crop recommended."}

        return {"status": "valid"}
