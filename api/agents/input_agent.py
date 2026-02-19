
class InputAgent:
    def validate_input(self, city):
        """
        Validates the user input.
        """
        print(f"📥 InputAgent: Validating '{city}'...")
        
        if not city or not isinstance(city, str):
            return {"error": "City name must be a non-empty string."}
        
        city = city.strip()
        if len(city) < 2:
            return {"error": "City name is too short."}
            
        # Optional: Add a check against a known list of Tamil Nadu districts if strictly required.
        # For now, we allow any valid string to permit testing with major cities.
        
        return {"city": city, "status": "valid"}
