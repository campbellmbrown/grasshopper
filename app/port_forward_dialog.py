from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
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

from app.connection import DEVICE_TYPE_ICONS, DeviceType, PortForward
from app.icons import get_icon
from app.ssh import SSH_DIR


class PortForwardDialog(QDialog):
    def __init__(self, title: str):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        default_port_forward = PortForward.default()
        self.device_type_combo_box = QComboBox()
        for device_type in DeviceType:
            self.device_type_combo_box.addItem(get_icon(DEVICE_TYPE_ICONS[device_type]), device_type)
        self.name_input = QLineEdit(default_port_forward.name)
        self.local_port_input = QSpinBox()
        self.local_port_input.setRange(0, 65535)
        self.local_port_input.setValue(default_port_forward.local_port)
        self.target_host_input = QLineEdit(default_port_forward.target_host)
        self.target_host_input.setFixedWidth(250)
        self.target_port_input = QSpinBox()
        self.target_port_input.setRange(0, 65535)
        self.target_port_input.setValue(default_port_forward.target_port)
        self.remote_server_user_input = QLineEdit(default_port_forward.remote_server_user)
        self.remote_server_user_input.setFixedWidth(80)
        self.remote_server_host_input = QLineEdit(default_port_forward.remote_server_host)
        self.remote_server_host_input.setFixedWidth(250)
        self.remote_server_port_input = QSpinBox()
        self.remote_server_port_input.setRange(0, 65535)
        self.remote_server_port_input.setValue(default_port_forward.remote_server_port)
        self.key_input = QLineEdit(default_port_forward.key)
        self.select_key_button = QPushButton("Select")
        self.select_key_button.clicked.connect(self._select_key)
        self.notes_input = QTextEdit(default_port_forward.notes)

        details_group = QGroupBox("Details")
        details_group_layout = QGridLayout()
        details_group_layout.addWidget(QLabel("Device Type"), 0, 0)
        details_group_layout.addWidget(QLabel("Name"), 0, 1)
        details_group_layout.addWidget(self.device_type_combo_box, 1, 0)
        details_group_layout.addWidget(self.name_input, 1, 1)
        details_group.setLayout(details_group_layout)

        connection_group = QGroupBox("Connection")
        connection_group_layout = QGridLayout()
        connection_group_layout.addWidget(QLabel("Local Port"), 0, 2)
        connection_group_layout.addWidget(self.local_port_input, 1, 2)
        connection_group_layout.addWidget(QLabel("Target Host"), 2, 1)
        connection_group_layout.addWidget(QLabel("Target Port"), 2, 2)
        connection_group_layout.addWidget(self.target_host_input, 3, 1)
        connection_group_layout.addWidget(self.target_port_input, 3, 2)
        connection_group_layout.addWidget(QLabel("Server User"), 4, 0)
        connection_group_layout.addWidget(QLabel("Server Host"), 4, 1)
        connection_group_layout.addWidget(QLabel("Server Port"), 4, 2)
        connection_group_layout.addWidget(self.remote_server_user_input, 5, 0)
        connection_group_layout.addWidget(self.remote_server_host_input, 5, 1)
        connection_group_layout.addWidget(self.remote_server_port_input, 5, 2)
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

    def populate_fields(self, port_forward: PortForward):
        self.device_type_combo_box.setCurrentText(port_forward.device_type)
        self.name_input.setText(port_forward.name)
        self.local_port_input.setValue(port_forward.local_port)
        self.target_host_input.setText(port_forward.target_host)
        self.target_port_input.setValue(port_forward.target_port)
        self.remote_server_user_input.setText(port_forward.remote_server_user)
        self.remote_server_host_input.setText(port_forward.remote_server_host)
        self.remote_server_port_input.setValue(port_forward.remote_server_port)
        self.key_input.setText(port_forward.key)
        self.notes_input.setPlainText(port_forward.notes)

    def to_port_forward(self) -> PortForward:
        return PortForward(
            device_type=self.device_type_combo_box.currentText(),
            name=self.name_input.text(),
            notes=self.notes_input.toPlainText(),
            local_port=self.local_port_input.value(),
            target_host=self.target_host_input.text(),
            target_port=self.target_port_input.value(),
            remote_server_user=self.remote_server_user_input.text(),
            remote_server_host=self.remote_server_host_input.text(),
            remote_server_port=self.remote_server_port_input.value(),
            key=self.key_input.text(),
        )

    def _accept_if_valid(self):
        error_message = ""
        if not self.name_input.text():
            error_message += "Name is required\n"
        if not self.target_host_input.text():
            error_message += "Target Host is required\n"
        if not self.remote_server_user_input.text():
            error_message += "Server User is required\n"
        if not self.remote_server_host_input.text():
            error_message += "Server Host is required\n"

        if error_message:
            error_message = error_message[:-1]  # Remove the trailing newline
            QMessageBox.critical(self, "Error", error_message)
        else:
            self.accept()

    def _select_key(self):
        key_file, _ = QFileDialog.getOpenFileName(self, "Select Key File", directory=SSH_DIR)
        if key_file:
            self.key_input.setText(key_file)
