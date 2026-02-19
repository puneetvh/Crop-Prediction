import pandas as pd
import numpy as np
import joblib
import os
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.preprocessing import LabelEncoder

def train_crop_model():
    print("\n🌾 Training Crop Prediction Model (Random Forest)...")
    try:
        soil_df = pd.read_csv('api/Soil data.csv')
        soil_df = soil_df.rename(columns={
            'Nitrogen Value': 'N',
            'Phosphorous value': 'P',
            'Potassium value': 'K'
        })
        soil_df['District'] = soil_df['District'].str.title()
        
        # Deduplicate Soil Data (Group by District and take Mean)
        # This prevents data explosion (Cartesian product) when merging
        soil_df = soil_df.groupby('District').mean(numeric_only=True).reset_index()
        print(f"   Soil Data Deduplicated: {soil_df.shape[0]} districts")
        
        yield_df = pd.read_csv('api/Tamilnadu agriculture yield data.csv')
        yield_df['District_Name'] = yield_df['District_Name'].str.title()
        
        # 1. Filter for Top 20 Crops to improve learnability
        top_crops = yield_df['Crop'].value_counts().nlargest(20).index
        yield_df = yield_df[yield_df['Crop'].isin(top_crops)]
        print(f"   Focusing on Top 20 Crops: {list(top_crops[:5])}...")

        merged_df = pd.merge(yield_df, soil_df, left_on='District_Name', right_on='District', how='inner')
        print(f"   Merged Data Shape: {merged_df.shape}")
        
        # 2. Smart Weather Mapping based on Season
        def get_weather_features(season):
            # Returns (Temp, Humidity, Rainfall)
            if 'Kharif' in season: 
                # Monsoon/Summer: High Temp, High Rain
                return np.random.uniform(28, 35), np.random.uniform(70, 90), np.random.uniform(150, 300)
            elif 'Rabi' in season: 
                # Winter: Moderate Temp, Lower Rain
                return np.random.uniform(22, 28), np.random.uniform(50, 70), np.random.uniform(20, 80)
            elif 'Whole Year' in season:
                # Average
                return np.random.uniform(25, 32), np.random.uniform(60, 80), np.random.uniform(50, 150)
            else:
                return 28.0, 70.0, 100.0

        # Apply function
        weather_data = merged_df['Season'].apply(get_weather_features).tolist()
        weather_df = pd.DataFrame(weather_data, columns=['Temperature', 'Humidity', 'Rainfall'])
        
        # Concatenate
        merged_df = pd.concat([merged_df.reset_index(drop=True), weather_df.reset_index(drop=True)], axis=1)

        features = ['N', 'P', 'K', 'pH', 'Temperature', 'Humidity', 'Rainfall']
        target = 'Crop'
        
        X = merged_df[features]
        y = merged_df[target]
        
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
        
        # Lightweight Model for Vercel
        rf_model = RandomForestClassifier(n_estimators=30, max_depth=12, random_state=42, n_jobs=-1)
        rf_model.fit(X_train, y_train)
        
        y_pred = rf_model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        print(f"✅ Crop Model Accuracy: {acc * 100:.2f}%")
        
        joblib.dump(rf_model, 'api/crop_model.pkl')
        joblib.dump(le, 'api/label_encoder.pkl')
        
    except Exception as e:
        print(f"❌ Error training Crop Model: {e}")

def train_weather_model():
    print("\n☁️ Training Weather Prediction Model (XGBoost) with Seasonality & Districts...")
    try:
        df = pd.read_csv('api/TNweather_1.csv')
        
        # Parse Dates
        if 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'])
        elif 'date' in df.columns:
            df['time'] = pd.to_datetime(df['date'])
        else:
            print("⚠️ No time/date column found. Creating synthetic time index.")
            df['time'] = pd.date_range(start='2020-01-01', periods=len(df), freq='H')

        # Feature Engineering: Seasonality
        df['day_of_year'] = df['time'].dt.dayofyear
        df['sin_day'] = np.sin(2 * np.pi * df['day_of_year'] / 365.0)
        df['cos_day'] = np.cos(2 * np.pi * df['day_of_year'] / 365.0)
        
        # Feature Engineering: City Encoding
        if 'city' in df.columns:
            le_city = LabelEncoder()
            df['city_encoded'] = le_city.fit_transform(df['city'].astype(str))
            # Save encoder for Agent
            joblib.dump(le_city, 'api/city_encoder.pkl')
            print(f"   Encoded {len(le_city.classes_)} cities.")
        else:
            print("⚠️ 'city' column missing. Using dummy city code 0.")
            df['city_encoded'] = 0

        # Targets (Shift -1 for next step prediction)
        df['target_temp'] = df['temperature_2m'].shift(-1)
        df['target_hum'] = df['relative_humidity_2m'].shift(-1)
        # Use precipitation for rainfall
        if 'precipitation' in df.columns:
            df['target_rain'] = df['precipitation'].shift(-1)
            rain_col = 'precipitation'
        elif 'rain' in df.columns:
             df['target_rain'] = df['rain'].shift(-1)
             rain_col = 'rain'
        else:
            df['target_rain'] = 0
            rain_col = 'rain' # Dummy
            
        df = df.dropna()

        # Input Features: [Temp, Hum, Rain, Sin, Cos, City]
        features = ['temperature_2m', 'relative_humidity_2m', rain_col, 'sin_day', 'cos_day', 'city_encoded']
        X = df[features]
        
        # Sample for speed if needed
        if len(df) > 100000:
            X = X.iloc[-100000:]
            y_temp = df['target_temp'].iloc[-100000:]
            y_hum = df['target_hum'].iloc[-100000:]
            y_rain = df['target_rain'].iloc[-100000:]
        else:
            y_temp = df['target_temp']
            y_hum = df['target_hum']
            y_rain = df['target_rain']
        
        # Train Temp
        print("   Training Temperature Model...")
        xgb_temp = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, objective='reg:squarederror')
        xgb_temp.fit(X, y_temp)
        print(f"✅ Temp MSE: {mean_squared_error(y_temp, xgb_temp.predict(X)):.4f}")
        xgb_temp.save_model('api/weather_xgb_temp.json')
        
        # Train Hum
        print("   Training Humidity Model...")
        xgb_hum = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, objective='reg:squarederror')
        xgb_hum.fit(X, y_hum)
        print(f"✅ Hum MSE: {mean_squared_error(y_hum, xgb_hum.predict(X)):.4f}")
        xgb_hum.save_model('api/weather_xgb_hum.json')

        # Train Rain
        print("   Training All-New Rainfall Model...")
        xgb_rain = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, objective='reg:squarederror')
        xgb_rain.fit(X, y_rain)
        print(f"✅ Rain MSE: {mean_squared_error(y_train, xgb_rain.predict(X)):.4f}")
        xgb_rain.save_model('api/weather_xgb_rain.json')
        
    except Exception as e:
        print(f"❌ Error training Weather Model: {e}")

def train_disease_model():
    print("\n🦠 Training Disease Prediction Model (Random Forest)...")
    try:
        data = []
        for _ in range(3000):
            temp = np.random.uniform(15, 40)
            hum = np.random.uniform(30, 100)
            crop_id = np.random.choice(['Rice', 'Wheat', 'Cotton', 'Sugarcane', 'Maize', 'Banana', 'Groundnut', 'Turmeric', 'Tea', 'Coffee'])
            
            disease = "Healthy"
            
            # Logic from disease_agent.py
            if crop_id == 'Rice':
                if hum > 85: disease = "Blast Disease"
                elif temp > 30 and hum > 70: disease = "Bacterial Blight"
            elif crop_id == 'Wheat':
                if hum > 70: disease = "Rust"
                elif temp < 20: disease = "Smut"
            elif crop_id == 'Maize':
                if hum > 80: disease = "Leaf Blight"
            elif crop_id == 'Cotton':
                if temp > 30: disease = "Root Rot"
                elif hum > 90: disease = "Boll Rot"
            elif crop_id == 'Sugarcane':
                if hum > 90: disease = "Red Rot"
                elif temp > 30: disease = "Wilt"
            elif crop_id == 'Groundnut':
                if hum > 80: disease = "Tikka Disease"
                elif hum > 75: disease = "Rust"
            elif crop_id == 'Turmeric':
                if hum > 80: disease = "Leaf Spot"
                elif hum > 90: disease = "Rhizome Rot"
            elif crop_id == 'Banana':
                if temp > 28: disease = "Panama Wilt"
                elif hum > 80: disease = "Sigatoka"
                
            data.append([crop_id, temp, hum, disease])
            
        df = pd.DataFrame(data, columns=['Crop', 'Temperature', 'Humidity', 'Disease'])
        
        # Encode Crop manually to match Agent logic (or use one-hot but Agent needs to replicate)
        # To simplify Agent integration, let's use LabelEncoder for Crop too or simple OneHot.
        # Agent has 'Crop' string.
        # Let's use OneHot encoding for training, and Agent will need to create OneHot vector.
        # Actually, simpler: Use separate models per crop? Or LabelEncode Crop.
        # Random Forest handles LabelEncoded categorical features okay-ish.
        
        le_crop = LabelEncoder()
        df['Crop_Encoded'] = le_crop.fit_transform(df['Crop'])
        
        X = df[['Crop_Encoded', 'Temperature', 'Humidity']]
        y = df['Disease']
        
        le_disease = LabelEncoder()
        y_encoded = le_disease.fit_transform(y)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
        
        rf = RandomForestClassifier(n_estimators=50, random_state=42)
        rf.fit(X_train, y_train)
        
        acc = accuracy_score(y_test, rf.predict(X_test))
        print(f"✅ Disease Model Accuracy: {acc * 100:.2f}%")
        
        joblib.dump(rf, 'api/disease_model.pkl')
        joblib.dump(le_disease, 'api/disease_label_encoder.pkl')
        joblib.dump(le_crop, 'api/crop_name_encoder.pkl') # Save this to encode crop name input
        
    except Exception as e:
        print(f"❌ Error training Disease Model: {e}")

if __name__ == "__main__":
    train_crop_model()
    train_weather_model()
    train_disease_model()
