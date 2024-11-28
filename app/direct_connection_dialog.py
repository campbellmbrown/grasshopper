import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
)

from app.connection import DirectConnection


class DirectConnectionDialog(QDialog):
    def __init__(self, title: str):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        default_direct_connection = DirectConnection.default()
        self.name_input = QLineEdit(default_direct_connection.name)
        self.name_input.setPlaceholderText("Name")
        self.user_input = QLineEdit(default_direct_connection.user)
        self.user_input.setPlaceholderText("User")
        self.user_input.setFixedWidth(80)
        self.host_input = QLineEdit(default_direct_connection.host)
        self.host_input.setPlaceholderText("Host")
        self.host_input.setFixedWidth(250)
        self.port_input = QSpinBox()
        self.port_input.setRange(0, 65535)
        self.port_input.setValue(default_direct_connection.port)
        self.key_input = QLineEdit(default_direct_connection.key)
        self.key_input.setPlaceholderText("Key")
        self.select_key_button = QPushButton("Select")
        self.select_key_button.clicked.connect(self._select_key)
        self.notes_input = QTextEdit(default_direct_connection.notes)
        self.notes_input.setPlaceholderText("Notes")

        details_group = QGroupBox("Details")
        details_group_layout = QVBoxLayout()
        details_group_layout.addWidget(QLabel("Name"))
        details_group_layout.addWidget(self.name_input)
        details_group.setLayout(details_group_layout)

        connection_group = QGroupBox("Connection")
        connection_group_layout = QGridLayout()
        connection_group_layout.addWidget(QLabel("User"), 0, 0)
        connection_group_layout.addWidget(QLabel("Host"), 0, 1)
        connection_group_layout.addWidget(QLabel("Port"), 0, 2)
        connection_group_layout.addWidget(self.user_input, 1, 0)
        connection_group_layout.addWidget(self.host_input, 1, 1)
        connection_group_layout.addWidget(self.port_input, 1, 2)
        connection_group.setLayout(connection_group_layout)

        keys_group = QGroupBox("Keys")
        keys_group_layout = QHBoxLayout()
        keys_group_layout.addWidget(QLabel("Private Key"))
        keys_group_layout.addWidget(self.key_input)
        keys_group_layout.addWidget(self.select_key_button)
        keys_group.setLayout(keys_group_layout)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept_if_valid)
        self.buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(details_group)
        layout.addWidget(connection_group)
        layout.addWidget(keys_group)
        layout.addWidget(QLabel("Notes"))
        layout.addWidget(self.notes_input)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def populate_fields(self, direct_connection: DirectConnection):
        self.name_input.setText(direct_connection.name)
        self.user_input.setText(direct_connection.user)
        self.host_input.setText(direct_connection.host)
        self.port_input.setValue(direct_connection.port)
        self.key_input.setText(direct_connection.key)
        self.notes_input.setPlainText(direct_connection.notes)

    def to_direct_connection(self) -> DirectConnection:
        return DirectConnection(
            name=self.name_input.text(),
            user=self.user_input.text(),
            host=self.host_input.text(),
            port=self.port_input.value(),
            key=self.key_input.text(),
            notes=self.notes_input.toPlainText(),
        )

    def accept_if_valid(self):
        error_message = ""
        if not self.name_input.text():
            error_message += "Name is required\n"
        if not self.user_input.text():
            error_message += "User is required\n"
        if not self.host_input.text():
            error_message += "Host is required\n"

        if error_message:
            error_message = error_message[:-1]  # Remove the trailing newline
            QMessageBox.warning(self, "Missing Properties", error_message)
        else:
            self.accept()

    def _select_key(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Key File", directory=os.path.join(os.environ["USERPROFILE"], ".ssh")
        )
        if file_path:
            self.key_input.setText(file_path)
