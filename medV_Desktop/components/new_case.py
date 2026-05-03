from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QComboBox, QCheckBox, QMessageBox, QHBoxLayout


TEXTS = {
	"English": {
		"title": "AI Inference - New Case",
		"patient_label": "Patient",
		"xray_label": "Chest X-Ray",
		"age_label": "Age",
		"sex_label": "Sex",
		"hiv_label": "HIV Status",
		"unknown": "Unknown / N/A",
		"genexpert_label": "GeneXpert Result",
		"sputum_label": "Sputum Grade",
		"select_xray": "Select X-Ray Image",
		"clinical": "Clinical Data",
		"symptoms": "Symptoms",
		"lab": "Laboratory Data",
		"run": "Run Analysis",
		"back": "Back",
		"error_title": "Error",
		"error_xray": "Please select an X-ray image.",
		"failed_title": "Analysis Failed",
		"select_patient": "Please select a patient.",
		"no_patients": "No patients available",
	},
	"Amharic": {
		"title": "AI ትንተና - አዲስ ኬስ",
		"patient_label": "ታካሚ",
		"xray_label": "የደረት ኤክስሬይ",
		"age_label": "እድሜ",
		"sex_label": "ጾታ",
		"hiv_label": "HIV ሁኔታ",
		"unknown": "ያልታወቀ / N/A",
		"genexpert_label": "GeneXpert ውጤት",
		"sputum_label": "የአክታ ደረጃ",
		"select_xray": "የኤክስሬይ ምስል ምረጥ",
		"clinical": "የክሊኒካል መረጃ",
		"symptoms": "ምልክቶች",
		"lab": "የላብ መረጃ",
		"run": "ትንተና አስኪድ",
		"back": "ተመለስ",
		"error_title": "ስህተት",
		"error_xray": "እባክዎ የኤክስሬይ ምስል ይምረጡ።",
		"failed_title": "ትንተና አልተሳካም",
		"select_patient": "እባክዎ ታካሚ ይምረጡ።",
		"no_patients": "ታካሚ አልተገኘም",
	},
}

class NewCasePage(QWidget):
	def __init__(self, on_submit, on_back=None):
		super().__init__()
		self.setObjectName("PageCard")
		self.language = "English"
		self.on_submit = on_submit
		self.on_back = on_back

		layout = QVBoxLayout()
		top_row = QHBoxLayout()
		self.back_btn = QPushButton()
		self.back_btn.clicked.connect(lambda: self.on_back() if self.on_back else None)
		self.title = QLabel()
		self.title.setObjectName("PageTitle")
		top_row.addWidget(self.back_btn)
		top_row.addWidget(self.title)
		top_row.addStretch()
		layout.addLayout(top_row)

		self.upload_btn = QPushButton()
		self.upload_btn.clicked.connect(self.select_file)
		self.patient_field_label = QLabel()
		self.patient_combo = QComboBox()
		layout.addWidget(self.patient_field_label)
		layout.addWidget(self.patient_combo)
		self.xray_field_label = QLabel()
		self.file_path = QLineEdit()
		self.file_path.setReadOnly(True)
		file_row = QHBoxLayout()
		file_row.addWidget(self.xray_field_label)
		file_row.addWidget(self.upload_btn)
		file_row.addWidget(self.file_path)
		layout.addLayout(file_row)

		self.clinical_label = QLabel()
		layout.addWidget(self.clinical_label)
		self.age = QLineEdit()
		self.age.setPlaceholderText("Age")
		self.age_field_label = QLabel()
		self.sex = QComboBox()
		self.sex.addItems(["Male", "Female"])
		self.sex_field_label = QLabel()
		self.hiv = QComboBox()
		self.hiv.addItems(["Unknown / N/A", "Positive", "Negative"])
		self.hiv_field_label = QLabel()
		layout.addWidget(self.age_field_label)
		layout.addWidget(self.age)
		layout.addWidget(self.sex_field_label)
		layout.addWidget(self.sex)
		layout.addWidget(self.hiv_field_label)
		layout.addWidget(self.hiv)

		self.symptom_label = QLabel()
		layout.addWidget(self.symptom_label)
		self.symptoms = []
		sym_row = QHBoxLayout()
		for s in ["Cough >2 weeks", "Fever", "Weight Loss", "Night Sweats"]:
			cb = QCheckBox(s)
			sym_row.addWidget(cb)
			self.symptoms.append(cb)
		layout.addLayout(sym_row)

		self.lab_label = QLabel()
		layout.addWidget(self.lab_label)
		self.genexpert = QComboBox()
		self.genexpert.addItems(["Unknown / N/A", "Positive", "Negative"])
		self.genexpert_field_label = QLabel()
		self.sputum = QComboBox()
		self.sputum.addItems(["Unknown / N/A", "1+", "2+", "3+"])
		self.sputum_field_label = QLabel()
		layout.addWidget(self.genexpert_field_label)
		lab_row = QHBoxLayout()
		lab_row.addWidget(self.genexpert)
		layout.addWidget(self.sputum_field_label)
		lab_row.addWidget(self.sputum)
		layout.addLayout(lab_row)

		self.submit_btn = QPushButton()
		self.submit_btn.clicked.connect(self.submit)
		layout.addWidget(self.submit_btn)
		layout.addStretch()
		self.setLayout(layout)
		self.set_language(self.language)

	def set_language(self, language):
		self.language = language
		texts = TEXTS.get(language, TEXTS["English"])
		self.title.setText(texts["title"])
		self.patient_field_label.setText(texts["patient_label"])
		self.xray_field_label.setText(texts["xray_label"])
		self.upload_btn.setText(texts["select_xray"])
		self.clinical_label.setText(texts["clinical"])
		self.age_field_label.setText(texts["age_label"])
		self.sex_field_label.setText(texts["sex_label"])
		self.hiv_field_label.setText(texts["hiv_label"])
		self.symptom_label.setText(texts["symptoms"])
		self.lab_label.setText(texts["lab"])
		self.genexpert_field_label.setText(texts["genexpert_label"])
		self.sputum_field_label.setText(texts["sputum_label"])
		self.hiv.setItemText(0, texts["unknown"])
		self.genexpert.setItemText(0, texts["unknown"])
		self.sputum.setItemText(0, texts["unknown"])
		self.submit_btn.setText(texts["run"])
		self.back_btn.setText(texts["back"])
		self.back_btn.setIcon(self.style().standardIcon(self.style().SP_ArrowBack))
		self.upload_btn.setIcon(self.style().standardIcon(self.style().SP_DialogOpenButton))
		self.submit_btn.setIcon(self.style().standardIcon(self.style().SP_MediaPlay))

	def select_file(self):
		fname, _ = QFileDialog.getOpenFileName(self, "Select X-Ray Image", "", "Images (*.png *.jpg *.jpeg)")
		if fname:
			self.file_path.setText(fname)

	def submit(self):
		texts = TEXTS.get(self.language, TEXTS["English"])
		if not self.file_path.text():
			QMessageBox.warning(self, texts["error_title"], texts["error_xray"])
			return
		if self.patient_combo.currentData() is None:
			QMessageBox.warning(self, texts["error_title"], texts["select_patient"])
			return
		case_data = {
			"patient_id": self.patient_combo.currentData(),
			"age": self.age.text().strip() or None,
			"sex": self.sex.currentText(),
			"hiv": None if self.hiv.currentIndex() == 0 else self.hiv.currentText(),
			"symptoms": [cb.text() for cb in self.symptoms if cb.isChecked()],
			"genexpert": None if self.genexpert.currentIndex() == 0 else self.genexpert.currentText(),
			"sputum": None if self.sputum.currentIndex() == 0 else self.sputum.currentText(),
		}
		result = self.on_submit(case_data, self.file_path.text())
		if result and not result.get("success", True):
			msg = result.get("message", "Unknown error")
			if result.get("response"):
				msg += f"\nServer: {result['response']}"
			QMessageBox.warning(self, TEXTS.get(self.language, TEXTS["English"])["failed_title"], msg)
		else:
			self.file_path.clear()
			self.age.clear()
			for cb in self.symptoms:
				cb.setChecked(False)

	def set_patients(self, patients):
		self.patient_combo.clear()
		items = patients if isinstance(patients, list) else []
		if not items:
			self.patient_combo.addItem(TEXTS.get(self.language, TEXTS["English"])["no_patients"], None)
			return
		for patient in items:
			name = patient.get("name", "Unknown")
			pid = patient.get("id")
			self.patient_combo.addItem(f"{name} ({pid})", pid)
