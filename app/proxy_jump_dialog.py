import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
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

from app.connection import DEVICE_TYPE_ICONS, DeviceType, ProxyJump
from app.icons import get_icon


class ProxyJumpDialog(QDialog):
    def __init__(self, title: str):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        default_proxy_jump = ProxyJump.default()
        self.device_type_combo_box = QComboBox()
        for device_type in DeviceType:
            self.device_type_combo_box.addItem(get_icon(DEVICE_TYPE_ICONS[device_type]), device_type)
        self.name_input = QLineEdit(default_proxy_jump.name)
        self.target_user_input = QLineEdit(default_proxy_jump.target_user)
        self.target_user_input.setFixedWidth(80)
        self.target_host_input = QLineEdit(default_proxy_jump.target_host)
        self.target_host_input.setFixedWidth(250)
        self.target_port_input = QSpinBox()
        self.target_port_input.setRange(0, 65535)
        self.target_port_input.setValue(default_proxy_jump.target_port)
        self.jump_user_input = QLineEdit(default_proxy_jump.jump_user)
        self.jump_user_input.setFixedWidth(80)
        self.jump_host_input = QLineEdit(default_proxy_jump.jump_host)
        self.jump_host_input.setFixedWidth(250)
        self.jump_port_input = QSpinBox()
        self.jump_port_input.setRange(0, 65535)
        self.jump_port_input.setValue(default_proxy_jump.jump_port)
        self.key_input = QLineEdit(default_proxy_jump.key)
        self.select_key_button = QPushButton("Select")
        self.select_key_button.clicked.connect(self._select_key)
        self.notes_input = QTextEdit(default_proxy_jump.notes)

        details_group = QGroupBox("Details")
        details_group_layout = QGridLayout()
        details_group_layout.addWidget(QLabel("Device Type"), 0, 0)
        details_group_layout.addWidget(QLabel("Name"), 0, 1)
        details_group_layout.addWidget(self.device_type_combo_box, 1, 0)
        details_group_layout.addWidget(self.name_input, 1, 1)
        details_group.setLayout(details_group_layout)

        connection_group = QGroupBox("Connection")
        connection_group_layout = QGridLayout()
        connection_group_layout.addWidget(QLabel("Jump User"), 0, 0)
        connection_group_layout.addWidget(QLabel("Jump Host"), 0, 1)
        connection_group_layout.addWidget(QLabel("Jump Port"), 0, 2)
        connection_group_layout.addWidget(self.jump_user_input, 1, 0)
        connection_group_layout.addWidget(self.jump_host_input, 1, 1)
        connection_group_layout.addWidget(self.jump_port_input, 1, 2)
        connection_group_layout.addWidget(QLabel("Target User"), 2, 0)
        connection_group_layout.addWidget(QLabel("Target Host"), 2, 1)
        connection_group_layout.addWidget(QLabel("Target Port"), 2, 2)
        connection_group_layout.addWidget(self.target_user_input, 3, 0)
        connection_group_layout.addWidget(self.target_host_input, 3, 1)
        connection_group_layout.addWidget(self.target_port_input, 3, 2)
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

    def populate_fields(self, proxy_jump: ProxyJump):
        self.name_input.setText(proxy_jump.name)
        self.target_user_input.setText(proxy_jump.target_user)
        self.target_host_input.setText(proxy_jump.target_host)
        self.target_port_input.setValue(proxy_jump.target_port)
        self.jump_user_input.setText(proxy_jump.jump_user)
        self.jump_host_input.setText(proxy_jump.jump_host)
        self.jump_port_input.setValue(proxy_jump.jump_port)
        self.key_input.setText(proxy_jump.key)
        self.notes_input.setPlainText(proxy_jump.notes)

    def to_proxy_jump(self) -> ProxyJump:
        return ProxyJump(
            device_type=self.device_type_combo_box.currentText(),
            name=self.name_input.text(),
            target_user=self.target_user_input.text(),
            target_host=self.target_host_input.text(),
            target_port=self.target_port_input.value(),
            jump_user=self.jump_user_input.text(),
            jump_host=self.jump_host_input.text(),
            jump_port=self.jump_port_input.value(),
            key=self.key_input.text(),
            notes=self.notes_input.toPlainText(),
        )

    def _accept_if_valid(self):
        error_message = ""
        if not self.name_input.text():
            error_message += "Name is required\n"
        if not self.target_user_input.text():
            error_message += "Target User is required\n"
        if not self.target_host_input.text():
            error_message += "Target Host is required\n"
        if not self.jump_user_input.text():
            error_message += "Jump User is required\n"
        if not self.jump_host_input.text():
            error_message += "Jump Host is required\n"

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
