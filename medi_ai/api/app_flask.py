"""
Flask application for MediVision TB detection.
Lightweight alternative to FastAPI for desktop app integration.

Run with: flask --app api.app_flask run --host 0.0.0.0 --port 8000
Or: python api/app_flask.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import tempfile
import json
from typing import Dict, Any

from inference.medivision import MediVisionInference
import config


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for desktop apps


# Global inference engine
inference_engine: MediVisionInference = None


def initialize_inference_engine():
    """Initialize inference engine on app startup."""
    global inference_engine
    
    logger.info("🚀 Initializing MediVision inference engine...")
    try:
        inference_engine = MediVisionInference()
        logger.info("✓ Inference engine initialized")
    except Exception as e:
        logger.error(f"✗ Failed to initialize inference engine: {e}")
        raise


def error_response(message: str, code: str = "ERROR", status_code: int = 400) -> tuple:
    """
    Create error response.
    
    Args:
        message: Error message
        code: Error code
        status_code: HTTP status code
        
    Returns:
        Tuple of (response_dict, http_status_code)
    """
    return jsonify({
        "status": "error",
        "error_code": code,
        "detail": message
    }), status_code


def success_response(data: Dict[str, Any], status_code: int = 200) -> tuple:
    """
    Create success response.
    
    Args:
        data: Response data
        status_code: HTTP status code
        
    Returns:
        Tuple of (response_dict, http_status_code)
    """
    return jsonify({
        "status": "success",
        **data
    }), status_code


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check() -> tuple:
    """
    Health check endpoint.
    
    Returns:
        JSON response with health status
    """
    if inference_engine is None:
        return error_response("Inference engine not initialized", "ENGINE_NOT_INIT", 503)
    
    info = inference_engine.get_model_info()
    image_loaded = info['image_model']['loaded']
    tabular_loaded = info['tabular_model']['loaded']
    
    status = "healthy" if (image_loaded and tabular_loaded) else "degraded"
    message = (
        "All models loaded" if (image_loaded and tabular_loaded)
        else f"Image: {image_loaded}, Tabular: {tabular_loaded}"
    )
    
    return success_response({
        "status": status,
        "image_model_loaded": image_loaded,
        "tabular_model_loaded": tabular_loaded,
        "device": info['device'],
        "message": message
    })


# ============================================================================
# IMAGE PREDICTION ENDPOINTS
# ============================================================================

@app.route('/predict/image', methods=['POST'])
def predict_image() -> tuple:
    """
    Predict TB from chest X-ray image (file path).
    
    JSON body:
        {
            "image_path": "/path/to/xray.jpg"
        }
    
    Returns:
        JSON response with TB probability and prediction
    """
    if inference_engine is None:
        return error_response("Inference engine not initialized", "ENGINE_NOT_INIT", 503)
    
    if inference_engine.image_model is None:
        return error_response("Image model not loaded", "MODEL_NOT_LOADED", 503)
    
    try:
        data = request.get_json()
        if not data or 'image_path' not in data:
            return error_response("Missing required field: image_path", "INVALID_INPUT")
        
        image_path = data['image_path']
        result = inference_engine.predict_image(image_path)
        return success_response(result)
    
    except FileNotFoundError as e:
        logger.error(f"Image not found: {e}")
        return error_response(f"Image not found: {e}", "FILE_NOT_FOUND", 404)
    
    except Exception as e:
        logger.error(f"Image prediction error: {e}")
        return error_response(f"Prediction failed: {str(e)}", "PREDICTION_ERROR")


@app.route('/predict/image/upload', methods=['POST'])
def predict_image_upload() -> tuple:
    """
    Predict TB from uploaded image file.
    
    Form data:
        - file: Image file (JPEG/PNG)
    
    Returns:
        JSON response with prediction
    """
    if inference_engine is None:
        return error_response("Inference engine not initialized", "ENGINE_NOT_INIT", 503)
    
    if inference_engine.image_model is None:
        return error_response("Image model not loaded", "MODEL_NOT_LOADED", 503)
    
    try:
        # Check if file in request
        if 'file' not in request.files:
            return error_response("No file provided", "NO_FILE")
        
        file = request.files['file']
        if file.filename == '':
            return error_response("No file selected", "NO_FILE")
        
        # Save temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            file.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        # Predict
        result = inference_engine.predict_image(tmp_path)
        
        # Clean up
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        
        return success_response(result)
    
    except Exception as e:
        logger.error(f"Upload prediction error: {e}")
        return error_response(f"Prediction failed: {str(e)}", "PREDICTION_ERROR")


# ============================================================================
# TABULAR PREDICTION ENDPOINT
# ============================================================================

@app.route('/predict/tabular', methods=['POST'])
def predict_tabular() -> tuple:
    """
    Predict TB from clinical features.
    
    JSON body:
        {
            "clinical_data": {
                "age": 45,
                "bmi": 22.5,
                "cough_duration": 3,
                ...
            }
        }
    
    Or:
        {
            "clinical_data": [45, 22.5, 3, ...]
        }
    
    Returns:
        JSON response with TB probability
    """
    if inference_engine is None:
        return error_response("Inference engine not initialized", "ENGINE_NOT_INIT", 503)
    
    if inference_engine.tabular_model is None:
        return error_response("Tabular model not loaded", "MODEL_NOT_LOADED", 503)
    
    try:
        data = request.get_json()
        if not data or 'clinical_data' not in data:
            return error_response("Missing required field: clinical_data", "INVALID_INPUT")
        
        clinical_data = data['clinical_data']
        result = inference_engine.predict_tabular(clinical_data)
        return success_response(result)
    
    except ValueError as e:
        logger.error(f"Tabular data validation error: {e}")
        return error_response(f"Invalid data: {str(e)}", "VALIDATION_ERROR")
    
    except Exception as e:
        logger.error(f"Tabular prediction error: {e}")
        return error_response(f"Prediction failed: {str(e)}", "PREDICTION_ERROR")


# ============================================================================
# FUSION PREDICTION ENDPOINT
# ============================================================================

@app.route('/predict/fusion', methods=['POST'])
def predict_fusion() -> tuple:
    """
    Predict TB using weighted fusion (70% image + 30% tabular).
    
    JSON body:
        {
            "image_path": "/path/to/xray.jpg",
            "clinical_data": {
                "age": 45,
                "bmi": 22.5,
                ...
            }
        }
    
    Returns:
        JSON response with fused probability and individual predictions
    """
    if inference_engine is None:
        return error_response("Inference engine not initialized", "ENGINE_NOT_INIT", 503)
    
    if inference_engine.image_model is None or inference_engine.tabular_model is None:
        return error_response("One or more models not loaded", "MODEL_NOT_LOADED", 503)
    
    try:
        data = request.get_json()
        if not data or 'image_path' not in data or 'clinical_data' not in data:
            return error_response("Missing required fields: image_path, clinical_data", "INVALID_INPUT")
        
        image_path = data['image_path']
        clinical_data = data['clinical_data']
        
        result = inference_engine.predict_fusion(image_path, clinical_data)
        return success_response(result)
    
    except FileNotFoundError as e:
        logger.error(f"Image not found: {e}")
        return error_response(f"Image not found", "FILE_NOT_FOUND", 404)
    
    except Exception as e:
        logger.error(f"Fusion prediction error: {e}")
        return error_response(f"Prediction failed: {str(e)}", "PREDICTION_ERROR")


# ============================================================================
# CONFIGURATION ENDPOINTS
# ============================================================================

@app.route('/config', methods=['GET'])
def get_config() -> tuple:
    """
    Get current inference configuration.
    
    Returns:
        JSON response with current weights and threshold
    """
    if inference_engine is None:
        return error_response("Inference engine not initialized", "ENGINE_NOT_INIT", 503)
    
    return success_response({
        "image_weight": inference_engine.image_weight,
        "tabular_weight": inference_engine.tabular_weight,
        "decision_threshold": inference_engine.threshold
    })


@app.route('/config', methods=['POST'])
def update_config() -> tuple:
    """
    Update inference configuration.
    
    JSON body:
        {
            "image_weight": 0.70,
            "tabular_weight": 0.30,
            "decision_threshold": 0.50
        }
    
    Returns:
        JSON response with updated configuration
    """
    if inference_engine is None:
        return error_response("Inference engine not initialized", "ENGINE_NOT_INIT", 503)
    
    try:
        data = request.get_json()
        
        # Update weights if provided
        if 'image_weight' in data and 'tabular_weight' in data:
            inference_engine.set_fusion_weights(data['image_weight'], data['tabular_weight'])
        
        # Update threshold if provided
        if 'decision_threshold' in data:
            inference_engine.set_decision_threshold(data['decision_threshold'])
        
        return success_response({
            "image_weight": inference_engine.image_weight,
            "tabular_weight": inference_engine.tabular_weight,
            "decision_threshold": inference_engine.threshold
        })
    
    except ValueError as e:
        logger.error(f"Config update validation error: {e}")
        return error_response(f"Invalid configuration: {str(e)}", "VALIDATION_ERROR")
    
    except Exception as e:
        logger.error(f"Config update error: {e}")
        return error_response(f"Update failed: {str(e)}", "CONFIG_ERROR")


# ============================================================================
# MODEL MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/models/info', methods=['GET'])
def get_models_info() -> tuple:
    """
    Get information about loaded models.
    
    Returns:
        JSON response with model details
    """
    if inference_engine is None:
        return error_response("Inference engine not initialized", "ENGINE_NOT_INIT", 503)
    
    info = inference_engine.get_model_info()
    return success_response(info)


@app.route('/models/reload', methods=['POST'])
def reload_models() -> tuple:
    """
    Reload all models from disk.
    
    Returns:
        JSON response with status
    """
    if inference_engine is None:
        return error_response("Inference engine not initialized", "ENGINE_NOT_INIT", 503)
    
    try:
        inference_engine.reload_models()
        return success_response({
            "message": "Models reloaded successfully"
        })
    except Exception as e:
        logger.error(f"Model reload error: {e}")
        return error_response(f"Reload failed: {str(e)}", "RELOAD_ERROR")


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.route('/', methods=['GET'])
def root() -> dict:
    """
    Get API information.
    
    Returns:
        JSON response with API details and endpoints
    """
    return jsonify({
        "name": "MediVision TB Detection API",
        "version": "1.0.0",
        "framework": "Flask",
        "description": "Multi-modal TB detection using DenseNet121 + XGBoost",
        "endpoints": {
            "health": "/health",
            "predictions": {
                "image": "/predict/image",
                "image_upload": "/predict/image/upload",
                "tabular": "/predict/tabular",
                "fusion": "/predict/fusion"
            },
            "configuration": {
                "get": "/config",
                "update": "/config"
            },
            "models": {
                "info": "/models/info",
                "reload": "/models/reload"
            }
        }
    })


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return error_response("Endpoint not found", "NOT_FOUND", 404)


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return error_response("Method not allowed", "METHOD_NOT_ALLOWED", 405)


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return error_response("Internal server error", "INTERNAL_ERROR", 500)


# ============================================================================
# APP CONTEXT
# ============================================================================

@app.before_request
def before_request():
    """Check if inference engine is initialized."""
    if inference_engine is None and request.endpoint not in ['root', 'health']:
        pass  # Allow request, will be handled by endpoint


if __name__ == "__main__":
    logger.info("Starting MediVision Flask server...")
    initialize_inference_engine()
    
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )
#check check check