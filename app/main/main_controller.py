import logging

import qdarktheme  # type: ignore[import]
from PySide6.QtWidgets import QApplication

from app.dialogs.about_controller import AboutController
from app.dialogs.about_view import AboutView
from app.dialogs.new_version_controller import NewVersionController
from app.dialogs.new_version_view import NewVersionView
from app.main.log_controller import LogController
from app.main.main_view import MainView
from app.model.model import Model
from app.model.version_service import VersionInfo
from app.thread.get_latest_version_thread import GetLatestVersionThread


class MainController:
    def __init__(self, view: MainView, model: Model) -> None:
        self.model = model
        view.setWindowTitle(f"Grasshopper {model.version.current}")

        # set up logging
        app_logger_handler = LogController(view.log_view)
        app_logger_handler.add_to_logger()
        logging.getLogger().setLevel(logging.INFO)
        logging.info("v%s", model.version.current)

        view.open_ssh_directory_action.triggered.connect(model.ssh.open_ssh_directory)
        view.dark_theme_action.triggered.connect(lambda: self._change_theme("dark"))
        view.light_theme_action.triggered.connect(lambda: self._change_theme("light"))
        view.about_action.triggered.connect(self._on_about)
        view.prompt_to_download_new_version_action.triggered.connect(self._change_prompt_to_download_new_version)

        view.prompt_to_download_new_version_action.setChecked(model.settings.prompt_to_download_new_version)
        if model.settings.theme == "dark":
            view.dark_theme_action.setChecked(True)
            self._change_theme("dark")
        else:  # Default to light theme
            view.light_theme_action.setChecked(True)
            self._change_theme("light")

        self.version_check_thread = GetLatestVersionThread(model)
        self.version_check_thread.new_version_available.connect(self._on_new_version_available)
        self.version_check_thread.start()

    def _on_new_version_available(self, latest: VersionInfo) -> None:
        """Show a dialog to inform the user that a new version is available."""
        if self.model.settings.prompt_to_download_new_version:
            new_version_dialog = NewVersionView()
            NewVersionController(latest, new_version_dialog, self.model)
            new_version_dialog.exec()

    def _on_about(self):
        """Show the about dialog."""
        about_dialog = AboutView()
        AboutController(about_dialog, self.model)
        about_dialog.exec()

    def _change_theme(self, theme: str):
        """Change the application theme."""
        stylesheet = qdarktheme.load_stylesheet(theme)
        application = QApplication.instance()
        assert isinstance(application, QApplication)
        application.setStyleSheet(stylesheet)
        self.model.settings.set_theme(theme)

    def _change_prompt_to_download_new_version(self, checked: bool):
        """Change the setting to prompt to download new version setting.

        Args:
            checked (bool): Whether to prompt to download new versions.
        """
        self.model.settings.set_prompt_to_download_new_version(checked)
