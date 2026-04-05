import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QFont
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QStackedWidget,
    QPushButton,
    QLabel,
    QComboBox,
    QMessageBox,
    QStyle,
)

from components import api
from components.login import LoginPage
from components.register import RegisterPage
from components.dashboard import DashboardPage
from components.new_case import NewCasePage
from components.result_page import ResultPage
from components.patients_page import PatientsPage
from components.patient_detail_page import PatientDetailPage
from components.users_page import UsersPage


ROLE_UI_TO_BACKEND = {
    "Doctor": "clinician",
    "Technician": "radiologist",
    "Admin": "admin",
    "Auditor": "auditor",
}

ROLE_NORMALIZE = {
    "doctor": "clinician",
    "clinician": "clinician",
    "c": "clinician",
    "technician": "radiologist",
    "radiologist": "radiologist",
    "r": "radiologist",
    "admin": "admin",
    "l": "admin",
    "auditor": "auditor",
    "a": "auditor",
}


TEXTS = {
    "English": {
        "app_title": "MediVision Desktop",
        "brand": "MediVision",
        "nav_dashboard": "Dashboard",
        "nav_inference": "AI Inference",
        "nav_result": "Results",
        "logout": "Logout",
        "back": "Back",
        "lang": "Language",
        "auth_guard": "Please login first.",
        "auth_guard_title": "Authentication Required",
        "logout_title": "Signed Out",
        "logout_msg": "You have been logged out.",
    },
    "Amharic": {
        "app_title": "MediVision ዴስክቶፕ",
        "brand": "MediVision",
        "nav_dashboard": "ዳሽቦርድ",
        "nav_inference": "AI ትንተና",
        "nav_result": "ውጤት",
        "logout": "ውጣ",
        "back": "ተመለስ",
        "lang": "ቋንቋ",
        "auth_guard": "እባክዎ መጀመሪያ ይግቡ።",
        "auth_guard_title": "ማረጋገጫ ያስፈልጋል",
        "logout_title": "ወጥተዋል",
        "logout_msg": "ከሲስተሙ ወጥተዋል።",
    },
}


def build_medivision_icon(size=64):
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    painter.setBrush(QColor("#ffffff"))
    painter.setPen(QPen(QColor("#2e7bb8"), 2))
    painter.drawRoundedRect(2, 2, size - 4, size - 4, 12, 12)

    baseline = int(size * 0.52)
    points = [
        (int(size * 0.12), baseline),
        (int(size * 0.28), baseline),
        (int(size * 0.36), baseline - int(size * 0.18)),
        (int(size * 0.48), baseline + int(size * 0.16)),
        (int(size * 0.58), baseline - int(size * 0.10)),
        (int(size * 0.72), baseline),
        (int(size * 0.88), baseline),
    ]
    painter.setPen(QPen(QColor("#2e7bb8"), 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    for i in range(len(points) - 1):
        painter.drawLine(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1])
    painter.end()
    return QIcon(pixmap)


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.token = None
        self.user_role = None
        self.user_id = None
        self.hospital_id = None
        self.hospital_name = None
        self.hospital_code = None
        self.language = "English"
        self.ui_font_family = "Segoe UI"
        self.ui_font_size = 16
        self.history = []
        self.current_key = "login"
        self.patients_cache = []

        self.page_keys = {
            "login": 0,
            "register": 1,
            "dashboard": 2,
            "inference": 3,
            "result": 4,
            "patients": 5,
            "patient_detail": 6,
            "users": 7,
        }

        self.root_layout = QVBoxLayout()
        self.root_layout.setContentsMargins(12, 10, 12, 12)
        self.root_layout.setSpacing(10)
        self.setLayout(self.root_layout)

        self._build_top_bar()
        self._build_body()
        self._build_pages()
        self._apply_icons()
        self._apply_theme()
        self.apply_language()
        self.navigate_to("login", push_history=False)

    def _build_top_bar(self):
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        self.back_btn = QPushButton()
        self.back_btn.clicked.connect(self.go_back)
        top_bar.addWidget(self.back_btn)

        top_bar.addStretch()

        self.lang_label = QLabel()
        top_bar.addWidget(self.lang_label)

        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "English")
        self.lang_combo.addItem("Amharic", "Amharic")
        self.lang_combo.currentIndexChanged.connect(self.on_language_change)
        top_bar.addWidget(self.lang_combo)

        self.font_label = QLabel("Font")
        top_bar.addWidget(self.font_label)

        self.font_combo = QComboBox()
        self.font_combo.addItems(["Segoe UI", "Nyala", "Noto Sans Ethiopic", "Arial"])
        self.font_combo.setCurrentText(self.ui_font_family)
        self.font_combo.currentTextChanged.connect(self.on_font_settings_change)
        top_bar.addWidget(self.font_combo)

        self.font_size_label = QLabel("Size")
        top_bar.addWidget(self.font_size_label)

        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems([str(i) for i in range(12, 25)])
        self.font_size_combo.setCurrentText(str(self.ui_font_size))
        self.font_size_combo.currentTextChanged.connect(self.on_font_settings_change)
        top_bar.addWidget(self.font_size_combo)

        self.logout_btn = QPushButton()
        self.logout_btn.clicked.connect(self.logout)
        top_bar.addWidget(self.logout_btn)

        self.session_context_label = QLabel("")
        top_bar.addWidget(self.session_context_label)

        self.root_layout.addLayout(top_bar)

    def _build_body(self):
        body = QHBoxLayout()
        body.setSpacing(12)

        self.nav_container = QWidget()
        self.nav_container.setObjectName("NavContainer")
        nav_layout = QVBoxLayout()
        nav_layout.setContentsMargins(10, 10, 10, 10)
        nav_layout.setSpacing(8)

        self.brand_label = QLabel()
        self.brand_label.setObjectName("BrandLabel")
        nav_layout.addWidget(self.brand_label)

        self.nav_dashboard_btn = QPushButton()
        self.nav_dashboard_btn.clicked.connect(lambda: self.navigate_to("dashboard"))
        nav_layout.addWidget(self.nav_dashboard_btn)

        self.nav_inference_btn = QPushButton()
        self.nav_inference_btn.clicked.connect(self.show_inference)
        nav_layout.addWidget(self.nav_inference_btn)

        self.nav_result_btn = QPushButton()
        self.nav_result_btn.clicked.connect(lambda: self.navigate_to("result"))
        nav_layout.addWidget(self.nav_result_btn)

        self.nav_patients_btn = QPushButton()
        self.nav_patients_btn.clicked.connect(self.show_patients)
        nav_layout.addWidget(self.nav_patients_btn)

        self.nav_users_btn = QPushButton()
        self.nav_users_btn.clicked.connect(self.show_users)
        nav_layout.addWidget(self.nav_users_btn)

        nav_layout.addStretch()

        self.nav_logout_btn = QPushButton()
        self.nav_logout_btn.clicked.connect(self.logout)
        nav_layout.addWidget(self.nav_logout_btn)

        self.nav_container.setLayout(nav_layout)
        self.nav_container.setFixedWidth(180)

        self.pages = QStackedWidget()

        self.stack_container = QWidget()
        stack_grid = QGridLayout()
        stack_grid.setContentsMargins(0, 0, 0, 0)
        stack_grid.addWidget(self.pages, 0, 0)

        self.watermark_logo = QLabel()
        self.watermark_logo.setStyleSheet("background: transparent;")
        self.watermark_logo.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.watermark_logo.setMargin(16)
        self.watermark_logo.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        stack_grid.addWidget(self.watermark_logo, 0, 0, alignment=Qt.AlignRight | Qt.AlignBottom)
        self.stack_container.setLayout(stack_grid)

        body.addWidget(self.nav_container)
        body.addWidget(self.stack_container, 1)
        self.root_layout.addLayout(body, 1)

    def _build_pages(self):
        self.login_page = LoginPage(self.handle_login, self.show_register)
        self.register_page = RegisterPage(self.handle_register, self.show_login)
        self.dashboard_page = DashboardPage([], self.show_result, self.show_inference)
        self.new_case_page = NewCasePage(self.handle_new_case, self.show_dashboard)
        self.result_page = ResultPage({}, self.show_dashboard)
        self.patients_page = PatientsPage(self.show_patients, self.show_patient_detail, self.create_patient_from_ui)
        self.patient_detail_page = PatientDetailPage(self.show_patients)
        self.users_page = UsersPage(self.show_users, self.create_user_from_admin)

        self.pages.addWidget(self.login_page)
        self.pages.addWidget(self.register_page)
        self.pages.addWidget(self.dashboard_page)
        self.pages.addWidget(self.new_case_page)
        self.pages.addWidget(self.result_page)
        self.pages.addWidget(self.patients_page)
        self.pages.addWidget(self.patient_detail_page)
        self.pages.addWidget(self.users_page)

        self.set_auth_state(False)

    def _apply_icons(self):
        self.back_btn.setIcon(self.style().standardIcon(QStyle.SP_ArrowBack))
        self.logout_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
        self.nav_dashboard_btn.setIcon(self.style().standardIcon(QStyle.SP_DesktopIcon))
        self.nav_inference_btn.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        self.nav_result_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        self.nav_patients_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogListView))
        self.nav_users_btn.setIcon(self.style().standardIcon(QStyle.SP_DirHomeIcon))
        self.nav_logout_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
        if hasattr(self.dashboard_page, "new_case_btn"):
            self.dashboard_page.new_case_btn.setIcon(self.style().standardIcon(QStyle.SP_CommandLink))
        if hasattr(self.new_case_page, "back_btn"):
            self.new_case_page.back_btn.setIcon(self.style().standardIcon(QStyle.SP_ArrowBack))
        if hasattr(self.new_case_page, "upload_btn"):
            self.new_case_page.upload_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        if hasattr(self.new_case_page, "submit_btn"):
            self.new_case_page.submit_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        if hasattr(self.result_page, "back_btn"):
            self.result_page.back_btn.setIcon(self.style().standardIcon(QStyle.SP_ArrowBack))
        if hasattr(self.login_page, "login_btn"):
            self.login_page.login_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogOkButton))
        if hasattr(self.login_page, "register_btn"):
            self.login_page.register_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        if hasattr(self.register_page, "register_btn"):
            self.register_page.register_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        if hasattr(self.register_page, "login_btn"):
            self.register_page.login_btn.setIcon(self.style().standardIcon(QStyle.SP_ArrowBack))

    def _build_hospital_logo(self, text, size=86):
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(46, 123, 184, 34))
        painter.setPen(QPen(QColor(46, 123, 184, 48), 2))
        painter.drawRoundedRect(1, 1, size - 2, size - 2, 14, 14)
        painter.setPen(QPen(QColor(27, 40, 56, 56), 2))
        cx = int(size / 2)
        cy = int(size / 2)
        painter.drawLine(cx, 18, cx, size - 18)
        painter.drawLine(18, cy, size - 18, cy)
        painter.setPen(QColor(16, 37, 63, 68))
        font = QFont(self.ui_font_family, max(8, int(size / 8)))
        font.setBold(True)
        painter.setFont(font)
        initials = "".join([w[:1] for w in (text or "Hospital").split()[:2]]).upper() or "H"
        painter.drawText(pixmap.rect(), Qt.AlignBottom | Qt.AlignHCenter, initials)
        painter.end()
        return pixmap

    def _apply_theme(self):
        self.setStyleSheet(
            """
            QWidget {
                background: #f4f7fb;
                color: #1b2838;
                font-family: '%s', 'Nyala', 'Noto Sans Ethiopic', 'Segoe UI';
                font-size: %spx;
            }
            QStackedWidget {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgba(40, 167, 69, 40),
                    stop: 0.52 rgba(255, 193, 7, 32),
                    stop: 1 rgba(220, 53, 69, 40)
                );
                border-radius: 14px;
                border: 1px solid #d8e3ed;
            }
            QWidget#PageCard {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgba(255, 255, 255, 225),
                    stop: 0.2 rgba(40, 167, 69, 20),
                    stop: 0.55 rgba(255, 255, 255, 225),
                    stop: 0.8 rgba(255, 193, 7, 18),
                    stop: 1 rgba(220, 53, 69, 20)
                );
                border: 1px solid #d9e4ef;
                border-radius: 12px;
                padding: 12px;
            }
            QLabel#PageTitle {
                font-size: %spx;
                font-weight: 600;
                color: #10253f;
                padding-bottom: 6px;
            }
            QLabel#BrandLabel {
                font-size: %spx;
                font-weight: 700;
                color: #1f5f8a;
                padding: 6px 4px 10px 4px;
            }
            QWidget#NavContainer {
                background: #e9f0f7;
                border: 1px solid #d2e0ec;
                border-radius: 12px;
            }
            QLineEdit, QComboBox, QTableWidget {
                background: #ffffff;
                border: 1px solid #d5e1ec;
                border-radius: 8px;
                padding: 8px;
                min-height: 30px;
            }
            QPushButton {
                background: #2e7bb8;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 9px 14px;
                font-weight: 600;
                text-align: left;
                min-height: 34px;
            }
            QPushButton:hover {
                background: #25679a;
            }
            QPushButton:disabled {
                background: #9ab9d0;
            }
            QHeaderView::section {
                background: #dce9f5;
                border: none;
                padding: 6px;
                font-weight: 600;
            }
            """
            % (
                self.ui_font_family,
                self.ui_font_size,
                self.ui_font_size + 9,
                self.ui_font_size + 7,
            )
        )

    def on_language_change(self, _index):
        language = self.lang_combo.currentData() or "English"
        self.language = language
        self._apply_runtime_font()
        self.apply_language()

    def on_font_settings_change(self, _value):
        self.ui_font_family = self.font_combo.currentText()
        try:
            self.ui_font_size = int(self.font_size_combo.currentText())
        except ValueError:
            self.ui_font_size = 16
        self._apply_runtime_font()
        self._apply_theme()
        self.apply_language()

    def _apply_runtime_font(self):
        font_family = self.ui_font_family
        # Ethiopic-friendly fallback when Amharic is selected.
        if self.language == "Amharic" and font_family in ["Segoe UI", "Arial"]:
            font_family = "Nyala"
        QApplication.setFont(QFont(font_family, max(10, self.ui_font_size - 2)))

    def apply_language(self):
        texts = TEXTS.get(self.language, TEXTS["English"])
        self.setWindowTitle(texts["app_title"])
        self.brand_label.setText(texts["brand"])
        self.back_btn.setText(texts["back"])
        self.lang_label.setText(texts["lang"])
        self.logout_btn.setText(texts["logout"])
        self.nav_dashboard_btn.setText(texts["nav_dashboard"])
        self.nav_inference_btn.setText(texts["nav_inference"])
        self.nav_result_btn.setText(texts["nav_result"])
        self.nav_patients_btn.setText("Patients" if self.language == "English" else "ታካሚዎች")
        self.nav_users_btn.setText("Users" if self.language == "English" else "ተጠቃሚዎች")
        self.nav_logout_btn.setText(texts["logout"])
        self._update_session_context_label()

        for page in [
            self.login_page,
            self.register_page,
            self.dashboard_page,
            self.new_case_page,
            self.result_page,
            self.patients_page,
            self.patient_detail_page,
            self.users_page,
        ]:
            if hasattr(page, "set_language"):
                page.set_language(self.language)
        self._apply_icons()

    def set_auth_state(self, logged_in):
        self.nav_container.setVisible(logged_in)
        self.logout_btn.setVisible(logged_in)
        self.session_context_label.setVisible(logged_in)
        self.back_btn.setEnabled(True)
        self.apply_role_nav_visibility()

    def _update_session_context_label(self):
        if not self.token:
            self.session_context_label.setText("")
            self.watermark_logo.clear()
            return
        role = self.user_role or "-"
        hospital_name = self.hospital_name or "Hospital"
        hospital_code = self.hospital_code or self.hospital_id or "-"
        self.session_context_label.setText(f"Hospital: {hospital_name} ({hospital_code}) | Role: {role}")
        self.watermark_logo.setPixmap(self._build_hospital_logo(hospital_name, 92))

    def refresh_patients_cache(self, limit=200):
        payload = api.client.list_patients(self.token, limit=limit)
        if isinstance(payload, dict) and payload.get("success"):
            self.patients_cache = payload.get("results", [])
            return self.patients_cache
        # Fallback helper for compatibility
        self.patients_cache = api.get_patients(self.token)
        return self.patients_cache

    def apply_role_nav_visibility(self):
        role = ROLE_NORMALIZE.get(str(self.user_role or "").strip().lower(), self.user_role)
        can_patients = role in ["clinician", "radiologist", "admin"]
        can_inference = role in ["clinician", "radiologist"]
        can_results = role in ["clinician", "radiologist", "admin", "patient"]
        can_users = role == "admin"
        self.nav_patients_btn.setVisible(can_patients)
        self.nav_inference_btn.setVisible(can_inference)
        self.nav_result_btn.setVisible(can_results)
        self.nav_users_btn.setVisible(can_users)
        self.nav_dashboard_btn.setVisible(role is not None)

    def require_auth(self):
        if self.token:
            return True
        texts = TEXTS.get(self.language, TEXTS["English"])
        QMessageBox.warning(self, texts["auth_guard_title"], texts["auth_guard"])
        self.navigate_to("login", push_history=False)
        return False

    def navigate_to(self, key, push_history=True):
        guarded_pages = {"dashboard", "inference", "result", "patients", "patient_detail", "users"}
        if key in guarded_pages and not self.require_auth():
            return

        if push_history and self.current_key != key:
            self.history.append(self.current_key)

        self.current_key = key
        self.pages.setCurrentIndex(self.page_keys[key])

    def go_back(self):
        if not self.history:
            return
        prev_key = self.history.pop()
        self.current_key = prev_key
        self.pages.setCurrentIndex(self.page_keys[prev_key])

    def show_register(self):
        self.navigate_to("register")

    def show_login(self):
        self.navigate_to("login")

    def show_dashboard(self):
        if not self.require_auth():
            return
        cases = api.get_recent_cases(self.token)
        if not isinstance(cases, list):
            patients = api.get_patients(self.token)
            if isinstance(patients, list):
                cases = [
                    {
                        "id": p.get("id", "-"),
                        "date": str(p.get("created_at", "-")).split("T")[0],
                        "score": p.get("age", "-"),
                        "risk": "High" if p.get("hiv_status") else "Low",
                    }
                    for p in patients
                ]
            else:
                cases = []
        self.dashboard_page.set_cases(cases)
        self.navigate_to("dashboard")

    def show_inference(self):
        if not self.require_auth():
            return
        patients = self.refresh_patients_cache(limit=200)
        if not patients:
            QMessageBox.information(self, "No Patients", "No patients found in your hospital. Create a patient record first.")
            self.show_patients()
            return
        self.new_case_page.set_patients(patients)
        self.navigate_to("inference")

    def show_patients(self):
        if not self.require_auth():
            return
        patients = self.refresh_patients_cache(limit=200)
        self.patients_page.set_patients(patients)
        role = ROLE_NORMALIZE.get(str(self.user_role or "").strip().lower(), self.user_role)
        self.patients_page.set_create_enabled(role in ["clinician", "radiologist"])
        self.navigate_to("patients")

    def create_patient_from_ui(self, payload):
        role = ROLE_NORMALIZE.get(str(self.user_role or "").strip().lower(), self.user_role)
        if role not in ["clinician", "radiologist"]:
            return {"success": False, "message": "Only doctor/technician can create patients."}
        result = api.client.create_patient(
            token=self.token,
            name=payload.get("name", ""),
            age=int(payload.get("age") or 0),
            sex=payload.get("sex", "male"),
            hiv_status=payload.get("hiv_status", False),
            symptoms=payload.get("symptoms", []),
            comorbidities=payload.get("comorbidities", []),
        )
        if result.get("success"):
            self.refresh_patients_cache(limit=200)
        return result

    def show_patient_detail(self, patient_id):
        if not self.require_auth():
            return
        payload = api.client.get_patient(self.token, patient_id)
        if payload.get("success"):
            self.patient_detail_page.set_patient(payload)
            self.navigate_to("patient_detail")

    def show_users(self):
        if not self.require_auth():
            return
        if self.user_role != "admin":
            QMessageBox.warning(self, "Access denied", "Only admin can access users page.")
            return
        payload = api.client.list_users(self.token)
        users = payload.get("results", []) if isinstance(payload, dict) else []
        self.users_page.set_users(users)
        self.navigate_to("users")

    def create_user_from_admin(self, payload):
        if self.user_role != "admin":
            return {"success": False, "message": "Only admin can create users."}
        return api.client.create_user(
            token=self.token,
            username=payload.get("username"),
            password=payload.get("password"),
            role=payload.get("role"),
            email=payload.get("email"),
            first_name=payload.get("first_name"),
            last_name=payload.get("last_name"),
            native_name=payload.get("native_name"),
            phone_num=payload.get("phone_num"),
        )

    def show_result(self, case_id=None):
        if not self.require_auth():
            return
        result_data = {}
        if case_id:
            result_data = api.get_case_result(self.token, case_id)
            if not result_data.get("success", True):
                patient = api.client.get_screening(self.token, case_id)
                if patient.get("success"):
                    try:
                        tb_score = float(patient.get("tb_score", 0))
                    except (TypeError, ValueError):
                        tb_score = 0.0
                    result_data = {
                        "score": patient.get("tb_score", "N/A"),
                        "risk": "High" if tb_score >= 60 else "Low",
                        "shap": {},
                        "recommendation": patient.get("triage_recommendation", "No recommendation."),
                    }
                else:
                    patient = api.get_patient(self.token, case_id)
                    if patient.get("success"):
                        result_data = {
                            "score": patient.get("age", "N/A"),
                            "risk": "High" if patient.get("hiv_status") else "Low",
                            "shap": {},
                            "recommendation": f"Patient: {patient.get('name', 'N/A')} | Symptoms: {', '.join(patient.get('symptoms', []))}",
                        }
        self.result_page.set_result(result_data)
        self.result_page.set_language(self.language)
        self._apply_icons()
        self.navigate_to("result")

    def logout(self):
        if self.token:
            api.client.auth_logout(self.token)
        self.token = None
        self.user_role = None
        self.user_id = None
        self.hospital_id = None
        self.hospital_name = None
        self.hospital_code = None
        self.patients_cache = []
        self.history.clear()
        self.set_auth_state(False)
        self.navigate_to("login", push_history=False)
        texts = TEXTS.get(self.language, TEXTS["English"])
        QMessageBox.information(self, texts["logout_title"], texts["logout_msg"])

    def handle_register(self, email, username, password, role, first_name, last_name, native_name, phone_num, hospital_code, hospital_name):
        result = api.register(
            email,
            username,
            password,
            role,
            first_name,
            last_name,
            native_name,
            phone_num,
            hospital_code,
            hospital_name,
        )
        if result.get("success"):
            self.show_login()
        return result

    def handle_login(self, email, password, role):
        result = api.login(email, password, role)
        if result.get("success"):
            selected = ROLE_UI_TO_BACKEND.get(role)
            server_role = result.get("role")
            if selected != server_role:
                return {
                    "success": False,
                    "message": f"Selected role '{role}' does not match account role '{server_role}'.",
                    "status_code": 403,
                }
            self.token = result["token"]
            self.user_role = result.get("role")
            self.user_id = result.get("user_id")
            self.hospital_id = result.get("hospital_id")
            self.hospital_name = result.get("hospital_name")
            self.hospital_code = result.get("hospital_code")
            self.set_auth_state(True)
            self._update_session_context_label()
            self.show_dashboard()
        return result

    def handle_new_case(self, case_data, image_path):
        if not case_data.get("patient_id"):
            return {"success": False, "message": "Patient selection is required for inference."}
        result = api.submit_new_case(self.token, case_data, image_path)
        if result.get("success"):
            self.show_result(result.get("screening_id") or result.get("case_id") or result.get("id"))
        return result


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(build_medivision_icon())
    main_app = MainApp()
    main_app.setWindowIcon(build_medivision_icon())
    main_app.resize(1160, 760)
    main_app.show()
    sys.exit(app.exec_())
