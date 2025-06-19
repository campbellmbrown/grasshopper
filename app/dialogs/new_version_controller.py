from PySide6.QtWidgets import QMessageBox

from app.dialogs.new_version_view import NewVersionView
from app.model.model import Model
from app.model.version_service import VersionInfo


class NewVersionController:
    def __init__(self, latest: VersionInfo, view: NewVersionView, model: Model) -> None:
        self.view = view
        self.model = model

        view.label.setText(
            f"The current app version is {model.version.current}. A new version is available:<br><br>"
            f"{latest.tag} (published {latest.publish_date})<br><br>"
            "Would you like to view/download the new version?<br>"
            f'<a href="{latest.url}">{latest.url}</a>'
        )

        view.dont_ask_again_button.clicked.connect(self._on_dont_ask_again)

    def _on_dont_ask_again(self):
        self.model.settings.set_prompt_to_download_new_version(False)
        QMessageBox.information(
            self.view,
            "Preferences Updated",
            "The prompt to download new versions has been disabled. This can be re-enabled in the settings.",
        )
        self.view.reject()
