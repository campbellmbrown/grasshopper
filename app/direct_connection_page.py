import json
import logging
import os
import subprocess
from enum import IntEnum
from typing import Any

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QAction,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QMessageBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.common import StyleSheets, ViewBase
from app.connection import DEVICE_TYPE_ICONS, DeviceType, DirectConnection
from app.connection_status import (
    CONNECTION_STATUS_ICONS,
    ConnectionStatus,
    ConnectionStatusThread,
)
from app.direct_connection_dialog import DirectConnectionDialog
from app.icons import get_icon

DIRECT_CONNECTIONS_PATH = os.path.join(os.environ["APPDATA"], "StaSSH", "direct_connections.json")


class DirectConnectionsHeader(IntEnum):
    """Headers for the direct connections table."""

    NAME = 0
    USER = 1
    HOST = 2
    PORT = 3
    KEY = 4
    CONNECTION_STATUS = 5


class DirectConnectionsModel(QAbstractTableModel):
    """Model for the direct connections table."""

    def __init__(self):
        super().__init__()
        self.direct_connections: list[DirectConnection] = []
        self.connection_statuses: list[ConnectionStatus] = []

        self.headers = {
            DirectConnectionsHeader.NAME: "Name",
            DirectConnectionsHeader.USER: "User",
            DirectConnectionsHeader.HOST: "Host Name",
            DirectConnectionsHeader.PORT: "Port",
            DirectConnectionsHeader.KEY: "Key",
            DirectConnectionsHeader.CONNECTION_STATUS: "Status",
        }
        assert len(self.headers) == len(DirectConnectionsHeader)
        self._load()

    def add_direct_connection(self, direct_connection: DirectConnection) -> None:
        """Add a direct connection to the model.

        Args:
            direct_connection (DirectConnection): The direct connection to add.
        """
        row = len(self.direct_connections)
        self.beginInsertRows(QModelIndex(), row, row)
        self.direct_connections.append(direct_connection)
        self.connection_statuses.append(ConnectionStatus.UNKNOWN)
        self.endInsertRows()
        self.dataChanged.emit(self.index(row, 0), self.index(row, len(self.headers) - 1))
        self._save()

    def delete_direct_connection(self, row: int) -> None:
        """Delete a direct connection from the model.

        Args:
            row (int): The row of the direct connection to delete.
        """
        self.beginRemoveRows(QModelIndex(), row, row)
        self.direct_connections.pop(row)
        self.connection_statuses.pop(row)
        self.endRemoveRows()
        self._save()

    def get_direct_connection(self, row: int) -> DirectConnection:
        """Get a direct connection from the model by row."""
        return self.direct_connections[row]

    def update_direct_connection(self, row: int, direct_connection: DirectConnection) -> None:
        """Update a direct connection in the model."""
        self.direct_connections[row] = direct_connection
        self._save()
        self.dataChanged.emit(self.index(row, 0), self.index(row, len(self.headers) - 1))

    def new_connection_status(self, direct_connection: DirectConnection, status: ConnectionStatus) -> None:
        if direct_connection in self.direct_connections:  # Guard against the connection being deleted or edited
            row = self.direct_connections.index(direct_connection)
            self.connection_statuses[row] = status
            self.dataChanged.emit(self.index(row, 0), self.index(row, len(self.headers) - 1))

    def rowCount(self, parent: QModelIndex) -> int:
        return len(self.direct_connections)

    def columnCount(self, parent: QModelIndex) -> int:
        return len(DirectConnectionsHeader)

    def data(self, index: QModelIndex, role: int) -> Any:
        if not index.isValid():
            return

        col = index.column()
        row = index.row()

        if role == Qt.ItemDataRole.DecorationRole:
            if col == DirectConnectionsHeader.NAME:
                return get_icon(DEVICE_TYPE_ICONS[DeviceType(self.direct_connections[row].device_type)])
            if col == DirectConnectionsHeader.CONNECTION_STATUS:
                return get_icon(CONNECTION_STATUS_ICONS[self.connection_statuses[row]])

        if role == Qt.ItemDataRole.DisplayRole:  # What's displayed to the user
            if col == DirectConnectionsHeader.NAME:
                return self.direct_connections[row].name
            if col == DirectConnectionsHeader.USER:
                return self.direct_connections[row].user
            if col == DirectConnectionsHeader.HOST:
                return self.direct_connections[row].host
            if col == DirectConnectionsHeader.PORT:
                return self.direct_connections[row].port
            if col == DirectConnectionsHeader.KEY:
                # Display the key file name only
                return os.path.basename(self.direct_connections[row].key)
            if col == DirectConnectionsHeader.CONNECTION_STATUS:
                return self.connection_statuses[row].value

        if role == Qt.ItemDataRole.UserRole:  # Application-specific purposes
            if col == DirectConnectionsHeader.NAME:
                return self.direct_connections[row].name
            if col == DirectConnectionsHeader.USER:
                return self.direct_connections[row].user
            if col == DirectConnectionsHeader.HOST:
                return self.direct_connections[row].host
            if col == DirectConnectionsHeader.PORT:
                return self.direct_connections[row].port
            if col == DirectConnectionsHeader.KEY:
                return self.direct_connections[row].key
            if col == DirectConnectionsHeader.CONNECTION_STATUS:
                return self.connection_statuses[row].value

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def headerData(self, section: int, orientation: Qt.Orientation, role: int) -> Any:
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self.headers[DirectConnectionsHeader(section)]
            if role == Qt.ItemDataRole.TextAlignmentRole:
                return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            if role == Qt.ItemDataRole.TextColorRole:
                return QColor(Qt.GlobalColor.gray)

    def _load(self):
        if not os.path.exists(DIRECT_CONNECTIONS_PATH):
            return
        with open(DIRECT_CONNECTIONS_PATH) as file:
            try:
                loaded_direct_connections = json.load(file)
            except json.JSONDecodeError:
                loaded_direct_connections = None
            if loaded_direct_connections is not None and "direct_connections" in loaded_direct_connections:
                direct_connections = loaded_direct_connections["direct_connections"]
                for connection in direct_connections:
                    self.direct_connections.append(DirectConnection.from_dict(connection))
                    self.connection_statuses.append(ConnectionStatus.UNKNOWN)

    def _save(self):
        if not os.path.exists(DIRECT_CONNECTIONS_PATH):
            os.makedirs(os.path.dirname(DIRECT_CONNECTIONS_PATH), exist_ok=True)
        with open(DIRECT_CONNECTIONS_PATH, "w") as file:
            json.dump({"direct_connections": [conn.to_dict() for conn in self.direct_connections]}, file, indent=4)


class DirectConnectionsView(ViewBase):
    def __init__(self):
        super().__init__()

    def attach_model(self, proxy_model: QSortFilterProxyModel) -> None:
        self.setModel(proxy_model)
        header = self.horizontalHeader()
        assert isinstance(header, QHeaderView)
        header.setSectionResizeMode(DirectConnectionsHeader.NAME.value, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(DirectConnectionsHeader.USER.value, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(DirectConnectionsHeader.HOST.value, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(DirectConnectionsHeader.PORT.value, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(DirectConnectionsHeader.KEY.value, QHeaderView.ResizeMode.ResizeToContents)


class DirectConnectionsWidget(QWidget):
    def __init__(self):
        super().__init__()

        view = DirectConnectionsView()
        self.model = DirectConnectionsModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSortRole(Qt.ItemDataRole.UserRole)
        self.proxy_model.setSourceModel(self.model)
        view.attach_model(self.proxy_model)
        view.item_activated.connect(self._on_direct_connection_activated)
        view.new_item.connect(self._on_new_direct_connection)
        view.edit_item.connect(self._on_edit_direct_connection)
        view.duplicate_item.connect(self._on_duplicate_direct_connection)
        view.delete_item.connect(self._on_delete_direct_connection)

        new_button = QToolButton()
        new_button.setStyleSheet(StyleSheets.TRANSPARENT_TOOLBUTTON)
        new_button.setDefaultAction(view.new_action)

        refresh_connection_status_action = QAction(get_icon("reload.png"), "Refresh Connection Status")
        refresh_connection_status_action.triggered.connect(self._on_refresh_status)
        refresh_connection_status_button = QToolButton()
        refresh_connection_status_button.setStyleSheet(StyleSheets.TRANSPARENT_TOOLBUTTON)
        refresh_connection_status_button.setDefaultAction(refresh_connection_status_action)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(new_button)
        buttons_layout.addWidget(refresh_connection_status_button)
        buttons_layout.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(buttons_layout)
        layout.addWidget(view)
        self.setLayout(layout)

        self.connection_status_threads: list[ConnectionStatusThread] = []
        for connection in self.model.direct_connections:
            self._start_connection_status_thread(connection)

    def _on_refresh_status(self):
        """Refresh all connection statuses."""
        for connection in self.model.direct_connections:
            self.model.new_connection_status(connection, ConnectionStatus.UNKNOWN)
            self._start_connection_status_thread(connection)

    def _start_connection_status_thread(self, direct_connection: DirectConnection):
        """Start a thread to check the connection status of a DirectConnection."""
        thread = ConnectionStatusThread(direct_connection)
        thread.status_updated.connect(
            lambda status, conn=direct_connection: self._on_connection_status_updated(status, conn)
        )
        thread.finished.connect(lambda: self._on_thread_finished(thread))
        thread.start()
        self.connection_status_threads.append(thread)

    def _on_connection_status_updated(self, status: ConnectionStatus, direct_connection: DirectConnection):
        """When a connection status thread updates the status of a DirectConnection."""
        logging.info(f"Network check for {direct_connection.name} complete: {status.value}")
        self.model.new_connection_status(direct_connection, status)

    def _on_thread_finished(self, thread: ConnectionStatusThread):
        """When a connection status thread finishes."""
        self.connection_status_threads.remove(thread)
        thread.deleteLater()

    def _on_direct_connection_activated(self, row: int):
        """Open a new terminal window and connect to the host."""
        source_index = self.proxy_model.mapToSource(self.proxy_model.index(row, 0))
        conn = self.model.get_direct_connection(source_index.row())

        key_arg = f"-i {conn.key}" if conn.key else ""
        command = f"ssh {key_arg} {conn.user}@{conn.host} -p{conn.port}"
        logging.info(f"Running: {command}")
        subprocess.Popen(["start", "cmd", "/k", command], shell=True)

    def _on_new_direct_connection(self):
        """Open a new direct connection dialog."""
        dialog = DirectConnectionDialog("New Direct Connection")
        result = dialog.exec_()
        if result == QDialog.DialogCode.Accepted:
            new_direct_connection = dialog.to_direct_connection()
            self.model.add_direct_connection(new_direct_connection)
            self._start_connection_status_thread(new_direct_connection)

    def _on_edit_direct_connection(self, row: int):
        """Open an edit direct connection dialog."""
        source_index = self.proxy_model.mapToSource(self.proxy_model.index(row, 0))
        direct_connection = self.model.get_direct_connection(source_index.row())

        dialog = DirectConnectionDialog("Edit Direct Connection")
        dialog.populate_fields(direct_connection)
        result = dialog.exec_()
        if result == QDialog.DialogCode.Accepted:
            edited_direct_connection = dialog.to_direct_connection()
            self.model.update_direct_connection(source_index.row(), dialog.to_direct_connection())
            self.model.new_connection_status(edited_direct_connection, ConnectionStatus.UNKNOWN)
            self._start_connection_status_thread(edited_direct_connection)

    def _on_duplicate_direct_connection(self, row: int):
        """Duplicate a direct connection into a new direct connection dialog."""
        source_index = self.proxy_model.mapToSource(self.proxy_model.index(row, 0))
        direct_connection = self.model.get_direct_connection(source_index.row()).copy()
        direct_connection.name += " (Copy)"
        dialog = DirectConnectionDialog("New Direct Connection")
        dialog.populate_fields(direct_connection)
        result = dialog.exec_()
        if result == QDialog.DialogCode.Accepted:
            new_direct_connection = dialog.to_direct_connection()
            self.model.add_direct_connection(new_direct_connection)
            self._start_connection_status_thread(new_direct_connection)

    def _on_delete_direct_connection(self, row: int):
        """Delete a direct connection."""
        confirmed = QMessageBox.question(
            self,
            "Delete Direct Connection",
            "Are you sure you want to delete this direct connection?",
            (QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No),
            QMessageBox.StandardButton.Yes,
        )
        if confirmed == QMessageBox.StandardButton.Yes:
            source_index = self.proxy_model.mapToSource(self.proxy_model.index(row, 0))
            self.model.delete_direct_connection(source_index.row())
