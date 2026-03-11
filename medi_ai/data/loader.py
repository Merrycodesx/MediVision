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
    
    def load_bbox(self) -> pd.DataFrame:
        """Load bounding box annotations if available."""
        if self.bbox_df is not None:
            return self.bbox_df
            
        if not os.path.exists(config.BBOX_LIST):
            if config.VERBOSE:
                print(f"[WARNING] BBox file not found: {config.BBOX_LIST}")
            return None
            
        self.bbox_df = pd.read_csv(config.BBOX_LIST)
        if config.VERBOSE:
            print(f"[INFO] Loaded bounding boxes for {len(self.bbox_df)} annotations.")
        return self.bbox_df
    
    def get_split_ids(self) -> Tuple[List[str], List[str], List[str]]:
        """
        Get image IDs for train/val/test splits.
        
        Returns:
            Tuple of (train_ids, val_ids, test_ids)
        """
        # Read train/val split
        with open(config.TRAIN_VAL_LIST, 'r') as f:
            train_val_ids = [line.strip() for line in f if line.strip()]
        
        # Read test split
        with open(config.TEST_LIST, 'r') as f:
            test_ids = [line.strip() for line in f if line.strip()]
        
        # Further split train/val
        np.random.seed(config.RANDOM_STATE)
        np.random.shuffle(train_val_ids)
        split_idx = int(len(train_val_ids) * (config.TRAIN_SIZE / (config.TRAIN_SIZE + config.VAL_SIZE)))
        train_ids = train_val_ids[:split_idx]
        val_ids = train_val_ids[split_idx:]
        
        if config.VERBOSE:
            print(f"[INFO] Data split - Train: {len(train_ids)}, Val: {len(val_ids)}, Test: {len(test_ids)}")
        
        return train_ids, val_ids, test_ids
    
    def load_image(self, image_id: str) -> np.ndarray:
        """
        Load a single image by ID.
        
        Args:
            image_id: Image filename (e.g., '00000001_000.png')
            
        Returns:
            Image as numpy array (H, W) for grayscale or (H, W, 3) for RGB
        """
        image_path = os.path.join(config.IMAGES_DIR, image_id)
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Load as grayscale
        img = Image.open(image_path).convert(config.IMAGE_FORMAT)
        return np.array(img)
    
    def get_label_from_findings(self, findings: str) -> int:
        """
        Extract TB label from findings string.
        
        TB is labeled as 1 if 'Tuberculosis' appears in findings, 0 otherwise.
        
        Args:
            findings: Pipe-separated findings string (e.g., 'Atelectasis|No Finding')
            
        Returns:
            1 if TB present, 0 otherwise
        """
        if pd.isna(findings):
            return 0
        
        findings_lower = str(findings).lower()
        return 1 if 'tuberculosis' in findings_lower else 0
    
    def create_dataset_dict(self) -> Dict:
        """
        Create a dictionary with all data organized by split.
        
        Returns:
            Dictionary with 'train', 'val', 'test' keys, each containing
            list of tuples (image_id, metadata_dict, tb_label)
        """
        metadata = self.load_metadata()
        train_ids, val_ids, test_ids = self.get_split_ids()
        
        dataset = {'train': [], 'val': [], 'test': []}
        
        # Create metadata lookup
        id_to_row = {}
        for idx, row in metadata.iterrows():
            id_to_row[row['image_id']] = row
        
        # Process each split
        for split, ids in [('train', train_ids), ('val', val_ids), ('test', test_ids)]:
            for img_id in ids:
                if img_id not in id_to_row:
                    continue
                
                row = id_to_row[img_id]
                
                # Extract metadata
                meta_dict = {
                    'age': float(row['age']) if pd.notna(row['age']) else 0,
                    'sex': row['sex'],  # 'M' or 'F'
                }
                
                # Extract TB label
                tb_label = self.get_label_from_findings(row['findings'])
                
                dataset[split].append((img_id, meta_dict, tb_label))
        
        if config.VERBOSE:
            for split in ['train', 'val', 'test']:
                tb_count = sum(1 for _, _, label in dataset[split] if label == 1)
                total = len(dataset[split])
                print(f"[INFO] {split.upper()} - Total: {total}, TB: {tb_count}, No TB: {total-tb_count}")
        
        return dataset