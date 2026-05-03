from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QProgressBar, QPushButton
from PyQt5.QtGui import QPixmap


TEXTS = {
    "English": {
        "title": "Case Result",
        "back": "Back",
        "empty": "No result data or error loading result.",
        "score": "TB Abnormality Score",
        "risk": "Risk Level",
        "shap": "Feature Importance (SHAP)",
        "no_shap": "No SHAP data available.",
        "recommendation": "Clinical Recommendation",
        "no_recommendation": "No recommendation.",
    },
    "Amharic": {
        "title": "የኬስ ውጤት",
        "back": "ተመለስ",
        "empty": "የውጤት መረጃ አልተገኘም።",
        "score": "TB የተለየ ነጥብ",
        "risk": "የአደጋ ደረጃ",
        "shap": "የባህሪ አስተዋጽኦ (SHAP)",
        "no_shap": "የSHAP መረጃ የለም።",
        "recommendation": "የክሊኒካል ምክር",
        "no_recommendation": "ምክር የለም።",
    },
}

class ResultPage(QWidget):
    def __init__(self, result, on_back=None):
        super().__init__()
        self.setObjectName("PageCard")
        self.language = "English"
        self.result = result if isinstance(result, dict) else {}
        self.on_back = on_back
        layout = QVBoxLayout()
        top_row = QHBoxLayout()
        self.back_btn = QPushButton()
        self.back_btn.clicked.connect(lambda: self.on_back() if self.on_back else None)
        self.title = QLabel()
        self.title.setObjectName("PageTitle")
        top_row.addWidget(self.back_btn)
        top_row.addWidget(self.title)
        top_row.addStretch()
        layout.addLayout(top_row)

        self.empty_label = QLabel()
        layout.addWidget(self.empty_label)

        img_layout = QHBoxLayout()
        self.xray = QLabel()
        self.heatmap = QLabel()
        img_layout.addWidget(self.xray)
        img_layout.addWidget(self.heatmap)
        layout.addLayout(img_layout)

        self.score_label = QLabel()
        self.risk_label = QLabel()
        self.shap_title = QLabel()
        self.no_shap = QLabel()
        layout.addWidget(self.score_label)
        layout.addWidget(self.risk_label)
        layout.addWidget(self.shap_title)

        self.shap_container = QVBoxLayout()
        layout.addLayout(self.shap_container)
        layout.addWidget(self.no_shap)

        self.recommendation_title = QLabel()
        self.recommendation_text = QLabel()
        layout.addWidget(self.recommendation_title)
        layout.addWidget(self.recommendation_text)
        layout.addStretch()
        self.setLayout(layout)
        self.set_language(self.language)

    def set_result(self, result):
        self.result = result if isinstance(result, dict) else {}
        self.set_language(self.language)

    def set_language(self, language):
        self.language = language
        texts = TEXTS.get(language, TEXTS["English"])
        self.title.setText(texts["title"])
        self.back_btn.setText(texts["back"])
        self.back_btn.setIcon(self.style().standardIcon(self.style().SP_ArrowBack))

        if self.result.get("xray_path"):
            self.xray.setPixmap(QPixmap(self.result["xray_path"]).scaled(220, 220))
        else:
            self.xray.clear()
        if self.result.get("heatmap_path"):
            self.heatmap.setPixmap(QPixmap(self.result["heatmap_path"]).scaled(220, 220))
        else:
            self.heatmap.clear()

        has_result = bool(self.result)
        self.empty_label.setVisible(not has_result)
        self.empty_label.setText(texts["empty"])

        self.score_label.setText(f"{texts['score']}: {self.result.get('score', 'N/A')}")
        self.risk_label.setText(f"{texts['risk']}: {self.result.get('risk', 'N/A')}")
        self.shap_title.setText(f"{texts['shap']}:")

        while self.shap_container.count():
            item = self.shap_container.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        shap = self.result.get("shap", {})
        if shap:
            self.no_shap.setVisible(False)
            for feat, val in shap.items():
                bar = QProgressBar()
                bar.setValue(int(val * 100))
                bar.setFormat(f"{feat}: {val:.2f}")
                self.shap_container.addWidget(bar)
        else:
            self.no_shap.setVisible(True)
            self.no_shap.setText(texts["no_shap"])

        self.recommendation_title.setText(f"{texts['recommendation']}:")
        self.recommendation_text.setText(self.result.get("recommendation", texts["no_recommendation"]))
