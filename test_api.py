import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check endpoint...")
    
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_prediction():
    """Test the prediction endpoint"""
    print("Testing prediction endpoint...")
    
    # Test data
    test_data = {
        "branch": "Victoria Island",
        "service_type": "Transfer",
        "hour": 10,
        "day_of_week": 1,
        "service_duration": 5,
        "current_queue_length": 3
    }
    
    response = requests.post(
        f"{BASE_URL}/api/predict",
        json=test_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_invalid_prediction():
    """Test prediction with invalid data"""
    print("Testing prediction with invalid data...")
    
    # Invalid test data (missing required fields)
    invalid_data = {
        "branch": "Victoria Island",
        "service_type": "Transfer"
        # Missing other required fields
    }
    
    response = requests.post(
        f"{BASE_URL}/api/predict",
        json=invalid_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_model_status():
    """Test model status endpoint"""
    print("Testing model status endpoint...")
    
    response = requests.get(f"{BASE_URL}/api/model/status")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_branches():
    """Test branches endpoint"""
    print("Testing branches endpoint...")
    
    response = requests.get(f"{BASE_URL}/api/branches")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_services():
    """Test services endpoint"""
    print("Testing services endpoint...")
    
    response = requests.get(f"{BASE_URL}/api/services")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def main():
    print("QueueSmart API Testing Suite")
    print("=" * 50)
    print("Make sure the API is running first with: python api/app.py")
    print("=" * 50)
    
    try:
        test_health_check()
        test_model_status()
        test_branches()
        test_services()
        test_prediction()
        test_invalid_prediction()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API. Make sure it's running on localhost:5000")
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    main()