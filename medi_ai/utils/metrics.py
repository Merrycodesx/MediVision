"""
Evaluation metrics and visualization utilities.
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, confusion_matrix, classification_report
)
from sklearn.metrics import ConfusionMatrixDisplay
import config


class MetricsCalculator:
    """Calculate and report evaluation metrics."""
    
    @staticmethod
    def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, 
                       y_proba: np.ndarray = None) -> dict:
        """
        Compute comprehensive evaluation metrics.
        
        Args:
            y_true: True labels
            y_pred: Binary predictions
            y_proba: Probability predictions (for AUC)
            
        Returns:
            Dictionary with all metrics
        """
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1': f1_score(y_true, y_pred, zero_division=0),
        }
        
        if y_proba is not None:
            metrics['auc_roc'] = roc_auc_score(y_true, y_proba)
        
        return metrics
    
    @staticmethod
    def print_metrics(metrics: dict, split_name: str = "Test") -> None:
        """
        Print metrics in formatted table.
        
        Args:
            metrics: Dictionary of metrics
            split_name: Name of dataset split
        """
        print(f"\n{split_name} Metrics:")
        print("-" * 40)
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"{key:.<20} {value:.4f}")
        print("-" * 40)
    
    @staticmethod
    def get_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        """
        Get confusion matrix.
        
        Args:
            y_true: True labels
            y_pred: Binary predictions
            
        Returns:
            Confusion matrix (2, 2)
        """
        return confusion_matrix(y_true, y_pred)
    
    @staticmethod
    def print_classification_report(y_true: np.ndarray, y_pred: np.ndarray) -> None:
        """
        Print sklearn classification report.
        
        Args:
            y_true: True labels
            y_pred: Binary predictions
        """
        print("\nDetailed Classification Report:")
        print(classification_report(y_true, y_pred, 
                                   target_names=['No TB', 'TB']))


class Visualizer:
    """Visualization utilities."""
    
    @staticmethod
    def plot_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray,
                            title: str = "Confusion Matrix",
                            save_path: str = None) -> None:
        """
        Plot confusion matrix.
        
        Args:
            y_true: True labels
            y_pred: Binary predictions
            title: Plot title
            save_path: Path to save figure (optional)
        """
        cm = confusion_matrix(y_true, y_pred)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, 
                                      display_labels=['No TB', 'TB'])
        disp.plot(cmap='Blues')
        plt.title(title, fontsize=14, fontweight='bold')
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"[INFO] Saved figure to {save_path}")
        
        plt.show()
    
    @staticmethod
    def plot_roc_curve(y_true: np.ndarray, y_proba: np.ndarray,
                      title: str = "ROC Curve",
                      save_path: str = None,
                      label: str = "ROC") -> None:
        """
        Plot ROC curve.
        
        Args:
            y_true: True labels
            y_proba: Probability predictions
            title: Plot title
            save_path: Path to save figure (optional)
            label: Label for legend
        """
        fpr, tpr, _ = roc_curve(y_true, y_proba)
        auc = roc_auc_score(y_true, y_proba)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label=f'{label} (AUC = {auc:.3f})', linewidth=2)
        plt.plot([0, 1], [0, 1], 'k--', label='Random', linewidth=1)
        plt.xlabel('False Positive Rate', fontsize=12)
        plt.ylabel('True Positive Rate', fontsize=12)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend(fontsize=11)
        plt.grid(alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"[INFO] Saved figure to {save_path}")
        
        plt.show()
    
    @staticmethod
    def plot_metrics_comparison(metrics_dict: dict, 
                               save_path: str = None) -> None:
        """
        Plot metrics comparison across splits/models.
        
        Args:
            metrics_dict: Dictionary like {'train': {...}, 'val': {...}, 'test': {...}}
            save_path: Path to save figure (optional)
        """
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # Accuracy, Precision, Recall, F1
        metrics_to_plot = ['accuracy', 'precision', 'recall', 'f1']
        splits = list(metrics_dict.keys())
        
        for i, metric in enumerate(metrics_to_plot):
            ax = axes[i // 2] if i < 2 else axes[1]
            values = [metrics_dict[split].get(metric, 0) for split in splits]
            ax.bar(splits, values, color=['#3498db', '#e74c3c', '#2ecc71'][:len(splits)])
            ax.set_ylabel(metric.capitalize(), fontsize=11)
            ax.set_ylim([0, 1.05])
            ax.grid(axis='y', alpha=0.3)
            
            # Add value labels on bars
            for j, v in enumerate(values):
                ax.text(j, v + 0.02, f'{v:.3f}', ha='center', fontsize=10)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"[INFO] Saved figure to {save_path}")
        
        plt.show()
    
    @staticmethod
    def plot_label_distribution(y_train: np.ndarray, y_val: np.ndarray,
                               y_test: np.ndarray,
                               save_path: str = None) -> None:
        """
        Plot class distribution across splits.
        
        Args:
            y_train, y_val, y_test: Labels for each split
            save_path: Path to save figure (optional)
        """
        fig, axes = plt.subplots(1, 3, figsize=(12, 4))
        
        splits = [('Train', y_train), ('Validation', y_val), ('Test', y_test)]
        
        for ax, (name, y) in zip(axes, splits):
            unique, counts = np.unique(y, return_counts=True)
            labels = ['No TB', 'TB']
            colors = ['#3498db', '#e74c3c']
            
            ax.bar(labels[:len(counts)], counts, color=colors[:len(counts)])
            ax.set_title(f'{name} (n={len(y)})', fontsize=12, fontweight='bold')
            ax.set_ylabel('Count', fontsize=11)
            
            # Add value labels on bars
            for i, v in enumerate(counts):
                ax.text(i, v + max(counts)*0.02, str(v), ha='center', fontsize=10)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"[INFO] Saved figure to {save_path}")
        
        plt.show()
