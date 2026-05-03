"""
FastAPI application for MediVision TB detection.
RESTful API for image, tabular, and fusion predictions.

Run with: uvicorn api.app_fastapi:app --host 0.0.0.0 --port 8000 --reload
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from typing import Optional

from inference.medivision import MediVisionInference, get_inference_engine
from api.schemas import (
    ImagePredictionRequest, ImagePredictionResponse,
    TabularPredictionRequest, TabularPredictionResponse,
    FusionPredictionRequest, FusionPredictionResponse,
    ConfigRequest, ConfigResponse,
    ModelInfoResponse, ErrorResponse, HealthCheckResponse
)
import config


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Global inference engine
inference_engine: Optional[MediVisionInference] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager.
    Initializes inference engine on startup, cleans up on shutdown.
    """
    global inference_engine
    
    # Startup
    logger.info("🚀 Starting MediVision FastAPI server...")
    try:
        inference_engine = get_inference_engine()
        logger.info("✓ Inference engine initialized")
    except Exception as e:
        logger.error(f"✗ Failed to initialize inference engine: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down MediVision server...")
    if inference_engine:
        inference_engine.unload_models()
    logger.info("✓ Server shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="MediVision TB Detection API",
    description="Multi-modal TB detection using DenseNet121 + XGBoost fusion",
    version="1.0.0",
    lifespan=lifespan
)


# Add CORS middleware for desktop app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for desktop apps
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["Health"],
    summary="Health check"
)
async def health_check() -> HealthCheckResponse:
    """
    Check API health and model availability.
    
    Returns:
        HealthCheckResponse with status and loaded models
    """
    if inference_engine is None:
        raise HTTPException(status_code=503, detail="Inference engine not initialized")
    
    info = inference_engine.get_model_info()
    
    image_loaded = info['image_model']['loaded']
    tabular_loaded = info['tabular_model']['loaded']
    
    status = "healthy" if (image_loaded and tabular_loaded) else "degraded"
    message = (
        "All models loaded" if (image_loaded and tabular_loaded)
        else f"Image: {image_loaded}, Tabular: {tabular_loaded}"
    )
    
    return HealthCheckResponse(
        status=status,
        image_model_loaded=image_loaded,
        tabular_model_loaded=tabular_loaded,
        device=info['device'],
        message=message
    )


# ============================================================================
# IMAGE PREDICTION ENDPOINT
# ============================================================================

@app.post(
    "/predict/image",
    response_model=ImagePredictionResponse,
    tags=["Predictions"],
    summary="Predict TB from chest X-ray"
)
async def predict_image(request: ImagePredictionRequest) -> ImagePredictionResponse:
    """
    Predict TB probability from chest X-ray image.
    
    Args:
        request: ImagePredictionRequest with image_path
        
    Returns:
        ImagePredictionResponse with TB probability and prediction
        
    Raises:
        HTTPException: If image not found or inference fails
    """
    if inference_engine is None:
        raise HTTPException(status_code=503, detail="Inference engine not initialized")
    
    if inference_engine.image_model is None:
        raise HTTPException(status_code=503, detail="Image model not loaded")
    
    try:
        result = inference_engine.predict_image(request.image_path)
        return ImagePredictionResponse(**result)
    
    except FileNotFoundError as e:
        logger.error(f"Image not found: {e}")
        raise HTTPException(status_code=404, detail=f"Image not found: {request.image_path}")
    
    except Exception as e:
        logger.error(f"Image prediction error: {e}")
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")


@app.post(
    "/predict/image/upload",
    response_model=ImagePredictionResponse,
    tags=["Predictions"],
    summary="Predict TB from uploaded X-ray"
)
async def predict_image_upload(file: UploadFile = File(...)) -> ImagePredictionResponse:
    """
    Predict TB from uploaded image file.
    
    Args:
        file: Uploaded image file (JPEG/PNG)
        
    Returns:
        ImagePredictionResponse with prediction
    """
    if inference_engine is None:
        raise HTTPException(status_code=503, detail="Inference engine not initialized")
    
    if inference_engine.image_model is None:
        raise HTTPException(status_code=503, detail="Image model not loaded")
    
    # Save uploaded file temporarily
    import tempfile
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Predict
        result = inference_engine.predict_image(tmp_path)
        return ImagePredictionResponse(**result)
    
    except Exception as e:
        logger.error(f"Upload prediction error: {e}")
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")
    
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# ============================================================================
# TABULAR PREDICTION ENDPOINT
# ============================================================================

@app.post(
    "/predict/tabular",
    response_model=TabularPredictionResponse,
    tags=["Predictions"],
    summary="Predict TB from clinical data"
)
async def predict_tabular(request: TabularPredictionRequest) -> TabularPredictionResponse:
    """
    Predict TB probability from clinical features.
    
    Args:
        request: TabularPredictionRequest with clinical_data
        
    Returns:
        TabularPredictionResponse with TB probability
        
    Raises:
        HTTPException: If tabular model not loaded or inference fails
    """
    if inference_engine is None:
        raise HTTPException(status_code=503, detail="Inference engine not initialized")
    
    if inference_engine.tabular_model is None:
        raise HTTPException(status_code=503, detail="Tabular model not loaded")
    
    try:
        result = inference_engine.predict_tabular(request.clinical_data)
        return TabularPredictionResponse(**result)
    
    except ValueError as e:
        logger.error(f"Tabular data validation error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")
    
    except Exception as e:
        logger.error(f"Tabular prediction error: {e}")
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")


# ============================================================================
# FUSION PREDICTION ENDPOINT
# ============================================================================

@app.post(
    "/predict/fusion",
    response_model=FusionPredictionResponse,
    tags=["Predictions"],
    summary="Predict TB from image + clinical data fusion"
)
async def predict_fusion(request: FusionPredictionRequest) -> FusionPredictionResponse:
    """
    Predict TB using weighted fusion of image and tabular models.
    
    Fusion: 70% Image + 30% Tabular
    
    Args:
        request: FusionPredictionRequest with image_path and clinical_data
        
    Returns:
        FusionPredictionResponse with fused probability
        
    Raises:
        HTTPException: If models not loaded or inference fails
    """
    if inference_engine is None:
        raise HTTPException(status_code=503, detail="Inference engine not initialized")
    
    if inference_engine.image_model is None or inference_engine.tabular_model is None:
        raise HTTPException(status_code=503, detail="One or more models not loaded")
    
    try:
        result = inference_engine.predict_fusion(request.image_path, request.clinical_data)
        return FusionPredictionResponse(**result)
    
    except FileNotFoundError as e:
        logger.error(f"Image not found: {e}")
        raise HTTPException(status_code=404, detail=f"Image not found: {request.image_path}")
    
    except Exception as e:
        logger.error(f"Fusion prediction error: {e}")
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")


# ============================================================================
# CONFIGURATION ENDPOINTS
# ============================================================================

@app.get(
    "/config",
    response_model=ConfigResponse,
    tags=["Configuration"],
    summary="Get current configuration"
)
async def get_config() -> ConfigResponse:
    """
    Get current inference configuration.
    
    Returns:
        ConfigResponse with current weights and threshold
    """
    if inference_engine is None:
        raise HTTPException(status_code=503, detail="Inference engine not initialized")
    
    return ConfigResponse(
        image_weight=inference_engine.image_weight,
        tabular_weight=inference_engine.tabular_weight,
        decision_threshold=inference_engine.threshold,
        status="success"
    )


@app.post(
    "/config",
    response_model=ConfigResponse,
    tags=["Configuration"],
    summary="Update configuration"
)
async def update_config(request: ConfigRequest) -> ConfigResponse:
    """
    Update inference configuration (weights, threshold).
    
    Args:
        request: ConfigRequest with new values
        
    Returns:
        ConfigResponse with updated configuration
        
    Raises:
        HTTPException: If update fails
    """
    if inference_engine is None:
        raise HTTPException(status_code=503, detail="Inference engine not initialized")
    
    try:
        # Update weights if provided
        if request.image_weight is not None and request.tabular_weight is not None:
            inference_engine.set_fusion_weights(request.image_weight, request.tabular_weight)
        
        # Update threshold if provided
        if request.decision_threshold is not None:
            inference_engine.set_decision_threshold(request.decision_threshold)
        
        return ConfigResponse(
            image_weight=inference_engine.image_weight,
            tabular_weight=inference_engine.tabular_weight,
            decision_threshold=inference_engine.threshold,
            status="success"
        )
    
    except Exception as e:
        logger.error(f"Configuration update error: {e}")
        raise HTTPException(status_code=400, detail=f"Update failed: {str(e)}")


# ============================================================================
# MODEL MANAGEMENT ENDPOINTS
# ============================================================================

@app.get(
    "/models/info",
    response_model=ModelInfoResponse,
    tags=["Models"],
    summary="Get model information"
)
async def get_models_info() -> ModelInfoResponse:
    """
    Get information about loaded models.
    
    Returns:
        ModelInfoResponse with model details
    """
    if inference_engine is None:
        raise HTTPException(status_code=503, detail="Inference engine not initialized")
    
    info = inference_engine.get_model_info()
    return ModelInfoResponse(
        **info,
        status="success"
    )


@app.post(
    "/models/reload",
    tags=["Models"],
    summary="Reload all models"
)
async def reload_models() -> dict:
    """
    Reload all models from disk.
    
    Useful if model files have been updated.
    
    Returns:
        Status message
    """
    if inference_engine is None:
        raise HTTPException(status_code=503, detail="Inference engine not initialized")
    
    try:
        inference_engine.reload_models()
        return {
            "status": "success",
            "message": "Models reloaded successfully"
        }
    except Exception as e:
        logger.error(f"Model reload error: {e}")
        raise HTTPException(status_code=500, detail=f"Reload failed: {str(e)}")


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get(
    "/",
    tags=["Info"],
    summary="API information"
)
async def root() -> dict:
    """
    Get API information and available endpoints.
    
    Returns:
        API information
    """
    return {
        "name": "MediVision TB Detection API",
        "version": "1.0.0",
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
            },
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "status": "error"
        }
    )


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting MediVision FastAPI server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
