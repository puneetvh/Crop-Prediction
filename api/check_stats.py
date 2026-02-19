import pandas as pd
import numpy as np

try:
    df = pd.read_csv('api/TNweather_1.csv')
    print("--- Temperature Stats ---")
    print(df['temperature_2m'].describe())
    print(f"Std Dev: {df['temperature_2m'].std()}")
    
    print("\n--- Humidity Stats ---")
    print(df['relative_humidity_2m'].describe())
    print(f"Std Dev: {df['relative_humidity_2m'].std()}")
    
except Exception as e:
    print(e)
