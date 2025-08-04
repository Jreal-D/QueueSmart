import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set style for plots
plt.style.use('default')
sns.set_palette("husl")

def load_data(file_path):
    """Load the synthetic banking data"""
    df = pd.read_csv(file_path)
    
    # Convert arrival_time to datetime
    df['arrival_time'] = pd.to_datetime(df['arrival_time'])
    
    print(f"Loaded {len(df)} records")
    print(f"Date range: {df['arrival_time'].min()} to {df['arrival_time'].max()}")
    
    return df

def clean_data(df):
    """Clean and validate the data"""
    
    # Remove any duplicate customer IDs (shouldn't happen but good practice)
    initial_count = len(df)
    df = df.drop_duplicates(subset=['customer_id'])
    
    # Remove any invalid service durations
    df = df[df['service_duration_minutes'] > 0]
    df = df[df['service_duration_minutes'] <= 120]  # Cap at 2 hours
    
    # Sort by arrival time
    df = df.sort_values('arrival_time').reset_index(drop=True)
    
    print(f"Cleaned data: {len(df)} records (removed {initial_count - len(df)} invalid records)")
    
    return df

def create_time_features(df):
    """Create time-based features for analysis"""
    
    df = df.copy()
    
    # Extract time components
    df['hour'] = df['arrival_time'].dt.hour
    df['day_of_week'] = df['arrival_time'].dt.dayofweek  # 0=Monday
    df['day_name'] = df['arrival_time'].dt.day_name()
    df['date'] = df['arrival_time'].dt.date
    df['month'] = df['arrival_time'].dt.month
    
    # Create time periods
    df['time_period'] = df['hour'].apply(lambda x: 
        'Morning' if 8 <= x < 12 else
        'Afternoon' if 12 <= x < 16 else
        'Other'
    )
    
    # Add business context features
    df['is_peak_hour'] = df['hour'].isin([9, 10, 11, 13, 14, 15])
    df['is_monday_friday'] = df['day_of_week'].isin([0, 4])  # Monday=0, Friday=4
    
    print("Time features created successfully")
    return df

def calculate_queue_metrics(df):
    """Calculate queue-related metrics"""
    
    df = df.copy()
    df_sorted = df.sort_values(['branch', 'arrival_time']).reset_index(drop=True)
    
    queue_data = []
    
    for branch in df_sorted['branch'].unique():
        branch_data = df_sorted[df_sorted['branch'] == branch].copy()
        
        current_queue = []
        
        for idx, row in branch_data.iterrows():
            arrival_time = row['arrival_time']
            service_duration = row['service_duration_minutes']
            
            # Remove customers who have finished service
            current_queue = [customer for customer in current_queue 
                           if customer['finish_time'] > arrival_time]
            
            # Calculate wait time based on queue
            if len(current_queue) == 0:
                wait_time = 0
                service_start = arrival_time
            else:
                # Wait time is when the last person in queue finishes
                last_finish = max([customer['finish_time'] for customer in current_queue])
                service_start = last_finish
                wait_time = (service_start - arrival_time).total_seconds() / 60  # in minutes
            
            service_end = service_start + timedelta(minutes=service_duration)
            
            # Add this customer to queue
            current_queue.append({
                'customer_id': row['customer_id'],
                'finish_time': service_end
            })
            
            queue_data.append({
                'customer_id': row['customer_id'],
                'wait_time_minutes': wait_time,
                'queue_length_on_arrival': len(current_queue) - 1,
                'service_start_time': service_start,
                'service_end_time': service_end
            })
    
    # Merge back with original data
    queue_df = pd.DataFrame(queue_data)
    df_final = df.merge(queue_df, on='customer_id')
    
    print("Queue metrics calculated successfully")
    return df_final

def analyze_customer_patterns(df):
    """Analyze customer arrival and service patterns"""
    
    print("=== CUSTOMER PATTERNS ANALYSIS ===\n")
    
    # Daily patterns
    daily_customers = df.groupby(['date', 'branch']).size().reset_index(name='customer_count')
    avg_daily = daily_customers.groupby('branch')['customer_count'].mean()
    
    print("Average daily customers by branch:")
    for branch, avg in avg_daily.items():
        print(f"  {branch}: {avg:.1f} customers")
    
    # Hourly patterns
    hourly_avg = df.groupby(['hour', 'branch']).size().unstack(fill_value=0).mean(axis=1)
    
    print(f"\nPeak hours across all branches:")
    peak_hours = hourly_avg.nlargest(3)
    for hour, count in peak_hours.items():
        print(f"  {hour}:00 - {count:.1f} average customers")
    
    # Service type distribution
    service_dist = df['service_type'].value_counts(normalize=True) * 100
    print(f"\nService type distribution:")
    for service, pct in service_dist.items():
        print(f"  {service}: {pct:.1f}%")

def create_visualizations(df):
    """Create visualizations for data analysis"""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. Hourly customer distribution
    hourly_data = df.groupby('hour').size()
    axes[0, 0].bar(hourly_data.index, hourly_data.values)
    axes[0, 0].set_title('Customer Arrivals by Hour')
    axes[0, 0].set_xlabel('Hour of Day')
    axes[0, 0].set_ylabel('Number of Customers')
    
    # 2. Service duration by type
    df.boxplot(column='service_duration_minutes', by='service_type', ax=axes[0, 1])
    axes[0, 1].set_title('Service Duration by Type')
    axes[0, 1].set_xlabel('Service Type')
    axes[0, 1].set_ylabel('Duration (minutes)')
    plt.setp(axes[0, 1].xaxis.get_majorticklabels(), rotation=45)
    
    # 3. Wait time distribution
    axes[1, 0].hist(df['wait_time_minutes'], bins=30, alpha=0.7)
    axes[1, 0].set_title('Wait Time Distribution')
    axes[1, 0].set_xlabel('Wait Time (minutes)')
    axes[1, 0].set_ylabel('Frequency')
    
    # 4. Daily patterns by branch
    daily_branch = df.groupby(['day_name', 'branch']).size().unstack(fill_value=0)
    daily_branch.plot(kind='bar', ax=axes[1, 1])
    axes[1, 1].set_title('Daily Customers by Branch')
    axes[1, 1].set_xlabel('Day of Week')
    axes[1, 1].set_ylabel('Number of Customers')
    axes[1, 1].legend(title='Branch')
    plt.setp(axes[1, 1].xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    plt.savefig('data/analysis_plots.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Visualizations saved to data/analysis_plots.png")

def process_banking_data(file_path):
    """Complete data processing pipeline"""
    
    print("Starting data processing pipeline...\n")
    
    # Load and clean data
    df = load_data(file_path)
    df = clean_data(df)
    
    # Create features
    df = create_time_features(df)
    df = calculate_queue_metrics(df)
    
    # Analyze patterns
    analyze_customer_patterns(df)
    
    # Create visualizations
    create_visualizations(df)
    
    # Save processed data
    output_file = 'data/processed_banking_data.csv'
    df.to_csv(output_file, index=False)
    print(f"\nProcessed data saved to {output_file}")
    
    return df