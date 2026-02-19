import pandas as pd
try:
    df = pd.read_csv('api/TNweather_1.csv', nrows=50000) # Sample more
    
    print("\n--- Precipitation Stats ---")
    print(df['precipitation'].describe())
    print("\n--- Rain Stats ---")
    print(df['rain'].describe())
    print("\n--- Unique Cities ---")
    print(df['city'].unique())
except Exception as e:
    print(e)
