"""
Configuration file for TB Multimodal Detection Pipeline.
All paths, hyperparameters, and settings are defined here.
"""

import os
from pathlib import Path

# ==================== Dataset Paths ====================

DATASET_ROOT = "/images/nih/cxr/dataset"  
IMAGES_DIR = os.path.join(DATASET_ROOT, "images")  # Folder containing all CXR images
DATA_ENTRY_CSV = os.path.join(DATASET_ROOT, "Data_entry_2017.csv")  # Metadata CSV
TRAIN_VAL_LIST = os.path.join(DATASET_ROOT, "train_val_list.txt")  # Train/val split file
TEST_LIST = os.path.join(DATASET_ROOT, "test_list.txt")  # Test split file
BBOX_LIST = os.path.join(DATASET_ROOT, "BBox_list_2017.csv")  