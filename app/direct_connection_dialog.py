from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
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

from app.connection import DEVICE_TYPE_ICONS, DeviceType, DirectConnection
from app.ssh import SSH_DIR
from app.utility.resource_provider import get_icon


class DirectConnectionDialog(QDialog):
    def __init__(self, title: str):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        default_direct_connection = DirectConnection.default()
        self.device_type_combo_box = QComboBox()
        for device_type in DeviceType:
            self.device_type_combo_box.addItem(get_icon(DEVICE_TYPE_ICONS[device_type]), device_type)
        self.name_input = QLineEdit(default_direct_connection.name)
        self.user_input = QLineEdit(default_direct_connection.user)
        self.user_input.setFixedWidth(80)
        self.host_input = QLineEdit(default_direct_connection.host)
        self.host_input.setFixedWidth(250)
        self.port_input = QSpinBox()
        self.port_input.setRange(0, 65535)
        self.port_input.setValue(default_direct_connection.port)
        self.key_input = QLineEdit(default_direct_connection.key)
        self.select_key_button = QPushButton("Select")
        self.select_key_button.clicked.connect(self._select_key)
        self.notes_input = QTextEdit(default_direct_connection.notes)

        details_group = QGroupBox("Details")
        details_group_layout = QGridLayout()
        details_group_layout.addWidget(QLabel("Device Type"), 0, 0)
        details_group_layout.addWidget(QLabel("Name"), 0, 1)
        details_group_layout.addWidget(self.device_type_combo_box, 1, 0)
        details_group_layout.addWidget(self.name_input, 1, 1)
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

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._accept_if_valid)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(details_group)
        layout.addWidget(connection_group)
        layout.addWidget(keys_group)
        layout.addWidget(QLabel("Notes"))
        layout.addWidget(self.notes_input)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def populate_fields(self, direct_connection: DirectConnection):
        self.device_type_combo_box.setCurrentText(direct_connection.device_type)
        self.name_input.setText(direct_connection.name)
        self.user_input.setText(direct_connection.user)
        self.host_input.setText(direct_connection.host)
        self.port_input.setValue(direct_connection.port)
        self.key_input.setText(direct_connection.key)
        self.notes_input.setPlainText(direct_connection.notes)

    def to_direct_connection(self) -> DirectConnection:
        return DirectConnection(
            device_type=self.device_type_combo_box.currentText(),
            name=self.name_input.text(),
            user=self.user_input.text(),
            host=self.host_input.text(),
            port=self.port_input.value(),
            key=self.key_input.text(),
            notes=self.notes_input.toPlainText(),
        )

    def _accept_if_valid(self):
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
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Key File", dir=SSH_DIR)
        if file_path:
            self.key_input.setText(file_path)
