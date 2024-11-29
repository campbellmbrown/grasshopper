import json
import logging
import os
import subprocess
from enum import IntEnum
from typing import Any

from PyQt5.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QSortFilterProxyModel,
    Qt,
    pyqtSignal,
)
from PyQt5.QtGui import QContextMenuEvent, QFont
from PyQt5.QtWidgets import (
    QAction,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.common import ViewBase
from app.connection import PortForward
from app.port_forward_dialog import PortForwardDialog

DATABASE_PATH = os.path.join(os.environ["APPDATA"], "StaSSH", "port_forwards.json")


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
                return self.port_forwards[row].key

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
            if role == Qt.ItemDataRole.FontRole:
                font = QFont()
                font.setBold(True)
                return font

    def _load(self):
        if not os.path.exists(DATABASE_PATH):
            return
        with open(DATABASE_PATH, "r") as file:
            try:
                loaded_port_forwards = json.load(file)
            except json.JSONDecodeError:
                loaded_port_forwards = None
            if loaded_port_forwards is not None and "port_forwards" in loaded_port_forwards:
                port_forwards = loaded_port_forwards["port_forwards"]
                for port_forward in port_forwards:
                    self.port_forwards.append(PortForward.from_dict(port_forward))

    def _save(self):
        if not os.path.exists(os.path.dirname(DATABASE_PATH)):
            os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        with open(DATABASE_PATH, "w") as file:
            json.dump({"port_forwards": [pf.to_dict() for pf in self.port_forwards]}, file, indent=4)


class PortForwardsView(ViewBase):
    new_port_forward = pyqtSignal()
    edit_port_forward = pyqtSignal(int)
    duplicate_port_forward = pyqtSignal(int)
    delete_port_forward = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.new_action = QAction("New")
        self.edit_action = QAction("Edit")
        self.duplicate_action = QAction("Duplicate")
        self.delete_action = QAction("Delete")
        self.menu = QMenu()
        self.menu.addAction(self.new_action)
        self.menu.addAction(self.edit_action)
        self.menu.addAction(self.duplicate_action)
        self.menu.addAction(self.delete_action)

        self.new_action.triggered.connect(self.new_port_forward)
        self.edit_action.triggered.connect(lambda: self.edit_port_forward.emit(self.currentIndex().row()))
        self.duplicate_action.triggered.connect(lambda: self.duplicate_port_forward.emit(self.currentIndex().row()))
        self.delete_action.triggered.connect(lambda: self.delete_port_forward.emit(self.currentIndex().row()))

    def attach_model(self, proxy_model: QSortFilterProxyModel) -> None:
        self.setModel(proxy_model)
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

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        index = self.indexAt(event.pos())
        is_valid = index.isValid()
        self.edit_action.setEnabled(is_valid)
        self.duplicate_action.setEnabled(is_valid)
        self.delete_action.setEnabled(is_valid)
        self.menu.exec_(event.globalPos())


class PortForwardsWidget(QWidget):
    def __init__(self):
        super().__init__()

        view = PortForwardsView()
        self.model = PortForwardsModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSortRole(Qt.ItemDataRole.UserRole)
        self.proxy_model.setSourceModel(self.model)
        view.attach_model(self.proxy_model)
        view.doubleClicked.connect(self._on_row_double_clicked)
        view.new_port_forward.connect(self._on_new_port_forward)
        view.edit_port_forward.connect(self._on_edit_port_forward)
        view.duplicate_port_forward.connect(self._on_duplicate_port_forward)
        view.delete_port_forward.connect(self._on_delete_port_forward)

        new_button = QPushButton("New")
        new_button.clicked.connect(self._on_new_port_forward)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(new_button)
        buttons_layout.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(buttons_layout)
        layout.addWidget(view)
        self.setLayout(layout)

    def _on_row_double_clicked(self, index: QModelIndex):
        """Open a new terminal window and connect to the host."""
        source_index = self.proxy_model.mapToSource(index)
        conn = self.model.get_port_forward(source_index.row())

        key_arg = f"-i {conn.key}" if conn.key else ""
        command = f"ssh {key_arg} {conn.user}@{conn.host} -p{conn.port}"
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
        source_index = self.proxy_model.mapToSource(self.proxy_model.index(row, 0))
        port_forward = self.model.get_port_forward(source_index.row())

        dialog = PortForwardDialog("Edit Port Forward")
        dialog.populate_fields(port_forward)
        result = dialog.exec_()
        if result == QDialog.DialogCode.Accepted:
            self.model.update_port_forward(source_index.row(), dialog.to_port_forward())

    def _on_duplicate_port_forward(self, row: int):
        """Duplicate a port forward into a new port forward dialog."""
        source_index = self.proxy_model.mapToSource(self.proxy_model.index(row, 0))
        port_forward = self.model.get_port_forward(source_index.row()).copy()
        port_forward.name += " (Copy)"
        dialog = PortForwardDialog("New Port Forward")
        dialog.populate_fields(port_forward)
        result = dialog.exec_()
        if result == QDialog.DialogCode.Accepted:
            self.model.add_port_forward(dialog.to_port_forward())

    def _on_delete_port_forward(self, row: int):
        """Delete a port forward."""
        source_index = self.proxy_model.mapToSource(self.proxy_model.index(row, 0))
        self.model.delete_port_forward(source_index.row())
