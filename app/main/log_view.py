from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QPlainTextEdit, QPushButton, QVBoxLayout, QWidget


class LogView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas"))  # Use a fixed width font
        self.log_text.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.clear_button = QPushButton("Clear")

        layout = QVBoxLayout()
        layout.addWidget(self.log_text)
        layout.addWidget(self.clear_button, alignment=Qt.AlignmentFlag.AlignRight)
        self.setLayout(layout)
