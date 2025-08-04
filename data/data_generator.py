import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import json
def generate_customer_arrivals(date, branch, total_customers=None):
    """Generate realistic customer arrival times for a specific day"""
    
    if total_customers is None:
        # More customers on Mondays and Fridays, fewer on Wednesdays
        day_multiplier = {0: 1.3, 1: 1.0, 2: 0.8, 3: 0.7, 4: 1.2}
        base_customers = random.randint(80, 150)
        total_customers = int(base_customers * day_multiplier[date.weekday()])
    
    arrivals = []
    
    # Generate arrival times throughout the day
    for i in range(total_customers):
        # Peak hours get more customers
        hour_weights = [0.05, 0.15, 0.20, 0.15, 0.10, 0.15, 0.10, 0.10]  # 8AM to 4PM
        hour = np.random.choice(range(8, 16), p=hour_weights)
        minute = random.randint(0, 59)
        
        arrival_time = date.replace(hour=hour, minute=minute)
        
        arrivals.append({
            'arrival_time': arrival_time,
            'branch': branch,
            'customer_id': f"CUST_{i+1}_{date.strftime('%Y%m%d')}"
        })
    
    return sorted(arrivals, key=lambda x: x['arrival_time'])
def generate_service_data(arrivals):
    """Generate service types and durations for customers"""
    
    service_types = {
        "Cash Withdrawal": {"min": 2, "max": 8, "weight": 0.4},
        "Transfer": {"min": 3, "max": 10, "weight": 0.25},
        "Account Opening": {"min": 15, "max": 45, "weight": 0.15},
        "General Inquiry": {"min": 1, "max": 5, "weight": 0.15},
        "Loan Application": {"min": 20, "max": 60, "weight": 0.05}
    }
    
    services = []
    
    for arrival in arrivals:
        # Choose service type based on weights
        service_type = np.random.choice(
            list(service_types.keys()),
            p=[service_types[s]["weight"] for s in service_types.keys()]
        )
        
        # Generate service duration
        min_time = service_types[service_type]["min"]
        max_time = service_types[service_type]["max"]
        duration = random.randint(min_time, max_time)
        
        services.append({
            'customer_id': arrival['customer_id'],
            'service_type': service_type,
            'service_duration_minutes': duration,
            'arrival_time': arrival['arrival_time'],
            'branch': arrival['branch']
        })
    
    return services
def generate_daily_data(date, branch):
    """Generate complete data for one day at one branch"""
    
    # Generate customer arrivals
    arrivals = generate_customer_arrivals(date, branch)
    
    # Generate service data
    services = generate_service_data(arrivals)
    
    # Convert to DataFrame
    df = pd.DataFrame(services)
    
    return df

def generate_dataset(start_date, end_date, branches):
    """Generate dataset for multiple days and branches"""
    
    all_data = []
    current_date = start_date
    
    while current_date <= end_date:
        # Only generate for working days (Monday to Friday)
        if current_date.weekday() < 5:
            for branch in branches:
                daily_data = generate_daily_data(current_date, branch)
                all_data.append(daily_data)
        
        current_date += timedelta(days=1)
    
    # Combine all data
    final_df = pd.concat(all_data, ignore_index=True)
    return final_df