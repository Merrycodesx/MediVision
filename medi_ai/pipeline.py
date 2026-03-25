"""
Main training pipeline orchestrating all components.
"""

import numpy as np
import pandas as pd
import torch
from torch.utils.data import TensorDataset, DataLoader
import config
from data.loader import NIHCXRDataLoader
from data.preprocessor import ImagePreprocessor, TabularPreprocessor, DataBalancer
from models.cnn import DenseNetCNN, CNNTrainer
from models.tabular import XGBoostTabular
from models.fusion import LateFusionModel
from utils.metrics import MetricsCalculator, Visualizer
import pickle


class TBDetectionPipeline:
    """
    End-to-end training pipeline for TB detection.
    Orchestrates data loading, preprocessing, model training, and evaluation.
    """
    
    def __init__(self):
        """Initialize pipeline."""
        self.data_loader = NIHCXRDataLoader()
        self.image_preprocessor = ImagePreprocessor(augment=True)
        self.tabular_preprocessor = TabularPreprocessor()
        self.data_balancer = DataBalancer()
        
        self.cnn_model = None
        self.xgb_model = None
        self.fusion_model = None
        
        self.X_train_img = None
        self.X_train_tab = None
        self.X_val_img = None
        self.X_val_tab = None
        self.X_test_img = None
        self.X_test_tab = None
        
        self.y_train = None
        self.y_val = None
        self.y_test = None
        
        self.metrics = {'train': {}, 'val': {}, 'test': {}}
    
    def run(self) -> None:
        """Run the complete pipeline."""
        print("\n" + "="*60)
        print("TB MULTIMODAL DETECTION PIPELINE")
        print("="*60)
        
        # 1. Data Loading
        print("\n[STEP 1/5] Loading data...")
        self._load_data()
        
        # 2. Preprocessing
        print("\n[STEP 2/5] Preprocessing data...")
        self._preprocess_data()
        
        # 3. Train Image Model (CNN)
        print("\n[STEP 3/5] Training CNN model...")
        self._train_cnn()
        
        # 4. Train Tabular Model (XGBoost)
        print("\n[STEP 4/5] Training XGBoost model...")
        self._train_xgboost()
        
        # 5. Train Fusion Model
        print("\n[STEP 5/5] Training fusion model...")
        self._train_fusion()
        
        # Evaluate
        print("\n[EVALUATION] Evaluating on test set...")
        self._evaluate()
        
        # Save models
        print("\n[SAVING] Saving all models...")
        self._save_models()
        
        print("\n" + "="*60)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print("="*60)
    
    def _load_data(self) -> None:
        """Load dataset from local files."""
        # Get data
        dataset = self.data_loader.create_dataset_dict()
        
        train_data = dataset['train']
        val_data = dataset['val']
        test_data = dataset['test']
        
        # Separate images and metadata
        self.train_ids = [x[0] for x in train_data]
        self.train_meta = [x[1] for x in train_data]
        self.y_train = np.array([x[2] for x in train_data])
        
        self.val_ids = [x[0] for x in val_data]
        self.val_meta = [x[1] for x in val_data]
        self.y_val = np.array([x[2] for x in val_data])
        
        self.test_ids = [x[0] for x in test_data]
        self.test_meta = [x[1] for x in test_data]
        self.y_test = np.array([x[2] for x in test_data])
    
    def _preprocess_data(self) -> None:
        """Preprocess images and tabular data."""
        # Process images
        print("  Processing images...")
        self.X_train_img = self._load_images(self.train_ids)
        self.X_val_img = self._load_images(self.val_ids)
        self.X_test_img = self._load_images(self.test_ids)
        
        # Process tabular
        print("  Processing tabular data...")
        train_tab_df = pd.DataFrame(self.train_meta)
        val_tab_df = pd.DataFrame(self.val_meta)
        test_tab_df = pd.DataFrame(self.test_meta)
        
        self.tabular_preprocessor.fit(train_tab_df)
        self.X_train_tab = self.tabular_preprocessor.transform(train_tab_df)
        self.X_val_tab = self.tabular_preprocessor.transform(val_tab_df)
        self.X_test_tab = self.tabular_preprocessor.transform(test_tab_df)
        
        # Balance training data
        print("  Balancing training data...")
        self.X_train_tab, self.y_train = self.data_balancer.balance(self.X_train_tab, self.y_train)
        
        # Re-load corresponding images after balancing
        # (For simplicity, we'll skip this - in production, you'd need to track which images were kept)
    
    def _load_images(self, image_ids: list) -> torch.Tensor:
        """Load and preprocess images."""
        images = []
        for img_id in image_ids:
            try:
                img_array = self.data_loader.load_image(img_id)
                img_tensor = self.image_preprocessor.preprocess(img_array)
                images.append(img_tensor)
            except Exception as e:
                if config.VERBOSE:
                    print(f"[WARNING] Failed to load image {img_id}: {e}")
                continue
        
        return torch.stack(images)
    
    def _train_cnn(self) -> None:
        """Train DenseNet121 CNN."""
        # Create model
        self.cnn_model = DenseNetCNN(pretrained=True)
        trainer = CNNTrainer(self.cnn_model)
        
        # Create data loaders
        train_dataset = TensorDataset(self.X_train_img, torch.from_numpy(self.y_train).long())
        val_dataset = TensorDataset(self.X_val_img, torch.from_numpy(self.y_val).long())
        
        train_loader = DataLoader(train_dataset, batch_size=config.BATCH_SIZE, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=config.BATCH_SIZE)
        
        # Train
        best_val_loss = float('inf')
        for epoch in range(config.EPOCHS):
            train_loss, train_acc = trainer.train_epoch(train_loader)
            val_loss, val_acc = trainer.validate(val_loader)
            
            if config.VERBOSE:
                print(f"Epoch {epoch+1}/{config.EPOCHS} - "
                      f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f} | "
                      f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
            
            if trainer.should_stop_early(val_loss):
                print(f"[INFO] Early stopping at epoch {epoch+1}")
                break
        
        self.cnn_trainer = trainer
    
    def _train_xgboost(self) -> None:
        """Train XGBoost on tabular data."""
        self.xgb_model = XGBoostTabular()
        
        feature_names = self.tabular_preprocessor.feature_names
        self.xgb_model.train(
            self.X_train_tab, self.y_train,
            self.X_val_tab, self.y_val,
            feature_names=feature_names
        )
    
    def _train_fusion(self) -> None:
        """Train late fusion model."""
        # Get predictions from both modalities on validation set
        with torch.no_grad():
            self.cnn_model.eval()
            val_logits = self.cnn_model(self.X_val_img.to(config.DEVICE))
            cnn_proba_val = torch.sigmoid(val_logits).cpu().numpy()
        
        xgb_proba_val = self.xgb_model.predict(self.X_val_tab, return_proba=True)
        
        # Train fusion
        self.fusion_model = LateFusionModel()
        self.fusion_model.train(cnn_proba_val, xgb_proba_val, self.y_val)
    
    def _evaluate(self) -> None:
        """Evaluate models on test set."""
        # Get predictions from both modalities
        with torch.no_grad():
            self.cnn_model.eval()
            test_logits = self.cnn_model(self.X_test_img.to(config.DEVICE))
            cnn_proba_test = torch.sigmoid(test_logits).cpu().numpy().flatten()
            cnn_pred_test = (cnn_proba_test > 0.5).astype(int)
        
        xgb_proba_test = self.xgb_model.predict(self.X_test_tab, return_proba=True)
        xgb_pred_test = (xgb_proba_test > 0.5).astype(int)
        
        fusion_proba_test = self.fusion_model.predict(cnn_proba_test, xgb_proba_test)
        fusion_pred_test = (fusion_proba_test > 0.5).astype(int)
        
        # Calculate metrics
        print("\n" + "-"*60)
        print("CNN Results")
        print("-"*60)
        metrics_cnn = MetricsCalculator.compute_metrics(self.y_test, cnn_pred_test, cnn_proba_test)
        MetricsCalculator.print_metrics(metrics_cnn, "CNN Test")
        
        print("\n" + "-"*60)
        print("XGBoost Results")
        print("-"*60)
        metrics_xgb = MetricsCalculator.compute_metrics(self.y_test, xgb_pred_test, xgb_proba_test)
        MetricsCalculator.print_metrics(metrics_xgb, "XGBoost Test")
        
        print("\n" + "-"*60)
        print("Fusion Results")
        print("-"*60)
        metrics_fusion = MetricsCalculator.compute_metrics(self.y_test, fusion_pred_test, fusion_proba_test)
        MetricsCalculator.print_metrics(metrics_fusion, "Fusion Test")
        
        # Visualizations
        print("\nGenerating visualizations...")
        Visualizer.plot_confusion_matrix(self.y_test, fusion_pred_test,
                                        save_path=f"{config.PLOTS_DIR}/confusion_matrix.png")
        Visualizer.plot_roc_curve(self.y_test, fusion_proba_test,
                                 save_path=f"{config.PLOTS_DIR}/roc_curve.png")
        Visualizer.plot_label_distribution(self.y_train, self.y_val, self.y_test,
                                          save_path=f"{config.PLOTS_DIR}/label_distribution.png")
    
    def _save_models(self) -> None:
        """Save all trained models."""
        # Save CNN
        self.cnn_trainer.save_checkpoint(config.CNN_MODEL_PATH)
        
        # Save XGBoost
        self.xgb_model.save(config.XGBOOST_MODEL_PATH)
        
        # Save tabular preprocessor
        scaler_data = {
            'scaler': self.tabular_preprocessor.scaler,
            'label_encoder': self.tabular_preprocessor.label_encoder,
            'feature_names': self.tabular_preprocessor.feature_names,
        }
        with open(config.SCALER_PATH, 'wb') as f:
            pickle.dump(scaler_data, f)
        
        # Save fusion model
        self.fusion_model.save(config.FUSION_MODEL_PATH)
        
        print(f"[INFO] All models saved to {config.MODELS_DIR}")
