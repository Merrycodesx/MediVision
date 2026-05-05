"""
MediVision – System Admin Dashboard
User management, logs, sync status, backup/restore, configuration.
"""
import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QFrame, QStackedWidget, QSizePolicy, QSpinBox,
                             QDialog, QLineEdit, QComboBox, QFormLayout,
                             QScrollArea, QTextEdit, QGridLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

from dashboard.components import (CardWidget, StatCard, SectionTitle, PrimaryButton,
                                   DangerButton, SuccessButton, DataTable,
                                   SidebarItem, FormInput, FormCombo)


DEMO_USERS = [
    ("U001", "Abebe Kebede",   "Clinician",     "abebe.k",   "🟢 Active",  "2024-01-15 09:22"),
    ("U002", "Tigist Alemu",   "Radiographer",  "tigist.a",  "🟢 Active",  "2024-01-15 08:55"),
    ("U003", "Dawit Haile",    "Lab Technician","dawit.h",   "🔴 Inactive","2024-01-14 17:00"),
    ("U004", "Selamawit Mulu", "Admin",         "selam.m",   "🟢 Active",  "2024-01-15 10:00"),
]

DEMO_LOGS = [
    ("2024-01-15 10:05", "abebe.k",  "Login",          "Success"),
    ("2024-01-15 10:03", "tigist.a", "Upload Image",   "TB-2024-005"),
    ("2024-01-15 09:58", "dawit.h",  "Save Lab Record","LR-005"),
    ("2024-01-15 09:45", "selam.m",  "Add User",       "U005"),
    ("2024-01-15 09:30", "abebe.k",  "Generate Report","TB-2024-001"),
    ("2024-01-15 09:12", "tigist.a", "Logout",         "Success"),
]


# ── Add User Dialog ───────────────────────────────────────────────
class AddUserDialog(QDialog):
    def __init__(self, theme_mgr, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New User")
        self.setMinimumSize(400, 360)
        c = theme_mgr.get_colors()
        self.setStyleSheet(f"background-color: {c['card']}; color: {c['text_primary']};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)

        title = QLabel("Add New User")
        title.setFont(QFont("Outfit", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {c['primary']};")
        layout.addWidget(title)

        fields = [("Full Name", ""), ("Username", ""), ("Email", ""), ("Password", "")]
        self.inputs = {}
        for label, ph in fields:
            inp = FormInput(label, theme_mgr, ph or label)
            layout.addWidget(inp)
            self.inputs[label] = inp

        role_combo = FormCombo("Role",
            ["Clinician", "Radiographer", "Lab Technician", "System Admin"], theme_mgr)
        layout.addWidget(role_combo)

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Add User")
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self.accept)
        for b, color in [(cancel_btn, c["border"]), (save_btn, c["primary"])]:
            b.setStyleSheet(f"""
                QPushButton {{
                    background-color: {'transparent' if b==cancel_btn else c['primary']};
                    color: {c['text_secondary'] if b==cancel_btn else 'white'};
                    border: 1px solid {color};
                    border-radius: 8px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                QPushButton:hover {{ background-color: {c['primary_light'] if b==cancel_btn else c['primary_hover']}; }}
            """)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)


# ── Admin Dashboard ───────────────────────────────────────────────
class AdminDashboard(QWidget):
    def __init__(self, lang_mgr, theme_mgr, parent=None):
        super().__init__(parent)
        self.lang  = lang_mgr
        self.theme = theme_mgr
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sub-Sidebar ──────────────────────────────────────────
        self.sub_sidebar = QWidget()
        self.sub_sidebar.setFixedWidth(220)
        sub_layout = QVBoxLayout(self.sub_sidebar)
        sub_layout.setContentsMargins(12, 24, 12, 24)
        sub_layout.setSpacing(6)

        self.sub_title = QLabel(self.lang.get("admin_title"))
        self.sub_title.setFont(QFont("Outfit", 13, QFont.Weight.Bold))
        self.sub_title.setWordWrap(True)
        sub_layout.addWidget(self.sub_title)
        sub_layout.addSpacing(16)

        nav_items = [
            ("👥", self.lang.get("user_mgmt"),       "users"),
            ("📋", self.lang.get("system_logs"),      "logs"),
            ("🔄", self.lang.get("data_sync"),        "sync"),
            ("💾", self.lang.get("backup_restore"),   "backup"),
            ("⚙️", self.lang.get("configuration"),   "config"),
        ]
        self.nav_buttons = {}
        for icon, label, key in nav_items:
            btn = SidebarItem(icon, label, self.theme)
            btn.clicked.connect(lambda checked, k=key: self._switch_panel(k))
            sub_layout.addWidget(btn)
            self.nav_buttons[key] = btn

        sub_layout.addStretch()
        root.addWidget(self.sub_sidebar)

        # ── Content Stack ────────────────────────────────────────
        self.content_stack = QStackedWidget()

        self.panels = {
            "users":  self._build_users_panel(),
            "logs":   self._build_logs_panel(),
            "sync":   self._build_sync_panel(),
            "backup": self._build_backup_panel(),
            "config": self._build_config_panel(),
        }
        for panel in self.panels.values():
            self.content_stack.addWidget(panel)

        root.addWidget(self.content_stack, 1)
        self._switch_panel("users")
        self.apply_theme()

    # ── Panel Builders ────────────────────────────────────────────

    def _build_users_panel(self):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(24, 16, 24, 16)
        v.setSpacing(16)

        # Stat row
        c = self.theme.get_colors()
        stats_row = QHBoxLayout()
        stats_row.setSpacing(14)
        self.user_stat_cards = [
            StatCard(self.lang.get("total_users"),    "4",  c["primary"], self.theme),
            StatCard(self.lang.get("active_sessions"),"3",  c["success"], self.theme),
        ]
        for sc in self.user_stat_cards:
            sc.setFixedWidth(200)
            stats_row.addWidget(sc)
        stats_row.addStretch()
        v.addLayout(stats_row)

        # Section title
        title_row = QHBoxLayout()
        tbl_title = QLabel(self.lang.get("user_mgmt"))
        tbl_title.setFont(QFont("Outfit", 16, QFont.Weight.Bold))

        self.add_user_btn = PrimaryButton(f"＋  {self.lang.get('add_user')}", self.theme)
        self.add_user_btn.setFixedWidth(160)
        self.add_user_btn.clicked.connect(self._add_user_dialog)

        title_row.addWidget(tbl_title)
        title_row.addStretch()
        title_row.addWidget(self.add_user_btn)
        v.addLayout(title_row)

        # User table card
        tbl_card = CardWidget(self.theme)
        tbl_v = QVBoxLayout(tbl_card)
        tbl_v.setContentsMargins(16, 16, 16, 16)

        self.user_table = DataTable(
            ["ID", self.lang.get("name"), self.lang.get("role"),
             self.lang.get("username"), self.lang.get("status"), self.lang.get("last_active")],
            self.theme
        )
        for row in DEMO_USERS:
            self.user_table.add_row(list(row))

        tbl_v.addWidget(self.user_table)
        v.addWidget(tbl_card)

        # Action buttons
        action_row = QHBoxLayout()
        self.edit_user_btn   = PrimaryButton(f"✏  {self.lang.get('edit')}",    self.theme)
        self.remove_user_btn = DangerButton(f"🗑  {self.lang.get('delete')}", self.theme)
        self.assign_role_btn = SuccessButton(f"🏷  {self.lang.get('assign_role')}", self.theme)
        for b in [self.edit_user_btn, self.remove_user_btn, self.assign_role_btn]:
            b.setFixedWidth(160)
            action_row.addWidget(b)
        action_row.addStretch()
        v.addLayout(action_row)
        return page

    def _build_logs_panel(self):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(24, 16, 24, 16)
        v.setSpacing(16)

        tbl_title = QLabel(self.lang.get("system_logs"))
        tbl_title.setFont(QFont("Outfit", 16, QFont.Weight.Bold))
        v.addWidget(tbl_title)

        tbl_card = CardWidget(self.theme)
        tbl_v = QVBoxLayout(tbl_card)
        tbl_v.setContentsMargins(16, 16, 16, 16)

        self.log_table = DataTable(
            [self.lang.get("log_time"), self.lang.get("log_user"),
             self.lang.get("log_event"), self.lang.get("status")],
            self.theme
        )
        for row in DEMO_LOGS:
            self.log_table.add_row(list(row))

        tbl_v.addWidget(self.log_table)

        refresh_btn = PrimaryButton(f"🔄  {self.lang.get('refresh')}", self.theme)
        refresh_btn.setFixedWidth(160)
        refresh_btn.clicked.connect(lambda: self._add_live_log())

        v.addWidget(tbl_card)
        v.addWidget(refresh_btn)
        return page

    def _build_sync_panel(self):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(24, 16, 24, 16)
        v.setSpacing(16)

        tbl_title = QLabel(self.lang.get("data_sync"))
        tbl_title.setFont(QFont("Outfit", 16, QFont.Weight.Bold))
        v.addWidget(tbl_title)

        c = self.theme.get_colors()
        # Sync status card
        sync_card = CardWidget(self.theme)
        sync_v = QVBoxLayout(sync_card)
        sync_v.setContentsMargins(24, 24, 24, 24)
        sync_v.setSpacing(14)

        status_row = QHBoxLayout()
        status_dot = QLabel("●")
        status_dot.setFont(QFont("Inter", 18))
        status_dot.setStyleSheet(f"color: {c['success']}; border: none;")
        status_lbl = QLabel("System is Online — Central Server Connected")
        status_lbl.setFont(QFont("Inter", 13))

        status_row.addWidget(status_dot)
        status_row.addWidget(status_lbl)
        status_row.addStretch()
        sync_v.addLayout(status_row)

        grid = QGridLayout()
        grid.setSpacing(12)
        fields = [
            ("Last Sync",          "2024-01-15  10:02:47"),
            ("Records Synced",     "1,284 records"),
            ("Pending Upload",     "3 files"),
            ("Server",             "moh-tb-central.eth"),
        ]
        for i, (lbl, val) in enumerate(fields):
            l = QLabel(lbl + ":")
            l.setFont(QFont("Inter", 11))
            l.setStyleSheet(f"color: {c['text_secondary']}; border: none;")
            r = QLabel(val)
            r.setFont(QFont("Inter", 11, QFont.Weight.Bold))
            r.setStyleSheet(f"color: {c['text_primary']}; border: none;")
            grid.addWidget(l, i, 0)
            grid.addWidget(r, i, 1)
        sync_v.addLayout(grid)

        self.sync_progress = __import__('PyQt6.QtWidgets', fromlist=['QProgressBar']).QProgressBar()
        self.sync_progress.setRange(0, 100)
        self.sync_progress.setValue(0)
        self.sync_progress.setTextVisible(True)
        self.sync_progress.setFixedHeight(12)
        self.sync_progress.setVisible(False)

        self.sync_btn = PrimaryButton(f"🔄  {self.lang.get('sync_now')}", self.theme)
        self.sync_btn.setFixedWidth(200)
        self.sync_btn.clicked.connect(self._simulate_sync)

        sync_v.addWidget(self.sync_progress)
        sync_v.addWidget(self.sync_btn)
        v.addWidget(sync_card)
        v.addStretch()
        return page

    def _build_backup_panel(self):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(24, 16, 24, 16)
        v.setSpacing(16)

        tbl_title = QLabel(self.lang.get("backup_restore"))
        tbl_title.setFont(QFont("Outfit", 16, QFont.Weight.Bold))
        v.addWidget(tbl_title)

        c = self.theme.get_colors()

        # Backup card
        bk_card = CardWidget(self.theme)
        bk_v = QVBoxLayout(bk_card)
        bk_v.setContentsMargins(24, 24, 24, 24)
        bk_v.setSpacing(16)

        bk_title = QLabel("Database Backup")
        bk_title.setFont(QFont("Inter", 13, QFont.Weight.Bold))
        bk_title.setStyleSheet(f"color: {c['text_primary']}; border: none;")

        info_grid = QGridLayout()
        info_rows = [
            ("Last Backup:",    "2024-01-14  23:00:00"),
            ("Backup Size:",    "142 MB"),
            ("Location:",       "/opt/medivision/backups/"),
        ]
        for i, (lbl, val) in enumerate(info_rows):
            l = QLabel(lbl)
            l.setFont(QFont("Inter", 11))
            l.setStyleSheet(f"color: {c['text_secondary']}; border: none;")
            r = QLabel(val)
            r.setFont(QFont("Inter", 11, QFont.Weight.Bold))
            r.setStyleSheet(f"color: {c['text_primary']}; border: none;")
            info_grid.addWidget(l, i, 0)
            info_grid.addWidget(r, i, 1)

        btn_row = QHBoxLayout()
        backup_btn  = SuccessButton(f"💾  {self.lang.get('backup_now')}", self.theme)
        restore_btn = DangerButton(f"♻  {self.lang.get('restore')}",    self.theme)
        backup_btn.setFixedWidth(200)
        restore_btn.setFixedWidth(200)
        backup_btn.clicked.connect(lambda: self._sim_action(backup_btn, "Backup complete!"))
        restore_btn.clicked.connect(lambda: self._sim_action(restore_btn, "Restore complete!"))
        btn_row.addWidget(backup_btn)
        btn_row.addWidget(restore_btn)
        btn_row.addStretch()

        self.backup_db_size = QLabel(f"  {self.lang.get('db_size')}: 284 MB   |   {self.lang.get('uptime')}: 14d 6h 32m")
        self.backup_db_size.setFont(QFont("Inter", 10))
        self.backup_db_size.setStyleSheet(f"color: {c['text_muted']}; border: none;")

        bk_v.addWidget(bk_title)
        bk_v.addLayout(info_grid)
        bk_v.addLayout(btn_row)
        bk_v.addWidget(self.backup_db_size)
        v.addWidget(bk_card)
        v.addStretch()
        return page

    def _build_config_panel(self):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(24, 16, 24, 16)
        v.setSpacing(16)

        cfg_title = QLabel(self.lang.get("configuration"))
        cfg_title.setFont(QFont("Outfit", 16, QFont.Weight.Bold))
        v.addWidget(cfg_title)

        cfg_card = CardWidget(self.theme)
        cfg_v = QVBoxLayout(cfg_card)
        cfg_v.setContentsMargins(24, 24, 24, 24)
        cfg_v.setSpacing(16)

        c = self.theme.get_colors()

        lang_row = FormCombo(self.lang.get("config_language"), ["English", "Amharic (አማርኛ)"], self.theme)
        theme_row = FormCombo(self.lang.get("config_theme"), ["Light (Medical Blue)", "Dark (Navy)"], self.theme)

        timeout_row = QHBoxLayout()
        timeout_lbl = QLabel(self.lang.get("config_timeout") + ":")
        timeout_lbl.setFont(QFont("Inter", 11))
        timeout_lbl.setStyleSheet(f"color: {c['text_secondary']}; border: none;")
        timeout_spin = QSpinBox()
        timeout_spin.setRange(5, 120)
        timeout_spin.setValue(30)
        timeout_spin.setMinimumHeight(40)
        timeout_spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {c['input_bg']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                padding: 0 8px;
                font-size: 13px;
            }}
        """)
        timeout_row.addWidget(timeout_lbl)
        timeout_row.addWidget(timeout_spin)
        timeout_row.addStretch()

        self.cfg_save_btn = PrimaryButton(f"✔  {self.lang.get('config_save')}", self.theme)
        self.cfg_save_btn.setFixedWidth(240)
        self.cfg_save_btn.clicked.connect(lambda: self._sim_action(self.cfg_save_btn, "Configuration saved!"))

        cfg_v.addWidget(lang_row)
        cfg_v.addWidget(theme_row)
        cfg_v.addLayout(timeout_row)
        cfg_v.addSpacing(20)
        cfg_v.addWidget(self.cfg_save_btn)
        cfg_v.addStretch()
        v.addWidget(cfg_card)
        v.addStretch()
        return page

    # ── Helpers ───────────────────────────────────────────────────
    def _switch_panel(self, key):
        for k, btn in self.nav_buttons.items():
            btn.set_active(k == key)
        self.content_stack.setCurrentWidget(self.panels[key])

    def _add_user_dialog(self):
        dlg = AddUserDialog(self.theme, self)
        if dlg.exec():
            n = self.user_table.rowCount() + 1
            uid = f"U{n:03d}"
            name = dlg.inputs["Full Name"].text() or "New User"
            self.user_table.add_row([uid, name, "Clinician", name.replace(" ", ".").lower(), "🟢 Active", "Just now"])

    def _add_live_log(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_table.add_row([now, "selam.m", "Manual Refresh", "Success"])

    def _simulate_sync(self):
        self.sync_progress.setVisible(True)
        self.sync_progress.setValue(0)
        self._sync_val = 0
        timer = QTimer(self)
        timer.timeout.connect(lambda: self._tick_sync(timer))
        timer.start(50)

    def _tick_sync(self, timer):
        self._sync_val += 5
        self.sync_progress.setValue(min(self._sync_val, 100))
        if self._sync_val >= 100:
            timer.stop()
            self.sync_btn.setText("✓  Sync Complete!")
            QTimer.singleShot(2000, lambda: self.sync_btn.setText(f"🔄  {self.lang.get('sync_now')}"))

    def _sim_action(self, btn, done_text):
        orig = btn.text()
        btn.setText(f"✓  {done_text}")
        QTimer.singleShot(2500, lambda: btn.setText(orig))

    def apply_theme(self):
        c = self.theme.get_colors()
        self.setStyleSheet(f"background-color: {c['bg']};")
        self.sub_sidebar.setStyleSheet(f"""
            QWidget {{
                background-color: {c['sidebar']};
                border-right: 1px solid {c['border']};
            }}
        """)
        self.sub_title.setStyleSheet(f"color: {c['primary']}; border: none;")
        for btn in self.nav_buttons.values():
            btn.apply_style()
        if hasattr(self, 'add_user_btn'):
            self.add_user_btn.apply_style()
        if hasattr(self, 'user_table'):
            self.user_table.apply_style()
        if hasattr(self, 'log_table'):
            self.log_table.apply_style()
        if hasattr(self, 'sync_btn'):
            self.sync_btn.apply_style()
        if hasattr(self, 'cfg_save_btn'):
            self.cfg_save_btn.apply_style()
        if hasattr(self, 'user_stat_cards'):
            for sc in self.user_stat_cards:
                sc.apply_style()

    def retranslate(self):
        self.sub_title.setText(self.lang.get("admin_title"))
