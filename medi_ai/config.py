"""
Configuration file for TB Multimodal Detection Pipeline.
All paths, hyperparameters, and settings are defined here.
"""

import os
from pathlib import Path

# ==================== Dataset Paths ====================
# Chest X-Ray Dataset (with train/val/test folder structure)
CXR_DATASET_ROOT = r"D:\Medi-TB\medi_AI\medi_ai\images\xray"  # Root directory - contains train/, val/, test/ folders
CXR_METADATA_EXCEL = r"D:\Medi-TB\medi_AI\medi_ai\images\xray\dataset_splits_with_metadata.csv"  # Excel file with columns: name, label, source, split

# Synthetic TB Tabular Dataset (from Hugging Face / synthetic-tb-screening)
TABULAR_DATASET_HIGH = r"D:\Medi-TB\medi_AI\medi_ai\images\table\tb_high_tb_burden.csv"
TABULAR_DATASET_MODERATE = r"D:\Medi-TB\medi_AI\medi_ai\images\table\tb_moderate_tb_burden.csv"
TABULAR_DATASET_LOW = r"D:\Medi-TB\medi_AI\medi_ai\images\table\tb_low_tb_burden.csv"
TABULAR_DATASET_CSV = [TABULAR_DATASET_HIGH, TABULAR_DATASET_MODERATE, TABULAR_DATASET_LOW]  # CSV with TB screening data


# ==================== Output Paths ====================
OUTPUT_DIR = "./tb_detection_output"
MODELS_DIR = os.path.join(OUTPUT_DIR, "models")
PLOTS_DIR = os.path.join(OUTPUT_DIR, "plots")
REPORTS_DIR = os.path.join(OUTPUT_DIR, "reports")
LOGS_DIR = os.path.join(OUTPUT_DIR, "logs")

# Create output directories if they don't exist
for dir_path in [MODELS_DIR, PLOTS_DIR, REPORTS_DIR, LOGS_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# ==================== Model Paths ====================
CNN_MODEL_PATH = os.path.join(MODELS_DIR, "densenet_cnn.pth")
XGBOOST_MODEL_PATH = os.path.join(MODELS_DIR, "xgboost_model.pkl")
FUSION_MODEL_PATH = os.path.join(MODELS_DIR, "fusion_model.pkl")
LABEL_ENCODER_PATH = os.path.join(MODELS_DIR, "label_encoder.pkl")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler.pkl")

# ==================== Report Paths ====================
TRAINING_REPORT_PATH = os.path.join(REPORTS_DIR, "01_training_report.html")
VALIDATION_REPORT_PATH = os.path.join(REPORTS_DIR, "02_validation_report.html")
PERFORMANCE_REPORT_PATH = os.path.join(REPORTS_DIR, "03_performance_metrics.html")
CORRELATION_REPORT_PATH = os.path.join(REPORTS_DIR, "04_correlation_analysis.html")
FINAL_SUMMARY_REPORT = os.path.join(REPORTS_DIR, "05_final_summary.html")

# ==================== Image Preprocessing ====================
IMAGE_SIZE = 224
IMAGE_NORMALIZE_MEAN = [0.485, 0.456, 0.406]  # ImageNet normalization
IMAGE_NORMALIZE_STD = [0.229, 0.224, 0.225]
IMAGE_FORMAT = "L"  # Grayscale ('L') or RGB ('RGB')

# ==================== Training Hyperparameters ====================
EPOCHS = 30
CNN_EPOCHS = EPOCHS
BATCH_SIZE = 32
LEARNING_RATE = 1e-4
CNN_LEARNING_RATE = LEARNING_RATE
WEIGHT_DECAY = 1e-5
DROPOUT_RATE = 0.3
PATIENCE = 5  # Early stopping patience

# ==================== XGBoost Hyperparameters ====================
XGBOOST_PARAMS = {
    'objective': 'binary:logistic',
    'max_depth': 6,
    'learning_rate': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'n_estimators': 100,
    'random_state': 42,
}

# ==================== Data Split ====================
TRAIN_SIZE = 0.8
VAL_SIZE = 0.1
TEST_SIZE = 0.1
RANDOM_STATE = 42

# ==================== Class Balance ====================
USE_SMOTE = True  # Apply SMOTE for imbalance handling
SMOTE_K_NEIGHBORS = 5

# ==================== Fusion Model ====================
FUSION_ALPHA = 0.5  # Weight for image modality (1-ALPHA for tabular)

# ==================== Device ====================
DEVICE = "cpu"  # "cuda" or "cpu"

# ==================== Logging ====================
VERBOSE = True
LOG_INTERVAL = 10  # Log every N batches