import xgboost as xgb
import pandas as pd
import numpy as np
import os
from sklearn.metrics import mean_squared_error
from datetime import datetime

def check_weather_metrics():
    print("Checking Weather Model Metrics...")
    try:
        model = xgb.XGBRegressor()
        model.load_model('api/weather_xgb_temp.json')
        
        df = pd.read_csv('api/TNweather_1.csv')
        # ... logic to recreate test set ...
        # Simplified: just predict on a sample
        
        # Parse Dates
        if 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'])
        elif 'date' in df.columns:
            df['time'] = pd.to_datetime(df['date'])
        else:
             df['time'] = pd.date_range(start='2020-01-01', periods=len(df), freq='H')

        df['day_of_year'] = df['time'].dt.dayofyear
        df['sin_day'] = np.sin(2 * np.pi * df['day_of_year'] / 365.0)
        df['cos_day'] = np.cos(2 * np.pi * df['day_of_year'] / 365.0)

        df['target_temp'] = df['temperature_2m'].shift(-1)
        df = df.dropna()
        
        # Last 20%
        split_idx = int(len(df) * 0.8)
        test_df = df.iloc[split_idx:]
        
        X_test = test_df[['temperature_2m', 'relative_humidity_2m', 'sin_day', 'cos_day']]
        y_test = test_df['target_temp']
        
        preds = model.predict(X_test)
        mse = mean_squared_error(y_test, preds)
        rmse = np.sqrt(mse)
        
        print(f"✅ Weather Temp MSE: {mse:.4f}")
        print(f"✅ Weather Temp RMSE: {rmse:.4f}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_weather_metrics()
