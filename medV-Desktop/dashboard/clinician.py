"""
MediVision – Clinician Dashboard
Clinical decision support: patient list, AI result, heatmap, triage, feedback.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
                             QSplitter, QScrollArea, QFrame, QPushButton, QDialog,
                             QCheckBox, QListWidget, QListWidgetItem, QSpacerItem,
                             QSizePolicy, QProgressBar, QTextEdit, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QBrush, QLinearGradient

from dashboard.components import (CardWidget, StatCard, RiskBadge, ProgressRing,
                                   PrimaryButton, DangerButton, SuccessButton,
                                   SectionTitle, FormInput, FormCombo, DataTable)


# ── Sample patient data ───────────────────────────────────────────
SAMPLE_PATIENTS = [
    {"id": "TB-2024-001", "name": "Abebe Kebede",  "age": 35, "score": 82, "risk": "High",   "date": "2024-01-15"},
    {"id": "TB-2024-002", "name": "Tigist Alemu",  "age": 28, "score": 34, "risk": "Low",    "date": "2024-01-14"},
    {"id": "TB-2024-003", "name": "Dawit Haile",   "age": 45, "score": 76, "risk": "High",   "date": "2024-01-13"},
    {"id": "TB-2024-004", "name": "Selamawit Mulu","age": 22, "score": 28, "risk": "Low",    "date": "2024-01-12"},
    {"id": "TB-2024-005", "name": "Yonas Tesfaye", "age": 52, "score": 58, "risk": "Medium", "date": "2024-01-11"},
    {"id": "TB-2024-006", "name": "Hiwot Bekele",  "age": 31, "score": 67, "risk": "Medium", "date": "2024-01-10"},
]


# ── Heatmap Simulation Widget ─────────────────────────────────────
class HeatmapWidget(QWidget):
    """Simulates a Grad-CAM heatmap on a chest X-ray."""
    def __init__(self, score=80, parent=None):
        super().__init__(parent)
        self.score = score
        self.setMinimumSize(260, 220)

    def set_score(self, score):
        self.score = score
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # Dark X-ray background
        painter.setBrush(QBrush(QColor("#0A0A0A")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, w, h, 10, 10)

        # Simulated lung outlines
        painter.setPen(QPen(QColor("#333333"), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(int(w * 0.10), int(h * 0.15), int(w * 0.35), int(h * 0.65))
        painter.drawEllipse(int(w * 0.52), int(h * 0.15), int(w * 0.35), int(h * 0.65))

        # Heatmap blobs based on score
        if self.score > 30:
            intensity = min(self.score / 100.0, 1.0)
            grad1 = QLinearGradient(int(w * 0.25), int(h * 0.25), int(w * 0.55), int(h * 0.65))
            grad1.setColorAt(0.0, QColor(255, 0, 0, int(200 * intensity)))
            grad1.setColorAt(0.5, QColor(255, 165, 0, int(150 * intensity)))
            grad1.setColorAt(1.0, QColor(0, 0, 255, 0))
            painter.setBrush(QBrush(grad1))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(w * 0.15), int(h * 0.20), int(w * 0.40), int(h * 0.50))

            if self.score > 55:
                grad2 = QLinearGradient(int(w * 0.55), int(h * 0.30), int(w * 0.85), int(h * 0.65))
                grad2.setColorAt(0.0, QColor(255, 50, 0, int(170 * intensity)))
                grad2.setColorAt(1.0, QColor(0, 0, 255, 0))
                painter.setBrush(QBrush(grad2))
                painter.drawEllipse(int(w * 0.50), int(h * 0.25), int(w * 0.35), int(h * 0.40))

        # Label
        painter.setPen(QPen(QColor("#AAAAAA")))
        painter.setFont(QFont("Inter", 9))
        painter.drawText(8, h - 8, "Grad-CAM Visualization")


# ── Feature Bar ───────────────────────────────────────────────────
class FeatureBar(QWidget):
    """SHAP feature importance horizontal bar."""
    def __init__(self, label, value, theme_mgr, parent=None):
        super().__init__(parent)
        self.theme_mgr = theme_mgr
        self.value = value  # 0.0–1.0
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)

        self.name_lbl = QLabel(label)
        self.name_lbl.setFont(QFont("Inter", 10))
        self.name_lbl.setFixedWidth(130)

        self.bar_widget = QProgressBar()
        self.bar_widget.setRange(0, 100)
        self.bar_widget.setValue(int(value * 100))
        self.bar_widget.setTextVisible(False)
        self.bar_widget.setFixedHeight(10)

        self.val_lbl = QLabel(f"{value:.2f}")
        self.val_lbl.setFont(QFont("Inter", 10, QFont.Weight.Bold))
        self.val_lbl.setFixedWidth(40)

        layout.addWidget(self.name_lbl)
        layout.addWidget(self.bar_widget)
        layout.addWidget(self.val_lbl)
        self.apply_style()

    def apply_style(self):
        c = self.theme_mgr.get_colors()
        self.name_lbl.setStyleSheet(f"color: {c['text_secondary']}; border: none;")
        self.val_lbl.setStyleSheet(f"color: {c['text_primary']}; border: none;")
        self.bar_widget.setStyleSheet(f"""
            QProgressBar {{
                background-color: {c['border']};
                border-radius: 5px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {c['primary']};
                border-radius: 5px;
            }}
        """)


# ── Patient List Item ─────────────────────────────────────────────
class PatientListItem(QWidget):
    selected = pyqtSignal(dict)

    def __init__(self, patient, theme_mgr, parent=None):
        super().__init__(parent)
        self.patient = patient
        self.theme_mgr = theme_mgr
        self.is_selected = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)

        left = QVBoxLayout()
        self.id_lbl = QLabel(patient["id"])
        self.id_lbl.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        self.name_lbl = QLabel(patient["name"])
        self.name_lbl.setFont(QFont("Inter", 10))
        left.addWidget(self.id_lbl)
        left.addWidget(self.name_lbl)

        self.badge = RiskBadge(patient["risk"])
        self.badge.setFixedWidth(70)

        layout.addLayout(left)
        layout.addStretch()
        layout.addWidget(self.badge)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(72)
        self.apply_style(False)

    def mousePressEvent(self, event):
        self.selected.emit(self.patient)

    def apply_style(self, selected):
        self.is_selected = selected
        c = self.theme_mgr.get_colors()
        bg = c["sidebar_active"] if selected else c["card"]
        border = c["primary"] if selected else c["border"]
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 10px;
            }}
        """)
        self.id_lbl.setStyleSheet(f"color: {c['primary'] if selected else c['text_primary']}; border: none;")
        self.name_lbl.setStyleSheet(f"color: {c['text_secondary']}; border: none;")


# ── Report Dialog ─────────────────────────────────────────────────
class ReportDialog(QDialog):
    def __init__(self, patient, score, risk, theme_mgr, lang_mgr, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MediVision – Report Preview")
        self.setMinimumSize(560, 480)
        c = theme_mgr.get_colors()
        self.setStyleSheet(f"background-color: {c['card']}; color: {c['text_primary']};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title = QLabel("MediVision — TB Screening Report")
        title.setFont(QFont("Outfit", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {c['primary']};")

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {c['border']};")

        details = QTextEdit()
        details.setReadOnly(True)
        details.setFont(QFont("Inter", 11))
        details.setText(
            f"Patient ID     : {patient['id']}\n"
            f"Patient Name   : {patient['name']}\n"
            f"Age / Sex      : {patient['age']} / Male\n"
            f"Study Date     : {patient['date']}\n\n"
            f"TB Risk Score  : {score} / 100\n"
            f"Risk Level     : {risk}\n\n"
            f"AI Triage:\n"
            f"  {'High Risk — Immediate GeneXpert and isolation recommended.' if risk=='High' else 'Routine follow-up recommended.'}\n\n"
            f"Clinical Features:\n"
            f"  HIV Status  : Positive\n"
            f"  Symptoms    : Cough >2wks, Night Sweats\n"
            f"  GeneXpert   : Detected\n\n"
            f"[This report is AI-assisted and does not replace clinical judgment.]\n"
            f"Generated by MediVision CAD System – {patient['date']}"
        )
        details.setStyleSheet(f"""
            QTextEdit {{
                background-color: {c['input_bg']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                padding: 12px;
            }}
        """)

        close_btn = QPushButton("Close Preview")
        close_btn.setMinimumHeight(42)
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }}
        """)

        layout.addWidget(title)
        layout.addWidget(sep)
        layout.addWidget(details)
        layout.addWidget(close_btn)


# ── Clinician Dashboard ───────────────────────────────────────────
class ClinicianDashboard(QWidget):
    def __init__(self, lang_mgr, theme_mgr, parent=None):
        super().__init__(parent)
        self.lang = lang_mgr
        self.theme = theme_mgr
        self.current_patient = SAMPLE_PATIENTS[0]
        self.patient_items   = []
        self._api_workers    = []   # keep worker refs alive (prevent GC)
        self._build_ui()
        self.select_patient(SAMPLE_PATIENTS[0])
        self._load_patients()       # fetch live data from API

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 16, 24, 16)
        root.setSpacing(16)

        # Page title
        self.page_title = SectionTitle(self.lang.get("clinician_title"), self.theme, 20)
        root.addWidget(self.page_title)

        # ── Stat Cards Row ──────────────────────────────────────
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)
        c = self.theme.get_colors()
        self.stat_cards = [
            StatCard(self.lang.get("cases_today"), "6",  c["primary"],  self.theme),
            StatCard(self.lang.get("high_risk"),   "2",  c["danger"],   self.theme),
            StatCard(self.lang.get("medium_risk"), "2",  c["warning"],  self.theme),
            StatCard(self.lang.get("low_risk"),    "2",  c["success"],  self.theme),
        ]
        for sc in self.stat_cards:
            stats_row.addWidget(sc)
        root.addLayout(stats_row)

        # ── Main Splitter ────────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        # LEFT: Patient List
        left_card = CardWidget(self.theme)
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.setSpacing(10)

        list_title = QLabel(self.lang.get("patient_list"))
        list_title.setFont(QFont("Outfit", 14, QFont.Weight.Bold))
        self.search_input = QLabel("🔍  " + self.lang.get("search"))
        self.search_input.setFont(QFont("Inter", 10))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        list_container = QWidget()
        self.list_layout = QVBoxLayout(list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(8)
        self.list_layout.addStretch()

        for p in SAMPLE_PATIENTS:
            item = PatientListItem(p, self.theme)
            item.selected.connect(self.select_patient)
            self.patient_items.append(item)
            self.list_layout.insertWidget(self.list_layout.count() - 1, item)

        scroll.setWidget(list_container)
        left_layout.addWidget(list_title)
        left_layout.addWidget(self.search_input)
        left_layout.addWidget(scroll)
        left_card.setMinimumWidth(280)

        # RIGHT: Result Panel
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setFrameShape(QFrame.Shape.NoFrame)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(16)

        # Images Row
        img_row = QHBoxLayout()
        img_row.setSpacing(16)

        self.xray_card = CardWidget(self.theme)
        xray_v = QVBoxLayout(self.xray_card)
        xray_lbl = QLabel(self.lang.get("cxr_image"))
        xray_lbl.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        self.xray_sim = QLabel()
        self.xray_sim.setMinimumHeight(220)
        self.xray_sim.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.xray_sim.setStyleSheet("background-color: #0A0A0A; border-radius: 8px; color: #555;")
        self.xray_sim.setText("[ Chest X-Ray ]")
        self.xray_sim.setFont(QFont("Inter", 11))
        xray_v.addWidget(xray_lbl)
        xray_v.addWidget(self.xray_sim)

        self.heatmap_card = CardWidget(self.theme)
        heatmap_v = QVBoxLayout(self.heatmap_card)
        heatmap_lbl = QLabel(self.lang.get("heatmap"))
        heatmap_lbl.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        self.heatmap_widget = HeatmapWidget(80)
        heatmap_v.addWidget(heatmap_lbl)
        heatmap_v.addWidget(self.heatmap_widget)

        img_row.addWidget(self.xray_card)
        img_row.addWidget(self.heatmap_card)
        right_layout.addLayout(img_row)

        # Score + Risk + SHAP Row
        score_row = QHBoxLayout()
        score_row.setSpacing(16)

        # Score Ring Card
        score_card = CardWidget(self.theme)
        score_v = QVBoxLayout(score_card)
        score_v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_title = QLabel(self.lang.get("tb_score"))
        score_title.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        score_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_ring = ProgressRing(82, 150)
        out_of = QLabel(self.lang.get("out_of_100"))
        out_of.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_v.addWidget(score_title)
        score_v.addWidget(self.score_ring, 0, Qt.AlignmentFlag.AlignCenter)
        score_v.addWidget(out_of)

        # Risk Level Card
        risk_card = CardWidget(self.theme)
        risk_v = QVBoxLayout(risk_card)
        risk_v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        risk_title = QLabel(self.lang.get("risk_level"))
        risk_title.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        risk_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.risk_badge_large = RiskBadge("High")
        self.risk_badge_large.setFixedHeight(44)
        self.risk_badge_large.setFont(QFont("Inter", 13, QFont.Weight.Bold))
        self.triage_label = QLabel(self.lang.get("triage_high"))
        self.triage_label.setWordWrap(True)
        self.triage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.triage_label.setFont(QFont("Inter", 10))
        risk_v.addWidget(risk_title)
        risk_v.addWidget(self.risk_badge_large)
        risk_v.addWidget(self.triage_label)

        # SHAP Card
        shap_card = CardWidget(self.theme)
        shap_v = QVBoxLayout(shap_card)
        shap_title = QLabel(self.lang.get("feature_importance"))
        shap_title.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        shap_v.addWidget(shap_title)
        shap_features = [
            ("HIV Positive",  0.45),
            ("Sputum 2+",     0.38),
            ("Age (35)",      0.22),
            ("Cough >2wks",   0.18),
        ]
        self.shap_bars = []
        for feat, val in shap_features:
            bar = FeatureBar(feat, val, self.theme)
            shap_v.addWidget(bar)
            self.shap_bars.append(bar)

        score_row.addWidget(score_card)
        score_row.addWidget(risk_card, 2)
        score_row.addWidget(shap_card, 2)
        right_layout.addLayout(score_row)

        # Threshold Slider Card
        slider_card = CardWidget(self.theme)
        slider_v = QHBoxLayout(slider_card)
        slider_v.setContentsMargins(16, 12, 16, 12)
        slider_lbl = QLabel(self.lang.get("threshold") + ":")
        slider_lbl.setFont(QFont("Inter", 11))
        self.threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_slider.setRange(0, 100)
        self.threshold_slider.setValue(50)
        self.threshold_val = QLabel("50")
        self.threshold_val.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        self.threshold_val.setFixedWidth(30)
        self.threshold_slider.valueChanged.connect(
            lambda v: self.threshold_val.setText(str(v))
        )
        slider_v.addWidget(slider_lbl)
        slider_v.addWidget(self.threshold_slider)
        slider_v.addWidget(self.threshold_val)
        right_layout.addWidget(slider_card)

        # Feedback + Report Button Row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        self.approve_btn = SuccessButton(self.lang.get("approve_ai"), self.theme)
        self.reject_btn  = DangerButton(self.lang.get("reject_ai"),  self.theme)
        self.report_btn  = PrimaryButton(f"📄  {self.lang.get('generate_report')}", self.theme)
        self.approve_btn.clicked.connect(lambda: self._feedback("approved"))
        self.reject_btn.clicked.connect( lambda: self._feedback("rejected"))
        self.report_btn.clicked.connect(self._show_report)
        btn_row.addWidget(self.approve_btn)
        btn_row.addWidget(self.reject_btn)
        btn_row.addStretch()
        btn_row.addWidget(self.report_btn)
        right_layout.addLayout(btn_row)
        right_layout.addStretch()

        right_scroll.setWidget(right_widget)
        splitter.addWidget(left_card)
        splitter.addWidget(right_scroll)
        splitter.setSizes([300, 900])
        root.addWidget(splitter)
        self.apply_theme()

    def select_patient(self, patient):
        self.current_patient = patient
        for item in self.patient_items:
            item.apply_style(item.patient["id"] == patient["id"])

        score = patient["score"]
        risk  = patient["risk"]
        self.score_ring.set_score(score)
        self.heatmap_widget.set_score(score)
        self.risk_badge_large.set_level(risk)
        triage_key = {"High": "triage_high", "Medium": "triage_medium", "Low": "triage_low"}.get(risk, "triage_low")
        self.triage_label.setText(self.lang.get(triage_key))

    def _feedback(self, status):
        self.approve_btn.setText("✔ Approved!" if status == "approved" else self.lang.get("approve_ai"))
        self.reject_btn.setText("✘ Rejected!" if status == "rejected" else self.lang.get("reject_ai"))
        QTimer.singleShot(2000, lambda: (
            self.approve_btn.setText(self.lang.get("approve_ai")),
            self.reject_btn.setText(self.lang.get("reject_ai"))
        ))
        # Fire-and-forget feedback to backend
        if self.current_patient:
            from dashboard.api_client import APIClient, ApiWorker
            w = ApiWorker(APIClient.submit_feedback,
                          self.current_patient["id"], status)
            self._api_workers.append(w)
            w.start()

    def _show_report(self):
        p = self.current_patient
        dlg = ReportDialog(p, p["score"], p["risk"], self.theme, self.lang, self)
        dlg.exec()

    # ── API: Patient List ──────────────────────────────────────────────────────
    def _load_patients(self):
        """Fetch patient list from API in a background thread."""
        from dashboard.api_client import APIClient, ApiWorker
        w = ApiWorker(APIClient.get_patients)
        w.success.connect(self._on_patients_loaded)
        w.failure.connect(self._on_patients_error)
        w.no_auth.connect(lambda: None)   # stay on sample data on 401
        self._api_workers.append(w)
        w.start()

    def _on_patients_loaded(self, resp):
        if resp.status_code != 200:
            return
        try:
            data     = resp.json()
            raw_list = (data if isinstance(data, list)
                        else data.get("results", data.get("data", [])))
            if not raw_list:
                return
            patients = []
            for p in raw_list:
                patients.append({
                    "id":    str(p.get("id") or p.get("patient_id") or "—"),
                    "name":  str(p.get("name") or p.get("full_name") or "Unknown"),
                    "age":   int(p.get("age") or 0),
                    "score": int(p.get("tb_score") or p.get("score") or 0),
                    "risk":  str(p.get("risk_level") or p.get("risk") or "Low"),
                    "date":  str(p.get("date") or p.get("created_at") or "")[:10],
                })
            self._repopulate_patients(patients)
        except Exception:
            pass   # silently keep sample data on parse failure

    def _on_patients_error(self, *_):
        pass   # silently keep SAMPLE_PATIENTS on network error

    def _repopulate_patients(self, patients):
        """Replace patient list widgets with live API data."""
        for item in self.patient_items:
            self.list_layout.removeWidget(item)
            item.deleteLater()
        self.patient_items.clear()

        # Update stat cards
        high   = sum(1 for p in patients if p["risk"] == "High")
        medium = sum(1 for p in patients if p["risk"] == "Medium")
        low    = sum(1 for p in patients if p["risk"] == "Low")
        for sc, v in zip(self.stat_cards,
                         [str(len(patients)), str(high), str(medium), str(low)]):
            sc.update_value(v)

        for p in patients:
            item = PatientListItem(p, self.theme)
            item.selected.connect(self.select_patient)
            self.patient_items.append(item)
            self.list_layout.insertWidget(self.list_layout.count() - 1, item)

        if patients:
            self.select_patient(patients[0])

    def apply_theme(self):
        c = self.theme.get_colors()
        self.setStyleSheet(f"background-color: {c['bg']};")
        self.page_title.apply_style()
        for sc in self.stat_cards:
            sc.apply_style()
        self.search_input.setStyleSheet(f"color: {c['text_muted']}; border: none;")
        self.triage_label.setStyleSheet(f"color: {c['text_secondary']}; border: none;")
        self.threshold_val.setStyleSheet(f"color: {c['primary']}; border: none;")
        self.threshold_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 6px; background: {c['border']}; border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {c['primary']}; width: 18px; height: 18px;
                margin: -6px 0; border-radius: 9px;
            }}
            QSlider::sub-page:horizontal {{
                background: {c['primary']}; border-radius: 3px;
            }}
        """)
        for b in self.shap_bars:
            b.apply_style()
        self.approve_btn.apply_style()
        self.reject_btn.apply_style()
        self.report_btn.apply_style()
        self.xray_sim.setStyleSheet(f"background-color: #0A0A0A; border-radius: 8px; color: #555;")

    def retranslate(self):
        self.page_title.setText(self.lang.get("clinician_title"))
        self.approve_btn.setText(self.lang.get("approve_ai"))
        self.reject_btn.setText(self.lang.get("reject_ai"))
        self.report_btn.setText(f"📄  {self.lang.get('generate_report')}")
