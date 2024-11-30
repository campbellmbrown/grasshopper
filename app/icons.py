import os
import sys

from PyQt5.QtGui import QIcon


def get_icon(png: str) -> QIcon:
    icon_path = f"resources/{png}"
    if hasattr(sys, "_MEIPASS"):
        icon_path = os.path.join(sys._MEIPASS, icon_path)
    return QIcon(icon_path)
