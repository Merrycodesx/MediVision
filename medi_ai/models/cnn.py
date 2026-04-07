"""
DenseNet121 CNN model for X-ray image classification.
"""

import torch
import torch.nn as nn
import torchvision.models as models
from typing import Tuple
import config


class DenseNetCNN(nn.Module):
    """
    DenseNet121 model for binary classification (TB vs No TB).
    Optimized for medical imaging with dropout regularization.
    """
    
    def __init__(self, pretrained=True, dropout_rate=config.DROPOUT_RATE):
        """
        Initialize DenseNet121.
        
        Args:
            pretrained: Use ImageNet pre-trained weights
            dropout_rate: Dropout probability
        """
        super(DenseNetCNN, self).__init__()
        
        # Load pre-trained DenseNet121
        self.densenet = models.densenet121(pretrained=pretrained)
        
        # Freeze early layers (optional, for transfer learning)
        # Uncomment to freeze batch norm and first few blocks
        # for param in list(self.densenet.parameters())[:-10]:
        #     param.requires_grad = False
        
        # Modify final classification layer
        num_features = self.densenet.classifier.in_features
        self.densenet.classifier = nn.Sequential(
            nn.Dropout(dropout_rate),
            nn.Linear(num_features, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(512, 1),  # Binary classification
        )
        
        self.dropout_rate = dropout_rate
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Input images (B, 3, H, W)
            
        Returns:
            Logits (B, 1)
        """
        return self.densenet(x)
    
    def extract_features(self, x: torch.Tensor) -> torch.Tensor:
        """
        Extract deep features before classification.
        Useful for interpretability and visualization.
        
        Args:
            x: Input images (B, 3, H, W)
            
        Returns:
            Feature tensor (B, num_features)
        """
        return self.densenet.features(x)
    
    def get_grad_cam_hooks(self):
        """Return target layer for Grad-CAM visualization."""
        return self.densenet.features[-1]  # Last dense block


class CNNTrainer:
    """Trainer for DenseNet CNN model."""
    
    def __init__(self, model: DenseNetCNN, device: str = config.DEVICE):
        """
        Initialize trainer.
        
        Args:
            model: DenseNet model
            device: 'cuda' or 'cpu'
        """
        self.model = model.to(device)
        self.device = device
        self.criterion = nn.BCEWithLogitsLoss()
        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=config.LEARNING_RATE,
            weight_decay=config.WEIGHT_DECAY
        )
        self.best_val_loss = float('inf')
        self.patience_counter = 0
    
    def train_epoch(self, train_loader) -> Tuple[float, float]:
        """
        Train for one epoch.
        
        Args:
            train_loader: DataLoader with (image, label) tuples
            
        Returns:
            Tuple of (avg_loss, avg_accuracy)
        """
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        
        for batch_idx, (images, labels) in enumerate(train_loader):
            images = images.to(self.device)
            labels = labels.float().unsqueeze(1).to(self.device)
            
            self.optimizer.zero_grad()
            outputs = self.model(images)
            loss = self.criterion(outputs, labels)
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            
            # Compute accuracy
            predictions = (torch.sigmoid(outputs) > 0.5).int()
            correct += (predictions == labels.int()).sum().item()
            total += labels.size(0)
            
            if config.VERBOSE and (batch_idx + 1) % config.LOG_INTERVAL == 0:
                print(f"  [Batch {batch_idx + 1}] Loss: {loss.item():.4f}")
        
        avg_loss = total_loss / len(train_loader)
        avg_acc = correct / total if total > 0 else 0
        
        return avg_loss, avg_acc
    
    def validate(self, val_loader) -> Tuple[float, float]:
        """
        Validate on validation set.
        
        Args:
            val_loader: DataLoader with (image, label) tuples
            
        Returns:
            Tuple of (avg_loss, avg_accuracy)
        """
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(self.device)
                labels = labels.float().unsqueeze(1).to(self.device)
                
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                
                total_loss += loss.item()
                
                predictions = (torch.sigmoid(outputs) > 0.5).int()
                correct += (predictions == labels.int()).sum().item()
                total += labels.size(0)
        
        avg_loss = total_loss / len(val_loader)
        avg_acc = correct / total if total > 0 else 0
        
        return avg_loss, avg_acc
    
    def should_stop_early(self, val_loss: float) -> bool:
        """
        Check early stopping criterion.
        
        Args:
            val_loss: Validation loss
            
        Returns:
            True if should stop, False otherwise
        """
        if val_loss < self.best_val_loss:
            self.best_val_loss = val_loss
            self.patience_counter = 0
            return False
        else:
            self.patience_counter += 1
            return self.patience_counter >= config.PATIENCE
    
    def save_checkpoint(self, path: str) -> None:
        """Save model checkpoint."""
        torch.save(self.model.state_dict(), path)
        if config.VERBOSE:
            print(f"[INFO] Model saved to {path}")
    
    def load_checkpoint(self, path: str) -> None:
        """Load model checkpoint."""
        self.model.load_state_dict(torch.load(path, map_location=self.device))
        if config.VERBOSE:
            print(f"[INFO] Model loaded from {path}")
