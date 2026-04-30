from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QHBoxLayout


TEXTS = {
    "English": {
        "title": "MediVision Login",
        "email": "Email",
        "password": "Password",
        "login": "Login",
        "register": "Register",
        "login_failed": "Login Failed",
        "login_hint": "Login failed: invalid email/password or account is inactive.\nUse the same email used during registration and ensure user is active.",
    },
    "Amharic": {
        "title": "MediVision ግባ",
        "email": "ኢሜይል",
        "password": "የይለፍ ቃል",
        "login": "ግባ",
        "register": "ተመዝገብ",
        "login_failed": "መግቢያ አልተሳካም",
        "login_hint": "መግቢያ አልተሳካም፤ ኢሜይል/የይለፍ ቃል ወይም አካውንት ገቢር አይደለም።",
    },
}

class LoginPage(QWidget):
    def __init__(self, on_login, switch_to_register=None):
        super().__init__()
        self.setObjectName("PageCard")
        self.language = "English"
        self._switch_to_register = switch_to_register
        layout = QVBoxLayout()
        self.title = QLabel()
        self.title.setObjectName("PageTitle")
        layout.addWidget(self.title)
        self.email = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.role = QComboBox()
        self.role.addItems(["Doctor", "Technician", "Admin", "Auditor"])
        self.login_btn = QPushButton()
        self.login_btn.clicked.connect(self.try_login)
        layout.addWidget(self.email)
        layout.addWidget(self.password)
        layout.addWidget(self.role)
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.login_btn)
        if switch_to_register:
            self.register_btn = QPushButton()
            self.register_btn.clicked.connect(switch_to_register)
            btn_row.addWidget(self.register_btn)
        layout.addLayout(btn_row)
        layout.addStretch()
        self.setLayout(layout)
        self.on_login = on_login
        self.set_language(self.language)

    def set_language(self, language):
        self.language = language
        texts = TEXTS.get(language, TEXTS["English"])
        self.title.setText(texts["title"])
        self.email.setPlaceholderText(texts["email"])
        self.password.setPlaceholderText(texts["password"])
        self.login_btn.setText(texts["login"])
        self.login_btn.setIcon(self.style().standardIcon(self.style().SP_DialogOkButton))
        if self._switch_to_register:
            self.register_btn.setText(texts["register"])
            self.register_btn.setIcon(self.style().standardIcon(self.style().SP_FileDialogNewFolder))

    def try_login(self):
        email = self.email.text()
        password = self.password.text()
        role = self.role.currentText()
        result = self.on_login(email, password, role)
        if not result.get("success"):
            msg = result.get("message", "Unknown error")
            if result.get("status_code") == 401:
                msg = TEXTS.get(self.language, TEXTS["English"])["login_hint"]
            if result.get("response_json"):
                msg += f"\nDetails: {result['response_json']}"
            if result.get("response"):
                msg += f"\nServer: {result['response']}"
            QMessageBox.warning(
                self,
                TEXTS.get(self.language, TEXTS["English"])["login_failed"],
                msg,
            )
