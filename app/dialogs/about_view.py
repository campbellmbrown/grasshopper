from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout


class AboutView(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        self.logo = QLabel()
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.version_label = QLabel()
        self.sha_label = QLabel()
        self.author_label = QLabel()
        self.link_label = QLabel()
        self.link_label.setOpenExternalLinks(True)

        layout = QVBoxLayout()
        layout.addWidget(self.logo)
        layout.addWidget(self.version_label)
        layout.addWidget(self.sha_label)
        layout.addWidget(self.author_label)
        layout.addWidget(self.link_label)
        self.setLayout(layout)
