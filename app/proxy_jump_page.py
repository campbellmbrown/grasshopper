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
from app.connection import DEVICE_TYPE_ICONS, DeviceType, ProxyJump
from app.icons import get_icon
from app.proxy_jump_dialog import ProxyJumpDialog


class ProxyJumpsHeader(IntEnum):
    """Headers for the proxy jumps table."""

    NAME = 0
    TARGET_USER = 1
    TARGET_HOST = 2
    TARGET_PORT = 3
    JUMP_USER = 4
    JUMP_HOST = 5
    JUMP_PORT = 6
    KEY = 7


class ProxyJumpsModel(QAbstractTableModel):
    """Model for the proxy jumps table."""

    def __init__(self):
        self.proxy_jumps: list[ProxyJump] = []
        super().__init__()

        self.headers = {
            ProxyJumpsHeader.NAME: "Name",
            ProxyJumpsHeader.TARGET_USER: "Target User",
            ProxyJumpsHeader.TARGET_HOST: "Target Host",
            ProxyJumpsHeader.TARGET_PORT: "Target Port",
            ProxyJumpsHeader.JUMP_USER: "Jump User",
            ProxyJumpsHeader.JUMP_HOST: "Jump Host",
            ProxyJumpsHeader.JUMP_PORT: "Jump Port",
            ProxyJumpsHeader.KEY: "Key",
        }
        assert len(self.headers) == len(ProxyJumpsHeader)

        self.source = ConfigFile("proxy_jumps.json")
        self._load()

    def add_proxy_jump(self, proxy_jump: ProxyJump) -> None:
        """Add a proxy jump to the model.

        Args:
            proxy_jump (ProxyJump): The proxy jump to add.
        """
        row = len(self.proxy_jumps)
        self.beginInsertRows(QModelIndex(), row, row)
        self.proxy_jumps.append(proxy_jump)
        self.endInsertRows()
        self.dataChanged.emit(self.index(row, 0), self.index(row, len(self.headers) - 1))
        self._save()

    def delete_proxy_jump(self, row: int) -> None:
        """Delete a proxy jump from the model.

        Args:
            row (int): The row of the proxy jump to delete.
        """
        self.beginRemoveRows(QModelIndex(), row, row)
        self.proxy_jumps.pop(row)
        self.endRemoveRows()
        self._save()

    def move_up(self, row: int) -> None:
        """Move a proxy jump up in the model.

        Args:
            row (int): The row of the proxy jump to move up.
        """
        if row > 0:
            self.beginMoveRows(QModelIndex(), row, row, QModelIndex(), row - 1)
            self.proxy_jumps.insert(row - 1, self.proxy_jumps.pop(row))
            self.endMoveRows()
            self._save()

    def move_down(self, row: int) -> None:
        """Move a proxy jump down in the model.

        Args:
            row (int): The row of the proxy jump to move down.
        """
        if row < len(self.proxy_jumps) - 1:
            self.beginMoveRows(QModelIndex(), row, row, QModelIndex(), row + 2)
            self.proxy_jumps.insert(row + 1, self.proxy_jumps.pop(row))
            self.endMoveRows()

    def get_proxy_jump(self, row: int) -> ProxyJump:
        """Get a proxy jump from the model by row."""
        return self.proxy_jumps[row]

    def update_proxy_jump(self, row: int, proxy_jump: ProxyJump) -> None:
        """Update a proxy jump in the model."""
        self.proxy_jumps[row] = proxy_jump
        self._save()
        self.dataChanged.emit(self.index(row, 0), self.index(row, len(self.headers) - 1))

    def rowCount(self, parent: QModelIndex) -> int:
        return len(self.proxy_jumps)

    def columnCount(self, parent: QModelIndex) -> int:
        return len(ProxyJumpsHeader)

    def data(self, index: QModelIndex, role: int) -> Any:
        if not index.isValid():
            return

        col = index.column()
        row = index.row()

        if role == Qt.ItemDataRole.DecorationRole:
            if col == ProxyJumpsHeader.NAME:
                return get_icon(DEVICE_TYPE_ICONS[DeviceType(self.proxy_jumps[row].device_type)])

        if role == Qt.ItemDataRole.DisplayRole:  # What's displayed to the user
            if col == ProxyJumpsHeader.NAME:
                return self.proxy_jumps[row].name
            if col == ProxyJumpsHeader.TARGET_USER:
                return self.proxy_jumps[row].target_user
            if col == ProxyJumpsHeader.TARGET_HOST:
                return self.proxy_jumps[row].target_host
            if col == ProxyJumpsHeader.TARGET_PORT:
                return self.proxy_jumps[row].target_port
            if col == ProxyJumpsHeader.JUMP_USER:
                return self.proxy_jumps[row].jump_user
            if col == ProxyJumpsHeader.JUMP_HOST:
                return self.proxy_jumps[row].jump_host
            if col == ProxyJumpsHeader.JUMP_PORT:
                return self.proxy_jumps[row].jump_port
            if col == ProxyJumpsHeader.KEY:
                # Display the key file name only
                return os.path.basename(self.proxy_jumps[row].key)

        if role == Qt.ItemDataRole.UserRole:  # Application-specific purposes
            if col == ProxyJumpsHeader.NAME:
                return self.proxy_jumps[row].name
            if col == ProxyJumpsHeader.TARGET_USER:
                return self.proxy_jumps[row].target_user
            if col == ProxyJumpsHeader.TARGET_HOST:
                return self.proxy_jumps[row].target_host
            if col == ProxyJumpsHeader.TARGET_PORT:
                return self.proxy_jumps[row].target_port
            if col == ProxyJumpsHeader.JUMP_USER:
                return self.proxy_jumps[row].jump_user
            if col == ProxyJumpsHeader.JUMP_HOST:
                return self.proxy_jumps[row].jump_host
            if col == ProxyJumpsHeader.JUMP_PORT:
                return self.proxy_jumps[row].jump_port
            if col == ProxyJumpsHeader.KEY:
                return self.proxy_jumps[row].key

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def headerData(self, section: int, orientation: Qt.Orientation, role: int) -> Any:
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self.headers[ProxyJumpsHeader(section)]
            if role == Qt.ItemDataRole.TextAlignmentRole:
                return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            if role == Qt.ItemDataRole.TextColorRole:
                return QColor(Qt.GlobalColor.gray)

    def _load(self):
        loaded_proxy_jumps = self.source.load()
        if "proxy_jumps" in loaded_proxy_jumps:
            for proxy_jump in loaded_proxy_jumps["proxy_jumps"]:
                self.proxy_jumps.append(ProxyJump.from_dict(proxy_jump))

    def _save(self):
        self.source.save({"proxy_jumps": [pj.to_dict() for pj in self.proxy_jumps]})


class ProxyJumpsView(ViewBase):
    def __init__(self):
        super().__init__()

    def attach_model(self, model: QAbstractItemModel) -> None:
        self.setModel(model)
        header = self.horizontalHeader()
        assert isinstance(header, QHeaderView)
        header.setSectionResizeMode(ProxyJumpsHeader.NAME.value, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(ProxyJumpsHeader.TARGET_USER.value, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(ProxyJumpsHeader.TARGET_HOST.value, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(ProxyJumpsHeader.TARGET_PORT.value, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(ProxyJumpsHeader.JUMP_USER.value, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(ProxyJumpsHeader.JUMP_HOST.value, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(ProxyJumpsHeader.JUMP_PORT.value, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(ProxyJumpsHeader.KEY.value, QHeaderView.ResizeMode.ResizeToContents)


class ProxyJumpsWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.view = ProxyJumpsView()
        self.model = ProxyJumpsModel()
        self.view.attach_model(self.model)
        self.view.item_activated.connect(self._on_proxy_jump_activated)
        self.view.new_item.connect(self._on_new_proxy_jump)
        self.view.edit_item.connect(self._on_edit_proxy_jump)
        self.view.duplicate_item.connect(self._on_duplicate_proxy_jump)
        self.view.delete_item.connect(self._on_delete_proxy_jump)
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

    def _on_proxy_jump_activated(self, row: int):
        """Open a new terminal window and connect to the host through the proxy jump."""
        pj = self.model.get_proxy_jump(row)
        command = pj.command()
        logging.info(f"Running: {command}")
        subprocess.Popen(["start", "cmd", "/k", command], shell=True)

    def _on_new_proxy_jump(self):
        """Open a new proxy jump dialog."""
        dialog = ProxyJumpDialog("New proxy jump")
        result = dialog.exec_()
        if result == QDialog.DialogCode.Accepted:
            self.model.add_proxy_jump(dialog.to_proxy_jump())

    def _on_edit_proxy_jump(self, row: int):
        """Open an edit proxy jump dialog."""
        proxy_jump = self.model.get_proxy_jump(row)

        dialog = ProxyJumpDialog("Edit proxy jump")
        dialog.populate_fields(proxy_jump)
        result = dialog.exec_()
        if result == QDialog.DialogCode.Accepted:
            self.model.update_proxy_jump(row, dialog.to_proxy_jump())

    def _on_duplicate_proxy_jump(self, row: int):
        """Duplicate a proxy jump into a new proxy jump dialog."""
        proxy_jump = self.model.get_proxy_jump(row).copy()
        proxy_jump.name += " (Copy)"
        dialog = ProxyJumpDialog("New proxy jump")
        dialog.populate_fields(proxy_jump)
        result = dialog.exec_()
        if result == QDialog.DialogCode.Accepted:
            self.model.add_proxy_jump(dialog.to_proxy_jump())

    def _on_delete_proxy_jump(self, row: int):
        """Delete a proxy jump."""
        confirmed = QMessageBox.question(
            self,
            "Delete Proxy Jump",
            "Are you sure you want to delete this proxy jump?",
            (QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No),
            QMessageBox.StandardButton.Yes,
        )
        if confirmed == QMessageBox.StandardButton.Yes:
            self.model.delete_proxy_jump(row)

    def _on_copy_command(self, row: int):
        """Copy the SSH command to the clipboard."""
        pj = self.model.get_proxy_jump(row)
        command = pj.command()
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
