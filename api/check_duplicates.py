import pandas as pd
df = pd.read_csv('api/Soil data.csv')
print("Soil Data Stats:")
print(f"Shape: {df.shape}")
print(f"Unique Districts: {df['District'].nunique()}")
print(df['District'].value_counts().head())

yield_df = pd.read_csv('api/Tamilnadu agriculture yield data.csv')
print("\nYield Data Stats:")
print(f"Shape: {yield_df.shape}")
