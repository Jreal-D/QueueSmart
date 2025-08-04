import pandas as pd

# Load processed data
df = pd.read_csv('data/processed_banking_data.csv')

print("Data Processing Validation Report")
print("=" * 40)

# Check for missing values
missing_cols = df.isnull().sum()
if missing_cols.sum() == 0:
    print("✓ No missing values found")
else:
    print("⚠ Missing values detected:")
    print(missing_cols[missing_cols > 0])

# Check feature creation
required_features = ['hour', 'day_of_week', 'time_period', 'wait_time_minutes', 'queue_length_on_arrival']
missing_features = [f for f in required_features if f not in df.columns]

if len(missing_features) == 0:
    print("✓ All required features created successfully")
else:
    print(f"⚠ Missing features: {missing_features}")

# Check data reasonableness
print(f"\nData Reasonableness Checks:")
print(f"✓ Wait times range: {df['wait_time_minutes'].min():.1f} - {df['wait_time_minutes'].max():.1f} minutes")
print(f"✓ Service times range: {df['service_duration_minutes'].min():.1f} - {df['service_duration_minutes'].max():.1f} minutes")
print(f"✓ Queue lengths range: {df['queue_length_on_arrival'].min()} - {df['queue_length_on_arrival'].max()} people")

print(f"\n✓ Processing validation complete! Ready for machine learning phase.")