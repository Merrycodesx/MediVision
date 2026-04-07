from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox

from components.geez_keyboard import GeezKeyboardDialog


TEXTS = {
    "English": {
        "title": "Register New Account",
        "email": "Email",
        "username": "Username",
        "first_name": "First Name",
        "last_name": "Last Name",
        "native_name": "Native Name",
        "phone": "Phone Number",
        "hospital_code": "Hospital Code",
        "hospital_name": "Hospital Name (for first admin/bootstrap)",
        "password": "Password",
        "geez_keyboard": "Ge'ez Keyboard",
        "register": "Register",
        "back": "Back to Login",
        "success_title": "Success",
        "success_msg": "Registration successful! Please login.",
        "failed_title": "Registration Failed",
    },
    "Amharic": {
        "title": "አዲስ አካውንት ይመዝገቡ",
        "email": "ኢሜይል",
        "username": "የተጠቃሚ ስም",
        "first_name": "ስም",
        "last_name": "የአባት ስም",
        "native_name": "የአገር ቋንቋ ስም",
        "phone": "ስልክ ቁጥር",
        "hospital_code": "የሆስፒታል ኮድ",
        "hospital_name": "የሆስፒታል ስም (ለመጀመሪያ Admin)",
        "password": "የይለፍ ቃል",
        "geez_keyboard": "ግዕዝ ኪቦርድ",
        "register": "ተመዝገብ",
        "back": "ወደ መግቢያ ተመለስ",
        "success_title": "ተሳክቷል",
        "success_msg": "ምዝገባ ተሳክቷል። እባክዎ ይግቡ።",
        "failed_title": "ምዝገባ አልተሳካም",
    },
}


class RegisterPage(QWidget):
    def __init__(self, on_register, switch_to_login):
        super().__init__()
        self.setObjectName("PageCard")
        self.language = "English"
        layout = QVBoxLayout()
        self.title = QLabel()
        self.title.setObjectName("PageTitle")
        layout.addWidget(self.title)
        self.email = QLineEdit()
        self.username = QLineEdit()
        self.first_name = QLineEdit()
        self.last_name = QLineEdit()
        self.native_name = QLineEdit()
        self.geez_keyboard_btn = QPushButton()
        self.geez_keyboard_btn.clicked.connect(self.open_geez_keyboard)
        self.phone_num = QLineEdit()
        self.hospital_code = QLineEdit()
        self.hospital_name = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.role = QComboBox()
        self.role.addItems(["Doctor", "Technician", "Admin"])
        self.register_btn = QPushButton()
        self.register_btn.clicked.connect(self.try_register)
        self.login_btn = QPushButton()
        self.login_btn.clicked.connect(switch_to_login)
        layout.addWidget(self.email)
        layout.addWidget(self.username)
        layout.addWidget(self.first_name)
        layout.addWidget(self.last_name)
        native_name_row = QHBoxLayout()
        native_name_row.addWidget(self.native_name)
        native_name_row.addWidget(self.geez_keyboard_btn)
        layout.addLayout(native_name_row)
        layout.addWidget(self.phone_num)
        layout.addWidget(self.hospital_code)
        layout.addWidget(self.hospital_name)
        layout.addWidget(self.password)
        layout.addWidget(self.role)
        layout.addWidget(self.register_btn)
        layout.addWidget(self.login_btn)
        layout.addStretch()
        self.setLayout(layout)
        self.on_register = on_register
        self.set_language(self.language)

    def set_language(self, language):
        self.language = language
        texts = TEXTS.get(language, TEXTS["English"])
        self.title.setText(texts["title"])
        self.email.setPlaceholderText(texts["email"])
        self.username.setPlaceholderText(texts["username"])
        self.first_name.setPlaceholderText(texts["first_name"])
        self.last_name.setPlaceholderText(texts["last_name"])
        self.native_name.setPlaceholderText(texts["native_name"])
        self.geez_keyboard_btn.setText(texts["geez_keyboard"])
        self.phone_num.setPlaceholderText(texts["phone"])
        self.hospital_code.setPlaceholderText(texts["hospital_code"])
        self.hospital_name.setPlaceholderText(texts["hospital_name"])
        self.password.setPlaceholderText(texts["password"])
        self.register_btn.setText(texts["register"])
        self.login_btn.setText(texts["back"])
        self.register_btn.setIcon(self.style().standardIcon(self.style().SP_FileDialogNewFolder))
        self.login_btn.setIcon(self.style().standardIcon(self.style().SP_ArrowBack))

    def open_geez_keyboard(self):
        dialog = GeezKeyboardDialog(self.native_name, self)
        dialog.exec_()

    def try_register(self):
        email = self.email.text()
        username = self.username.text()
        password = self.password.text()
        role = self.role.currentText()
        first_name = self.first_name.text()
        last_name = self.last_name.text()
        native_name = self.native_name.text()
        phone_num = self.phone_num.text()
        hospital_code = self.hospital_code.text()
        hospital_name = self.hospital_name.text()
        result = self.on_register(
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
            texts = TEXTS.get(self.language, TEXTS["English"])
            QMessageBox.information(self, texts["success_title"], texts["success_msg"])
        else:
            msg = result.get("message", "Registration failed")
            if result.get("response_json"):
                msg += f"\nDetails: {result['response_json']}"
            elif result.get("response"):
                msg += f"\nServer: {result['response']}"
            QMessageBox.warning(self, TEXTS.get(self.language, TEXTS["English"])["failed_title"], msg)
