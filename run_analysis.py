from data_processor import process_banking_data
import pandas as pd

# Run the complete analysis
print("QueueSmart Data Analysis Pipeline")
print("=" * 40)

# Process the data
df = process_banking_data('data/sample_banking_data.csv')

# Display summary statistics
print("\n=== SUMMARY STATISTICS ===")
print(f"Total customers analyzed: {len(df):,}")
print(f"Average wait time: {df['wait_time_minutes'].mean():.1f} minutes")
print(f"Maximum wait time: {df['wait_time_minutes'].max():.1f} minutes")
print(f"Average service duration: {df['service_duration_minutes'].mean():.1f} minutes")

# Show peak performance issues
print(f"\n=== PEAK PERFORMANCE INSIGHTS ===")
peak_wait = df[df['is_peak_hour'] == True]['wait_time_minutes'].mean()
normal_wait = df[df['is_peak_hour'] == False]['wait_time_minutes'].mean()

print(f"Average wait during peak hours: {peak_wait:.1f} minutes")
print(f"Average wait during normal hours: {normal_wait:.1f} minutes")
print(f"Peak hour impact: {((peak_wait/normal_wait - 1) * 100):.1f}% longer wait times")

print("\nAnalysis complete! Check the generated plots and processed data files.")