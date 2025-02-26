import logging
import os
import subprocess
from enum import IntEnum
from typing import Any

from PyQt5.QtCore import QAbstractItemModel, QAbstractTableModel, QModelIndex, Qt
from PyQt5.QtGui import QClipboard, QColor
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QMessageBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.common import StyleSheets, ViewBase
from app.config_file import ConfigFile
from app.connection import DEVICE_TYPE_ICONS, DeviceType, PortForward
from app.icons import get_icon
from app.port_forward_dialog import PortForwardDialog


class PortForwardsHeader(IntEnum):
    """Headers for the port forwards table."""

    NAME = 0
    LOCAL_PORT = 1
    TARGET_HOST = 2
    TARGET_PORT = 3
    REMOTE_SERVER_USER = 4
    REMOTE_SERVER_HOST = 5
    REMOTE_SERVER_PORT = 6
    KEY = 7


class PortForwardsModel(QAbstractTableModel):
    """Model for the direct connections table."""

    def __init__(self):
        self.port_forwards: list[PortForward] = []
        super().__init__()

        self.headers = {
            PortForwardsHeader.NAME: "Name",
            PortForwardsHeader.LOCAL_PORT: "Local Port",
            PortForwardsHeader.TARGET_HOST: "Target Host",
            PortForwardsHeader.TARGET_PORT: "Target Port",
            PortForwardsHeader.REMOTE_SERVER_USER: "Server User",
            PortForwardsHeader.REMOTE_SERVER_HOST: "Server Host",
            PortForwardsHeader.REMOTE_SERVER_PORT: "Server Port",
            PortForwardsHeader.KEY: "Key",
        }
        assert len(self.headers) == len(PortForwardsHeader)

        self.source = ConfigFile("port_forwards.json")
        self._load()

    def add_port_forward(self, port_forward: PortForward) -> None:
        """Add a port forward to the model.

        Args:
            port_forward (PortForward): The port forward to add.
        """
        row = len(self.port_forwards)
        self.beginInsertRows(QModelIndex(), row, row)
        self.port_forwards.append(port_forward)
        self.endInsertRows()
        self.dataChanged.emit(self.index(row, 0), self.index(row, len(self.headers) - 1))
        self._save()

    def delete_port_forward(self, row: int) -> None:
        """Delete a port forward from the model.

        Args:
            row (int): The row of the port forward to delete.
        """
        self.beginRemoveRows(QModelIndex(), row, row)
        self.port_forwards.pop(row)
        self.endRemoveRows()
        self._save()

    def move_up(self, row: int) -> None:
        """Move a port forward up in the model.

        Args:
            row (int): The row of the port forward to move up.
        """
        if row > 0:
            self.beginMoveRows(QModelIndex(), row, row, QModelIndex(), row - 1)
            self.port_forwards.insert(row - 1, self.port_forwards.pop(row))
            self.endMoveRows()
            self._save()

    def move_down(self, row: int) -> None:
        """Move a port forward down in the model.

        Args:
            row (int): The row of the port forward to move down.
        """
        if row < len(self.port_forwards) - 1:
            self.beginMoveRows(QModelIndex(), row, row, QModelIndex(), row + 2)
            self.port_forwards.insert(row + 1, self.port_forwards.pop(row))
            self.endMoveRows()

    def get_port_forward(self, row: int) -> PortForward:
        """Get a port forward from the model."""
        return self.port_forwards[row]

    def update_port_forward(self, row: int, port_forward: PortForward) -> None:
        """Update a port forward in the model."""
        self.port_forwards[row] = port_forward
        self._save()
        self.dataChanged.emit(self.index(row, 0), self.index(row, len(self.headers) - 1))

    def rowCount(self, parent: QModelIndex) -> int:
        return len(self.port_forwards)

    def columnCount(self, parent: QModelIndex) -> int:
        return len(PortForwardsHeader)

    def data(self, index: QModelIndex, role: int) -> Any:
        if not index.isValid():
            return

        col = index.column()
        row = index.row()

        if role == Qt.ItemDataRole.DecorationRole:
            if col == PortForwardsHeader.NAME:
                return get_icon(DEVICE_TYPE_ICONS[DeviceType(self.port_forwards[row].device_type)])

        if role == Qt.ItemDataRole.DisplayRole:  # What's displayed to the user
            if col == PortForwardsHeader.NAME:
                return self.port_forwards[row].name
            if col == PortForwardsHeader.LOCAL_PORT:
                return self.port_forwards[row].local_port
            if col == PortForwardsHeader.TARGET_HOST:
                return self.port_forwards[row].target_host
            if col == PortForwardsHeader.TARGET_PORT:
                return self.port_forwards[row].target_port
            if col == PortForwardsHeader.REMOTE_SERVER_USER:
                return self.port_forwards[row].remote_server_user
            if col == PortForwardsHeader.REMOTE_SERVER_HOST:
                return self.port_forwards[row].remote_server_host
            if col == PortForwardsHeader.REMOTE_SERVER_PORT:
                return self.port_forwards[row].remote_server_port
            if col == PortForwardsHeader.KEY:
                # Display the key file name only
                return os.path.basename(self.port_forwards[row].key)

        if role == Qt.ItemDataRole.UserRole:  # Application-specific purposes
            if col == PortForwardsHeader.NAME:
                return self.port_forwards[row].name
            if col == PortForwardsHeader.LOCAL_PORT:
                return self.port_forwards[row].local_port
            if col == PortForwardsHeader.TARGET_HOST:
                return self.port_forwards[row].target_host
            if col == PortForwardsHeader.TARGET_PORT:
                return self.port_forwards[row].target_port
            if col == PortForwardsHeader.REMOTE_SERVER_USER:
                return self.port_forwards[row].remote_server_user
            if col == PortForwardsHeader.REMOTE_SERVER_HOST:
                return self.port_forwards[row].remote_server_host
            if col == PortForwardsHeader.REMOTE_SERVER_PORT:
                return self.port_forwards[row].remote_server_port
            if col == PortForwardsHeader.KEY:
                return self.port_forwards[row].key

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def headerData(self, section: int, orientation: Qt.Orientation, role: int) -> Any:
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self.headers[PortForwardsHeader(section)]
            if role == Qt.ItemDataRole.TextAlignmentRole:
                return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            if role == Qt.ItemDataRole.TextColorRole:
                return QColor(Qt.GlobalColor.gray)

    def _load(self):
        loaded_port_forwards = self.source.load()
        if "port_forwards" in loaded_port_forwards:
            for port_forward in loaded_port_forwards["port_forwards"]:
                self.port_forwards.append(PortForward.from_dict(port_forward))

    def _save(self):
        self.source.save({"port_forwards": [pf.to_dict() for pf in self.port_forwards]})


class PortForwardsView(ViewBase):
    def __init__(self):
        super().__init__()

    def attach_model(self, model: QAbstractItemModel) -> None:
        self.setModel(model)
        header = self.horizontalHeader()
        assert isinstance(header, QHeaderView)
        header.setSectionResizeMode(PortForwardsHeader.NAME.value, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(PortForwardsHeader.LOCAL_PORT.value, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(PortForwardsHeader.TARGET_HOST.value, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(PortForwardsHeader.TARGET_PORT.value, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(
            PortForwardsHeader.REMOTE_SERVER_USER.value, QHeaderView.ResizeMode.ResizeToContents
        )
        header.setSectionResizeMode(
            PortForwardsHeader.REMOTE_SERVER_HOST.value, QHeaderView.ResizeMode.ResizeToContents
        )
        header.setSectionResizeMode(
            PortForwardsHeader.REMOTE_SERVER_PORT.value, QHeaderView.ResizeMode.ResizeToContents
        )
        header.setSectionResizeMode(PortForwardsHeader.KEY.value, QHeaderView.ResizeMode.ResizeToContents)


class PortForwardsWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.view = PortForwardsView()
        self.model = PortForwardsModel()
        self.view.attach_model(self.model)
        self.view.item_activated.connect(self._on_port_forward_activated)
        self.view.new_item.connect(self._on_new_port_forward)
        self.view.edit_item.connect(self._on_edit_port_forward)
        self.view.duplicate_item.connect(self._on_duplicate_port_forward)
        self.view.delete_item.connect(self._on_delete_port_forward)
        self.view.copy_command.connect(self._on_copy_command)

        new_button = QToolButton()
        new_button.setStyleSheet(StyleSheets.TRANSPARENT_TOOLBUTTON)
        new_button.setDefaultAction(self.view.new_action)

        move_up_action = QAction(get_icon("up.png"), "Move Up")
        move_down_action = QAction(get_icon("down.png"), "Move Down")
        move_up_button = QToolButton()
        move_up_button.setStyleSheet(StyleSheets.TRANSPARENT_TOOLBUTTON)
        move_up_button.setDefaultAction(move_up_action)
        move_down_button = QToolButton()
        move_down_button.setStyleSheet(StyleSheets.TRANSPARENT_TOOLBUTTON)
        move_down_button.setDefaultAction(move_down_action)
        move_up_action.triggered.connect(self._move_selected_row_up)
        move_down_action.triggered.connect(self._move_selected_row_down)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(new_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(move_up_button)
        buttons_layout.addWidget(move_down_button)

        layout = QVBoxLayout()
        layout.addLayout(buttons_layout)
        layout.addWidget(self.view)
        self.setLayout(layout)

    def _on_port_forward_activated(self, row: int):
        """Open a new terminal window and connect to the host."""
        source_index = self.model.index(row, 0)
        pf = self.model.get_port_forward(source_index.row())
        command = pf.command()
        logging.info(f"Running: {command}")
        subprocess.Popen(["start", "cmd", "/k", command], shell=True)

    def _on_new_port_forward(self):
        """Open a new port forward dialog."""
        dialog = PortForwardDialog("New Port Forward")
        result = dialog.exec_()
        if result == QDialog.DialogCode.Accepted:
            self.model.add_port_forward(dialog.to_port_forward())

    def _on_edit_port_forward(self, row: int):
        """Open an edit port forward dialog."""
        source_index = self.model.index(row, 0)
        port_forward = self.model.get_port_forward(source_index.row())

        dialog = PortForwardDialog("Edit Port Forward")
        dialog.populate_fields(port_forward)
        result = dialog.exec_()
        if result == QDialog.DialogCode.Accepted:
            self.model.update_port_forward(source_index.row(), dialog.to_port_forward())

    def _on_duplicate_port_forward(self, row: int):
        """Duplicate a port forward into a new port forward dialog."""
        source_index = self.model.index(row, 0)
        port_forward = self.model.get_port_forward(source_index.row()).copy()
        port_forward.name += " (Copy)"
        dialog = PortForwardDialog("New Port Forward")
        dialog.populate_fields(port_forward)
        result = dialog.exec_()
        if result == QDialog.DialogCode.Accepted:
            self.model.add_port_forward(dialog.to_port_forward())

    def _on_delete_port_forward(self, row: int):
        """Delete a port forward."""
        confirmed = QMessageBox.question(
            self,
            "Delete Port Forward",
            "Are you sure you want to delete this port forward?",
            (QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No),
            QMessageBox.StandardButton.Yes,
        )
        if confirmed == QMessageBox.StandardButton.Yes:
            source_index = self.model.index(row, 0)
            self.model.delete_port_forward(source_index.row())

    def _on_copy_command(self, row: int):
        """Copy the SSH command to the clipboard."""
        pf = self.model.get_port_forward(row)
        command = pf.command()
        clipboard = QApplication.clipboard()
        assert isinstance(clipboard, QClipboard)
        clipboard.setText(command)
        logging.info(f"Copied to clipboard: {command}")

    def _move_selected_row_up(self):
        """Move the selected row up."""
        selected_index = self.view.currentIndex()
        if selected_index.isValid():
            self.model.move_up(selected_index.row())

    def _move_selected_row_down(self):
        """Move the selected row down."""
        selected_index = self.view.currentIndex()
        if selected_index.isValid():
            self.model.move_down(selected_index.row())
