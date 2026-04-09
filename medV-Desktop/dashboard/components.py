"""
MediVision – Shared UI Components
Reusable widgets used across all dashboards.
"""
from PyQt6.QtWidgets import (QWidget, QFrame, QLabel, QPushButton, QHBoxLayout,
                             QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView,
                             QComboBox, QSizePolicy, QGraphicsDropShadowEffect,
                             QAbstractItemView, QSpacerItem, QLineEdit)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QBrush, QCursor, QIcon


# ─────────────────────────── CardWidget ────────────────────────────
class CardWidget(QFrame):
    """Base card with rounded corners and soft shadow."""
    def __init__(self, theme_mgr, parent=None):
        super().__init__(parent)
        self.theme_mgr = theme_mgr
        self.setObjectName("CardWidget")
        self._add_shadow()
        self.apply_style()

    def _add_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 25))
        self.setGraphicsEffect(shadow)

    def apply_style(self):
        c = self.theme_mgr.get_colors()
        self.setStyleSheet(f"""
            QFrame#CardWidget {{
                background-color: {c['card']};
                border: 1px solid {c['border']};
                border-radius: 14px;
            }}
        """)


# ─────────────────────────── StatCard ──────────────────────────────
class StatCard(QFrame):
    """Dashboard KPI summary card."""
    def __init__(self, title, value, accent, theme_mgr, parent=None):
        super().__init__(parent)
        self.theme_mgr = theme_mgr
        self.accent = accent
        self.setObjectName("StatCard")
        self.setFixedHeight(110)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)

        self.title_lbl = QLabel(title)
        self.title_lbl.setFont(QFont("Inter", 10))

        self.value_lbl = QLabel(str(value))
        self.value_lbl.setFont(QFont("Outfit", 26, QFont.Weight.Bold))

        self.bar = QFrame()
        self.bar.setFixedHeight(3)
        self.bar.setStyleSheet(f"background-color: {accent}; border-radius: 2px;")

        layout.addWidget(self.bar)
        layout.addWidget(self.title_lbl)
        layout.addWidget(self.value_lbl)
        self.apply_style()

    def apply_style(self):
        c = self.theme_mgr.get_colors()
        self.setStyleSheet(f"""
            QFrame#StatCard {{
                background-color: {c['card']};
                border: 1px solid {c['border']};
                border-radius: 14px;
            }}
        """)
        self.title_lbl.setStyleSheet(f"color: {c['text_secondary']};")
        self.value_lbl.setStyleSheet(f"color: {c['text_primary']};")

    def update_value(self, value):
        self.value_lbl.setText(str(value))


# ─────────────────────────── RiskBadge ─────────────────────────────
class RiskBadge(QLabel):
    """Colored risk level badge."""
    COLORS = {
        "High":   ("#EF4444", "#FEE2E2"),
        "Medium": ("#F59E0B", "#FEF3C7"),
        "Low":    ("#22C55E", "#DCFCE7"),
    }

    def __init__(self, level="Low", parent=None):
        super().__init__(parent)
        self.set_level(level)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(28)
        self.setFont(QFont("Inter", 10, QFont.Weight.Bold))

    def set_level(self, level):
        self.setText(level)
        fg, bg = self.COLORS.get(level, ("#6B7280", "#F3F4F6"))
        self.setStyleSheet(f"""
            QLabel {{
                color: {fg};
                background-color: {bg};
                border-radius: 6px;
                padding: 2px 14px;
            }}
        """)


# ─────────────────────────── DataTable ─────────────────────────────
class DataTable(QTableWidget):
    """Styled table widget for records."""
    def __init__(self, headers, theme_mgr, parent=None):
        super().__init__(parent)
        self.theme_mgr = theme_mgr
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.setShowGrid(False)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.apply_style()

    def apply_style(self):
        c = self.theme_mgr.get_colors()
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {c['card']};
                color: {c['text_primary']};
                border: none;
                font-family: Inter;
                font-size: 13px;
                gridline-color: transparent;
                alternate-background-color: {c['table_row_alt']};
            }}
            QHeaderView::section {{
                background-color: {c['table_header']};
                color: {c['text_secondary']};
                font-weight: bold;
                font-size: 12px;
                border: none;
                padding: 10px 6px;
            }}
            QTableWidget::item {{
                padding: 10px 8px;
            }}
            QTableWidget::item:selected {{
                background-color: {c['primary_light']};
                color: {c['primary']};
            }}
        """)

    def add_row(self, values):
        row = self.rowCount()
        self.insertRow(row)
        for col, val in enumerate(values):
            if isinstance(val, QWidget):
                self.setCellWidget(row, col, val)
            else:
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.setItem(row, col, item)
        self.setRowHeight(row, 48)


# ─────────────────────────── ProgressRing ──────────────────────────
class ProgressRing(QWidget):
    """Circular progress ring for displaying TB score."""
    def __init__(self, score=0, size=160, parent=None):
        super().__init__(parent)
        self.score = score
        self.ring_size = size
        self.setFixedSize(size, size)

    def set_score(self, score):
        self.score = max(0, min(100, score))
        self.update()

    def _get_color(self):
        if self.score >= 70:
            return "#EF4444"
        elif self.score >= 40:
            return "#F59E0B"
        return "#22C55E"

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx, cy = self.ring_size / 2, self.ring_size / 2
        r = self.ring_size / 2 - 16

        # Background ring
        pen = QPen(QColor("#E5E7EB"), 10)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(int(cx - r), int(cy - r), int(2 * r), int(2 * r), 0, 360 * 16)

        # Score arc
        span = int((self.score / 100) * 360 * 16)
        pen.setColor(QColor(self._get_color()))
        painter.setPen(pen)
        painter.drawArc(int(cx - r), int(cy - r), int(2 * r), int(2 * r), 90 * 16, -span)

        # Score text
        painter.setPen(QColor(self._get_color()))
        font = QFont("Outfit", int(self.ring_size * 0.18), QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, str(self.score))


# ─────────────────────────── PrimaryButton ─────────────────────────
class PrimaryButton(QPushButton):
    def __init__(self, text, theme_mgr, parent=None):
        super().__init__(text, parent)
        self.theme_mgr = theme_mgr
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(42)
        self.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        self.apply_style()

    def apply_style(self):
        c = self.theme_mgr.get_colors()
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0 20px;
            }}
            QPushButton:hover {{ background-color: {c['primary_hover']}; }}
            QPushButton:pressed {{ background-color: {c['primary']}; }}
        """)


class DangerButton(QPushButton):
    def __init__(self, text, theme_mgr, parent=None):
        super().__init__(text, parent)
        self.theme_mgr = theme_mgr
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(42)
        self.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        self.apply_style()

    def apply_style(self):
        c = self.theme_mgr.get_colors()
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['danger_bg']};
                color: {c['danger']};
                border: 1px solid {c['danger']};
                border-radius: 8px;
                padding: 0 20px;
            }}
            QPushButton:hover {{ background-color: {c['danger']}; color: white; }}
        """)


class SuccessButton(QPushButton):
    def __init__(self, text, theme_mgr, parent=None):
        super().__init__(text, parent)
        self.theme_mgr = theme_mgr
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(42)
        self.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        self.apply_style()

    def apply_style(self):
        c = self.theme_mgr.get_colors()
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['success_bg']};
                color: {c['success']};
                border: 1px solid {c['success']};
                border-radius: 8px;
                padding: 0 20px;
            }}
            QPushButton:hover {{ background-color: {c['success']}; color: white; }}
        """)


# ─────────────────────────── SidebarItem ───────────────────────────
class SidebarItem(QPushButton):
    """Navigation item for the sidebar."""
    def __init__(self, icon_text, label, theme_mgr, parent=None):
        super().__init__(parent)
        self.theme_mgr = theme_mgr
        self.icon_text = icon_text
        self.label_text = label
        self.is_active = False
        self.setText(f"  {icon_text}  {label}")
        self.setFont(QFont("Inter", 12))
        self.setFixedHeight(48)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setCheckable(False)
        self.apply_style()

    def set_active(self, active):
        self.is_active = active
        self.apply_style()

    def apply_style(self):
        c = self.theme_mgr.get_colors()
        if self.is_active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {c['sidebar_active']};
                    color: {c['primary']};
                    border: none;
                    border-left: 3px solid {c['primary']};
                    border-radius: 8px;
                    text-align: left;
                    padding-left: 16px;
                    font-weight: bold;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {c['text_secondary']};
                    border: none;
                    border-radius: 8px;
                    text-align: left;
                    padding-left: 19px;
                }}
                QPushButton:hover {{
                    background-color: {c['sidebar_hover']};
                    color: {c['text_primary']};
                }}
            """)


# ─────────────────────────── TopBar ────────────────────────────────
class TopBar(QWidget):
    """Top navigation bar with user info, theme toggle, lang switch."""
    theme_toggled = pyqtSignal()
    language_changed = pyqtSignal(str)
    logout_requested = pyqtSignal()

    def __init__(self, username, role, lang_mgr, theme_mgr, parent=None):
        super().__init__(parent)
        self.lang_mgr = lang_mgr
        self.theme_mgr = theme_mgr
        self.username = username
        self.role = role
        self.setFixedHeight(64)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)

        # Brand
        self.brand = QLabel("⚕  MediVision")
        self.brand.setFont(QFont("Outfit", 16, QFont.Weight.Bold))

        layout.addWidget(self.brand)
        layout.addStretch()

        # Offline badge
        self.status_lbl = QLabel("● Offline Mode Ready")
        self.status_lbl.setFont(QFont("Inter", 10))

        # Language Switch
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "አማርኛ"])
        self.lang_combo.setFixedWidth(120)
        self.lang_combo.currentIndexChanged.connect(
            lambda i: self.language_changed.emit("en" if i == 0 else "am")
        )

        # Theme Toggle
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setFixedSize(38, 38)
        self.theme_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.theme_btn.clicked.connect(self._toggle_theme)

        # User info
        self.user_lbl = QLabel(f"👤  {username}  ·  {role}")
        self.user_lbl.setFont(QFont("Inter", 11))

        # Logout
        self.logout_btn = QPushButton("⏻  Logout")
        self.logout_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.logout_btn.setFixedHeight(36)
        self.logout_btn.clicked.connect(self.logout_requested.emit)

        layout.addWidget(self.status_lbl)
        layout.addSpacing(20)
        layout.addWidget(self.lang_combo)
        layout.addSpacing(8)
        layout.addWidget(self.theme_btn)
        layout.addSpacing(16)
        layout.addWidget(self.user_lbl)
        layout.addSpacing(16)
        layout.addWidget(self.logout_btn)

        self.apply_style()

    def _toggle_theme(self):
        self.theme_mgr.toggle()
        self.theme_btn.setText("☀️" if self.theme_mgr.is_dark else "🌙")
        self.theme_toggled.emit()
        self.apply_style()

    def apply_style(self):
        c = self.theme_mgr.get_colors()
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {c['topbar']};
                border-bottom: 1px solid {c['border']};
            }}
        """)
        self.brand.setStyleSheet(f"color: {c['primary']}; border: none;")
        self.status_lbl.setStyleSheet(f"color: {c['success']}; border: none;")
        self.user_lbl.setStyleSheet(f"color: {c['text_primary']}; border: none;")
        self.lang_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {c['input_bg']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 4px 8px;
                font-family: Inter;
                font-size: 11px;
            }}
            QComboBox::drop-down {{ border: none; }}
        """)
        self.theme_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['input_bg']};
                border: 1px solid {c['border']};
                border-radius: 19px;
                font-size: 15px;
            }}
            QPushButton:hover {{ background-color: {c['primary_light']}; }}
        """)
        self.logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['danger_bg']};
                color: {c['danger']};
                border: 1px solid {c['danger']};
                border-radius: 6px;
                padding: 0 14px;
                font-family: Inter;
                font-size: 11px;
            }}
            QPushButton:hover {{ background-color: {c['danger']}; color: white; }}
        """)


# ─────────────────────────── SectionTitle ──────────────────────────
class SectionTitle(QLabel):
    def __init__(self, text, theme_mgr, size=18, parent=None):
        super().__init__(text, parent)
        self.theme_mgr = theme_mgr
        self.setFont(QFont("Outfit", size, QFont.Weight.Bold))
        self.apply_style()

    def apply_style(self):
        c = self.theme_mgr.get_colors()
        self.setStyleSheet(f"color: {c['text_primary']}; border: none;")


# ─────────────────────────── FormInput ─────────────────────────────
class FormInput(QWidget):
    """Labelled input field widget."""
    def __init__(self, label, theme_mgr, placeholder="", parent=None):
        super().__init__(parent)
        self.theme_mgr = theme_mgr
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.lbl = QLabel(label)
        self.lbl.setFont(QFont("Inter", 10, QFont.Weight.Bold))

        self.field = QLineEdit()
        self.field.setPlaceholderText(placeholder)
        self.field.setMinimumHeight(40)

        layout.addWidget(self.lbl)
        layout.addWidget(self.field)
        self.apply_style()

    def apply_style(self):
        c = self.theme_mgr.get_colors()
        self.lbl.setStyleSheet(f"color: {c['text_secondary']}; border: none;")
        self.field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {c['input_bg']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                padding: 0 12px;
                font-family: Inter;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {c['primary']};
            }}
        """)

    def text(self):
        return self.field.text()


# ─────────────────────────── FormCombo ─────────────────────────────
class FormCombo(QWidget):
    """Labelled combo box widget."""
    def __init__(self, label, items, theme_mgr, parent=None):
        super().__init__(parent)
        self.theme_mgr = theme_mgr
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.lbl = QLabel(label)
        self.lbl.setFont(QFont("Inter", 10, QFont.Weight.Bold))

        self.combo = QComboBox()
        self.combo.addItems(items)
        self.combo.setMinimumHeight(40)

        layout.addWidget(self.lbl)
        layout.addWidget(self.combo)
        self.apply_style()

    def apply_style(self):
        c = self.theme_mgr.get_colors()
        self.lbl.setStyleSheet(f"color: {c['text_secondary']}; border: none;")
        self.combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {c['input_bg']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                padding: 0 12px;
                font-family: Inter;
                font-size: 13px;
            }}
            QComboBox::drop-down {{ border: none; width: 24px; }}
            QComboBox QAbstractItemView {{
                background-color: {c['card']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                selection-background-color: {c['primary_light']};
            }}
        """)

    def current_text(self):
        return self.combo.currentText()
