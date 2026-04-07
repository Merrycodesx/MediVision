from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout


TEXTS = {
    "English": {
        "title": "Patient Detail",
        "back": "Back",
        "empty": "No patient data loaded.",
        "name": "Name",
        "age": "Age",
        "sex": "Sex",
        "hiv": "HIV Status",
        "symptoms": "Symptoms",
    },
    "Amharic": {
        "title": "የታካሚ ዝርዝር",
        "back": "ተመለስ",
        "empty": "የታካሚ መረጃ አልተጫነም።",
        "name": "ስም",
        "age": "እድሜ",
        "sex": "ጾታ",
        "hiv": "HIV ሁኔታ",
        "symptoms": "ምልክቶች",
    },
}


class PatientDetailPage(QWidget):
    def __init__(self, on_back):
        super().__init__()
        self.setObjectName("PageCard")
        self.language = "English"
        self.patient = {}

        layout = QVBoxLayout()
        top = QHBoxLayout()
        self.back_btn = QPushButton()
        self.back_btn.clicked.connect(on_back)
        self.title = QLabel()
        self.title.setObjectName("PageTitle")
        top.addWidget(self.back_btn)
        top.addWidget(self.title)
        top.addStretch()
        layout.addLayout(top)

        self.empty = QLabel()
        layout.addWidget(self.empty)

        self.name = QLabel()
        self.age = QLabel()
        self.sex = QLabel()
        self.hiv = QLabel()
        self.symptoms = QLabel()
        layout.addWidget(self.name)
        layout.addWidget(self.age)
        layout.addWidget(self.sex)
        layout.addWidget(self.hiv)
        layout.addWidget(self.symptoms)
        layout.addStretch()

        self.setLayout(layout)
        self.set_language(self.language)

    def set_language(self, language):
        self.language = language
        t = TEXTS.get(language, TEXTS["English"])
        self.title.setText(t["title"])
        self.back_btn.setText(t["back"])
        self.back_btn.setIcon(self.style().standardIcon(self.style().SP_ArrowBack))
        self.empty.setText(t["empty"])
        self._render()

    def set_patient(self, patient):
        self.patient = patient if isinstance(patient, dict) else {}
        self._render()

    def _render(self):
        t = TEXTS.get(self.language, TEXTS["English"])
        has_data = bool(self.patient)
        self.empty.setVisible(not has_data)
        self.name.setText(f"{t['name']}: {self.patient.get('name', '-')}")
        self.age.setText(f"{t['age']}: {self.patient.get('age', '-')}")
        self.sex.setText(f"{t['sex']}: {self.patient.get('sex', '-')}")
        self.hiv.setText(f"{t['hiv']}: {'Yes' if self.patient.get('hiv_status') else 'No'}")
        symptoms = self.patient.get('symptoms', [])
        self.symptoms.setText(f"{t['symptoms']}: {', '.join(symptoms) if symptoms else '-'}")
