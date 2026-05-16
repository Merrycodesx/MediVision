"""
MediVision - Inference class for TB detection using multimodal approach.
Combines DenseNet121 (image), XGBoost (tabular), and fusion layer.
Designed for desktop application integration via REST API.
"""

import torch
import numpy as np
import pickle
import os
from typing import Dict, Optional, Tuple, Union, List
from pathlib import Path
import logging
import cv2

from models.cnn import DenseNetCNN
from models.tabular import XGBoostClassifier
from data.preprocessor import ImagePreprocessor, TabularPreprocessor
import config


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class MediVisionInference:
    """
    Multi-modal inference engine for TB detection.
    
    Provides methods for:
    - Image-only predictions (DenseNet121)
    - Tabular-only predictions (XGBoost)
    - Fused predictions (70% image + 30% tabular)
    - Model management (load, save, reload)
    """
    
    def __init__(self, 
                 image_model_path: Optional[str] = None,
                 tabular_model_path: Optional[str] = None,
                 scaler_path: Optional[str] = None,
                 device: Optional[str] = None):
        """
        Initialize MediVision inference engine.
        
        Args:
            image_model_path: Path to densenet_cnn.pth
            tabular_model_path: Path to xgboost_model.pkl or .json
            scaler_path: Path to scaler.pkl (TabularPreprocessor state)
            device: 'cuda' or 'cpu' (auto-detected if None)
            
        Raises:
            RuntimeError: If model files not found or loading fails
        """
        # Set defaults
        self.image_model_path = image_model_path or config.CNN_MODEL_PATH
        self.tabular_model_path = tabular_model_path or config.XGBOOST_MODEL_PATH
        self.scaler_path = scaler_path or config.SCALER_PATH
        
        # Auto-detect device
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize models as None
        self.image_model = None
        self.tabular_model = None
        self.image_preprocessor = None
        self.tabular_preprocessor = None
        
        # Configuration
        self.image_weight = 0.70  # 70% image
        self.tabular_weight = 0.30  # 30% tabular
        self.threshold = 0.5  # Decision threshold
        
        logger.info(f"MediVision initialized - Device: {self.device}")
        
        # Load models if paths are provided
        self._load_all_models()
    
    def _load_all_models(self) -> None:
        """Load all models simultaneously with error handling."""
        try:
            logger.info("Loading pre-trained models...")
            self.load_image_model()
            logger.info("✓ Image model loaded")
        except Exception as e:
            logger.warning(f"⚠ Failed to load image model: {e}")
        
        try:
            self.load_tabular_model()
            logger.info("✓ Tabular model loaded")
        except Exception as e:
            logger.warning(f"⚠ Failed to load tabular model: {e}")
        
        # Verify at least one model is loaded
        if self.image_model is None and self.tabular_model is None:
            raise RuntimeError("Failed to load any models. Check file paths.")
    
    def load_image_model(self) -> None:
        """
        Load DenseNet121 model from checkpoint.
        
        Raises:
            FileNotFoundError: If model file not found
            RuntimeError: If loading fails
        """
        if not os.path.exists(self.image_model_path):
            raise FileNotFoundError(f"Image model not found: {self.image_model_path}")
        
        try:
            self.image_model = DenseNetCNN(pretrained=False).to(self.device)
            self.image_model.load_state_dict(
                torch.load(self.image_model_path, map_location=self.device)
            )
            self.image_model.eval()
            self.image_preprocessor = ImagePreprocessor(augment=False)
            logger.info(f"Loaded image model from {self.image_model_path}")
        except Exception as e:
            logger.error(f"Error loading image model: {e}")
            raise RuntimeError(f"Failed to load image model: {e}")
    
    def load_tabular_model(self) -> None:
        """
        Load XGBoost and scaler from files.
        
        Raises:
            FileNotFoundError: If model files not found
            RuntimeError: If loading fails
        """
        if not os.path.exists(self.tabular_model_path):
            raise FileNotFoundError(f"Tabular model not found: {self.tabular_model_path}")
        
        if not os.path.exists(self.scaler_path):
            raise FileNotFoundError(f"Scaler not found: {self.scaler_path}")
        
        try:
            # Load XGBoost model
            self.tabular_model = XGBoostClassifier()
            self.tabular_model.load(self.tabular_model_path)
            
            # Load preprocessor/scaler
            self.tabular_preprocessor = TabularPreprocessor()
            self.tabular_preprocessor.load(self.scaler_path)
            
            logger.info(f"Loaded tabular model from {self.tabular_model_path}")
            logger.info(f"Loaded preprocessor from {self.scaler_path}")
        except Exception as e:
            logger.error(f"Error loading tabular model: {e}")
            raise RuntimeError(f"Failed to load tabular model: {e}")
    
    def predict_image(self, image_path: str) -> Dict[str, Union[float, str]]:
        """
        Predict TB probability from chest X-ray image.
        
        Args:
            image_path: Path to JPEG/PNG X-ray image
            
        Returns:
            Dictionary with keys:
                - 'probability': TB probability (0-1)
                - 'prediction': 'TB' or 'No TB' (based on threshold)
                - 'confidence': Confidence percentage
                
        Raises:
            RuntimeError: If image model not loaded
            FileNotFoundError: If image file not found
            ValueError: If image cannot be processed
        """
        if self.image_model is None:
            raise RuntimeError("Image model not loaded. Call load_image_model() first.")
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        try:
            # Load and preprocess image
            from PIL import Image
            image = Image.open(image_path).convert('RGB')
            image_array = np.array(image)
            image_tensor = self.image_preprocessor.preprocess(image_array)
            image_tensor = image_tensor.unsqueeze(0).to(self.device)
            
            # Predict
            self.image_model.eval()
            with torch.no_grad():
                logits = self.image_model(image_tensor)
                probability = torch.sigmoid(logits).item()
            
            # Format result
            prediction = 'TB' if probability > self.threshold else 'No TB'
            confidence = max(probability, 1 - probability)
            
            base_name = os.path.basename(image_path)
            heatmap_save_path = os.path.join(config.PLOTS_DIR, "gradcam_explainability", f"heatmap_{base_name}")
            
            # Generate it dynamically during inference
            self.generate_gradcam(image_path, heatmap_save_path)

            return {
                'probability': float(probability),
                'prediction': prediction,
                'confidence': float(confidence),
                'heatmap_path': heatmap_save_path,
                'model': 'DenseNet121',
                'status': 'success'
            }
        
        except Exception as e:
            logger.error(f"Error predicting image: {e}")
            raise ValueError(f"Failed to process image: {e}")
    
    def predict_tabular(self, clinical_data: Union[Dict, List, np.ndarray]) -> Dict[str, Union[float, str]]:
        """
        Predict TB probability from clinical features.
        
        Args:
            clinical_data: Clinical symptoms as one of:
                - Dictionary: {'age': 45, 'bmi': 22.5, 'cough_duration': 3, ...}
                - List: [45, 22.5, 3, ...] (must match feature order)
                - numpy array: (1, n_features)
                
        Returns:
            Dictionary with keys:
                - 'probability': TB probability (0-1)
                - 'prediction': 'TB' or 'No TB'
                - 'confidence': Confidence percentage
                - 'features_used': Number of features
                
        Raises:
            RuntimeError: If tabular model not loaded
            ValueError: If data format invalid or missing features
        """
        if self.tabular_model is None:
            raise RuntimeError("Tabular model not loaded. Call load_tabular_model() first.")
        
        try:
            # Convert to numpy array if needed
            if isinstance(clinical_data, dict):
                # Convert dict to array using feature order
                if self.tabular_preprocessor.feature_names is None:
                    raise ValueError("Preprocessor not fitted - cannot infer feature order from dict")
                
                # Create array in correct order
                data_array = np.array([
                    clinical_data.get(feat, np.nan) 
                    for feat in self.tabular_preprocessor.feature_names
                ])
                data_array = data_array.reshape(1, -1)
            
            elif isinstance(clinical_data, list):
                data_array = np.array(clinical_data).reshape(1, -1)
            
            elif isinstance(clinical_data, np.ndarray):
                if clinical_data.ndim == 1:
                    data_array = clinical_data.reshape(1, -1)
                else:
                    data_array = clinical_data
            
            else:
                raise ValueError(f"Invalid data type: {type(clinical_data)}")
            
            # Preprocess (scale)
            data_scaled = self.tabular_preprocessor.transform(data_array)
            
            # Predict
            probability = self.tabular_model.predict_proba(data_scaled)[0]
            
            # Format result
            prediction = 'TB' if probability > self.threshold else 'No TB'
            confidence = max(probability, 1 - probability)
            
            return {
                'probability': float(probability),
                'prediction': prediction,
                'confidence': float(confidence),
                'features_used': data_scaled.shape[1],
                'model': 'XGBoost',
                'status': 'success'
            }
        
        except Exception as e:
            logger.error(f"Error predicting tabular: {e}")
            raise ValueError(f"Failed to process tabular data: {e}")
    
    def predict_fusion(self, image_path: str, 
                      clinical_data: Union[Dict, List, np.ndarray]) -> Dict[str, Union[float, str]]:
        """
        Predict TB using weighted fusion of image and tabular modalities.
        
        Fusion Formula:
            P(TB) = 0.70 * P_image(TB) + 0.30 * P_tabular(TB)
        
        Args:
            image_path: Path to chest X-ray
            clinical_data: Clinical features (dict, list, or array)
            
        Returns:
            Dictionary with keys:
                - 'probability': Fused TB probability (0-1)
                - 'prediction': 'TB' or 'No TB'
                - 'confidence': Confidence percentage
                - 'image_probability': Individual image prediction
                - 'tabular_probability': Individual tabular prediction
                - 'weights': {'image': 0.70, 'tabular': 0.30}
                
        Raises:
            RuntimeError: If models not loaded
            FileNotFoundError: If image not found
            ValueError: If data invalid
        """
        try:
            # Get individual predictions
            image_result = self.predict_image(image_path)
            tabular_result = self.predict_tabular(clinical_data)
            
            # Fuse predictions
            fused_prob = (
                self.image_weight * image_result['probability'] +
                self.tabular_weight * tabular_result['probability']
            )
            
            # Format result
            prediction = 'TB' if fused_prob > self.threshold else 'No TB'
            confidence = max(fused_prob, 1 - fused_prob)
            
            return {
                'probability': float(fused_prob),
                'prediction': prediction,
                'confidence': float(confidence),
                'image_probability': image_result['probability'],
                'tabular_probability': tabular_result['probability'],
                'image_prediction': image_result['prediction'],
                'tabular_prediction': tabular_result['prediction'],
                'weights': {
                    'image': self.image_weight,
                    'tabular': self.tabular_weight
                },
                'model': 'Fusion (DenseNet121 + XGBoost)',
                'status': 'success'
            }
        
        except Exception as e:
            logger.error(f"Error in fusion prediction: {e}")
            raise ValueError(f"Failed fusion prediction: {e}")
    
    def set_fusion_weights(self, image_weight: float, tabular_weight: float) -> None:
        """
        Customize fusion weights (must sum to 1.0).
        
        Args:
            image_weight: Weight for image modality (0-1)
            tabular_weight: Weight for tabular modality (0-1)
            
        Raises:
            ValueError: If weights don't sum to 1.0 or invalid
        """
        if not (0 <= image_weight <= 1 and 0 <= tabular_weight <= 1):
            raise ValueError("Weights must be between 0 and 1")
        
        if abs((image_weight + tabular_weight) - 1.0) > 1e-6:
            raise ValueError(f"Weights must sum to 1.0, got {image_weight + tabular_weight}")
        
        self.image_weight = image_weight
        self.tabular_weight = tabular_weight
        logger.info(f"Fusion weights updated: Image={image_weight:.2%}, Tabular={tabular_weight:.2%}")
    
    def set_decision_threshold(self, threshold: float) -> None:
        """
        Set decision threshold for TB/No TB classification.
        
        Args:
            threshold: Probability threshold (0-1), default 0.5
            
        Raises:
            ValueError: If threshold not in [0, 1]
        """
        if not (0 <= threshold <= 1):
            raise ValueError("Threshold must be between 0 and 1")
        
        self.threshold = threshold
        logger.info(f"Decision threshold updated to {threshold:.2%}")

    def generate_gradcam(self, image_path: str, save_path: str) -> str:
        """
        Generates a Grad-CAM heatmap overlay for a given X-ray image 
        and saves it to the specified location.
        """
        if self.image_model is None:
            raise RuntimeError("Image model not loaded.")

        # 1. Load and preprocess image specifically with gradient tracking enabled
        from PIL import Image
        image = Image.open(image_path).convert('RGB')
        image_array = np.array(image)
        image_tensor = self.image_preprocessor.preprocess(image_array)
        image_tensor = image_tensor.unsqueeze(0).to(self.device)

        # 2. Extract feature maps from DenseNet's last block
        features_layer = self.image_model.features
        
        self.image_model.eval()
        with torch.enable_grad():
            # Run forward pass up to feature maps
            feature_maps = features_layer(image_tensor)
            feature_maps.requires_grad_()
            
            # Replicate the classifier pool/flatten path
            import torch.nn.functional as F
            pooled = F.adaptive_avg_pool2d(feature_maps, (1, 1))
            flattened = torch.flatten(pooled, 1)
            output = self.image_model.classifier(flattened)
            
            # Target the class driving the prediction
            target_class = output.argmax(dim=1)
            score = output[0][target_class]
            
            # Backward pass to gather gradients
            self.image_model.zero_grad()
            score.backward()

        # 3. Process Gradients & Feature Maps
        gradients = feature_maps.grad.detach().cpu().numpy()[0]
        feature_maps = feature_maps.detach().cpu().numpy()[0]
        
        # Calculate weights based on mean gradient intensity
        weights = np.mean(gradients, axis=(1, 2))
        cam = np.zeros(feature_maps.shape[1:], dtype=np.float32)
        
        for i, w in enumerate(weights):
            cam += w * feature_maps[i]
            
        # 4. Clean up map (ReLU + Normalize)
        cam = np.maximum(cam, 0)
        cam = cv2.resize(cam, (224, 224))
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)

        # 5. Load original and overlay the Jet color map
        img = cv2.imread(image_path)
        img = cv2.resize(img, (224, 224))
        
        heatmap = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)
        overlay_result = cv2.addWeighted(img, 0.6, heatmap, 0.4, 0)
        
        # Save output to your structured directory
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        cv2.imwrite(save_path, overlay_result)
        logger.info(f"[XAI] Grad-CAM saved successfully to {save_path}")
        return save_path
    
    def get_model_info(self) -> Dict[str, any]:
        """
        Get information about loaded models.
        
        Returns:
            Dictionary with model details
        """
        info = {
            'device': self.device,
            'image_model': {
                'loaded': self.image_model is not None,
                'path': self.image_model_path if self.image_model is not None else None,
                'type': 'DenseNet121'
            },
            'tabular_model': {
                'loaded': self.tabular_model is not None,
                'path': self.tabular_model_path if self.tabular_model is not None else None,
                'type': 'XGBoost'
            },
            'fusion_config': {
                'image_weight': self.image_weight,
                'tabular_weight': self.tabular_weight,
                'decision_threshold': self.threshold
            }
        }
        return info
    
    def reload_models(self) -> None:
        """Reload all models from disk."""
        logger.info("Reloading models...")
        self.image_model = None
        self.tabular_model = None
        self._load_all_models()
        logger.info("Models reloaded successfully")
    
    def unload_models(self) -> None:
        """Unload all models from memory."""
        self.image_model = None
        self.tabular_model = None
        logger.info("Models unloaded from memory")


# Convenience function for global inference instance
_inference_engine = None

def get_inference_engine() -> MediVisionInference:
    """Get or create global inference engine."""
    global _inference_engine
    if _inference_engine is None:
        _inference_engine = MediVisionInference()
    return _inference_engine

def create_inference_engine(**kwargs) -> MediVisionInference:
    """Create a new inference engine with custom parameters."""
    return MediVisionInference(**kwargs)
