"""
Data loader for NIH CXR dataset.
Handles loading images, metadata from CSV, and organizing data splits.
"""

import os
import pandas as pd
import numpy as np
from PIL import Image
from typing import Tuple, List, Dict
import config


class NIHCXRDataLoader:
    """
    Loads NIH Chest X-ray dataset from local files.
    
    Expects:
    - images/: folder with CXR images (e.g., 00000001_000.png)
    - Data_entry_2017.csv: metadata including labels
    - train_val_list.txt: image IDs for train/val split
    - test_list.txt: image IDs for test split
    - BBox_list_2017.csv: (optional) bounding box annotations
    """
    
    def __init__(self):
        """Initialize data loader and validate paths."""
        self._validate_paths()
        self.data_entry_df = None
        self.bbox_df = None
        
    def _validate_paths(self):
        """Check if all required files exist."""
        required_files = [
            config.IMAGES_DIR,
            config.DATA_ENTRY_CSV,
            config.TRAIN_VAL_LIST,
            config.TEST_LIST,
        ]
        
        for path in required_files:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Required file not found: {path}")
                
        if config.VERBOSE:
            print(f"[INFO] All dataset paths validated.")
    
    def load_metadata(self) -> pd.DataFrame:
        """Load metadata from Data_entry_2017.csv."""
        if self.data_entry_df is not None:
            return self.data_entry_df
            
        self.data_entry_df = pd.read_csv(config.DATA_ENTRY_CSV)
        
        # Standardize column names
        if 'Image Index' in self.data_entry_df.columns:
            self.data_entry_df.rename(columns={'Image Index': 'image_id'}, inplace=True)
        if 'Patient Sex' in self.data_entry_df.columns:
            self.data_entry_df.rename(columns={'Patient Sex': 'sex'}, inplace=True)
        if 'Patient Age' in self.data_entry_df.columns:
            self.data_entry_df.rename(columns={'Patient Age': 'age'}, inplace=True)
        if 'Finding Labels' in self.data_entry_df.columns:
            self.data_entry_df.rename(columns={'Finding Labels': 'findings'}, inplace=True)
            
        if config.VERBOSE:
            print(f"[INFO] Loaded metadata for {len(self.data_entry_df)} samples.")
            
        return self.data_entry_df