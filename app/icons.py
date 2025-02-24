import os
import sys

from PyQt5.QtGui import QIcon, QPixmap


def get_resource_path(resource: str) -> str:
    path = f"resources/{resource}"
    if hasattr(sys, "_MEIPASS"):
        path = os.path.join(sys._MEIPASS, path)
    return path


def get_icon(png: str) -> QIcon:
    return QIcon(get_resource_path(png))


def get_pixmap(png: str) -> QPixmap:
    return QPixmap(get_resource_path(png))
