
import sys
import os

# Add current directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.orchestrator import AgentOrchestrator

def test_workflow():
    print("🧪 Testing Agent Workflow...")
    orchestrator = AgentOrchestrator()
    
    cities = ["Coimbatore"]
    
    for city in cities:
        print(f"\n--- Testing City: '{city}' ---")
        result = orchestrator.run_workflow(city)
        print(result)
        
        if "error" in result:
            print(f"✅ Error handled correctly: {result['error']}")
        else:
            weather = result.get('weather', {})
            crop = result.get('crop', {})
            disease = result.get('disease', {})
            
            # Checks
            has_90_days = len(weather.get('forecast', {}).get('temperature_90_days', [])) == 90
            has_crop = crop.get('recommended_crop') != "Unknown"
            
            if has_90_days and has_crop:
                print("✅ Success: 90 days forecast and Crop recommended.")
            else:
                print("❌ Failure: Missing data.")

if __name__ == "__main__":
    test_workflow()
