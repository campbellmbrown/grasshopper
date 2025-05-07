import socket
from enum import Enum

from PyQt6.QtCore import QThread, pyqtSignal

from app.connection import DirectConnection


class ConnectionStatus(str, Enum):
    UNKNOWN = "Unknown"
    ONLINE = "Online"
    OFFLINE = "Offline"


CONNECTION_STATUS_ICONS = {
    ConnectionStatus.UNKNOWN: "gray_circle.png",
    ConnectionStatus.ONLINE: "green_circle.png",
    ConnectionStatus.OFFLINE: "red_circle.png",
}


class ConnectionStatusThread(QThread):
    """Thread to check the connection status of a DirectConnection."""

    status_updated = pyqtSignal(ConnectionStatus)

    def __init__(self, direct_connection: DirectConnection):
        super().__init__()
        self.direct_connection = direct_connection

    def run(self):
        try:
            with socket.create_connection((self.direct_connection.host, self.direct_connection.port), timeout=1):
                status = ConnectionStatus.ONLINE
        except OSError:
            status = ConnectionStatus.OFFLINE

        self.status_updated.emit(status)
