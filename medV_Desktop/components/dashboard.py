from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QHBoxLayout
from PyQt5.QtGui import QColor


TEXTS = {
    "English": {
        "title": "Recent Cases",
        "empty": "No cases found or error loading cases.",
        "view": "View",
        "new_case": "Open AI Inference",
        "headers": ["Case ID", "Date", "TB Score", "Risk", "Action"],
    },
    "Amharic": {
        "title": "የቅርብ ኬሶች",
        "empty": "ኬስ አልተገኘም ወይም ስህተት አለ።",
        "view": "ክፈት",
        "new_case": "AI ትንተና ክፈት",
        "headers": ["መለያ", "ቀን", "TB ነጥብ", "አደጋ", "እርምጃ"],
    },
}


class DashboardPage(QWidget):
    def __init__(self, cases, on_view_case, on_new_case=None):
        super().__init__()
        self.setObjectName("PageCard")
        self.language = "English"
        self._on_view_case = on_view_case
        self._on_new_case = on_new_case
        self._cases = cases if isinstance(cases, list) else []
        layout = QVBoxLayout()
        self.title = QLabel()
        self.title.setObjectName("PageTitle")
        layout.addWidget(self.title)

        action_row = QHBoxLayout()
        action_row.addStretch()
        self.new_case_btn = QPushButton()
        self.new_case_btn.clicked.connect(lambda: self._on_new_case() if self._on_new_case else None)
        action_row.addWidget(self.new_case_btn)
        layout.addLayout(action_row)

        self.empty_label = QLabel()
        layout.addWidget(self.empty_label)

        self.table = QTableWidget(0, 5)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.set_cases(self._cases)
        self.set_language(self.language)

    def set_language(self, language):
        self.language = language
        texts = TEXTS.get(language, TEXTS["English"])
        self.title.setText(texts["title"])
        self.empty_label.setText(texts["empty"])
        self.new_case_btn.setText(texts["new_case"])
        self.table.setHorizontalHeaderLabels(texts["headers"])
        self.set_cases(self._cases)

    def set_cases(self, cases):
        self._cases = cases if isinstance(cases, list) else []
        self.table.setRowCount(len(self._cases))
        self.empty_label.setVisible(len(self._cases) == 0)
        for i, case in enumerate(self._cases):
            self.table.setItem(i, 0, QTableWidgetItem(str(case.get("id", "-"))))
            self.table.setItem(i, 1, QTableWidgetItem(str(case.get("date", "-"))))
            self.table.setItem(i, 2, QTableWidgetItem(str(case.get("score", "-"))))
            self.table.setItem(i, 3, QTableWidgetItem(str(case.get("risk", "-"))))
            btn = QPushButton(TEXTS.get(self.language, TEXTS["English"])["view"])
            btn.setIcon(self.style().standardIcon(self.style().SP_FileDialogDetailedView))
            btn.clicked.connect(lambda _, cid=case.get("id", ""): self._on_view_case(cid))
            self.table.setCellWidget(i, 4, btn)
            if i % 2 == 0:
                for col in range(5):
                    item = self.table.item(i, col)
                    if item:
                        item.setBackground(QColor(246, 249, 252))
