"""
Configuration file for TB Multimodal Detection Pipeline.
All paths, hyperparameters, and settings are defined here.
"""

import os
import torch
from pathlib import Path

# ==================== Dataset Paths ====================

DATASET_ROOT = "/images/nih/cxr/dataset"  
IMAGES_DIR = os.path.join(DATASET_ROOT, "images")  # Folder containing all CXR images
DATA_ENTRY_CSV = os.path.join(DATASET_ROOT, "Data_entry_2017.csv")  # Metadata CSV
TRAIN_VAL_LIST = os.path.join(DATASET_ROOT, "train_val_list.txt")  # Train/val split file
TEST_LIST = os.path.join(DATASET_ROOT, "test_list.txt")  # Test split file
BBOX_LIST = os.path.join(DATASET_ROOT, "BBox_list_2017.csv")

# ==================== Model Hyperparameters ====================

DROPOUT_RATE = 0.5
LEARNING_RATE = 0.001
BATCH_SIZE = 32
NUM_EPOCHS = 50
NUM_CLASSES = 2

# ==================== Model Paths ====================

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models', 'trained')
CNN_MODEL_PATH = os.path.join(MODELS_DIR, 'densenet_cnn.pth')
XGB_MODEL_PATH = os.path.join(MODELS_DIR, 'xgboost_model.json')
FUSION_MODEL_PATH = os.path.join(MODELS_DIR, 'fusion_model.pkl')
SCALER_PATH = os.path.join(MODELS_DIR, 'scaler.pkl')

# ==================== Device Configuration ====================

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'  