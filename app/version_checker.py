import logging

import requests
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from app.settings import Settings
from app.utility.semver import SemVer
from app.version import __version__


class NewVersionDialog(QDialog):
    """Dialog to inform the user that a new version is available, presenting them with a link to download it."""

    def __init__(self, settings: Settings, latest_version: str, url: str, publish_date: str):
        super().__init__()
        self.settings = settings
        self.setWindowTitle("New Version Available")
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        label = QLabel(
            f"The current app version is {__version__}. A new version is available:<br><br>"
            f"{latest_version} (published {publish_date})<br><br>"
            "Would you like to view/download the new version?<br>"
            f'<a href="{url}">{url}</a>'
        )
        label.setOpenExternalLinks(True)

        dont_ask_again_button = QPushButton("Don't ask again")
        dont_ask_again_button.clicked.connect(self._on_dont_ask_again)
        buttons = QDialogButtonBox()
        buttons.addButton(dont_ask_again_button, QDialogButtonBox.ButtonRole.ActionRole)
        buttons.addButton(QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def _on_dont_ask_again(self):
        self.settings.set_prompt_to_download_new_version(False)
        QMessageBox.information(
            self,
            "Preferences Updated",
            "The prompt to download new versions has been disabled. This can be re-enabled in the settings.",
        )
        self.reject()


class GetLatestVersionThread(QThread):
    """Get the latest release from Github and emit a signal if a new version is available."""

    new_version_available = pyqtSignal(str, str, str)  # version, url, publish date

    def run(self):
        latest_release = self._get_latest_release()
        if latest_release is None:
            return

        if "tag_name" not in latest_release:
            logging.warning("Failed to get tag name from the latest release.")
            return
        if "html_url" not in latest_release:
            logging.warning("Failed to get URL from the latest release.")
            return
        if "published_at" not in latest_release:
            logging.warning("Failed to get publish date from the latest release.")
            return

        tag_name = latest_release["tag_name"]
        if not isinstance(tag_name, str):
            logging.warning("Latest release tag name is not a string.")
            return

        tag_name = tag_name.removeprefix("v")
        latest_version = SemVer(tag_name)
        if not latest_version.is_valid:
            logging.warning("Latest release tag name is not in the correct format (%s).", tag_name)
            return

        this_version = SemVer(__version__)
        assert this_version.is_valid

        if latest_version > this_version:
            logging.info("New version available: %s", tag_name)
            logging.info("Download at: %s", latest_release["html_url"])
            self.new_version_available.emit(tag_name, latest_release["html_url"], latest_release["published_at"])
        else:
            logging.info("No new version available.")

    def _get_latest_release(self) -> dict | None:
        url = "https://api.github.com/repos/campbellmbrown/stassh/releases/latest"
        logging.info("Checking %s...", url)
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            logging.warning("Failed to get latest release from Github.")
            return None

        response.raise_for_status()
        return response.json()
