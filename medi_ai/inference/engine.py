import os
import pickle
import numpy as np
from PIL import Image
import torch
from torchvision import transforms
import xgboost as xgb
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

class TBInferenceEngine:
    def __init__(self):
        self.cnn_model = None
        self.xgb_model = None
        self.fusion_model = None
        self.scaler = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.loaded = False

    def load_models(self):
        models_dir = os.path.join(os.path.dirname(__file__), '..', 'models', 'trained')
        
        # Load CNN
        self.cnn_model = None
        cnn_path = os.path.join(models_dir, 'densenet_cnn.pth')
        if os.path.exists(cnn_path):
            from models.cnn import DenseNetCNN
            self.cnn_model = DenseNetCNN()
            self.cnn_model.load_state_dict(torch.load(cnn_path, map_location=self.device))
            self.cnn_model.to(self.device)
            self.cnn_model.eval()

        # Load XGBoost
        xgb_path = os.path.join(models_dir, 'xgboost_model.json')
        if os.path.exists(xgb_path):
            self.xgb_model = xgb.XGBClassifier()
            self.xgb_model.load_model(xgb_path)

        # Load Fusion
        fusion_path = os.path.join(models_dir, 'fusion_model.pkl')
        if os.path.exists(fusion_path):
            with open(fusion_path, 'rb') as f:
                self.fusion_model = pickle.load(f)

        # Load Scaler
        scaler_path = os.path.join(models_dir, 'scaler.pkl')
        if os.path.exists(scaler_path):
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)

        self.loaded = any([self.cnn_model is not None, self.xgb_model is not None, self.fusion_model is not None, self.scaler is not None])

    def preprocess_image(self, image_path):
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        image = Image.open(image_path).convert('RGB')
        return transform(image).unsqueeze(0).to(self.device)

    def predict_image(self, image_path):
        if self.cnn_model is None:
            return None
        image_tensor = self.preprocess_image(image_path)
        with torch.no_grad():
            outputs = self.cnn_model(image_tensor)
            probs = torch.sigmoid(outputs)
            return probs.cpu().numpy()[0][0]  # Probability of TB

    def predict_tabular(self, age, sex):
        if self.xgb_model is None or self.scaler is None:
            return None
        sex_num = 1 if sex.lower() == 'm' else 0
        features = np.array([[age, sex_num]])
        features_scaled = self.scaler.transform(features)
        prob = self.xgb_model.predict_proba(features_scaled)[0][1]
        return prob

    def predict_fusion(self, img_prob, tab_prob):
        if self.fusion_model is None:
            return (img_prob + tab_prob) / 2  # Simple average
        features = np.array([[img_prob, tab_prob]])
        prob = self.fusion_model.predict_proba(features)[0][1]
        return prob

    def predict(self, image_path=None, age=None, sex=None):
        img_prob = self.predict_image(image_path) if image_path else None
        tab_prob = self.predict_tabular(age, sex) if age is not None and sex else None

        if img_prob is not None and tab_prob is not None:
            tb_score = self.predict_fusion(img_prob, tab_prob)
        elif img_prob is not None:
            tb_score = img_prob
        elif tab_prob is not None:
            tb_score = tab_prob
        else:
            return {"error": "No valid inputs provided"}

        # Convert to percentage
        tb_score *= 100

        # Triage recommendation
        if tb_score > 80:
            recommendation = "high risk - refer to GeneXpert"
        elif tb_score > 50:
            recommendation = "medium risk - follow up"
        else:
            recommendation = "low risk - routine care"

        return {
            "tb_score": round(tb_score, 2),
            "triage_recommendation": recommendation,
            "image_prob": round(img_prob * 100, 2) if img_prob is not None else None,
            "tabular_prob": round(tab_prob * 100, 2) if tab_prob is not None else None,
        }
