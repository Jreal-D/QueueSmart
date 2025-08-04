import pandas as pd
import matplotlib.pyplot as plt

# Load generated data
df = pd.read_csv('data/sample_banking_data.csv')

# Basic validation
print("Data Validation Report:")
print(f"Total records: {len(df)}")
print(f"Unique customers: {df['customer_id'].nunique()}")
print(f"Branches: {df['branch'].unique()}")
print(f"Service types: {df['service_type'].unique()}")

# Check for reasonable service times
print(f"\nService duration stats:")
print(df['service_duration_minutes'].describe())

# Simple visualization
plt.figure(figsize=(10, 6))
df['service_type'].value_counts().plot(kind='bar')
plt.title('Distribution of Service Types')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('data/service_distribution.png')
plt.show()

print("\nData validation complete!")