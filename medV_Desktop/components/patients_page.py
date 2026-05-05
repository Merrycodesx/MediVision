from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QHBoxLayout, QLineEdit, QComboBox, QMessageBox


TEXTS = {
    "English": {
        "title": "Patients",
        "empty": "No patients found.",
        "search": "Search name/age...",
        "refresh": "Refresh",
        "create": "Create Patient",
        "name": "Name",
        "age": "Age",
        "sex": "Sex",
        "hiv": "HIV",
        "view": "Open",
        "headers": ["ID", "Name", "Age", "Sex", "HIV", "Action"],
    },
    "Amharic": {
        "title": "ታካሚዎች",
        "empty": "ምንም ታካሚ አልተገኘም።",
        "search": "በስም/እድሜ ፈልግ...",
        "refresh": "አድስ",
        "create": "ታካሚ ፍጠር",
        "name": "ስም",
        "age": "እድሜ",
        "sex": "ጾታ",
        "hiv": "HIV",
        "view": "ክፈት",
        "headers": ["መለያ", "ስም", "እድሜ", "ጾታ", "HIV", "እርምጃ"],
    },
}


class PatientsPage(QWidget):
    def __init__(self, on_refresh, on_open_patient, on_create_patient):
        super().__init__()
        self.setObjectName("PageCard")
        self.language = "English"
        self.on_refresh = on_refresh
        self.on_open_patient = on_open_patient
        self.on_create_patient = on_create_patient
        self.patients = []
        self.can_create = False

        layout = QVBoxLayout()
        self.title = QLabel()
        self.title.setObjectName("PageTitle")
        layout.addWidget(self.title)

        top_row = QHBoxLayout()
        self.name_input = QLineEdit()
        self.age_input = QLineEdit()
        self.sex_input = QComboBox()
        self.sex_input.addItems(["male", "female"])
        self.hiv_input = QComboBox()
        self.hiv_input.addItems(["negative", "positive"])
        self.create_btn = QPushButton()
        self.create_btn.clicked.connect(self.create_patient)
        top_row.addWidget(self.name_input)
        top_row.addWidget(self.age_input)
        top_row.addWidget(self.sex_input)
        top_row.addWidget(self.hiv_input)
        top_row.addWidget(self.create_btn)
        top_row.addStretch()
        self.refresh_btn = QPushButton()
        self.refresh_btn.clicked.connect(self.on_refresh)
        top_row.addWidget(self.refresh_btn)
        layout.addLayout(top_row)

        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.apply_local_filter)
        layout.addWidget(self.search_input)

        self.empty_label = QLabel()
        layout.addWidget(self.empty_label)

        self.table = QTableWidget(0, 6)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.set_language(self.language)

    def set_language(self, language):
        self.language = language
        texts = TEXTS.get(language, TEXTS["English"])
        self.title.setText(texts["title"])
        self.name_input.setPlaceholderText(texts["name"])
        self.age_input.setPlaceholderText(texts["age"])
        self.search_input.setPlaceholderText(texts["search"])
        self.create_btn.setText(texts["create"])
        self.refresh_btn.setText(texts["refresh"])
        self.create_btn.setVisible(self.can_create)
        self.name_input.setVisible(self.can_create)
        self.age_input.setVisible(self.can_create)
        self.sex_input.setVisible(self.can_create)
        self.hiv_input.setVisible(self.can_create)
        self.refresh_btn.setIcon(self.style().standardIcon(self.style().SP_BrowserReload))
        self.create_btn.setIcon(self.style().standardIcon(self.style().SP_FileDialogNewFolder))
        self.empty_label.setText(texts["empty"])
        self.table.setHorizontalHeaderLabels(texts["headers"])
        self.set_patients(self.patients)

    def set_create_enabled(self, enabled):
        self.can_create = bool(enabled)
        self.set_language(self.language)

    def set_patients(self, patients):
        self.patients = patients if isinstance(patients, list) else []
        self.empty_label.setVisible(len(self.patients) == 0)
        self.table.setRowCount(len(self.patients))
        for i, p in enumerate(self.patients):
            self.table.setItem(i, 0, QTableWidgetItem(str(p.get("id", "-"))))
            self.table.setItem(i, 1, QTableWidgetItem(str(p.get("name", "-"))))
            self.table.setItem(i, 2, QTableWidgetItem(str(p.get("age", "-"))))
            self.table.setItem(i, 3, QTableWidgetItem(str(p.get("sex", "-"))))
            self.table.setItem(i, 4, QTableWidgetItem("Yes" if p.get("hiv_status") else "No"))
            btn = QPushButton(TEXTS.get(self.language, TEXTS["English"])["view"])
            btn.setIcon(self.style().standardIcon(self.style().SP_FileDialogDetailedView))
            btn.clicked.connect(lambda _, pid=p.get("id"): self.on_open_patient(pid))
            self.table.setCellWidget(i, 5, btn)
        self.apply_local_filter(self.search_input.text())

    def apply_local_filter(self, text):
        text = (text or "").strip().lower()
        for i, p in enumerate(self.patients):
            hay = f"{p.get('name', '')} {p.get('age', '')}".lower()
            self.table.setRowHidden(i, bool(text) and text not in hay)

    def create_patient(self):
        name = self.name_input.text().strip()
        age_raw = self.age_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Patient name is required.")
            return
        if not age_raw.isdigit():
            QMessageBox.warning(self, "Error", "Age must be a valid number.")
            return
        payload = {
            "name": name,
            "age": age_raw,
            "sex": self.sex_input.currentText(),
            "hiv_status": self.hiv_input.currentText() == "positive",
            "symptoms": [],
            "comorbidities": [],
        }
        result = self.on_create_patient(payload)
        if result.get("success"):
            self.name_input.clear()
            self.age_input.clear()
            self.on_refresh()
        else:
            msg = result.get("message", "Failed to create patient.")
            if result.get("response_json"):
                msg += f"\nDetails: {result['response_json']}"
            QMessageBox.warning(self, "Error", msg)
