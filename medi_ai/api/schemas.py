"""
Pydantic schemas for MediVision API requests and responses.
Ensures type safety and automatic validation/documentation.
"""

from pydantic import BaseModel, Field, model_validator,validator
from typing import Optional, Dict, List, Union
from enum import Enum


class PredictionEnum(str, Enum):
    """Prediction result enum."""
    TB = "TB"
    NO_TB = "No TB"


class ImagePredictionRequest(BaseModel):
    """Schema for image prediction API request."""
    image_path: str = Field(..., description="Path to chest X-ray image (JPEG/PNG)")
    
    class Config:
        schema_extra = {
            "example": {
                "image_path": "/path/to/xray.jpg"
            }
        }


class ImagePredictionResponse(BaseModel):
    """Schema for image prediction API response."""
    probability: float = Field(..., ge=0, le=1, description="TB probability (0-1)")
    prediction: PredictionEnum = Field(..., description="TB or No TB")
    confidence: float = Field(..., ge=0, le=1, description="Confidence percentage")
    model: str = Field(..., description="Model used (DenseNet121)")
    status: str = Field(..., description="Status (success/error)")
    
    class Config:
        schema_extra = {
            "example": {
                "probability": 0.75,
                "prediction": "TB",
                "confidence": 0.75,
                "model": "DenseNet121",
                "status": "success"
            }
        }


class TabularPredictionRequest(BaseModel):
    """Schema for tabular prediction API request."""
    clinical_data: Union[Dict[str, float], List[float]] = Field(
        ..., 
        description="Clinical features as dict (feature names) or list (ordered values)"
    )
    
    @validator('clinical_data')
    def validate_data(cls, v):
        """Ensure data is not empty."""
        if isinstance(v, dict) and len(v) == 0:
            raise ValueError("clinical_data dict cannot be empty")
        if isinstance(v, list) and len(v) == 0:
            raise ValueError("clinical_data list cannot be empty")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "clinical_data": {
                    "age": 45,
                    "bmi": 22.5,
                    "cough_duration": 3,
                    "sex": "M"
                }
            }
        }


class TabularPredictionResponse(BaseModel):
    """Schema for tabular prediction API response."""
    probability: float = Field(..., ge=0, le=1, description="TB probability (0-1)")
    prediction: PredictionEnum = Field(..., description="TB or No TB")
    confidence: float = Field(..., ge=0, le=1, description="Confidence percentage")
    features_used: int = Field(..., description="Number of features processed")
    model: str = Field(..., description="Model used (XGBoost)")
    status: str = Field(..., description="Status (success/error)")
    
    class Config:
        schema_extra = {
            "example": {
                "probability": 0.62,
                "prediction": "TB",
                "confidence": 0.62,
                "features_used": 46,
                "model": "XGBoost",
                "status": "success"
            }
        }


class FusionPredictionRequest(BaseModel):
    """Schema for fusion prediction API request."""
    image_path: str = Field(..., description="Path to chest X-ray image")
    clinical_data: Union[Dict[str, float], List[float]] = Field(
        ..., 
        description="Clinical features as dict or list"
    )
    
    @validator('clinical_data')
    def validate_data(cls, v):
        """Ensure data is not empty."""
        if isinstance(v, dict) and len(v) == 0:
            raise ValueError("clinical_data cannot be empty")
        if isinstance(v, list) and len(v) == 0:
            raise ValueError("clinical_data cannot be empty")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "image_path": "/path/to/xray.jpg",
                "clinical_data": {
                    "age": 45,
                    "bmi": 22.5,
                    "cough_duration": 3,
                    "sex": "M"
                }
            }
        }


class FusionPredictionResponse(BaseModel):
    """Schema for fusion prediction API response."""
    probability: float = Field(..., ge=0, le=1, description="Fused TB probability")
    prediction: PredictionEnum = Field(..., description="TB or No TB (final)")
    confidence: float = Field(..., ge=0, le=1, description="Confidence percentage")
    image_probability: float = Field(..., ge=0, le=1, description="Image model probability")
    tabular_probability: float = Field(..., ge=0, le=1, description="Tabular model probability")
    image_prediction: PredictionEnum = Field(..., description="Image model prediction")
    tabular_prediction: PredictionEnum = Field(..., description="Tabular model prediction")
    weights: Dict[str, float] = Field(..., description="Fusion weights (image, tabular)")
    model: str = Field(..., description="Model used (Fusion)")
    status: str = Field(..., description="Status (success/error)")
    
    class Config:
        schema_extra = {
            "example": {
                "probability": 0.70,
                "prediction": "TB",
                "confidence": 0.70,
                "image_probability": 0.75,
                "tabular_probability": 0.62,
                "image_prediction": "TB",
                "tabular_prediction": "TB",
                "weights": {
                    "image": 0.70,
                    "tabular": 0.30
                },
                "model": "Fusion (DenseNet121 + XGBoost)",
                "status": "success"
            }
        }


class ConfigRequest(BaseModel):
    """Schema for configuration update request."""
    image_weight: Optional[float] = Field(
        None, 
        ge=0, 
        le=1, 
        description="Image modality weight (0-1)"
    )
    tabular_weight: Optional[float] = Field(
        None, 
        ge=0, 
        le=1, 
        description="Tabular modality weight (0-1)"
    )
    decision_threshold: Optional[float] = Field(
        None, 
        ge=0, 
        le=1, 
        description="Decision threshold (0-1)"
    )
    
    @model_validator(mode='after')
    def validate_weights(self) -> 'ConfigRequest':
        image_w = self.image_weight
        tabular_w = self.tabular_weight
        if abs((image_w + tabular_w) - 1.0) > 1e-6:
            raise ValueError(f"Weights must sum to 1.0 (currently {image_w + tabular_w})")
        return self
    
    class Config:
        schema_extra = {
            "example": {
                "image_weight": 0.70,
                "tabular_weight": 0.30,
                "decision_threshold": 0.50
            }
        }


class ConfigResponse(BaseModel):
    """Schema for configuration response."""
    image_weight: float = Field(..., description="Image weight")
    tabular_weight: float = Field(..., description="Tabular weight")
    decision_threshold: float = Field(..., description="Decision threshold")
    status: str = Field(..., description="Status")


class ModelInfoResponse(BaseModel):
    """Schema for model info response."""
    device: str = Field(..., description="Computing device (cuda/cpu)")
    image_model: Dict = Field(..., description="Image model info")
    tabular_model: Dict = Field(..., description="Tabular model info")
    fusion_config: Dict = Field(..., description="Fusion configuration")
    status: str = Field(..., description="Status")


class ErrorResponse(BaseModel):
    """Schema for error response."""
    detail: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    status: str = Field(default="error", description="Status")


class HealthCheckResponse(BaseModel):
    """Schema for health check response."""
    status: str = Field(..., description="Health status (healthy/degraded)")
    image_model_loaded: bool = Field(..., description="Is image model loaded")
    tabular_model_loaded: bool = Field(..., description="Is tabular model loaded")
    device: str = Field(..., description="Computing device")
    message: str = Field(..., description="Status message")
