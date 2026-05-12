"""
MediVision – Dashboard Main Window
Loads after login, routes to the correct role-based dashboard.

Usage:
    python medivision_dashboard_main.py
    # or import DashboardWindow and call show() after passing role/username
"""
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QSizePolicy, QStackedWidget)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from dashboard.theme import ThemeManager
from dashboard.lang import LanguageManager
from dashboard.components import TopBar, SidebarItem
from dashboard.clinician import ClinicianDashboard
from dashboard.radiographer import RadiographerDashboard
from dashboard.lab_technician import LabDashboard
from dashboard.admin import AdminDashboard


# ── Dashboard Window ──────────────────────────────────────────────
class DashboardWindow(QMainWindow):
    """
    Main window that shows after successful login.
    Args:
        role     (str): One of "Clinician", "Radiographer", "Lab Technician", "System Admin"
        username (str): Logged-in username
    """
    def __init__(self, role="Clinician", username="user", parent=None):
        super().__init__(parent)
        self.role     = role
        self.username = username
        self.lang_mgr  = LanguageManager()
        self.theme_mgr = ThemeManager()

        self.setWindowTitle("MediVision – TB Screening CAD System")
        self.resize(1360, 820)
        self.setMinimumSize(1100, 700)

        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Top Bar ───────────────────────────────────────────────
        self.topbar = TopBar(self.username, self.role, self.lang_mgr, self.theme_mgr)
        self.topbar.theme_toggled.connect(self._on_theme_toggled)
        self.topbar.language_changed.connect(self._on_language_changed)
        self.topbar.logout_requested.connect(self._logout)
        root.addWidget(self.topbar)

        # ── Body (sidebar + dashboard) ────────────────────────────
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # Left sidebar (role nav) — visible only for roles with multiple views
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(12, 20, 12, 20)
        sidebar_layout.setSpacing(6)

        self.role_lbl = QLabel(self.role)
        self.role_lbl.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        self.role_lbl.setWordWrap(True)
        sidebar_layout.addWidget(self.role_lbl)
        sidebar_layout.addSpacing(12)

        self.nav_btns = self._build_sidebar_nav(sidebar_layout)
        sidebar_layout.addStretch()

        body.addWidget(self.sidebar)

        # Dashboard content
        self.dashboard_stack = QStackedWidget()
        self.dashboard_widget = self._load_dashboard()
        self.dashboard_stack.addWidget(self.dashboard_widget)
        body.addWidget(self.dashboard_stack, 1)

        root.addLayout(body)
        self.apply_theme()

    def _build_sidebar_nav(self, layout) -> dict:
        """Build nav items based on role."""
        nav = {}

        # All roles get a "Dashboard" and "Logout" item
        dash_btn = SidebarItem("🏠", "Dashboard", self.theme_mgr)
        dash_btn.set_active(True)
        dash_btn.clicked.connect(lambda: self._activate_nav("dashboard", dash_btn))
        layout.addWidget(dash_btn)
        nav["dashboard"] = dash_btn

        # Role-specific extras
        if self.role == "Clinician":
            items = [("🧑‍⚕", "Patients",       "patients"),
                     ("📊", "AI Results",      "results"),
                     ("📄", "Reports",         "reports")]
        elif self.role == "Radiographer":
            items = [("📤", "Upload X-Ray",    "upload"),
                     ("🗂",  "Upload History",  "history")]
        elif self.role == "Lab Technician":
            items = [("🧪", "Lab Entry",       "entry"),
                     ("📋", "Records",         "records")]
        elif self.role == "System Admin":
            items = [("👥", "Users",           "users"),
                     ("📋", "Logs",            "logs"),
                     ("⚙️", "Settings",       "settings")]
        else:
            items = []

        for icon, label, key in items:
            btn = SidebarItem(icon, label, self.theme_mgr)
            btn.clicked.connect(lambda checked, k=key, b=btn: self._activate_nav(k, b))
            layout.addWidget(btn)
            nav[key] = btn

        return nav

    def _activate_nav(self, key, active_btn):
        for btn in self.nav_btns.values():
            btn.set_active(False)
        active_btn.set_active(True)

    def _load_dashboard(self) -> QWidget:
        """Return the correct dashboard widget for the role."""
        mapping = {
            "Clinician":      ClinicianDashboard,
            "Radiographer":   RadiographerDashboard,
            "Lab Technician": LabDashboard,
            "System Admin":   AdminDashboard,
        }
        cls = mapping.get(self.role, ClinicianDashboard)
        return cls(self.lang_mgr, self.theme_mgr)

    def _on_theme_toggled(self):
        self.apply_theme()
        if hasattr(self.dashboard_widget, 'apply_theme'):
            self.dashboard_widget.apply_theme()
        if isinstance(self.dashboard_widget, AdminDashboard):
            self.dashboard_widget.apply_theme()

    def _on_language_changed(self, lang):
        self.lang_mgr.set_language(lang)
        if hasattr(self.dashboard_widget, 'retranslate'):
            self.dashboard_widget.retranslate()

    def _logout(self):
        self.close()
        # Re-show the auth window (it was hidden, not destroyed)
        for widget in QApplication.topLevelWidgets():
            from medivision_desktop_ui import MainWindow
            if isinstance(widget, MainWindow):
                widget.show()
                widget.navigate_to("login")
                return
        # Fallback: restart the auth app fresh
        import subprocess, sys
        subprocess.Popen([sys.executable, "medivision_desktop_ui.py"])
        QApplication.quit()

    def apply_theme(self):
        c = self.theme_mgr.get_colors()
        self.centralWidget().setStyleSheet(f"background-color: {c['bg']};")
        self.sidebar.setStyleSheet(f"""
            QWidget {{
                background-color: {c['sidebar']};
                border-right: 1px solid {c['border']};
            }}
        """)
        self.role_lbl.setStyleSheet(f"color: {c['primary']}; border: none;")
        self.topbar.apply_style()
        for btn in self.nav_btns.values():
            btn.apply_style()


# ── Quick preview: launch with a demo role ────────────────────────
def _preview(role="Clinician"):
    app = QApplication.instance() or QApplication(sys.argv)
    app.setFont(QFont("Inter", 10))
    win = DashboardWindow(role=role, username="demo.user")
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="MediVision Dashboard Preview")
    parser.add_argument("--role", default="Clinician",
                        choices=["Clinician", "Radiographer", "Lab Technician", "System Admin"])
    parser.add_argument("--user", default="demo.user")
    args = parser.parse_args()
    _preview(role=args.role)
