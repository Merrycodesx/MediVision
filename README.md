<<<<<<< HEAD
# TB Multimodal Detection


**Models:**
- **Image**: DenseNet121 CNN for chest X-ray (CXR) analysis
- **Tabular**: XGBoost for clinical/demographic features (age, sex)
- **Fusion**: Late fusion with Logistic Regression for combined predictions

**Features:**
- Handles missing modalities (image-only, tabular-only, or both)
- SMOTE-based class balancing
- Comprehensive evaluation metrics and visualizations
- Modular, extensible architecture
- Works with NIH CXR dataset

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```
```

**Expected NIH CXR structure:**
```
dataset/
├── images/              # All CXR images (.png files)
├── Data_entry_2017.csv  # Metadata (Image Index, Patient Sex, Patient Age, Finding Labels, etc.)
├── train_val_list.txt   # List of train/val image filenames (one per line)
└── test_list.txt        # List of test image filenames (one per line)
```



## Usage

### Training

```bash
python main_train.py
```

This will:
1. Load NIH CXR dataset with metadata
2. Preprocess images and tabular features
3. Train DenseNet121 CNN
4. Train XGBoost on tabular data
5. Train late fusion model
6. Evaluate on test set
7. Save all models to `models/trained/`

**Output:**
- `models/trained/densenet_cnn.pth` - Trained CNN weights
- `models/trained/xgboost_model.json` - XGBoost model
- `models/trained/fusion_model.pkl` - Fusion model
- `models/trained/scaler.pkl` - Preprocessing objects
- `models/plots/` - Visualizations (confusion matrix, ROC curves, etc.)

### Inference

```python
from inference.engine import TBInferenceEngine

# Initialize
engine = TBInferenceEngine()
engine.load_models()

# Predict from image only
result_img = engine.predict(image_path="path/to/image.png")

# Predict from tabular only
result_tab = engine.predict(age=45.0, sex='M')

# Predict from both (multimodal)
result_multi = engine.predict(
    image_path="path/to/image.png",
    age=45.0,
    sex='M'
)

print(result_multi)
```

## Project Structure

```
tb_multimodal_detection/
├── config.py              # All paths, hyperparameters
├── main_train.py          # Entry point
├── pipeline.py            # Training orchestration
├── data/
│   ├── loader.py          # NIH CXR dataset loading
│   └── preprocessor.py    # Image and tabular preprocessing
├── models/
│   ├── cnn.py             # DenseNet121 model
│   ├── tabular.py         # XGBoost model
│   └── fusion.py          # Late fusion model
├── inference/
│   └── engine.py          # Inference pipeline
├── utils/
│   └── metrics.py         # Evaluation and visualization
├── requirements.txt
└── README.md
```

## Key Classes

### Data Loading
- `NIHCXRDataLoader` - Loads NIH dataset from local files

### Preprocessing
- `ImagePreprocessor` - Image normalization & augmentation
- `TabularPreprocessor` - Feature scaling & encoding
- `DataBalancer` - SMOTE for class imbalance

### Models
- `DenseNetCNN` - DenseNet121 with custom classifier
- `CNNTrainer` - Training loop with early stopping
- `XGBoostTabular` - XGBoost wrapper
- `LateFusionModel` - Learned late fusion

### Inference
- `TBInferenceEngine` - Unified inference interface

=======
# MediVision
An AI-powered system for TB detection using CXR images, lab results, and clinical data
>>>>>>> 708b70ebe0c9f378c409202b5b0090c2451bb34d
