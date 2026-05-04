"""
Decision-Level Fusion for TB Detection.
Combines independent image and tabular probabilities at inference time.
Handles cases where only one modality is available.
"""

import numpy as np
from sklearn.linear_model import LogisticRegression
import pickle
import os
import config


class DecisionLevelFusion:
    """
    Fuses predictions from Image and Tabular branches at decision level.
    Works with calibrated probabilities from each branch.
    """
    
    def __init__(self, fusion_type='weighted_average', weights=None):
        """
        Args:
            fusion_type: 'weighted_average' or 'logistic_regression'
            weights: [w_image, w_tabular] for weighted average (must sum to 1)
        """
        self.fusion_type = fusion_type
        self.weights = weights if weights is not None else [0.5, 0.5]
        self.meta_classifier = None  # For logistic regression fusion
        self.is_trained = False
    
    def weighted_average_fusion(self, p_image, p_tabular, weight_image=0.5):
        """
        Combine using weighted average.
        
        Args:
            p_image: Probability from image branch (0-1)
            p_tabular: Probability from tabular branch (0-1)
            weight_image: Weight for image prediction
            
        Returns:
            fused_probability: Combined probability
        """
        weight_tabular = 1.0 - weight_image
        fused = weight_image * p_image + weight_tabular * p_tabular
        return float(np.clip(fused, 0, 1))
    
    def logistic_regression_fusion(self, p_image, p_tabular):
        """
        Combine using trained logistic regression meta-classifier.
        
        Args:
            p_image: Probability from image branch
            p_tabular: Probability from tabular branch
            
        Returns:
            fused_probability: Combined probability
        """
        if self.meta_classifier is None:
            raise ValueError("Meta-classifier not trained. Call train_meta_classifier first.")
        
        # Stack probabilities as features
        X = np.array([[p_image, p_tabular]]).reshape(1, -1)
        fused = self.meta_classifier.predict_proba(X)[0, 1]
        return float(fused)
    
    def train_meta_classifier(self, val_probs_image, val_probs_tabular, val_labels):
        """
        Train logistic regression meta-classifier on validation data.
        
        Args:
            val_probs_image: Image predictions on validation set (N,)
            val_probs_tabular: Tabular predictions on validation set (N,)
            val_labels: True labels on validation set (N,)
        """
        X = np.column_stack([val_probs_image, val_probs_tabular])
        self.meta_classifier = LogisticRegression(random_state=42)
        self.meta_classifier.fit(X, val_labels)
        self.is_trained = True
        
        print(f"[Fusion] Meta-classifier trained. Coefficients: {self.meta_classifier.coef_[0]}")
    
    def fuse(self, p_image=None, p_tabular=None):
        """
        Fuse predictions handling missing modalities.
        
        Args:
            p_image: Probability from image (None if not available)
            p_tabular: Probability from tabular (None if not available)
            
        Returns:
            dict with 'probability', 'source', and 'confidence'
        """
        # Handle missing modalities
        if p_image is None and p_tabular is None:
            raise ValueError("At least one modality must be provided")
        
        if p_image is None:
            return {
                'probability': float(p_tabular),
                'source': 'tabular_only',
                'confidence': 'medium'
            }
        
        if p_tabular is None:
            return {
                'probability': float(p_image),
                'source': 'image_only',
                'confidence': 'medium'
            }
        
        # Both modalities available
        if self.fusion_type == 'weighted_average':
            fused_prob = self.weighted_average_fusion(p_image, p_tabular, 
                                                      weight_image=self.weights[0])
        elif self.fusion_type == 'logistic_regression':
            fused_prob = self.logistic_regression_fusion(p_image, p_tabular)
        else:
            raise ValueError(f"Unknown fusion type: {self.fusion_type}")
        
        return {
            'probability': fused_prob,
            'p_image': float(p_image),
            'p_tabular': float(p_tabular),
            'source': 'fusion',
            'confidence': 'high'
        }
    
    def save(self, path):
        """Save fusion model."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump({
                'fusion_type': self.fusion_type,
                'weights': self.weights,
                'meta_classifier': self.meta_classifier,
                'is_trained': self.is_trained
            }, f)
        print(f"[Fusion] Model saved to {path}")
    
    def load(self, path):
        """Load fusion model."""
        with open(path, 'rb') as f:
            data = pickle.load(f)
        
        self.fusion_type = data['fusion_type']
        self.weights = data['weights']
        self.meta_classifier = data['meta_classifier']
        self.is_trained = data['is_trained']
        print(f"[Fusion] Model loaded from {path}")


class MultimodalInferenceEngine:
    """
    Unified inference engine combining image and tabular models with fusion.
    """
    
    def __init__(self, cnn_model, xgboost_model, fusion_model, 
                 image_preprocessor, tabular_preprocessor):
        """
        Args:
            cnn_model: Trained CNN model
            xgboost_model: Trained XGBoost model
            fusion_model: DecisionLevelFusion instance
            image_preprocessor: ImagePreprocessor instance
            tabular_preprocessor: TabularPreprocessor instance
        """
        self.cnn_model = cnn_model
        self.xgboost_model = xgboost_model
        self.fusion_model = fusion_model
        self.image_preprocessor = image_preprocessor
        self.tabular_preprocessor = tabular_preprocessor
    
    def predict(self, image_path=None, tabular_features=None):
        """
        Make prediction using available modalities.
        
        Args:
            image_path: Path to CXR image (None if not available)
            tabular_features: Dict or array of clinical features (None if not available)
            
        Returns:
            dict with TB probability, source, and individual branch probabilities
        """
        p_image = None
        p_tabular = None
        
        # Get image prediction if available
        if image_path is not None:
            try:
                from PIL import Image
                import torch
                
                img = Image.open(image_path).convert('L')
                img_array = np.array(img)
                img_tensor = self.image_preprocessor.preprocess(img_array)
                
                with torch.no_grad():
                    output = self.cnn_model(img_tensor.unsqueeze(0))
                    p_image = torch.sigmoid(output).item()
                
                print(f"[Inference] Image prediction: {p_image:.4f}")
            except Exception as e:
                print(f"[Inference] Error processing image: {e}")
                p_image = None
        
        # Get tabular prediction if available
        if tabular_features is not None:
            try:
                if isinstance(tabular_features, dict):
                    tabular_features = np.array(list(tabular_features.values())).reshape(1, -1)
                elif isinstance(tabular_features, list):
                    tabular_features = np.array(tabular_features).reshape(1, -1)
                
                tabular_processed = self.tabular_preprocessor.transform(tabular_features)
                p_tabular = self.xgboost_model.predict_proba(tabular_processed)[0, 1]
                
                print(f"[Inference] Tabular prediction: {p_tabular:.4f}")
            except Exception as e:
                print(f"[Inference] Error processing tabular data: {e}")
                p_tabular = None
        
        # Fuse predictions
        result = self.fusion_model.fuse(p_image, p_tabular)
        
        return result
    
    def batch_predict(self, image_paths=None, tabular_features_list=None):
        """
        Make predictions for multiple samples.
        
        Args:
            image_paths: List of image paths
            tabular_features_list: List of tabular feature dicts/arrays
            
        Returns:
            List of prediction dicts
        """
        results = []
        
        # Ensure lists match
        if image_paths is None:
            image_paths = [None] * len(tabular_features_list)
        if tabular_features_list is None:
            tabular_features_list = [None] * len(image_paths)
        
        for img_path, tab_features in zip(image_paths, tabular_features_list):
            result = self.predict(img_path, tab_features)
            results.append(result)
        
        return results
