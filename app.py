from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from datetime import datetime
import json
import os

from api.models import PredictionRequest, PredictionResponse, ErrorResponse
from api.utils import ModelManager, RequestValidator, calculate_confidence_level, calculate_estimated_service_time

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Initialize model manager
model_manager = ModelManager()

# Dashboard Routes
@app.route('/dashboard')
@app.route('/dashboard/')
def dashboard():
    """Serve the dashboard HTML file"""
    dashboard_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dashboard', 'index.html')
    return send_file(dashboard_path)

@app.route('/dashboard/<path:filename>')
def dashboard_static(filename):
    """Serve dashboard static files (CSS, JS)"""
    dashboard_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dashboard')
    return send_from_directory(dashboard_dir, filename)

# Customer Interface Route
@app.route('/customer')
@app.route('/customer/')
def customer_interface():
    """Serve the customer interface HTML file"""
    customer_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'customer', 'index.html')
    return send_file(customer_path)

@app.route('/customer/<path:filename>')
def customer_static(filename):
    """Serve customer static files (CSS, JS)"""
    customer_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'customer')
    return send_from_directory(customer_dir, filename)

# Keep all your existing API routes exactly the same...
@app.route('/', methods=['GET'])
def home():
    """Health check endpoint"""
    return jsonify({
        'service': 'QueueSmart API',
        'version': '1.0.0',
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'model_ready': model_manager.is_model_ready(),
        'dashboard_url': '/dashboard',
        'customer_url': '/customer'  # Add this line
    })

@app.route('/api/predict', methods=['POST'])
def predict_wait_time():
    """Main prediction endpoint"""
    try:
        # Check if model is ready
        if not model_manager.is_model_ready():
            error = ErrorResponse(
                error_code="MODEL_NOT_READY",
                message="ML model is not loaded or ready",
                details="Please contact system administrator"
            )
            return jsonify(error.to_dict()), 503
        
        # Get request data
        if not request.is_json:
            error = ErrorResponse(
                error_code="INVALID_REQUEST",
                message="Request must be JSON",
                details="Content-Type must be application/json"
            )
            return jsonify(error.to_dict()), 400
        
        data = request.get_json()
        
        # Validate request
        is_valid, validation_message = RequestValidator.validate_prediction_request(data)
        if not is_valid:
            error = ErrorResponse(
                error_code="VALIDATION_ERROR",
                message="Invalid request data",
                details=validation_message
            )
            return jsonify(error.to_dict()), 400
        
        # Create prediction request
        pred_request = PredictionRequest.from_dict(data)
        
        # Get prediction
        wait_time = model_manager.get_prediction(
            branch=pred_request.branch,
            service_type=pred_request.service_type,
            hour=pred_request.hour,
            day_of_week=pred_request.day_of_week,
            service_duration=pred_request.service_duration,
            current_queue_length=pred_request.current_queue_length
        )
        
        # Calculate additional response data
        confidence = calculate_confidence_level(wait_time, pred_request.current_queue_length)
        estimated_time = calculate_estimated_service_time(wait_time)
        
        # Create response
        response = PredictionResponse(
            wait_time_minutes=wait_time,
            confidence_level=confidence,
            branch=pred_request.branch,
            queue_position=pred_request.current_queue_length + 1,
            estimated_service_time=estimated_time,
            timestamp=datetime.now().isoformat()
        )
        
        return jsonify(response.to_dict()), 200
        
    except Exception as e:
        error = ErrorResponse(
            error_code="INTERNAL_ERROR",
            message="Internal server error",
            details=str(e)
        )
        return jsonify(error.to_dict()), 500

@app.route('/api/model/status', methods=['GET'])
def model_status():
    """Get model status and information"""
    try:
        if model_manager.is_model_ready():
            model_info = model_manager.get_model_info()
            return jsonify({
                'status': 'success',
                'model_info': model_info,
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Model not loaded',
                'timestamp': datetime.now().isoformat()
            }), 503
    except Exception as e:
        error = ErrorResponse(
            error_code="STATUS_ERROR",
            message="Could not retrieve model status",
            details=str(e)
        )
        return jsonify(error.to_dict()), 500

@app.route('/api/branches', methods=['GET'])
def get_branches():
    """Get list of available branches"""
    branches = [
        "Victoria Island",
        "Ikeja", 
        "Surulere",
        "Abuja",
        "Port Harcourt"
    ]
    
    return jsonify({
        'status': 'success',
        'branches': branches,
        'count': len(branches),
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/services', methods=['GET'])
def get_services():
    """Get list of available service types"""
    services = [
        "Account Opening",
        "Cash Withdrawal", 
        "Transfer",
        "Loan Application",
        "General Inquiry"
    ]
    
    return jsonify({
        'status': 'success',
        'services': services,
        'count': len(services),
        'timestamp': datetime.now().isoformat()
    }), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    error_response = ErrorResponse(
        error_code="NOT_FOUND",
        message="Endpoint not found",
        details="Please check the API documentation for valid endpoints"
    )
    return jsonify(error_response.to_dict()), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    error_response = ErrorResponse(
        error_code="METHOD_NOT_ALLOWED",
        message="HTTP method not allowed for this endpoint",
        details="Please check the API documentation for valid HTTP methods"
    )
    return jsonify(error_response.to_dict()), 405

if __name__ == '__main__':
    print("Starting QueueSmart API with Dashboard...")
    print(f"Model ready: {model_manager.is_model_ready()}")
    print("API available at: http://localhost:5000")
    print("Dashboard available at: http://localhost:5000/dashboard")
    
    # Run in debug mode for development
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
