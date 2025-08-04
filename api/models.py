from flask import Flask
from datetime import datetime
import json

class PredictionRequest:
    """Model for prediction request data"""
    
    def __init__(self, branch, service_type, hour, day_of_week, 
                 service_duration, current_queue_length):
        self.branch = branch
        self.service_type = service_type
        self.hour = hour
        self.day_of_week = day_of_week
        self.service_duration = service_duration
        self.current_queue_length = current_queue_length
    
    def to_dict(self):
        return {
            'branch': self.branch,
            'service_type': self.service_type,
            'hour': self.hour,
            'day_of_week': self.day_of_week,
            'service_duration': self.service_duration,
            'current_queue_length': self.current_queue_length
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            branch=data.get('branch'),
            service_type=data.get('service_type'),
            hour=data.get('hour'),
            day_of_week=data.get('day_of_week'),
            service_duration=data.get('service_duration'),
            current_queue_length=data.get('current_queue_length')
        )

class PredictionResponse:
    """Model for prediction response data"""
    
    def __init__(self, wait_time_minutes, confidence_level, branch, 
                 queue_position, estimated_service_time, timestamp):
        self.wait_time_minutes = wait_time_minutes
        self.confidence_level = confidence_level
        self.branch = branch
        self.queue_position = queue_position
        self.estimated_service_time = estimated_service_time
        self.timestamp = timestamp
    
    def to_dict(self):
        return {
            'wait_time_minutes': round(self.wait_time_minutes, 1),
            'confidence_level': self.confidence_level,
            'branch': self.branch,
            'queue_position': self.queue_position,
            'estimated_service_time': self.estimated_service_time,
            'timestamp': self.timestamp,
            'status': 'success'
        }

class ErrorResponse:
    """Model for error responses"""
    
    def __init__(self, error_code, message, details=None):
        self.error_code = error_code
        self.message = message
        self.details = details
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        response = {
            'status': 'error',
            'error_code': self.error_code,
            'message': self.message,
            'timestamp': self.timestamp
        }
        if self.details:
            response['details'] = self.details
        return response