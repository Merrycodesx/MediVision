"""
Inference engine for TB detection.
Handles predictions from image only, tabular only, or multimodal inputs.
"""

import torch
import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple
import config
from data.preprocessor import ImagePreprocessor, TabularPreprocessor
from models.cnn import DenseNetCNN
from models.tabular import XGBoostTabular
from models.fusion import LateFusionModel


class TBInferenceEngine:
    """
    Complete inference engine for TB detection.
    Can operate on image only, tabular only, or both modalities.
    """
    
    def __init__(self, device: str = config.DEVICE):
        """
        Initialize inference engine.
        Requires pre-trained models to be available.
        
        Args:
            device: 'cuda' or 'cpu'
        """
        self.device = device
        self.cnn = None
        self.xgb = None
        self.fusion = None
        self.image_preprocessor = ImagePreprocessor(augment=False)
        self.tabular_preprocessor = None
        self.is_loaded = False
    
    def load_models(self) -> None:
        """Load all pre-trained models."""
        # Load CNN
        self.cnn = DenseNetCNN(pretrained=False)
        self.cnn.load_checkpoint(config.CNN_MODEL_PATH)
        self.cnn.eval()
        
        # Load XGBoost
        self.xgb = XGBoostTabular()
        self.xgb.load(config.XGBOOST_MODEL_PATH)
        
        # Load tabular preprocessor
        import pickle
        with open(config.SCALER_PATH, 'rb') as f:
            scaler_data = pickle.load(f)
        self.tabular_preprocessor = TabularPreprocessor()
        self.tabular_preprocessor.scaler = scaler_data['scaler']
        self.tabular_preprocessor.label_encoder = scaler_data.get('label_encoder', {})
        self.tabular_preprocessor.feature_names = scaler_data['feature_names']
        self.tabular_preprocessor.is_fitted = True
        
        # Load fusion model
        self.fusion = LateFusionModel()
        self.fusion.load(config.FUSION_MODEL_PATH)
        
        self.is_loaded = True
        
        if config.VERBOSE:
            print("[INFO] All models loaded successfully.")
    
    def predict_from_image(self, image_path: str, return_proba: bool = True) -> Dict:
        """
        Predict using image only.
        
        Args:
            image_path: Path to CXR image
            return_proba: Return probability or binary prediction
            
        Returns:
            Dictionary with 'prediction', 'probability', and 'confidence'
        """
        if not self.is_loaded:
            raise RuntimeError("Models not loaded. Call load_models() first.")
        
        if self.cnn is None:
            raise RuntimeError("CNN model not loaded.")
        
        # Load and preprocess image
        from PIL import Image
        image = Image.open(image_path).convert('L')
        image_array = np.array(image)
        image_tensor = self.image_preprocessor.preprocess(image_array).unsqueeze(0)
        
        # Get prediction
        with torch.no_grad():
            image_tensor = image_tensor.to(self.device)
            logits = self.cnn(image_tensor)
            prob = torch.sigmoid(logits).cpu().numpy()[0, 0]
        
        prediction = 1 if prob > 0.5 else 0
        confidence = max(prob, 1 - prob)
        
        return {
            'modality': 'image',
            'prediction': prediction,
            'probability': float(prob),
            'confidence': float(confidence),
        }
    
    def predict_from_tabular(self, age: float, sex: str, return_proba: bool = True) -> Dict:
        """
        Predict using tabular data only.
        
        Args:
            age: Patient age in years
            sex: Patient sex ('M' or 'F')
            return_proba: Return probability or binary prediction
            
        Returns:
            Dictionary with 'prediction', 'probability', and 'confidence'
        """
        if not self.is_loaded:
            raise RuntimeError("Models not loaded. Call load_models() first.")
        
        if self.xgb is None or self.tabular_preprocessor is None:
            raise RuntimeError("XGBoost or tabular preprocessor not loaded.")
        
        # Create DataFrame
        data = pd.DataFrame({'age': [age], 'sex': [sex]})
        
        # Preprocess
        X = self.tabular_preprocessor.transform(data)
        
        # Get prediction
        prob = self.xgb.predict(X, return_proba=True)[0]
        prediction = 1 if prob > 0.5 else 0
        confidence = max(prob, 1 - prob)
        
        return {
            'modality': 'tabular',
            'prediction': prediction,
            'probability': float(prob),
            'confidence': float(confidence),
        }
    
    def predict_multimodal(self, image_path: str, age: float, sex: str,
                          return_proba: bool = True) -> Dict:
        """
        Predict using both image and tabular data (late fusion).
        
        Args:
            image_path: Path to CXR image
            age: Patient age in years
            sex: Patient sex ('M' or 'F')
            return_proba: Return probability or binary prediction
            
        Returns:
            Dictionary with predictions from all modalities and fusion
        """
        if not self.is_loaded:
            raise RuntimeError("Models not loaded. Call load_models() first.")
        
        if self.cnn is None or self.xgb is None or self.fusion is None:
            raise RuntimeError("Models not fully loaded.")
        
        # Get image prediction
        from PIL import Image
        image = Image.open(image_path).convert('L')
        image_array = np.array(image)
        image_tensor = self.image_preprocessor.preprocess(image_array).unsqueeze(0)
        
        with torch.no_grad():
            image_tensor = image_tensor.to(self.device)
            logits = self.cnn(image_tensor)
            cnn_prob = torch.sigmoid(logits).cpu().numpy()[0, 0]
        
        # Get tabular prediction
        data = pd.DataFrame({'age': [age], 'sex': [sex]})
        X = self.tabular_preprocessor.transform(data)
        xgb_prob = self.xgb.predict(X, return_proba=True)[0]
        
        # Get fusion prediction
        fusion_prob = self.fusion.predict(np.array([cnn_prob]), np.array([xgb_prob]))[0]
        
        fusion_pred = 1 if fusion_prob > 0.5 else 0
        fusion_conf = max(fusion_prob, 1 - fusion_prob)
        
        return {
            'modality': 'multimodal',
            'cnn': {
                'probability': float(cnn_prob),
                'prediction': 1 if cnn_prob > 0.5 else 0,
            },
            'xgb': {
                'probability': float(xgb_prob),
                'prediction': 1 if xgb_prob > 0.5 else 0,
            },
            'fusion': {
                'probability': float(fusion_prob),
                'prediction': fusion_pred,
                'confidence': float(fusion_conf),
            }
        }
    
    def predict(self, image_path: Optional[str] = None,
                age: Optional[float] = None,
                sex: Optional[str] = None,
                return_proba: bool = True) -> Dict:
        """
        Flexible prediction that handles missing modalities.
        
        Args:
            image_path: Path to CXR image (optional)
            age: Patient age (optional)
            sex: Patient sex (optional)
            return_proba: Return probability or binary prediction
            
        Returns:
            Prediction dictionary
        """
        has_image = image_path is not None
        has_tabular = age is not None and sex is not None
        
        if has_image and has_tabular:
            return self.predict_multimodal(image_path, age, sex, return_proba)
        elif has_image:
            return self.predict_from_image(image_path, return_proba)
        elif has_tabular:
            return self.predict_from_tabular(age, sex, return_proba)
        else:
            raise ValueError("At least one modality (image or tabular) must be provided.")
