from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QPushButton, QVBoxLayout


class NewVersionView(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("New Version Available")
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        self.label = QLabel()
        self.label.setOpenExternalLinks(True)

        self.dont_ask_again_button = QPushButton("Don't ask again")

        buttons = QDialogButtonBox()
        buttons.addButton(self.dont_ask_again_button, QDialogButtonBox.ButtonRole.ActionRole)
        buttons.addButton(QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(buttons)
        self.setLayout(layout)
