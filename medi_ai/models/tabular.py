"""
XGBoost model for tabular clinical data.
"""

import xgboost as xgb
import numpy as np
from typing import Tuple
import config


class XGBoostTabular:
    """
    XGBoost classifier for tabular features (age, sex, etc.).
    Binary classification: TB vs No TB.
    """
    
    def __init__(self, params: dict = None):
        """
        Initialize XGBoost model.
        
        Args:
            params: XGBoost hyperparameters (defaults from config)
        """
        if params is None:
            params = config.XGBOOST_PARAMS.copy()
        
        self.params = params
        self.model = None
        self.feature_importance = None
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: np.ndarray, y_val: np.ndarray,
              feature_names: list = None) -> None:
        """
        Train XGBoost model.
        
        Args:
            X_train: Training features (N, n_features)
            y_train: Training labels (N,)
            X_val: Validation features (M, n_features)
            y_val: Validation labels (M,)
            feature_names: Names of features for interpretability
        """
        # Create DMatrix for XGBoost
        dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=feature_names)
        dval = xgb.DMatrix(X_val, label=y_val, feature_names=feature_names)
        
        # Train with early stopping
        evals = [(dtrain, 'train'), (dval, 'eval')]
        evals_result = {}
        
        self.model = xgb.train(
            self.params,
            dtrain,
            num_boost_round=self.params.get('n_estimators', 100),
            evals=evals,
            evals_result=evals_result,
            early_stopping_rounds=10,
            verbose_eval=config.LOG_INTERVAL if config.VERBOSE else False,
        )
        
        # Store feature importance
        self.feature_importance = self.model.get_score(importance_type='weight')
        
        if config.VERBOSE:
            print(f"[INFO] XGBoost trained with {self.model.best_ntree_limit} trees.")
    
    def predict(self, X: np.ndarray, return_proba: bool = True) -> np.ndarray:
        """
        Make predictions.
        
        Args:
            X: Features (N, n_features)
            return_proba: If True, return probabilities; else return binary predictions
            
        Returns:
            Predictions or probabilities (N,)
        """
        if self.model is None:
            raise RuntimeError("Model must be trained first.")
        
        dmatrix = xgb.DMatrix(X)
        proba = self.model.predict(dmatrix)
        
        if return_proba:
            return proba
        else:
            return (proba > 0.5).astype(int)
    
    def get_feature_importance(self) -> dict:
        """
        Get feature importance scores.
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if self.feature_importance is None:
            raise RuntimeError("Model must be trained first.")
        return self.feature_importance
    
    def save(self, path: str) -> None:
        """
        Save model to file.
        
        Args:
            path: Path to save model (should be .json)
        """
        if self.model is None:
            raise RuntimeError("Model must be trained first.")
        
        self.model.save_model(path)
        if config.VERBOSE:
            print(f"[INFO] XGBoost model saved to {path}")
    
    def load(self, path: str) -> None:
        """
        Load model from file.
        
        Args:
            path: Path to load model from
        """
        self.model = xgb.Booster()
        self.model.load_model(path)
        self.feature_importance = self.model.get_score(importance_type='weight')
        
        if config.VERBOSE:
            print(f"[INFO] XGBoost model loaded from {path}")
