from PyQt6.QtCore import Qt

from app.dialogs.about.about_view import AboutView
from app.icons import get_icon, get_pixmap
from app.version import GIT_SHA, __version__


class AboutController:
    def __init__(self, view: AboutView) -> None:
        view.setWindowTitle("Grasshopper")
        view.setWindowIcon(get_icon("logo_32x32.png"))

        pixmap = get_pixmap("logo_256x256.png")
        # scale down
        pixmap = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio)
        view.logo.setPixmap(pixmap)

        view.version_label.setText(f"Version: {__version__}")
        view.sha_label.setText(f"SHA: {GIT_SHA}")
        view.author_label.setText("Author: Campbell Brown")
        view.link_label.setText(
            'GitHub: <a href="https://github.com/campbellmbrown/grasshopper">campbellmbrown/grasshopper</a>'
        )
