"""
MediVision – Lab Technician Dashboard
Lab data entry: GeneXpert, sputum, link to patient, records table.
"""
import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QFrame, QCheckBox, QFileDialog, QMessageBox,
                             QSizePolicy, QGridLayout, QSpacerItem, QScrollArea)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from dashboard.components import (CardWidget, StatCard, SectionTitle, PrimaryButton,
                                   SuccessButton, DataTable, FormInput, FormCombo)


DEMO_LAB_RECORDS = [
    ("LR-001", "TB-2024-001", "GeneXpert",  "Detected",     "20M",  "Dr. Haile"),
    ("LR-002", "TB-2024-002", "Sputum",     "Grade 2+",     "28F",  "Dr. Tigist"),
    ("LR-003", "TB-2024-003", "GeneXpert",  "Not Detected", "45M",  "Dr. Dawit"),
    ("LR-004", "TB-2024-004", "Sputum",     "Scanty",       "22F",  "Dr. Selamawit"),
]


class LabDashboard(QWidget):
    def __init__(self, lang_mgr, theme_mgr, parent=None):
        super().__init__(parent)
        self.lang        = lang_mgr
        self.theme       = theme_mgr
        self._api_workers = []   # keep worker refs alive
        self._build_ui()
        self._load_records()     # populate table from API

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 16, 24, 16)
        root.setSpacing(16)

        # Page Title
        self.page_title = SectionTitle(self.lang.get("lab_title"), self.theme, 20)
        root.addWidget(self.page_title)

        # Stat Cards
        c = self.theme.get_colors()
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)
        self.stat_cards = [
            StatCard("Records Today",      "8",  c["primary"], self.theme),
            StatCard("GeneXpert Detected", "3",  c["danger"],  self.theme),
            StatCard("Sputum Positive",    "2",  c["warning"], self.theme),
            StatCard("Pending Sync",       "1",  c["success"], self.theme),
        ]
        for sc in self.stat_cards:
            stats_row.addWidget(sc)
        root.addLayout(stats_row)

        # ── Main Row ─────────────────────────────────────────────
        main_row = QHBoxLayout()
        main_row.setSpacing(16)

        # LEFT: Entry Form
        form_card = CardWidget(self.theme)
        form_v = QVBoxLayout(form_card)
        form_v.setContentsMargins(24, 24, 24, 24)
        form_v.setSpacing(14)

        form_title = QLabel(self.lang.get("enter_lab_data"))
        form_title.setFont(QFont("Outfit", 15, QFont.Weight.Bold))

        # Row 1: Patient ID + Test Type
        r1 = QHBoxLayout()
        self.pid_input = FormInput(self.lang.get("link_patient"), self.theme, "e.g. TB-2024-001")
        self.test_type_combo = FormCombo(
            self.lang.get("test_type"),
            ["GeneXpert MTB/RIF", "Sputum Smear Microscopy", "Culture", "Chest X-Ray AI"],
            self.theme
        )
        r1.addWidget(self.pid_input)
        r1.addWidget(self.test_type_combo)

        # Row 2: GeneXpert Result + Sputum Grade
        r2 = QHBoxLayout()
        self.genexpert_combo = FormCombo(
            self.lang.get("genexpert_result"),
            [self.lang.get("detected"), self.lang.get("not_detected"), "Indeterminate", "Invalid"],
            self.theme
        )
        self.sputum_combo = FormCombo(
            self.lang.get("sputum_grade"),
            [self.lang.get("scanty"), self.lang.get("grade_1"),
             self.lang.get("grade_2"), self.lang.get("grade_3"), "Negative"],
            self.theme
        )
        r2.addWidget(self.genexpert_combo)
        r2.addWidget(self.sputum_combo)

        # Row 3: Checkboxes
        check_row = QHBoxLayout()
        self.rifampicin_cb = QCheckBox(self.lang.get("rifampicin_res"))
        self.rifampicin_cb.setFont(QFont("Inter", 11))

        self.hiv_positive_cb = QCheckBox(self.lang.get("hiv_pos"))
        self.hiv_positive_cb.setFont(QFont("Inter", 11))

        check_row.addWidget(self.rifampicin_cb)
        check_row.addWidget(self.hiv_positive_cb)
        check_row.addStretch()

        # Recorded By
        self.recorder_input = FormInput("Recorded By", self.theme, "Your name / ID")

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)

        # Upload report
        upload_row = QHBoxLayout()
        self.upload_lbl = QLabel("No report file selected")
        self.upload_lbl.setFont(QFont("Inter", 10))
        upload_btn = QPushButton(f"📎  {self.lang.get('upload_report')}")
        upload_btn.setMinimumHeight(38)
        upload_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        upload_btn.clicked.connect(self._browse_file)
        upload_row.addWidget(self.upload_lbl, 1)
        upload_row.addWidget(upload_btn)

        # Save Button
        self.save_btn = PrimaryButton(f"💾  {self.lang.get('save_sync')}", self.theme)
        self.save_btn.clicked.connect(self._save_record)

        self.feedback_lbl = QLabel("")
        self.feedback_lbl.setFont(QFont("Inter", 10))
        self.feedback_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form_v.addWidget(form_title)
        form_v.addLayout(r1)
        form_v.addLayout(r2)
        form_v.addLayout(check_row)
        form_v.addWidget(self.recorder_input)
        form_v.addWidget(sep)
        form_v.addLayout(upload_row)
        form_v.addSpacing(8)
        form_v.addWidget(self.save_btn)
        form_v.addWidget(self.feedback_lbl)
        form_v.addStretch()

        # RIGHT: Records Table
        table_card = CardWidget(self.theme)
        table_v = QVBoxLayout(table_card)
        table_v.setContentsMargins(20, 20, 20, 20)
        table_v.setSpacing(12)

        table_title = QLabel(self.lang.get("lab_records"))
        table_title.setFont(QFont("Outfit", 15, QFont.Weight.Bold))

        # Search
        search_row = QHBoxLayout()
        self.search_field = FormInput("", self.theme, "🔍  " + self.lang.get("search"))
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(38, 38)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        search_row.addWidget(self.search_field, 1)
        search_row.addWidget(refresh_btn)

        self.records_table = DataTable(
            ["Lab ID", "Patient ID", self.lang.get("test_type"),
             self.lang.get("result"), "Patient", self.lang.get("recorded_by")],
            self.theme
        )
        for row in DEMO_LAB_RECORDS:
            self.records_table.add_row(list(row))

        table_v.addWidget(table_title)
        table_v.addLayout(search_row)
        table_v.addWidget(self.records_table)

        main_row.addWidget(form_card, 4)
        main_row.addWidget(table_card, 6)
        root.addLayout(main_row)
        self._apply_checkbox_style()
        self._apply_upload_style(upload_btn)
        self._apply_refresh_style(refresh_btn)
        self.apply_theme()

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Upload Lab Report",
            "", "Reports (*.pdf *.csv *.jpg *.png);;All Files (*)"
        )
        if path:
            import os
            self.upload_lbl.setText(f"✓  {os.path.basename(path)}")
            c = self.theme.get_colors()
            self.upload_lbl.setStyleSheet(f"color: {c['success']}; border: none;")

    def _save_record(self):
        pid = self.pid_input.text().strip()
        if not pid:
            c = self.theme.get_colors()
            self.feedback_lbl.setText("⚠  Patient ID is required!")
            self.feedback_lbl.setStyleSheet(f"color: {c['danger']}; border: none;")
            return

        test   = self.test_type_combo.current_text()
        result = self.genexpert_combo.current_text()
        sputum = self.sputum_combo.current_text()
        rec_by = self.recorder_input.text().strip() or "Lab Tech"
        rif    = self.rifampicin_cb.isChecked()
        hiv    = self.hiv_positive_cb.isChecked()

        # Optimistic local update — immediate feedback
        lr_id = f"LR-{self.records_table.rowCount() + 1:03d}"
        self.records_table.add_row([lr_id, pid, test, result, "—", rec_by])

        c = self.theme.get_colors()
        self.feedback_lbl.setText("⏳  Syncing with server…")
        self.feedback_lbl.setStyleSheet(f"color: {c['text_secondary']}; border: none;")
        self.save_btn.setEnabled(False)

        # POST to backend
        from dashboard.api_client import APIClient, ApiWorker
        lab_data = {
            "patient_id":            pid,
            "test_type":             test,
            "result":                result,
            "sputum_grade":          sputum,
            "rifampicin_resistance": rif,
            "hiv_positive":          hiv,
            "recorded_by":           rec_by,
        }
        w = ApiWorker(APIClient.create_lab_record, lab_data)
        w.success.connect(self._on_lab_saved)
        w.failure.connect(self._on_lab_error)
        w.no_auth.connect(lambda: self._on_lab_error("Session expired – please log in again."))
        self._api_workers.append(w)
        w.start()

    def _on_lab_saved(self, resp):
        self.save_btn.setEnabled(True)
        c = self.theme.get_colors()
        if resp.status_code in (200, 201):
            self.feedback_lbl.setText("✓  Record saved and synced successfully!")
            self.feedback_lbl.setStyleSheet(f"color: {c['success']}; border: none;")
        else:
            self.feedback_lbl.setText(
                f"⚠  Saved locally, server returned HTTP {resp.status_code}."
            )
            self.feedback_lbl.setStyleSheet(f"color: {c['warning']}; border: none;")
        QTimer.singleShot(3000, lambda: self.feedback_lbl.setText(""))

    def _on_lab_error(self, msg):
        self.save_btn.setEnabled(True)
        c = self.theme.get_colors()
        short = msg[:70] + "…" if len(msg) > 70 else msg
        self.feedback_lbl.setText(f"⚠  Saved locally. Sync failed: {short}")
        self.feedback_lbl.setStyleSheet(f"color: {c['warning']}; border: none;")
        QTimer.singleShot(4000, lambda: self.feedback_lbl.setText(""))

    # ── API: Load Records ──────────────────────────────────────────────────────
    def _load_records(self):
        """Fetch lab records from the API and populate the table."""
        from dashboard.api_client import APIClient, ApiWorker
        w = ApiWorker(APIClient.get_lab_records)
        w.success.connect(self._on_records_loaded)
        w.failure.connect(lambda _: None)   # keep demo data on error
        self._api_workers.append(w)
        w.start()

    def _on_records_loaded(self, resp):
        if resp.status_code != 200:
            return
        try:
            data    = resp.json()
            records = data if isinstance(data, list) else data.get("results", [])
            if not records:
                return
            self.records_table.setRowCount(0)   # clear demo rows
            for r in records:
                lr_id   = str(r.get("id") or r.get("lab_id") or "—")
                pid     = str(r.get("patient_id") or "—")
                test    = str(r.get("test_type") or "—")
                result  = str(r.get("result") or "—")
                patient = str(r.get("patient_name") or "—")
                rec_by  = str(r.get("recorded_by") or "—")
                self.records_table.add_row([lr_id, pid, test, result, patient, rec_by])
        except Exception:
            pass   # keep demo data

    def _apply_checkbox_style(self):
        c = self.theme.get_colors()
        style = f"color: {c['text_primary']}; border: none;"
        self.rifampicin_cb.setStyleSheet(style)
        self.hiv_positive_cb.setStyleSheet(style)

    def _apply_upload_style(self, btn):
        c = self.theme.get_colors()
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['input_bg']};
                color: {c['primary']};
                border: 1px solid {c['primary']};
                border-radius: 8px;
                padding: 0 14px;
                font-family: Inter;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: {c['primary_light']}; }}
        """)

    def _apply_refresh_style(self, btn):
        c = self.theme.get_colors()
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['input_bg']};
                color: {c['text_secondary']};
                border: 1px solid {c['border']};
                border-radius: 8px;
            }}
            QPushButton:hover {{ background-color: {c['primary_light']}; }}
        """)

    def apply_theme(self):
        c = self.theme.get_colors()
        self.setStyleSheet(f"background-color: {c['bg']};")
        self.page_title.apply_style()
        for sc in self.stat_cards:
            sc.apply_style()
        self.pid_input.apply_style()
        self.recorder_input.apply_style()
        self.search_field.apply_style()
        self.test_type_combo.apply_style()
        self.genexpert_combo.apply_style()
        self.sputum_combo.apply_style()
        self.save_btn.apply_style()
        self.records_table.apply_style()
        self.upload_lbl.setStyleSheet(f"color: {c['text_muted']}; border: none;")
        self._apply_checkbox_style()

    def retranslate(self):
        self.page_title.setText(self.lang.get("lab_title"))
        self.save_btn.setText(f"💾  {self.lang.get('save_sync')}")
