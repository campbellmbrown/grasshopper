from PyQt6.QtCore import Qt

from app.dialogs.about_view import AboutView
from app.icons import get_icon, get_pixmap
from app.model.model import Model


class AboutController:
    def __init__(self, view: AboutView, model: Model) -> None:
        view.setWindowTitle("Grasshopper")
        view.setWindowIcon(get_icon("logo_32x32.png"))

        pixmap = get_pixmap("logo_256x256.png")
        # scale down
        pixmap = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio)
        view.logo.setPixmap(pixmap)

        view.version_label.setText(f"Version: {model.version.current}")
        view.sha_label.setText(f"SHA: {model.version.git_sha}")
        view.author_label.setText("Author: Campbell Brown")
        view.link_label.setText(
            'GitHub: <a href="https://github.com/campbellmbrown/grasshopper">campbellmbrown/grasshopper</a>'
        )
