from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


GEEZ_ROWS = [
    ("ሀ", ["ሀ", "ሁ", "ሂ", "ሃ", "ሄ", "ህ", "ሆ"]),
    ("ለ", ["ለ", "ሉ", "ሊ", "ላ", "ሌ", "ል", "ሎ"]),
    ("ሐ", ["ሐ", "ሑ", "ሒ", "ሓ", "ሔ", "ሕ", "ሖ"]),
    ("መ", ["መ", "ሙ", "ሚ", "ማ", "ሜ", "ም", "ሞ"]),
    ("ሠ", ["ሠ", "ሡ", "ሢ", "ሣ", "ሤ", "ሥ", "ሦ"]),
    ("ረ", ["ረ", "ሩ", "ሪ", "ራ", "ሬ", "ር", "ሮ"]),
    ("ሰ", ["ሰ", "ሱ", "ሲ", "ሳ", "ሴ", "ስ", "ሶ"]),
    ("ሸ", ["ሸ", "ሹ", "ሺ", "ሻ", "ሼ", "ሽ", "ሾ"]),
    ("ቀ", ["ቀ", "ቁ", "ቂ", "ቃ", "ቄ", "ቅ", "ቆ"]),
    ("ቐ", ["ቐ", "ቑ", "ቒ", "ቓ", "ቔ", "ቕ", "ቖ"]),
    ("በ", ["በ", "ቡ", "ቢ", "ባ", "ቤ", "ብ", "ቦ"]),
    ("ተ", ["ተ", "ቱ", "ቲ", "ታ", "ቴ", "ት", "ቶ"]),
    ("ቸ", ["ቸ", "ቹ", "ቺ", "ቻ", "ቼ", "ች", "ቾ"]),
    ("ቨ", ["ቨ", "ቩ", "ቪ", "ቫ", "ቬ", "ቭ", "ቮ"]),
    ("ኀ", ["ኀ", "ኁ", "ኂ", "ኃ", "ኄ", "ኅ", "ኆ"]),
    ("ነ", ["ነ", "ኑ", "ኒ", "ና", "ኔ", "ን", "ኖ"]),
    ("ኘ", ["ኘ", "ኙ", "ኚ", "ኛ", "ኜ", "ኝ", "ኞ"]),
    ("አ", ["አ", "ኡ", "ኢ", "ኣ", "ኤ", "እ", "ኦ"]),
    ("ከ", ["ከ", "ኩ", "ኪ", "ካ", "ኬ", "ክ", "ኮ"]),
    ("ኸ", ["ኸ", "ኹ", "ኺ", "ኻ", "ኼ", "ኽ", "ኾ"]),
    ("ወ", ["ወ", "ዉ", "ዊ", "ዋ", "ዌ", "ው", "ዎ"]),
    ("ዘ", ["ዘ", "ዙ", "ዚ", "ዛ", "ዜ", "ዝ", "ዞ"]),
    ("ዠ", ["ዠ", "ዡ", "ዢ", "ዣ", "ዤ", "ዥ", "ዦ"]),
    ("የ", ["የ", "ዩ", "ዪ", "ያ", "ዬ", "ይ", "ዮ"]),
    ("ዐ", ["ዐ", "ዑ", "ዒ", "ዓ", "ዔ", "ዕ", "ዖ"]),
    ("ደ", ["ደ", "ዱ", "ዲ", "ዳ", "ዴ", "ድ", "ዶ"]),
    ("ገ", ["ገ", "ጉ", "ጊ", "ጋ", "ጌ", "ግ", "ጎ"]),
    ("ጘ", ["ጘ", "ጙ", "ጚ", "ጛ", "ጜ", "ጝ", "ጞ"]),
    ("ጠ", ["ጠ", "ጡ", "ጢ", "ጣ", "ጤ", "ጥ", "ጦ"]),
    ("ጨ", ["ጨ", "ጩ", "ጪ", "ጫ", "ጬ", "ጭ", "ጮ"]),
    ("ጰ", ["ጰ", "ጱ", "ጲ", "ጳ", "ጴ", "ጵ", "ጶ"]),
    ("ፀ", ["ፀ", "ፁ", "ፂ", "ፃ", "ፄ", "ፅ", "ፆ"]),
    ("ፈ", ["ፈ", "ፉ", "ፊ", "ፋ", "ፌ", "ፍ", "ፎ"]),
    ("ፐ", ["ፐ", "ፑ", "ፒ", "ፓ", "ፔ", "ፕ", "ፖ"]),
]


class GeezKeyboardDialog(QDialog):
    def __init__(self, target_line_edit, parent=None):
        super().__init__(parent)
        self.target_line_edit = target_line_edit
        self.setWindowTitle("Ge'ez Keyboard")
        self.setModal(True)
        self.resize(860, 560)

        layout = QVBoxLayout(self)

        title = QLabel("Insert Ethiopic characters into the native name field.")
        title.setWordWrap(True)
        layout.addWidget(title)

        self.preview = QLabel(self.target_line_edit.text())
        self.preview.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.preview.setWordWrap(True)
        self.preview.setStyleSheet("padding: 8px; border: 1px solid #cfcfcf; border-radius: 6px;")
        layout.addWidget(self.preview)

        actions = QHBoxLayout()

        backspace_btn = QPushButton("Backspace")
        backspace_btn.clicked.connect(self.backspace_character)
        actions.addWidget(backspace_btn)

        space_btn = QPushButton("Space")
        space_btn.clicked.connect(lambda: self.insert_text(" "))
        actions.addWidget(space_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_text)
        actions.addWidget(clear_btn)

        actions.addStretch()
        layout.addLayout(actions)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        grid = QGridLayout(scroll_content)
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(8)

        for row_index, (label, characters) in enumerate(GEEZ_ROWS):
            row_label = QLabel(label)
            row_label.setAlignment(Qt.AlignCenter)
            row_label.setMinimumWidth(28)
            grid.addWidget(row_label, row_index, 0)

            for col_index, character in enumerate(characters, start=1):
                button = QPushButton(character)
                button.setMinimumSize(44, 40)
                button.clicked.connect(lambda checked=False, char=character: self.insert_text(char))
                grid.addWidget(button, row_index, col_index)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

        self.target_line_edit.textChanged.connect(self.preview.setText)

    def insert_text(self, text):
        self.target_line_edit.insert(text)
        self.preview.setText(self.target_line_edit.text())

    def backspace_character(self):
        current = self.target_line_edit.text()
        cursor_position = self.target_line_edit.cursorPosition()

        if self.target_line_edit.hasSelectedText():
            start = self.target_line_edit.selectionStart()
            end = start + len(self.target_line_edit.selectedText())
            updated = current[:start] + current[end:]
            self.target_line_edit.setText(updated)
            self.target_line_edit.setCursorPosition(start)
            self.preview.setText(updated)
            return

        if cursor_position <= 0:
            return

        updated = current[: cursor_position - 1] + current[cursor_position:]
        self.target_line_edit.setText(updated)
        self.target_line_edit.setCursorPosition(cursor_position - 1)
        self.preview.setText(updated)

    def clear_text(self):
        self.target_line_edit.clear()
        self.preview.clear()
