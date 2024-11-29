import json
import os
from dataclasses import dataclass

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QDialog, QDialogButtonBox, QVBoxLayout

DIRECT_CONNECTIONS_PATH = os.path.join(os.environ["APPDATA"], "StaSSH", "settings.json")

DEFAULT_PROMPT_TO_DOWNLOAD_NEW_VERSION = True


@dataclass
class Settings:
    """Settings for the application. These are saved to disk and loaded on startup."""

    prompt_to_download_new_version: bool = DEFAULT_PROMPT_TO_DOWNLOAD_NEW_VERSION

    def set_prompt_to_download_new_version(self, value: bool):
        self.prompt_to_download_new_version = value
        self.save()

    def load(self):
        self._load_defaults()
        if not os.path.exists(DIRECT_CONNECTIONS_PATH):
            return
        with open(DIRECT_CONNECTIONS_PATH) as file:
            try:
                settings = json.load(file)
            except json.JSONDecodeError:
                settings = None
            if settings is not None:
                self._from_json(settings)

    def save(self):
        if not os.path.exists(DIRECT_CONNECTIONS_PATH):
            os.makedirs(os.path.dirname(DIRECT_CONNECTIONS_PATH), exist_ok=True)
        with open(DIRECT_CONNECTIONS_PATH, "w") as file:
            file.write(json.dumps(self._to_json(), indent=4))

    def _to_json(self):
        return {"prompt_to_download_new_version": self.prompt_to_download_new_version}

    def _from_json(self, json: dict):
        if "prompt_to_download_new_version" in json:
            self.prompt_to_download_new_version = json["prompt_to_download_new_version"]

    def _load_defaults(self):
        self.prompt_to_download_new_version = DEFAULT_PROMPT_TO_DOWNLOAD_NEW_VERSION


class SettingsDialog(QDialog):
    """Dialog to change application settings."""

    def __init__(self, settings: Settings):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        self.prompt_to_download_new_version_checkbox = QCheckBox("Prompt to download new versions")
        self.prompt_to_download_new_version_checkbox.setChecked(settings.prompt_to_download_new_version)

        buttons = QDialogButtonBox()
        buttons.addButton(QDialogButtonBox.StandardButton.Save)
        buttons.addButton(QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.prompt_to_download_new_version_checkbox)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def to_settings(self) -> Settings:
        settings = Settings(prompt_to_download_new_version=self.prompt_to_download_new_version_checkbox.isChecked())
        return settings
