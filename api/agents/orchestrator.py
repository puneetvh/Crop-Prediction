from .weather_agent import WeatherAgent
from .crop_agent import CropAgent
from .disease_agent import DiseaseAgent
from .input_agent import InputAgent
from .error_agent import ErrorAgent

class AgentOrchestrator:
    def __init__(self):
        self.input_agent = InputAgent()
        self.weather_agent = WeatherAgent()
        self.crop_agent = CropAgent()
        self.disease_agent = DiseaseAgent()
        self.error_agent = ErrorAgent()

    def run_workflow(self, city):
        results = {}

        # Step 0: Input Validation
        print(f"🚀 Starting Workflow for {city}")
        input_validation = self.input_agent.validate_input(city)
        if "error" in input_validation:
            return input_validation
        
        valid_city = input_validation["city"]

        # Step 1: Weather
        weather_result = self.weather_agent.analyze(valid_city)
        if "error" in weather_result:
            return {"error": weather_result["error"]}
        
        # Error Check: Weather
        weather_check = self.error_agent.check_weather_data(weather_result)
        if "error" in weather_check:
            return weather_check

        results["weather"] = weather_result

        # Step 2: Crop
        crop_result = self.crop_agent.recommend_crop(weather_result)
        
        # Error Check: Crop
        crop_check = self.error_agent.check_crop_recommendation(crop_result)
        if "error" in crop_check:
            return crop_check

        results["crop"] = crop_result

        # Step 3: Disease
        disease_result = self.disease_agent.predict_disease(
            crop_result["recommended_crop"], 
            weather_result
        )
        results["disease"] = disease_result

        return results
