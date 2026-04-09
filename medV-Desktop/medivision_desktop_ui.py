import sys
import re
from pathlib import Path

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, QStackedWidget,
                             QComboBox, QCheckBox, QGraphicsDropShadowEffect, QGridLayout,
                             QSpacerItem, QSizePolicy, QFrame)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QPalette, QCursor, QPainter, QPixmap

_LANDING_BG_PATH = Path(__file__).resolve().parent / "assets" / "landing_bg.png"
from dashboard.api_client import APIClient, ApiWorker, AuthStore

# ---------------------------------------------------------
# TRANSLATIONS DICTIONARY
# ---------------------------------------------------------
TRANSLATIONS = {
    "en": {
        "app_title": "MediVision",
        "tagline": "AI-Powered TB Screening",
        "desc": "Advanced Computer-Aided Detection system for rapid\nand accurate Tuberculosis screening in medical facilities.",
        "login_btn": "Sign In",
        "register_btn": "Create Account",
        "username": "Username",
        "password": "Password",
        "role_placeholder": "Select Role...",
        "roles": ["Clinician", "Radiographer", "Lab Technician", "System Admin"],
        "remember_me": "Remember Me",
        "offline_mode": "Offline Mode Ready",
        "login_header": "Welcome Back",
        "no_account": "Don't have an account?",
        "register_header": "Register New Account",
        "full_name": "Full Name",
        "email": "Email Address",
        "confirm_pwd": "Confirm Password",
        "language": "Language",
        "already_have_acc": "Already have an account?",
        "verify_title": "Verify Your Account",
        "verify_desc": "Enter the 6-digit code sent to your email",
        "resend": "Resend Code",
        "verify_btn": "Verify Account",
        "req_field": "* Required",
        "pwd_mismatch": "Passwords do not match",
        "invalid_email": "Invalid Email",
        "back": "Back"
    },
    "am": {
        "app_title": "ሜዲቪዥን",
        "tagline": "በ AI የታገዘ የቲቢ ምርመራ",
        "desc": "በማከሚያ ተቋማት ፈጣን እና ትክክለኛ የሳንባ ነቀርሳ ምርመራ\nለማድረግ የሚረዳ የኮምፒውተር እገዛ ስርዓት።",
        "login_btn": "ግባ",
        "register_btn": "መለያ ፍጠር",
        "username": "የተጠቃሚ ስም",
        "password": "የይለፍ ቃል",
        "role_placeholder": "ሚና ይምረጡ...",
        "roles": ["ሀኪም", "ራዲዮግራፈር", "የላብራቶሪ ባለሙያ", "የስርዓት አስተዳዳሪ"],
        "remember_me": "አስታውሰኝ",
        "offline_mode": "ከመስመር ውጭ ይሰራል",
        "login_header": "እንኳን ደህና መጡ",
        "no_account": "መለያ የለዎትም?",
        "register_header": "አዲስ መለያ ይመዝገቡ",
        "full_name": "ሙሉ ስም",
        "email": "ኢሜል",
        "confirm_pwd": "የይለፍ ቃል አረጋግጥ",
        "language": "ቋንቋ",
        "already_have_acc": "መለያ አልዎት?",
        "verify_title": "መለያዎን ያረጋግጡ",
        "verify_desc": "በኢሜል የተላከውን 6 አሃዝ ኮድ ያስገቡ",
        "resend": "ኮድ በድጋሚ ላክ",
        "verify_btn": "አረጋግጥ",
        "req_field": "* ያስፈልጋል",
        "pwd_mismatch": "የይለፍ ቃል አይዛመድም",
        "invalid_email": "የተሳሳተ ኢሜል",
        "back": "ተመለስ"
    }
}

# ---------------------------------------------------------
# MANAGERS
# ---------------------------------------------------------
class ThemeManager:
    # Colors for Light Theme
    LIGHT = {
        "bg": "#E9F1FF",
        "card": "#FFFFFF",
        "text_primary": "#0E2A47",
        "text_secondary": "#4B5563",
        "primary": "#2A6FDB",
        "primary_hover": "#1F59B6",
        "border": "#D0D9E6",
        "success": "#22C55E",
        "error": "#EF4444",
        "input_bg": "#F9FAFB"
    }
    
    # Colors for Dark Theme
    DARK = {
        "bg": "#0B1E2D",
        "card": "#111827",
        "text_primary": "#E5E7EB",
        "text_secondary": "#9CA3AF",
        "primary": "#3B82F6",
        "primary_hover": "#2563EB",
        "border": "#374151",
        "success": "#22C55E",
        "error": "#F87171",
        "input_bg": "#1F2937"
    }

    def __init__(self):
        self.is_dark = False

    def get_colors(self):
        return self.DARK if self.is_dark else self.LIGHT

    def toggle(self):
        self.is_dark = not self.is_dark


class LanguageManager:
    def __init__(self):
        self.lang = "en"

    def get(self, key):
        return TRANSLATIONS[self.lang].get(key, key)

    def set_language(self, lang):
        if lang in TRANSLATIONS:
            self.lang = lang


# ---------------------------------------------------------
# REUSABLE COMPONENTS
# ---------------------------------------------------------
class CardWidget(QFrame):
    """A card-like widget with rounded corners and soft shadow"""
    def __init__(self, theme_mgr, parent=None):
        super().__init__(parent)
        self.theme_mgr = theme_mgr
        self.setObjectName("CardWidget")
        
        # Add soft shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30 if not self.theme_mgr.is_dark else 80))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)
        
        self.apply_style()

    def apply_style(self):
        c = self.theme_mgr.get_colors()
        self.setStyleSheet(f"""
            QFrame#CardWidget {{
                background-color: {c["card"]};
                border-radius: 16px;
                border: 1px solid {c["border"]};
            }}
        """)


class CustomInputField(QWidget):
    """Custom input field with label and optional error state"""
    def __init__(self, label_key, lang_mgr, theme_mgr, is_password=False, is_email=False, parent=None):
        super().__init__(parent)
        self.lang_mgr = lang_mgr
        self.theme_mgr = theme_mgr
        self.label_key = label_key
        self.is_password = is_password
        self.is_email = is_email
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        self.label = QLabel(self.lang_mgr.get(label_key))
        font = QFont("Inter", 10)
        font.setBold(True)
        self.label.setFont(font)
        
        self.input_field = QLineEdit()
        self.input_field.setMinimumHeight(44)
        if self.is_password:
            self.input_field.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.error_label = QLabel()
        self.error_label.setFont(QFont("Inter", 9))
        self.error_label.setVisible(False)
        
        layout.addWidget(self.label)
        layout.addWidget(self.input_field)
        layout.addWidget(self.error_label)
        
        self.apply_style()
        self.input_field.textChanged.connect(self.clear_error)

    def apply_style(self, error=False):
        c = self.theme_mgr.get_colors()
        self.label.setStyleSheet(f"color: {c['text_primary']};")
        self.error_label.setStyleSheet(f"color: {c['error']};")
        
        border_col = c['error'] if error else c['border']
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {c["input_bg"]};
                color: {c["text_primary"]};
                border: 1px solid {border_col};
                border-radius: 8px;
                padding: 0 12px;
                font-family: Inter, Roboto, sans-serif;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 2px solid {c["primary"]};
                background-color: {c["card"]};
            }}
        """)

    def set_error(self, err_key):
        self.error_label.setText(self.lang_mgr.get(err_key))
        self.error_label.setVisible(True)
        self.apply_style(error=True)

    def clear_error(self):
        self.error_label.setVisible(False)
        self.apply_style(error=False)

    def text(self):
        return self.input_field.text()
        
    def retranslate(self):
        self.label.setText(self.lang_mgr.get(self.label_key))


class CustomButton(QPushButton):
    """Modern primary/secondary button"""
    def __init__(self, text_key, lang_mgr, theme_mgr, is_primary=True, parent=None):
        super().__init__(parent)
        self.lang_mgr = lang_mgr
        self.theme_mgr = theme_mgr
        self.text_key = text_key
        self.is_primary = is_primary
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(44)
        self.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        self.update_text()
        self.apply_style()

    def apply_style(self):
        c = self.theme_mgr.get_colors()
        if self.is_primary:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {c["primary"]};
                    color: white;
                    border: none;
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    background-color: {c["primary_hover"]};
                }}
                QPushButton:pressed {{
                    background-color: {c["primary"]};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {c["primary"]};
                    border: 2px solid {c["primary"]};
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    background-color: {c["input_bg"]};
                }}
            """)

    def update_text(self):
        self.setText(self.lang_mgr.get(self.text_key))


# ---------------------------------------------------------
# PAGES
# ---------------------------------------------------------
class BasePage(QWidget):
    go_to = pyqtSignal(str) # Signal to request page change

    def __init__(self, lang_mgr, theme_mgr, parent=None):
        super().__init__(parent)
        self.lang_mgr = lang_mgr
        self.theme_mgr = theme_mgr

    def apply_theme(self):
        pass # Override in subclasses

    def retranslate(self):
        pass # Override in subclasses


class LandingPage(BasePage):
    def __init__(self, lang_mgr, theme_mgr, parent=None):
        super().__init__(lang_mgr, theme_mgr, parent)
        self._bg_pixmap = QPixmap(str(_LANDING_BG_PATH))
        if self._bg_pixmap.isNull():
            self._bg_pixmap = QPixmap()

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Center container
        self.container = QWidget()
        layout = QVBoxLayout(self.container)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(24)
        
        # Logo / Title
        self.title_lbl = QLabel()
        title_font = QFont("Outfit", 48, QFont.Weight.Bold)
        self.title_lbl.setFont(title_font)
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.tagline_lbl = QLabel()
        self.tagline_lbl.setFont(QFont("Inter", 16, QFont.Weight.Medium))
        self.tagline_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.desc_lbl = QLabel()
        self.desc_lbl.setFont(QFont("Inter", 11))
        self.desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.login_btn = CustomButton("login_btn", lang_mgr, theme_mgr, is_primary=True)
        self.login_btn.setMinimumWidth(200)
        self.reg_btn = CustomButton("register_btn", lang_mgr, theme_mgr, is_primary=False)
        self.reg_btn.setMinimumWidth(200)
        
        btn_layout.addWidget(self.login_btn)
        btn_layout.addWidget(self.reg_btn)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Routing signals
        self.login_btn.clicked.connect(lambda: self.go_to.emit("login"))
        self.reg_btn.clicked.connect(lambda: self.go_to.emit("register"))
        
        layout.addWidget(self.title_lbl)
        layout.addWidget(self.tagline_lbl)
        layout.addWidget(self.desc_lbl)
        layout.addSpacing(30)
        layout.addLayout(btn_layout)
        
        main_layout.addWidget(self.container)
        self.apply_theme()
        self.retranslate()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        w, h = self.width(), self.height()
        if w <= 0 or h <= 0:
            return
        c = self.theme_mgr.get_colors()
        if self._bg_pixmap.isNull():
            painter.fillRect(self.rect(), QColor(c["bg"]))
            return
        scaled = self._bg_pixmap.scaled(
            w, h,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = max(0, (scaled.width() - w) // 2)
        y = max(0, (scaled.height() - h) // 2)
        painter.drawPixmap(0, 0, scaled, x, y, w, h)

    def apply_theme(self):
        c = self.theme_mgr.get_colors()
        self.title_lbl.setStyleSheet(f"color: {c['primary']};")
        self.tagline_lbl.setStyleSheet(f"color: {c['text_primary']};")
        self.desc_lbl.setStyleSheet(f"color: {c['text_secondary']};")
        self.login_btn.apply_style()
        self.reg_btn.apply_style()
        self.update()

    def retranslate(self):
        self.title_lbl.setText(self.lang_mgr.get("app_title"))
        self.tagline_lbl.setText(self.lang_mgr.get("tagline"))
        self.desc_lbl.setText(self.lang_mgr.get("desc"))
        self.login_btn.update_text()
        self.reg_btn.update_text()


class LoginPage(BasePage):
    def __init__(self, lang_mgr, theme_mgr, parent=None):
        super().__init__(lang_mgr, theme_mgr, parent)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Card Wrapper
        self.card = CardWidget(theme_mgr)
        self.card.setFixedWidth(450)
        self.card.setMinimumHeight(550)
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)
        
        # Header
        self.header_lbl = QLabel()
        self.header_lbl.setFont(QFont("Outfit", 24, QFont.Weight.Bold))
        self.header_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Form Fields
        self.user_input = CustomInputField("username", lang_mgr, theme_mgr)
        self.pass_input = CustomInputField("password", lang_mgr, theme_mgr, is_password=True)
        
        # Role Dropdown
        self.role_combo = QComboBox()
        self.role_combo.setMinimumHeight(44)
        
        # Options row
        opt_layout = QHBoxLayout()
        self.remember_cb = QCheckBox()
        self.offline_lbl = QLabel()
        self.offline_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        font_small = QFont("Inter", 9)
        self.remember_cb.setFont(font_small)
        self.offline_lbl.setFont(font_small)
        
        opt_layout.addWidget(self.remember_cb)
        opt_layout.addWidget(self.offline_lbl)
        
        # Submit Button
        self.submit_btn = CustomButton("login_btn", lang_mgr, theme_mgr)
        self.submit_btn.clicked.connect(self.handle_login)
        
        # Links
        links_layout = QHBoxLayout()
        self.no_acc_lbl = QLabel()
        self.no_acc_lbl.setFont(font_small)
        self.create_link_btn = QPushButton()
        self.create_link_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.create_link_btn.setFlat(True)
        font_link = QFont("Inter", 9, QFont.Weight.Bold)
        self.create_link_btn.setFont(font_link)
        self.create_link_btn.clicked.connect(lambda: self.go_to.emit("register"))
        
        links_layout.addStretch()
        links_layout.addWidget(self.no_acc_lbl)
        links_layout.addWidget(self.create_link_btn)
        links_layout.addStretch()

        # Back link
        self.back_btn = QPushButton()
        self.back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.back_btn.setFlat(True)
        self.back_btn.clicked.connect(lambda: self.go_to.emit("landing"))

        card_layout.addWidget(self.back_btn, 0, Qt.AlignmentFlag.AlignLeft)
        card_layout.addWidget(self.header_lbl)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.user_input)
        card_layout.addWidget(self.pass_input)
        card_layout.addWidget(self.role_combo)
        card_layout.addLayout(opt_layout)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.submit_btn)

        # Inline API error banner (hidden when empty)
        self.api_error_lbl = QLabel("")
        self.api_error_lbl.setFont(QFont("Inter", 10))
        self.api_error_lbl.setWordWrap(True)
        self.api_error_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.api_error_lbl)

        card_layout.addLayout(links_layout)
        
        layout.addWidget(self.card)
        self.apply_theme()
        self.retranslate()

    def handle_login(self):
        valid = True
        if not self.user_input.text():
            self.user_input.set_error("req_field")
            valid = False
        if not self.pass_input.text():
            self.pass_input.set_error("req_field")
            valid = False
        if not valid:
            return

        # Clear any previous API error
        self.api_error_lbl.setText("")

        # Resolve canonical role key
        raw_role = self.role_combo.currentText()
        role_map = {
            "Clinician": "Clinician", "Radiographer": "Radiographer",
            "Lab Technician": "Lab Technician", "System Admin": "System Admin",
            "ሀኪም": "Clinician", "ራዲዮግራፈር": "Radiographer",
            "የላብራቶሪ ባለሙያ": "Lab Technician", "የስርዓት አስተዳዳሪ": "System Admin",
        }
        role = role_map.get(raw_role, "Clinician")

        # Lock UI while request is in-flight
        self.submit_btn.setText("Connecting…")
        self.submit_btn.setEnabled(False)

        email    = self.user_input.text().strip()
        password = self.pass_input.text()

        self._login_worker = ApiWorker(APIClient.login, email, password, role)
        self._login_worker.success.connect(lambda resp: self._on_login_result(resp, role, email))
        self._login_worker.failure.connect(self._on_login_error)
        self._login_worker.no_auth.connect(
            lambda: self._on_login_error("Invalid credentials. Please try again.")
        )
        self._login_worker.start()

    def _on_login_result(self, resp, role, email):
        """Called in the main thread when the login HTTP response arrives."""
        self.submit_btn.setEnabled(True)
        self.submit_btn.update_text()

        if resp.status_code in (200, 201):
            try:
                data  = resp.json()
                # Support access / token / access_token key variants
                token = (data.get("access") or data.get("token")
                         or data.get("access_token") or "")
                AuthStore.token    = token
                AuthStore.username = email
                AuthStore.role     = role
            except Exception:
                pass
            self._launch_dashboard(email, role)
        else:
            try:
                body = resp.json()
                msg  = (body.get("detail") or body.get("error")
                        or body.get("message") or "Invalid credentials.")
            except Exception:
                msg = f"Login failed (HTTP {resp.status_code}). Please try again."
            self.api_error_lbl.setText("⚠  " + str(msg))

    def _on_login_error(self, error_msg: str):
        """Called when a network error or 401 occurs."""
        self.submit_btn.setEnabled(True)
        self.submit_btn.update_text()
        self.api_error_lbl.setText("⚠  " + error_msg)

    def _launch_dashboard(self, username, role):
        from medivision_dashboard_main import DashboardWindow
        self.dashboard_win = DashboardWindow(role=role, username=username)
        self.dashboard_win.show()
        # Hide the auth window (don't close — keeps QApplication alive)
        self.window().hide()

    def apply_theme(self):
        c = self.theme_mgr.get_colors()
        self.card.apply_style()
        self.header_lbl.setStyleSheet(f"color: {c['text_primary']};")
        self.role_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {c["input_bg"]};
                color: {c["text_primary"]};
                border: 1px solid {c["border"]};
                border-radius: 8px;
                padding: 0 12px;
            }}
        """)
        self.remember_cb.setStyleSheet(f"color: {c['text_secondary']};")
        self.offline_lbl.setStyleSheet(f"color: {c['success']};")
        self.no_acc_lbl.setStyleSheet(f"color: {c['text_secondary']};")
        self.create_link_btn.setStyleSheet(f"color: {c['primary']}; border: none;")
        self.back_btn.setStyleSheet(f"color: {c['text_secondary']}; border: none;")
        
        self.user_input.apply_style()
        self.pass_input.apply_style()
        self.submit_btn.apply_style()
        if hasattr(self, "api_error_lbl"):
            self.api_error_lbl.setStyleSheet(f"color: {c['error']}; border: none;")

    def retranslate(self):
        self.header_lbl.setText(self.lang_mgr.get("login_header"))
        self.remember_cb.setText(self.lang_mgr.get("remember_me"))
        self.offline_lbl.setText("● " + self.lang_mgr.get("offline_mode"))
        self.submit_btn.update_text()
        self.no_acc_lbl.setText(self.lang_mgr.get("no_account"))
        self.create_link_btn.setText(self.lang_mgr.get("register_btn"))
        self.back_btn.setText("← " + self.lang_mgr.get("back"))
        
        self.user_input.retranslate()
        self.pass_input.retranslate()
        
        self.role_combo.clear()
        self.role_combo.addItems(self.lang_mgr.get("roles"))


class RegisterPage(BasePage):
    def __init__(self, lang_mgr, theme_mgr, parent=None):
        super().__init__(lang_mgr, theme_mgr, parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.card = CardWidget(theme_mgr)
        self.card.setFixedSize(500, 700)
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 30, 40, 30)
        card_layout.setSpacing(15)
        
        # Header
        self.header_lbl = QLabel()
        self.header_lbl.setFont(QFont("Outfit", 24, QFont.Weight.Bold))
        self.header_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Fields
        self.name_input = CustomInputField("full_name", lang_mgr, theme_mgr)
        self.user_input = CustomInputField("username", lang_mgr, theme_mgr)
        self.email_input = CustomInputField("email", lang_mgr, theme_mgr)
        
        pwd_layout = QHBoxLayout()
        self.pass_input = CustomInputField("password", lang_mgr, theme_mgr, is_password=True)
        self.conf_pass_input = CustomInputField("confirm_pwd", lang_mgr, theme_mgr, is_password=True)
        pwd_layout.addWidget(self.pass_input)
        pwd_layout.addWidget(self.conf_pass_input)
        pwd_layout.setSpacing(15)
        
        self.role_combo = QComboBox()
        self.role_combo.setMinimumHeight(44)
        
        # Submit
        self.submit_btn = CustomButton("register_btn", lang_mgr, theme_mgr)
        self.submit_btn.clicked.connect(self.handle_register)
        
        # Links
        links_layout = QHBoxLayout()
        self.has_acc_lbl = QLabel()
        self.login_link_btn = QPushButton()
        self.login_link_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.login_link_btn.setFlat(True)
        font_link = QFont("Inter", 9, QFont.Weight.Bold)
        self.login_link_btn.setFont(font_link)
        self.login_link_btn.clicked.connect(lambda: self.go_to.emit("login"))
        
        links_layout.addStretch()
        links_layout.addWidget(self.has_acc_lbl)
        links_layout.addWidget(self.login_link_btn)
        links_layout.addStretch()

        self.back_btn = QPushButton()
        self.back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.back_btn.setFlat(True)
        self.back_btn.clicked.connect(lambda: self.go_to.emit("landing"))

        card_layout.addWidget(self.back_btn, 0, Qt.AlignmentFlag.AlignLeft)
        card_layout.addWidget(self.header_lbl)
        card_layout.addWidget(self.name_input)
        card_layout.addWidget(self.user_input)
        card_layout.addWidget(self.email_input)
        card_layout.addLayout(pwd_layout)
        card_layout.addWidget(self.role_combo)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.submit_btn)
        card_layout.addLayout(links_layout)
        
        layout.addWidget(self.card)
        self.apply_theme()
        self.retranslate()

    def handle_register(self):
        valid = True
        
        # Regex for email
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, self.email_input.text()):
            self.email_input.set_error("invalid_email")
            valid = False
            
        if not self.name_input.text(): self.name_input.set_error("req_field"); valid = False
        if not self.user_input.text(): self.user_input.set_error("req_field"); valid = False
        if not self.pass_input.text(): self.pass_input.set_error("req_field"); valid = False
        
        if self.pass_input.text() != self.conf_pass_input.text():
            self.conf_pass_input.set_error("pwd_mismatch")
            valid = False
            
        if valid:
            self.go_to.emit("verify")

    def apply_theme(self):
        c = self.theme_mgr.get_colors()
        self.card.apply_style()
        self.header_lbl.setStyleSheet(f"color: {c['text_primary']};")
        self.role_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {c["input_bg"]};
                color: {c["text_primary"]};
                border: 1px solid {c["border"]};
                border-radius: 8px;
                padding: 0 12px;
            }}
        """)
        self.has_acc_lbl.setStyleSheet(f"color: {c['text_secondary']};")
        self.login_link_btn.setStyleSheet(f"color: {c['primary']}; border: none;")
        self.back_btn.setStyleSheet(f"color: {c['text_secondary']}; border: none;")
        
        self.name_input.apply_style()
        self.user_input.apply_style()
        self.email_input.apply_style()
        self.pass_input.apply_style()
        self.conf_pass_input.apply_style()
        self.submit_btn.apply_style()

    def retranslate(self):
        self.header_lbl.setText(self.lang_mgr.get("register_header"))
        self.submit_btn.update_text()
        self.has_acc_lbl.setText(self.lang_mgr.get("already_have_acc"))
        self.login_link_btn.setText(self.lang_mgr.get("login_btn"))
        self.back_btn.setText("← " + self.lang_mgr.get("back"))
        
        self.name_input.retranslate()
        self.user_input.retranslate()
        self.email_input.retranslate()
        self.pass_input.retranslate()
        self.conf_pass_input.retranslate()
        
        self.role_combo.clear()
        self.role_combo.addItems(self.lang_mgr.get("roles"))


class VerificationPage(BasePage):
    def __init__(self, lang_mgr, theme_mgr, parent=None):
        super().__init__(lang_mgr, theme_mgr, parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.card = CardWidget(theme_mgr)
        self.card.setFixedSize(450, 450)
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.header_lbl = QLabel()
        self.header_lbl.setFont(QFont("Outfit", 24, QFont.Weight.Bold))
        self.header_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.desc_lbl = QLabel()
        self.desc_lbl.setFont(QFont("Inter", 11))
        self.desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc_lbl.setWordWrap(True)
        
        # 6-Digit OTP Inputs
        otp_layout = QHBoxLayout()
        self.otp_inputs = []
        for i in range(6):
            inp = QLineEdit()
            inp.setMaxLength(1)
            inp.setAlignment(Qt.AlignmentFlag.AlignCenter)
            inp.setFont(QFont("Inter", 18, QFont.Weight.Bold))
            inp.setFixedSize(45, 55)
            
            # Simple auto-focus next (omitted proper signal connections for brevity)
            # but setting the style
            otp_layout.addWidget(inp)
            self.otp_inputs.append(inp)
            
        self.timer_lbl = QLabel("01:00")
        self.timer_lbl.setFont(QFont("Inter", 12))
        self.timer_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.submit_btn = CustomButton("verify_btn", lang_mgr, theme_mgr)
        self.submit_btn.clicked.connect(self.handle_verify)
        
        self.resend_btn = QPushButton()
        self.resend_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.resend_btn.setFlat(True)
        self.resend_btn.setFont(QFont("Inter", 10))
        
        card_layout.addWidget(self.header_lbl)
        card_layout.addWidget(self.desc_lbl)
        card_layout.addSpacing(20)
        card_layout.addLayout(otp_layout)
        card_layout.addWidget(self.timer_lbl)
        card_layout.addWidget(self.submit_btn)
        card_layout.addWidget(self.resend_btn)
        
        layout.addWidget(self.card)
        self.apply_theme()
        self.retranslate()

    def handle_verify(self):
        # Fake verification success
        self.go_to.emit("login")

    def apply_theme(self):
        c = self.theme_mgr.get_colors()
        self.card.apply_style()
        self.header_lbl.setStyleSheet(f"color: {c['text_primary']};")
        self.desc_lbl.setStyleSheet(f"color: {c['text_secondary']};")
        self.timer_lbl.setStyleSheet(f"color: {c['primary']};")
        self.resend_btn.setStyleSheet(f"color: {c['text_secondary']}; border: none;")
        
        for inp in self.otp_inputs:
            inp.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {c["input_bg"]};
                    color: {c["text_primary"]};
                    border: 1px solid {c["border"]};
                    border-radius: 8px;
                }}
                QLineEdit:focus {{ border: 2px solid {c["primary"]}; }}
            """)
            
        self.submit_btn.apply_style()

    def retranslate(self):
        self.header_lbl.setText(self.lang_mgr.get("verify_title"))
        self.desc_lbl.setText(self.lang_mgr.get("verify_desc"))
        self.submit_btn.update_text()
        self.resend_btn.setText(self.lang_mgr.get("resend"))


# ---------------------------------------------------------
# MAIN WINDOW
# ---------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.lang_mgr = LanguageManager()
        self.theme_mgr = ThemeManager()
        
        self.setWindowTitle("MediVision - TB Screening CAD")
        self.resize(1200, 800)
        
        # Main Widget & Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header (Top Bar with controls)
        self.setup_header()
        
        # Stacked Widget for Navigation
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("QStackedWidget { background: transparent; }")
        self.main_layout.addWidget(self.stack)
        
        # Initialize Pages
        self.pages = {
            "landing": LandingPage(self.lang_mgr, self.theme_mgr),
            "login": LoginPage(self.lang_mgr, self.theme_mgr),
            "register": RegisterPage(self.lang_mgr, self.theme_mgr),
            "verify": VerificationPage(self.lang_mgr, self.theme_mgr)
        }
        
        for name, page in self.pages.items():
            self.stack.addWidget(page)
            page.go_to.connect(self.navigate_to)
            
        self.navigate_to("landing")
        self.apply_theme()

    def setup_header(self):
        self.header = QWidget()
        self.header.setFixedHeight(60)
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        # Logo/Brand
        self.brand_lbl = QLabel("MediVision")
        self.brand_lbl.setFont(QFont("Outfit", 16, QFont.Weight.Bold))
        
        header_layout.addWidget(self.brand_lbl)
        header_layout.addStretch()
        
        # Controls
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English (EN)", "Amharic (AM)"])
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setFixedSize(40, 40)
        self.theme_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.theme_btn.clicked.connect(self.toggle_theme)
        
        header_layout.addWidget(self.lang_combo)
        header_layout.addWidget(self.theme_btn)
        
        self.main_layout.addWidget(self.header)

    def navigate_to(self, page_name):
        if page_name in self.pages:
            self.stack.setCurrentWidget(self.pages[page_name])

    def change_language(self, index):
        lang_code = "en" if index == 0 else "am"
        self.lang_mgr.set_language(lang_code)
        
        # Retranslate everything
        self.brand_lbl.setText(self.lang_mgr.get("app_title"))
        for page in self.pages.values():
            page.retranslate()

    def toggle_theme(self):
        self.theme_mgr.toggle()
        self.theme_btn.setText("☀️" if self.theme_mgr.is_dark else "🌙")
        self.apply_theme()
        
        for page in self.pages.values():
            page.apply_theme()

    def apply_theme(self):
        c = self.theme_mgr.get_colors()
        self.central_widget.setStyleSheet(f"background-color: {c['bg']};")
        self.brand_lbl.setStyleSheet(f"color: {c['primary']};")
        
        self.header.setStyleSheet(f"background-color: transparent;")
        
        self.lang_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {c["card"]};
                color: {c["text_primary"]};
                border: 1px solid {c["border"]};
                border-radius: 6px;
                padding: 5px 10px;
                font-family: Inter;
            }}
            QComboBox::drop-down {{ border: none; }}
        """)
        
        self.theme_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c["card"]};
                color: {c["text_primary"]};
                border: 1px solid {c["border"]};
                border-radius: 20px;
                font-size: 16px;
            }}
            QPushButton:hover {{ background-color: {c["input_bg"]}; }}
        """)

# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Try setting global font to modern sans-serif
    font = QFont("Inter", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
