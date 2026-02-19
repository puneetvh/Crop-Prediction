
import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import os

print("🚀 Starting Model Training from weather.csv...")

try:
    # 1. Load Data
    current_dir = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(current_dir, 'weather.csv'))
    
    # Cleaning
    # Drop rows with missing target
    df = df.dropna(subset=['MinTemp', 'MaxTemp', 'Humidity'])
    
    # We want to predict 'Next Day Temp' based on 'Current Temp'
    # Shift the data to create a supervised learning problem
    
    # Temp Model: Input [MinTemp, MaxTemp, Humidity] -> Output [Next MinTemp]
    df['TargetMinTemp'] = df['MinTemp'].shift(-1)
    df['TargetHumidity'] = df['Humidity'].shift(-1)
    
    df = df.dropna()
    
    X = df[['MinTemp', 'MaxTemp', 'Humidity']]
    y_temp = df['TargetMinTemp']
    y_hum = df['TargetHumidity']
    
    print(f"📊 Training on {len(df)} days of historical data...")

    # 2. Train Models
    temp_model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100)
    temp_model.fit(X, y_temp)
    print("✅ Temperature Model Trained")
    
    hum_model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100)
    hum_model.fit(X, y_hum)
    print("✅ Humidity Model Trained")
    
    # 3. Save
    joblib.dump(temp_model, os.path.join(current_dir, 'temp_model.pkl'))
    joblib.dump(hum_model, os.path.join(current_dir, 'hum_model.pkl'))
    print("💾 Models Saved Successfully: temp_model.pkl, hum_model.pkl")

except Exception as e:
    print(f"❌ Training Failed: {e}")
