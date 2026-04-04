"""
MediVision – Radiographer Dashboard
Image acquisition: drag & drop upload, patient metadata, preview, history.
"""
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QProgressBar, QFileDialog, QFrame, QScrollArea,
                             QSizePolicy, QSpacerItem, QGridLayout, QComboBox,
                             QLineEdit, QDateEdit)
from PyQt6.QtCore import Qt, QTimer, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QDragEnterEvent, QDropEvent, QPixmap

from dashboard.components import (CardWidget, StatCard, SectionTitle, PrimaryButton,
                                   DataTable, FormInput, FormCombo)


# ── Drag & Drop Upload Zone ───────────────────────────────────────
class UploadZone(QLabel):
    file_dropped = pyqtSignal(str)

    def __init__(self, theme_mgr, parent=None):
        super().__init__(parent)
        self.theme_mgr = theme_mgr
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(200)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._set_default_text()
        self.apply_style(False)

    def _set_default_text(self):
        self.setText("⬆\n\nDrag & drop chest X-ray here\nor click to browse\n\nJPG · PNG · DCM")
        self.setFont(QFont("Inter", 12))

    def apply_style(self, active=False):
        c = self.theme_mgr.get_colors()
        border_color = c["primary"] if active else c["border"]
        bg = c["primary_light"] if active else c["input_bg"]
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                border: 2px dashed {border_color};
                border-radius: 12px;
                color: {c['text_muted']};
                padding: 20px;
            }}
        """)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.apply_style(True)

    def dragLeaveEvent(self, event):
        self.apply_style(False)

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self.file_dropped.emit(path)
        self.apply_style(False)

    def mousePressEvent(self, event):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Chest X-Ray",
            "", "Images (*.jpg *.jpeg *.png *.bmp);;DICOM (*.dcm);;All Files (*)"
        )
        if path:
            self.file_dropped.emit(path)


# ── Image Preview Widget ──────────────────────────────────────────
class ImagePreviewWidget(QLabel):
    def __init__(self, theme_mgr, parent=None):
        super().__init__(parent)
        self.theme_mgr = theme_mgr
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(260)
        self.setScaledContents(False)
        self._show_placeholder()
        self.apply_style()

    def _show_placeholder(self):
        self.setText("[ Image Preview ]")
        self.setFont(QFont("Inter", 13))

    def load_image(self, path):
        if os.path.exists(path):
            pix = QPixmap(path)
            if not pix.isNull():
                scaled = pix.scaled(
                    self.width() - 20, self.height() - 20,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.setPixmap(scaled)
                self.setText("")
                return
        self.setText("[ Preview Unavailable ]")

    def apply_style(self):
        c = self.theme_mgr.get_colors()
        self.setStyleSheet(f"""
            QLabel {{
                background-color: #0A0A0A;
                color: #555555;
                border-radius: 10px;
            }}
        """)


# ── Radiographer Dashboard ────────────────────────────────────────
class RadiographerDashboard(QWidget):
    def __init__(self, lang_mgr, theme_mgr, parent=None):
        super().__init__(parent)
        self.lang            = lang_mgr
        self.theme           = theme_mgr
        self.upload_history  = []
        self._selected_path  = ""   # most recently staged X-ray file path
        self._pending_row    = 0    # history table row of current upload attempt
        self._api_workers    = []   # keep worker refs alive
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 16, 24, 16)
        root.setSpacing(16)

        # Title
        self.page_title = SectionTitle(self.lang.get("radiographer_title"), self.theme, 20)
        root.addWidget(self.page_title)

        # Stat Cards
        c = self.theme.get_colors()
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)
        self.stat_cards = [
            StatCard("Total Uploads Today", "12", c["primary"], self.theme),
            StatCard("Sent for Analysis",   "9",  c["success"], self.theme),
            StatCard("Pending Review",       "3",  c["warning"], self.theme),
        ]
        for sc in self.stat_cards:
            stats_row.addWidget(sc)
        root.addLayout(stats_row)

        # ── Main section ──────────────────────────────────────────
        main_row = QHBoxLayout()
        main_row.setSpacing(16)

        # LEFT: Upload + Metadata
        left_col = QVBoxLayout()
        left_col.setSpacing(16)

        # Upload card
        upload_card = CardWidget(self.theme)
        upload_v = QVBoxLayout(upload_card)
        upload_v.setContentsMargins(20, 20, 20, 20)
        upload_v.setSpacing(12)

        ul_title = QLabel(self.lang.get("upload_xray"))
        ul_title.setFont(QFont("Outfit", 14, QFont.Weight.Bold))

        self.upload_zone = UploadZone(self.theme)
        self.upload_zone.file_dropped.connect(self._on_file_selected)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)

        self.progress_lbl = QLabel("")
        self.progress_lbl.setFont(QFont("Inter", 10))
        self.progress_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        upload_v.addWidget(ul_title)
        upload_v.addWidget(self.upload_zone)
        upload_v.addWidget(self.progress_bar)
        upload_v.addWidget(self.progress_lbl)
        left_col.addWidget(upload_card)

        # Patient Metadata card
        meta_card = CardWidget(self.theme)
        meta_v = QVBoxLayout(meta_card)
        meta_v.setContentsMargins(20, 20, 20, 20)
        meta_v.setSpacing(12)

        meta_title = QLabel(self.lang.get("patient_meta"))
        meta_title.setFont(QFont("Outfit", 14, QFont.Weight.Bold))

        meta_grid = QGridLayout()
        meta_grid.setSpacing(12)

        self.patient_id_input = FormInput("Patient ID", self.theme, "e.g. PT-2024-001")
        self.patient_age_input = FormInput(self.lang.get("age"), self.theme, "e.g. 35")
        self.patient_sex_combo = FormCombo(
            self.lang.get("sex"), [self.lang.get("male"), self.lang.get("female")], self.theme
        )
        self.view_type_combo = FormCombo(
            self.lang.get("view_type"), ["PA (Postero-Anterior)", "AP (Antero-Posterior)", "Lateral"], self.theme
        )

        meta_grid.addWidget(self.patient_id_input,   0, 0)
        meta_grid.addWidget(self.patient_age_input,  0, 1)
        meta_grid.addWidget(self.patient_sex_combo,  1, 0)
        meta_grid.addWidget(self.view_type_combo,    1, 1)

        self.send_btn = PrimaryButton(f"🔬  {self.lang.get('send_analysis')}", self.theme)
        self.send_btn.clicked.connect(self._send_for_analysis)

        meta_v.addWidget(meta_title)
        meta_v.addLayout(meta_grid)
        meta_v.addWidget(self.send_btn)
        left_col.addWidget(meta_card)

        # RIGHT: Preview + History
        right_col = QVBoxLayout()
        right_col.setSpacing(16)

        # Preview card
        preview_card = CardWidget(self.theme)
        preview_v = QVBoxLayout(preview_card)
        preview_v.setContentsMargins(20, 20, 20, 20)

        prev_title = QLabel(self.lang.get("preview"))
        prev_title.setFont(QFont("Outfit", 14, QFont.Weight.Bold))

        self.preview_widget = ImagePreviewWidget(self.theme)

        # Preprocessing indicator
        preproc_row = QHBoxLayout()
        steps = ["Resize", "Normalize", "Denoise", "Enhance"]
        self.preproc_labels = []
        for step in steps:
            lbl = QLabel(f"○ {step}")
            lbl.setFont(QFont("Inter", 9))
            preproc_row.addWidget(lbl)
            self.preproc_labels.append(lbl)

        preview_v.addWidget(prev_title)
        preview_v.addWidget(self.preview_widget)
        preview_v.addLayout(preproc_row)
        right_col.addWidget(preview_card)

        # History table card
        history_card = CardWidget(self.theme)
        history_v = QVBoxLayout(history_card)
        history_v.setContentsMargins(20, 20, 20, 20)

        hist_title = QLabel(self.lang.get("upload_history"))
        hist_title.setFont(QFont("Outfit", 14, QFont.Weight.Bold))

        self.history_table = DataTable(
            ["Case ID", "Patient", "Date", "Status"], self.theme
        )
        # Seed demo data
        demo = [
            ("TB-2024-001", "Abebe Kebede",   "2024-01-15", "✓ Analyzed"),
            ("TB-2024-002", "Tigist Alemu",   "2024-01-14", "✓ Analyzed"),
            ("TB-2024-003", "Dawit Haile",    "2024-01-13", "⏳ Pending"),
        ]
        for row in demo:
            self.history_table.add_row(list(row))
        self.history_table.setFixedHeight(180)

        history_v.addWidget(hist_title)
        history_v.addWidget(self.history_table)
        right_col.addWidget(history_card)

        main_row.addLayout(left_col, 5)
        main_row.addLayout(right_col, 5)
        root.addLayout(main_row)
        self.apply_theme()

    def _on_file_selected(self, path):
        self._selected_path = path          # store for API upload
        self.preview_widget.load_image(path)
        self._animate_preprocessing()
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self._progress_timer = QTimer()
        self._progress_val = 0
        self._progress_timer.timeout.connect(self._tick_progress)
        self._progress_timer.start(40)

    def _tick_progress(self):
        self._progress_val += 3
        self.progress_bar.setValue(min(self._progress_val, 100))
        self.progress_lbl.setText(self.lang.get("processing"))
        if self._progress_val >= 100:
            self._progress_timer.stop()
            self.progress_lbl.setText("✓  " + self.lang.get("upload_success"))

    def _animate_preprocessing(self):
        c = self.theme.get_colors()
        for i, lbl in enumerate(self.preproc_labels):
            QTimer.singleShot(i * 500, lambda l=lbl: l.setText(
                l.text().replace("○", "●")
            ))
            QTimer.singleShot(i * 500, lambda l=lbl: l.setStyleSheet(
                f"color: {c['success']};"
            ))

    def _send_for_analysis(self):
        pid  = self.patient_id_input.text().strip() or "PT-NEW"
        age  = self.patient_age_input.text().strip()
        sex  = self.patient_sex_combo.current_text()
        view = self.view_type_combo.current_text()

        import datetime
        today = datetime.date.today().isoformat()
        self._pending_row = self.history_table.rowCount()
        self.history_table.add_row([pid, pid, today, "⏳ Sending…"])

        self.send_btn.setText("⏳  Sending…")
        self.send_btn.setEnabled(False)

        # Step 1: create / update patient record
        from dashboard.api_client import APIClient, ApiWorker
        patient_data = {
            "patient_id": pid, "age": age,
            "sex": sex,        "view_type": view,
        }
        self._send_w1 = ApiWorker(APIClient.create_patient, patient_data)
        self._send_w1.success.connect(lambda resp: self._on_patient_saved(resp, pid))
        self._send_w1.failure.connect(self._on_send_error)
        self._send_w1.no_auth.connect(
            lambda: self._on_send_error("Session expired – please log in again.")
        )
        self._api_workers.append(self._send_w1)
        self._send_w1.start()

    def _on_patient_saved(self, resp, pid):
        """Step 2: run inference after patient record is confirmed."""
        from dashboard.api_client import APIClient, ApiWorker
        self._send_w2 = ApiWorker(
            APIClient.run_inference, pid, self._selected_path or ""
        )
        self._send_w2.success.connect(self._on_inference_done)
        self._send_w2.failure.connect(self._on_send_error)
        self._api_workers.append(self._send_w2)
        self._send_w2.start()

    def _on_inference_done(self, resp):
        self.send_btn.setEnabled(True)
        row = self._pending_row
        status_item = self.history_table.item(row, 3)
        if status_item:
            status_item.setText("✓ Analyzed")
        try:
            data  = resp.json()
            score = data.get("tb_score") or data.get("score")
            if score is not None:
                self.send_btn.setText(f"✓  TB Score: {score}/100")
                QTimer.singleShot(
                    3000,
                    lambda: self.send_btn.setText(f"🔬  {self.lang.get('send_analysis')}")
                )
                return
        except Exception:
            pass
        self.send_btn.setText("✓  Analysis Complete!")
        QTimer.singleShot(2500, lambda: self.send_btn.setText(f"🔬  {self.lang.get('send_analysis')}"))

    def _on_send_error(self, msg):
        self.send_btn.setEnabled(True)
        row = getattr(self, "_pending_row", self.history_table.rowCount() - 1)
        status_item = self.history_table.item(row, 3)
        if status_item:
            status_item.setText("⚠ Failed")
        self.send_btn.setText("⚠  Network Error – Retry")
        QTimer.singleShot(
            3000,
            lambda: self.send_btn.setText(f"🔬  {self.lang.get('send_analysis')}")
        )

    def apply_theme(self):
        c = self.theme.get_colors()
        self.setStyleSheet(f"background-color: {c['bg']};")
        self.page_title.apply_style()
        for sc in self.stat_cards:
            sc.apply_style()
        self.upload_zone.apply_style(False)
        self.preview_widget.apply_style()
        self.patient_id_input.apply_style()
        self.patient_age_input.apply_style()
        self.patient_sex_combo.apply_style()
        self.view_type_combo.apply_style()
        self.send_btn.apply_style()
        self.history_table.apply_style()
        self.progress_lbl.setStyleSheet(f"color: {c['success']}; border: none;")
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {c['border']};
                border-radius: 4px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {c['primary']};
                border-radius: 4px;
            }}
        """)
        for lbl in self.preproc_labels:
            lbl.setStyleSheet(f"color: {c['text_muted']}; border:none;")

    def retranslate(self):
        self.page_title.setText(self.lang.get("radiographer_title"))
        self.send_btn.setText(f"🔬  {self.lang.get('send_analysis')}")
