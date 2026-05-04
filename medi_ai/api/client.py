"""
MediVision Python Client Library

Easy-to-use client for making predictions from desktop applications.

Usage:
    from api.client import MediVisionClient
    
    client = MediVisionClient("http://localhost:8000")
    result = client.predict_fusion(
        image_path="/path/to/xray.jpg",
        clinical_data={"age": 45, "bmi": 22.5}
    )
    print(result.probability)  # 0.75
    print(result.prediction)   # "TB"
"""

import requests
from typing import Dict, List, Union, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging


logger = logging.getLogger(__name__)


class PredictionType(str, Enum):
    """Prediction types."""
    TB = "TB"
    NO_TB = "No TB"


@dataclass
class ImagePrediction:
    """Image prediction result."""
    probability: float
    prediction: PredictionType
    confidence: float
    model: str = "DenseNet121"
    status: str = "success"
    
    def __str__(self):
        return f"{self.prediction} (prob={self.probability:.2%})"


@dataclass
class TabularPrediction:
    """Tabular prediction result."""
    probability: float
    prediction: PredictionType
    confidence: float
    features_used: int
    model: str = "XGBoost"
    status: str = "success"
    
    def __str__(self):
        return f"{self.prediction} (prob={self.probability:.2%}, features={self.features_used})"


@dataclass
class FusionPrediction:
    """Fusion prediction result."""
    probability: float
    prediction: PredictionType
    confidence: float
    image_probability: float
    tabular_probability: float
    image_prediction: PredictionType
    tabular_prediction: PredictionType
    weights: Dict[str, float]
    model: str = "Fusion"
    status: str = "success"
    
    def __str__(self):
        return (
            f"{self.prediction} (prob={self.probability:.2%})\n"
            f"  Image: {self.image_prediction} ({self.image_probability:.2%}) - weight {self.weights['image']:.0%}\n"
            f"  Tabular: {self.tabular_prediction} ({self.tabular_probability:.2%}) - weight {self.weights['tabular']:.0%}"
        )


@dataclass
class HealthStatus:
    """API health status."""
    status: str
    image_model_loaded: bool
    tabular_model_loaded: bool
    device: str
    message: str
    
    @property
    def is_healthy(self) -> bool:
        """Check if API is healthy."""
        return self.status == "healthy"
    
    @property
    def is_degraded(self) -> bool:
        """Check if API is degraded."""
        return self.status == "degraded"
    
    def __str__(self):
        status_icon = "✓" if self.is_healthy else "⚠"
        return (
            f"{status_icon} {self.status.upper()}\n"
            f"  Image Model: {'loaded' if self.image_model_loaded else 'not loaded'}\n"
            f"  Tabular Model: {'loaded' if self.tabular_model_loaded else 'not loaded'}\n"
            f"  Device: {self.device}"
        )


class MediVisionClientError(Exception):
    """Client exception."""
    pass


class MediVisionClient:
    """
    Client for MediVision TB detection API.
    
    Supports both image, tabular, and fusion predictions.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        """
        Initialize client.
        
        Args:
            base_url: API base URL (default: http://localhost:8000)
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make API request.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional request parameters
            
        Returns:
            Response JSON
            
        Raises:
            MediVisionClientError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault('timeout', self.timeout)
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.ConnectionError as e:
            raise MediVisionClientError(f"Connection failed: {e}")
        except requests.exceptions.Timeout as e:
            raise MediVisionClientError(f"Request timeout: {e}")
        except requests.exceptions.HTTPError as e:
            try:
                error_detail = response.json().get('detail', str(e))
            except:
                error_detail = str(e)
            raise MediVisionClientError(f"HTTP error: {error_detail}")
        except Exception as e:
            raise MediVisionClientError(f"Request failed: {e}")
    
    # ========================================================================
    # HEALTH & INFO
    # ========================================================================
    
    def health_check(self) -> HealthStatus:
        """
        Check API health.
        
        Returns:
            HealthStatus object
            
        Raises:
            MediVisionClientError: If health check fails
        """
        try:
            data = self._request('GET', '/health')
            return HealthStatus(
                status=data['status'],
                image_model_loaded=data['image_model_loaded'],
                tabular_model_loaded=data['tabular_model_loaded'],
                device=data['device'],
                message=data['message']
            )
        except MediVisionClientError as e:
            raise MediVisionClientError(f"Health check failed: {e}")
    
    def get_models_info(self) -> Dict[str, Any]:
        """
        Get model information.
        
        Returns:
            Dictionary with model details
        """
        return self._request('GET', '/models/info')
    
    def reload_models(self) -> bool:
        """
        Reload all models.
        
        Returns:
            True if successful
        """
        result = self._request('POST', '/models/reload')
        return result.get('status') == 'success'
    
    # ========================================================================
    # PREDICTIONS
    # ========================================================================
    
    def predict_image(self, image_path: str) -> ImagePrediction:
        """
        Predict TB from chest X-ray.
        
        Args:
            image_path: Path to JPEG/PNG image
            
        Returns:
            ImagePrediction object
            
        Raises:
            MediVisionClientError: If prediction fails
        """
        try:
            data = self._request(
                'POST',
                '/predict/image',
                json={'image_path': image_path}
            )
            return ImagePrediction(
                probability=data['probability'],
                prediction=PredictionType(data['prediction']),
                confidence=data['confidence'],
                model=data.get('model', 'DenseNet121'),
                status=data.get('status', 'success')
            )
        except Exception as e:
            raise MediVisionClientError(f"Image prediction failed: {e}")
    
    def predict_image_upload(self, image_path: str) -> ImagePrediction:
        """
        Predict TB from uploaded image.
        
        Args:
            image_path: Path to local image file
            
        Returns:
            ImagePrediction object
            
        Raises:
            MediVisionClientError: If prediction fails
        """
        try:
            with open(image_path, 'rb') as f:
                files = {'file': f}
                response = self.session.post(
                    f"{self.base_url}/predict/image/upload",
                    files=files,
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()
            
            return ImagePrediction(
                probability=data['probability'],
                prediction=PredictionType(data['prediction']),
                confidence=data['confidence'],
                model=data.get('model', 'DenseNet121'),
                status=data.get('status', 'success')
            )
        except Exception as e:
            raise MediVisionClientError(f"Image upload prediction failed: {e}")
    
    def predict_tabular(self, clinical_data: Union[Dict, List]) -> TabularPrediction:
        """
        Predict TB from clinical features.
        
        Args:
            clinical_data: Dictionary or list of clinical features
            
        Returns:
            TabularPrediction object
            
        Raises:
            MediVisionClientError: If prediction fails
        """
        try:
            data = self._request(
                'POST',
                '/predict/tabular',
                json={'clinical_data': clinical_data}
            )
            return TabularPrediction(
                probability=data['probability'],
                prediction=PredictionType(data['prediction']),
                confidence=data['confidence'],
                features_used=data['features_used'],
                model=data.get('model', 'XGBoost'),
                status=data.get('status', 'success')
            )
        except Exception as e:
            raise MediVisionClientError(f"Tabular prediction failed: {e}")
    
    def predict_fusion(self, image_path: str, 
                      clinical_data: Union[Dict, List]) -> FusionPrediction:
        """
        Predict TB using image + tabular fusion.
        
        Args:
            image_path: Path to chest X-ray
            clinical_data: Dictionary or list of clinical features
            
        Returns:
            FusionPrediction object
            
        Raises:
            MediVisionClientError: If prediction fails
        """
        try:
            data = self._request(
                'POST',
                '/predict/fusion',
                json={
                    'image_path': image_path,
                    'clinical_data': clinical_data
                }
            )
            return FusionPrediction(
                probability=data['probability'],
                prediction=PredictionType(data['prediction']),
                confidence=data['confidence'],
                image_probability=data['image_probability'],
                tabular_probability=data['tabular_probability'],
                image_prediction=PredictionType(data['image_prediction']),
                tabular_prediction=PredictionType(data['tabular_prediction']),
                weights=data['weights'],
                model=data.get('model', 'Fusion'),
                status=data.get('status', 'success')
            )
        except Exception as e:
            raise MediVisionClientError(f"Fusion prediction failed: {e}")
    
    # ========================================================================
    # CONFIGURATION
    # ========================================================================
    
    def get_config(self) -> Dict[str, float]:
        """
        Get current configuration.
        
        Returns:
            Dictionary with image_weight, tabular_weight, decision_threshold
        """
        data = self._request('GET', '/config')
        return {
            'image_weight': data['image_weight'],
            'tabular_weight': data['tabular_weight'],
            'decision_threshold': data['decision_threshold']
        }
    
    def set_config(self, image_weight: Optional[float] = None,
                  tabular_weight: Optional[float] = None,
                  decision_threshold: Optional[float] = None) -> Dict[str, float]:
        """
        Update configuration.
        
        Args:
            image_weight: Image model weight (0-1)
            tabular_weight: Tabular model weight (0-1)
            decision_threshold: Decision threshold (0-1)
            
        Returns:
            Updated configuration
            
        Raises:
            MediVisionClientError: If update fails
        """
        config_update = {}
        if image_weight is not None:
            config_update['image_weight'] = image_weight
        if tabular_weight is not None:
            config_update['tabular_weight'] = tabular_weight
        if decision_threshold is not None:
            config_update['decision_threshold'] = decision_threshold
        
        data = self._request('POST', '/config', json=config_update)
        return {
            'image_weight': data['image_weight'],
            'tabular_weight': data['tabular_weight'],
            'decision_threshold': data['decision_threshold']
        }
    
    # ========================================================================
    # CONTEXT MANAGER
    # ========================================================================
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def close(self):
        """Close session."""
        if self.session:
            self.session.close()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_client(base_url: str = "http://localhost:8000") -> MediVisionClient:
    """Create and return a MediVision client."""
    return MediVisionClient(base_url)


def quick_predict_fusion(image_path: str, clinical_data: Dict,
                        api_url: str = "http://localhost:8000") -> FusionPrediction:
    """
    Quick prediction without creating client.
    
    Args:
        image_path: Path to chest X-ray
        clinical_data: Clinical features dictionary
        api_url: API base URL
        
    Returns:
        FusionPrediction object
    """
    client = MediVisionClient(api_url)
    return client.predict_fusion(image_path, clinical_data)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create client
    client = MediVisionClient("http://localhost:8000")
    
    try:
        # Check health
        print("Checking API health...")
        health = client.health_check()
        print(health)
        print()
        
        if not health.is_healthy:
            print("Warning: API is degraded")
            sys.exit(1)
        
        # Example prediction
        print("Running prediction example...")
        clinical_data = {
            "age": 45,
            "bmi": 22.5,
            "cough_duration": 3,
            "sex": "M"
        }
        
        # You would use actual image path here
        image_path = "/path/to/xray.jpg"
        
        print(f"\nPredicting TB for patient:")
        print(f"  Age: {clinical_data['age']}")
        print(f"  BMI: {clinical_data['bmi']}")
        print(f"  Cough Duration: {clinical_data['cough_duration']} days")
        print()
        
        # Try fusion prediction if both models loaded
        if health.image_model_loaded and health.tabular_model_loaded:
            print("Running fusion prediction...")
            result = client.predict_fusion(image_path, clinical_data)
            print(result)
        else:
            print("Skipping fusion (models not loaded)")
    
    except MediVisionClientError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    finally:
        client.close()
