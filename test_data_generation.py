from data.data_generator import generate_dataset
from datetime import datetime, timedelta
import pandas as pd

# Test data generation
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 1, 7)  # One week
branches = ["Victoria Island", "Ikeja"]

print("Generating synthetic data...")
df = generate_dataset(start_date, end_date, branches)

print(f"Generated {len(df)} customer records")
print("\nFirst 10 records:")
print(df.head(10))

print("\nData summary:")
print(df.describe())

# Save to CSV
df.to_csv('data/sample_banking_data.csv', index=False)
print("\nData saved to data/sample_banking_data.csv")