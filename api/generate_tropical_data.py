
import pandas as pd
import numpy as np
import random

def generate_tropical_weather(days=5000):
    # Tamil Nadu / Tropical Climate Simulation
    # Month 1 (Jan) - Month 12 (Dec)
    # Summer: Mar-Jun (High Temps 30-40)
    # Monsoon: Oct-Dec (High Humidity, Moderate Temps 25-30)
    # Winter: Jan-Feb (Mild Temps 20-30)
    
    data = []
    
    for day in range(days):
        month = (day % 365) // 30 + 1
        
        # Base Temperature Trend
        if 3 <= month <= 6: # Summer
            base_temp = random.uniform(28, 38)
            humidity = random.uniform(30, 60)
        elif 10 <= month <= 12: # Monsoon
            base_temp = random.uniform(24, 30)
            humidity = random.uniform(70, 95)
        else: # Winter/Mild
            base_temp = random.uniform(22, 28)
            humidity = random.uniform(50, 75)
            
        # Add daily noise
        min_temp = base_temp - random.uniform(5, 10)
        max_temp = base_temp + random.uniform(0, 5)
        
        # Ensure physics
        if min_temp < 18: min_temp = 18 # TN rarely drops below 18
        
        data.append({
            'MinTemp': round(min_temp, 1),
            'MaxTemp': round(max_temp, 1),
            'Humidity': round(humidity, 1)
        })
        
    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    df = generate_tropical_weather()
    # Save to standard path so training script picks it up
    df.to_csv('api/weather.csv', index=False)
    print("✅ Generated 5000 days of Tropical Tamil Nadu Weather Data in api/weather.csv")
