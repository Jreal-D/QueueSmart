import os
import sys
from datetime import datetime, timedelta
import joblib
import numpy as np

# Add parent directory to path to import our models
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Now import from the models directory
sys.path.append(os.path.join(parent_dir, 'models'))
from .ml_predictor import predict_wait_time, load_model

class ModelManager:
    """Manages the ML model loading and predictions"""
    
    def __init__(self):
        self.model_data = None
        self.model_loaded = False
        self.load_model()
    
    def load_model(self):
        """Load the trained model"""
        try:
            # Get the correct path to the model file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)

            # ADD THESE DEBUG LINES:
            print(f"DEBUG: current_dir = {current_dir}")
            print(f"DEBUG: parent_dir = {parent_dir}")
            print(f"DEBUG: Files in parent_dir = {os.listdir(parent_dir) if os.path.exists(parent_dir) else 'NOT_FOUND'}")
            models_dir = os.path.join(parent_dir, 'models')
            print(f"DEBUG: models_dir = {models_dir}")
            print(f"DEBUG: models_dir exists = {os.path.exists(models_dir)}")
            if os.path.exists(models_dir):
                print(f"DEBUG: Files in models_dir = {os.listdir(models_dir)}")

            sys.path.insert(0, parent_dir)
            # Now import from the models directory
            sys.path.append(os.path.join(parent_dir, 'models'))
            from ml_predictor import predict_wait_time, load_model
            
            model_path = os.path.join(project_root, 'models', 'random_forest_tuned_model.joblib')
            
            if os.path.exists(model_path):
                self.model_data = load_model(model_path)
                self.model_loaded = True
                print(f"Model loaded successfully: {self.model_data['model_name']}")
            else:
                print(f"Model file not found: {model_path}")
                self.model_loaded = False
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            self.model_loaded = False
    
    def is_model_ready(self):
        """Check if model is loaded and ready"""
        return self.model_loaded and self.model_data is not None
    
    def get_prediction(self, branch, service_type, hour, day_of_week, 
                      service_duration, current_queue_length):
        """Get wait time prediction"""
        if not self.is_model_ready():
            raise Exception("Model not loaded")
        
        try:
            prediction = predict_wait_time(
                self.model_data, branch, service_type, hour, 
                day_of_week, service_duration, current_queue_length
            )
            return prediction
        except Exception as e:
            raise Exception(f"Prediction error: {str(e)}")
    
    def get_model_info(self):
        """Get information about the loaded model"""
        if not self.is_model_ready():
            return None
        
        return {
            'model_name': self.model_data['model_name'],
            'trained_date': self.model_data['timestamp'],
            'features': self.model_data['feature_columns'],
            'status': 'active'
        }

class RequestValidator:
    """Validates API requests"""
    
    @staticmethod
    def validate_prediction_request(data):
        """Validate prediction request data"""
        required_fields = [
            'branch', 'service_type', 'hour', 'day_of_week',
            'service_duration', 'current_queue_length'
        ]
        
        # Check required fields
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        # Validate data types and ranges
        try:
            hour = int(data['hour'])
            if not (8 <= hour <= 16):
                return False, "Hour must be between 8 and 16 (banking hours)"
            
            day_of_week = int(data['day_of_week'])
            if not (0 <= day_of_week <= 6):
                return False, "Day of week must be between 0 (Monday) and 6 (Sunday)"
            
            service_duration = float(data['service_duration'])
            if not (1 <= service_duration <= 120):
                return False, "Service duration must be between 1 and 120 minutes"
            
            queue_length = int(data['current_queue_length'])
            if not (0 <= queue_length <= 100):
                return False, "Queue length must be between 0 and 100"
            
            # Validate branch and service type
            valid_branches = ["Victoria Island", "Ikeja", "Surulere", "Abuja", "Port Harcourt"]
            if data['branch'] not in valid_branches:
                return False, f"Invalid branch. Must be one of: {', '.join(valid_branches)}"
            
            valid_services = ["Account Opening", "Cash Withdrawal", "Transfer", "Loan Application", "General Inquiry"]
            if data['service_type'] not in valid_services:
                return False, f"Invalid service type. Must be one of: {', '.join(valid_services)}"
            
        except (ValueError, TypeError) as e:
            return False, f"Invalid data type: {str(e)}"
        
        return True, "Valid"

def calculate_confidence_level(wait_time, queue_length):
    """Calculate confidence level for prediction"""
    # Simple confidence calculation based on queue length and wait time
    if queue_length == 0:
        return "High"
    elif queue_length <= 3:
        return "Medium"
    else:
        return "Low"

def calculate_estimated_service_time(wait_time_minutes):
    """Calculate estimated service completion time"""
    now = datetime.now()
    service_time = now + timedelta(minutes=wait_time_minutes)
    return service_time.strftime("%H:%M")
