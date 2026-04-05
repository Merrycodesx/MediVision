from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)


TEXTS = {
    "English": {
        "title": "Users (Admin)",
        "refresh": "Refresh",
        "create": "Create User",
        "username": "Username",
        "email": "Email",
        "password": "Password",
        "first_name": "First Name",
        "last_name": "Last Name",
        "native_name": "Native Name",
        "phone_num": "Phone Number",
        "role": "Role",
        "headers": ["ID", "Username", "Email", "Role", "Active"],
    },
    "Amharic": {
        "title": "ተጠቃሚዎች (Admin)",
        "refresh": "አድስ",
        "create": "ተጠቃሚ ፍጠር",
        "username": "የተጠቃሚ ስም",
        "email": "ኢሜይል",
        "password": "የይለፍ ቃል",
        "first_name": "ስም",
        "last_name": "የአባት ስም",
        "native_name": "የአገር ቋንቋ ስም",
        "phone_num": "ስልክ ቁጥር",
        "role": "ሚና",
        "headers": ["ID", "ስም", "ኢሜይል", "ሚና", "Active"],
    },
}


class UsersPage(QWidget):
    def __init__(self, on_refresh, on_create):
        super().__init__()
        self.setObjectName("PageCard")
        self.language = "English"
        self.on_refresh = on_refresh
        self.on_create = on_create

        layout = QVBoxLayout()
        self.title = QLabel()
        self.title.setObjectName("PageTitle")
        layout.addWidget(self.title)

        form_row = QHBoxLayout()
        self.username = QLineEdit()
        self.email = QLineEdit()
        self.first_name = QLineEdit()
        self.last_name = QLineEdit()
        self.native_name = QLineEdit()
        self.phone_num = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.role = QComboBox()
        self.role.addItems(["clinician", "radiologist", "admin", "auditor"])
        self.create_btn = QPushButton()
        self.create_btn.clicked.connect(self.create_user)
        self.refresh_btn = QPushButton()
        self.refresh_btn.clicked.connect(self.on_refresh)

        form_row.addWidget(self.username)
        form_row.addWidget(self.email)
        form_row.addWidget(self.first_name)
        form_row.addWidget(self.last_name)
        form_row.addWidget(self.native_name)
        form_row.addWidget(self.phone_num)
        form_row.addWidget(self.password)
        form_row.addWidget(self.role)
        form_row.addWidget(self.create_btn)
        form_row.addWidget(self.refresh_btn)
        layout.addLayout(form_row)

        self.table = QTableWidget(0, 5)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.set_language(self.language)

    def set_language(self, language):
        self.language = language
        t = TEXTS.get(language, TEXTS["English"])
        self.title.setText(t["title"])
        self.username.setPlaceholderText(t["username"])
        self.email.setPlaceholderText(t["email"])
        self.first_name.setPlaceholderText(t["first_name"])
        self.last_name.setPlaceholderText(t["last_name"])
        self.native_name.setPlaceholderText(t["native_name"])
        self.phone_num.setPlaceholderText(t["phone_num"])
        self.password.setPlaceholderText(t["password"])
        self.create_btn.setText(t["create"])
        self.refresh_btn.setText(t["refresh"])
        self.table.setHorizontalHeaderLabels(t["headers"])
        self.create_btn.setIcon(self.style().standardIcon(self.style().SP_FileDialogNewFolder))
        self.refresh_btn.setIcon(self.style().standardIcon(self.style().SP_BrowserReload))

    def set_users(self, users):
        rows = users if isinstance(users, list) else []
        self.table.setRowCount(len(rows))
        for i, user in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(user.get("id", "-"))))
            self.table.setItem(i, 1, QTableWidgetItem(str(user.get("username", "-"))))
            self.table.setItem(i, 2, QTableWidgetItem(str(user.get("email", "-"))))
            self.table.setItem(i, 3, QTableWidgetItem(str(user.get("role", "-"))))
            self.table.setItem(i, 4, QTableWidgetItem("Yes" if user.get("is_active") else "No"))

    def create_user(self):
        payload = {
            "username": self.username.text().strip(),
            "email": self.email.text().strip(),
            "first_name": self.first_name.text().strip(),
            "last_name": self.last_name.text().strip(),
            "native_name": self.native_name.text().strip(),
            "phone_num": self.phone_num.text().strip(),
            "password": self.password.text().strip(),
            "role": self.role.currentText(),
        }
        result = self.on_create(payload)
        if result.get("success"):
            QMessageBox.information(self, "Success", "User created.")
            self.username.clear()
            self.email.clear()
            self.first_name.clear()
            self.last_name.clear()
            self.native_name.clear()
            self.phone_num.clear()
            self.password.clear()
            self.on_refresh()
        else:
            msg = result.get("message", "Failed")
            if result.get("response_json"):
                msg += f"\nDetails: {result['response_json']}"
            QMessageBox.warning(self, "Error", msg)
