"""
Late fusion model combining CNN and XGBoost predictions.
Uses logistic regression for weighted ensemble.
"""

import numpy as np
from sklearn.linear_model import LogisticRegression
from typing import Tuple
import config


class LateFusionModel:
    """
    Late fusion model that combines predictions from image and tabular modalities.
    Uses logistic regression to learn optimal weighting.
    """
    
    def __init__(self):
        """Initialize fusion model."""
        self.model = LogisticRegression(max_iter=1000, random_state=config.RANDOM_STATE)
        self.is_fitted = False
    
    def train(self, cnn_proba: np.ndarray, xgb_proba: np.ndarray, y: np.ndarray) -> None:
        """
        Train fusion model on modality predictions.
        
        Args:
            cnn_proba: CNN predictions (N, 1) or (N,)
            xgb_proba: XGBoost predictions (N, 1) or (N,)
            y: True labels (N,)
        """
        # Ensure correct shapes
        cnn_proba = cnn_proba.reshape(-1, 1) if cnn_proba.ndim == 1 else cnn_proba
        xgb_proba = xgb_proba.reshape(-1, 1) if xgb_proba.ndim == 1 else xgb_proba
        
        # Stack predictions as features
        X_fusion = np.hstack([cnn_proba, xgb_proba])
        
        # Train logistic regression
        self.model.fit(X_fusion, y)
        self.is_fitted = True
        
        if config.VERBOSE:
            print(f"[INFO] Fusion model trained.")
            print(f"[INFO] Learned weights - CNN: {self.model.coef_[0][0]:.4f}, XGBoost: {self.model.coef_[0][1]:.4f}")
    
    def predict(self, cnn_proba: np.ndarray, xgb_proba: np.ndarray, 
                return_proba: bool = True) -> np.ndarray:
        """
        Make fusion predictions.
        
        Args:
            cnn_proba: CNN predictions (N, 1) or (N,)
            xgb_proba: XGBoost predictions (N, 1) or (N,)
            return_proba: If True, return probabilities; else return binary predictions
            
        Returns:
            Predictions or probabilities (N,)
        """
        if not self.is_fitted:
            raise RuntimeError("Fusion model must be trained first.")
        
        # Ensure correct shapes
        cnn_proba = cnn_proba.reshape(-1, 1) if cnn_proba.ndim == 1 else cnn_proba
        xgb_proba = xgb_proba.reshape(-1, 1) if xgb_proba.ndim == 1 else xgb_proba
        
        X_fusion = np.hstack([cnn_proba, xgb_proba])
        
        if return_proba:
            return self.model.predict_proba(X_fusion)[:, 1]
        else:
            return self.model.predict(X_fusion)
    
    def predict_single(self, cnn_proba: float, xgb_proba: float) -> Tuple[float, int]:
        """
        Make a single fusion prediction.
        
        Args:
            cnn_proba: Single CNN probability [0, 1]
            xgb_proba: Single XGBoost probability [0, 1]
            
        Returns:
            Tuple of (fusion_probability, binary_prediction)
        """
        X = np.array([[cnn_proba, xgb_proba]])
        prob = self.model.predict_proba(X)[0, 1]
        pred = self.model.predict(X)[0]
        return prob, int(pred)
    
    def save(self, path: str) -> None:
        """Save fusion model to pickle file."""
        import pickle
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)
        if config.VERBOSE:
            print(f"[INFO] Fusion model saved to {path}")
    
    def load(self, path: str) -> None:
        """Load fusion model from pickle file."""
        import pickle
        with open(path, 'rb') as f:
            self.model = pickle.load(f)
        self.is_fitted = True
        if config.VERBOSE:
            print(f"[INFO] Fusion model loaded from {path}")


class WeightedAverageEnsemble:
    """
    Simple weighted average of modality predictions.
    Alpha is the weight for image modality, (1-alpha) for tabular.
    """
    
    def __init__(self, alpha: float = config.FUSION_ALPHA):
        """
        Initialize weighted average ensemble.
        
        Args:
            alpha: Weight for CNN modality [0, 1]
        """
        self.alpha = alpha
    
    def predict(self, cnn_proba: np.ndarray, xgb_proba: np.ndarray,
                return_proba: bool = True) -> np.ndarray:
        """
        Weighted average of predictions.
        
        Args:
            cnn_proba: CNN probabilities
            xgb_proba: XGBoost probabilities
            return_proba: If True, return probabilities; else return binary
            
        Returns:
            Ensemble predictions
        """
        # Weighted average
        ensemble_proba = self.alpha * cnn_proba + (1 - self.alpha) * xgb_proba
        
        if return_proba:
            return ensemble_proba
        else:
            return (ensemble_proba > 0.5).astype(int)
