"""
Data preprocessing for image and tabular data.
Handles normalization, augmentation, encoding, and SMOTE balancing.
"""

import numpy as np
import pandas as pd
from PIL import Image, ImageEnhance
import torch
from torchvision import transforms
from sklearn.preprocessing import LabelEncoder, StandardScaler
from imblearn.over_sampling import SMOTE
from typing import Tuple, List, Dict, Any
import config


class ImagePreprocessor:
    """Handles image loading, preprocessing, and augmentation."""
    
    def __init__(self, augment=False):
        """
        Initialize image preprocessor.
        
        Args:
            augment: If True, apply data augmentation (for training)
        """
        self.augment = augment
        self.normalize = transforms.Normalize(
            mean=config.IMAGE_NORMALIZE_MEAN,
            std=config.IMAGE_NORMALIZE_STD
        )
    
    def preprocess(self, image: np.ndarray) -> torch.Tensor:
        """
        Preprocess a single image.
        
        Args:
            image: numpy array (H, W) for grayscale or (H, W, 3) for RGB
            
        Returns:
            torch.Tensor (3, H, W) ready for DenseNet
        """
        # Convert to PIL Image
        if image.dtype != np.uint8:
            image = (image * 255).astype(np.uint8)
        
        pil_image = Image.fromarray(image)
        
        # Resize
        pil_image = pil_image.resize((config.IMAGE_SIZE, config.IMAGE_SIZE), Image.LANCZOS)
        
        # Apply augmentation if enabled
        if self.augment:
            pil_image = self._augment(pil_image)
        
        # Convert to tensor and normalize
        image_tensor = transforms.ToTensor()(pil_image)
        
        # Convert grayscale to RGB if needed
        if image_tensor.shape[0] == 1:
            image_tensor = image_tensor.repeat(3, 1, 1)
        
        # Normalize
        image_tensor = self.normalize(image_tensor)
        
        return image_tensor
    
    def _augment(self, image: Image.Image) -> Image.Image:
        """Apply random augmentations."""
        # Random rotation
        if np.random.rand() > 0.5:
            angle = np.random.uniform(-15, 15)
            image = image.rotate(angle, expand=False)
        
        # Random brightness
        if np.random.rand() > 0.5:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(np.random.uniform(0.8, 1.2))
        
        # Random contrast
        if np.random.rand() > 0.5:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(np.random.uniform(0.8, 1.2))
        
        return image


class TabularPreprocessor:
    """Handles tabular data preprocessing."""
    
    def __init__(self):
        """Initialize with encoders and scalers."""
        self.label_encoder = {}  # For categorical features
        self.scaler = StandardScaler()
        self.feature_names = None
        self.is_fitted = False
    
    def fit(self, data: pd.DataFrame) -> None:
        """
        Fit preprocessor on training data.
        
        Args:
            data: DataFrame with columns 'age', 'sex'
        """
        # Handle missing values
        data = data.fillna(data.median(numeric_only=True))
        
        # Encode categorical features
        for col in ['sex']:
            if col in data.columns:
                le = LabelEncoder()
                data[col] = le.fit_transform(data[col])
                self.label_encoder[col] = le
        
        # Fit scaler
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        self.feature_names = list(numeric_cols)
        self.scaler.fit(data[self.feature_names])
        
        self.is_fitted = True
        
        if config.VERBOSE:
            print(f"[INFO] Tabular preprocessor fitted on {len(self.feature_names)} features.")
    
    def transform(self, data: pd.DataFrame) -> np.ndarray:
        """
        Transform data using fitted encoders/scalers.
        
        Args:
            data: DataFrame with columns 'age', 'sex'
            
        Returns:
            Scaled numpy array (N, n_features)
        """
        if not self.is_fitted:
            raise RuntimeError("Preprocessor must be fitted first.")
        
        # Handle missing values
        data = data.fillna(data.median(numeric_only=True))
        
        # Encode categorical features
        for col in ['sex']:
            if col in data.columns and col in self.label_encoder:
                data = data.copy()
                data[col] = self.label_encoder[col].transform(data[col])
        
        # Select numeric features
        X = data[self.feature_names]
        
        # Scale
        X_scaled = self.scaler.transform(X)
        
        return X_scaled
    
    def fit_transform(self, data: pd.DataFrame) -> np.ndarray:
        """Fit and transform in one step."""
        self.fit(data)
        return self.transform(data)


class DataBalancer:
    """Handles SMOTE for imbalanced data."""
    
    def __init__(self):
        """Initialize SMOTE."""
        self.smote = SMOTE(k_neighbors=config.SMOTE_K_NEIGHBORS, random_state=config.RANDOM_STATE)
    
    def balance(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Apply SMOTE to balance classes.
        
        Args:
            X: Features (N, n_features)
            y: Labels (N,)
            
        Returns:
            Tuple of (balanced_X, balanced_y)
        """
        if not config.USE_SMOTE:
            return X, y
        
        # Only apply if imbalanced
        unique, counts = np.unique(y, return_counts=True)
        if len(unique) < 2:
            return X, y
        
        minority_count = min(counts)
        if minority_count < config.SMOTE_K_NEIGHBORS:
            if config.VERBOSE:
                print(f"[WARNING] Minority class too small ({minority_count}) for SMOTE. Skipping.")
            return X, y
        
        X_balanced, y_balanced = self.smote.fit_resample(X, y)
        
        if config.VERBOSE:
            print(f"[INFO] SMOTE applied - Original: {len(y)}, Balanced: {len(y_balanced)}")
        
        return X_balanced, y_balanced