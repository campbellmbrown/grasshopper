import logging
import os
import subprocess
from sys import platform

import qdarktheme
from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QActionGroup, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDockWidget,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPlainTextEdit,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.direct_connection_page import DirectConnectionsWidget
from app.icons import get_icon, get_pixmap
from app.port_forward_page import PortForwardsWidget
from app.proxy_jump_page import ProxyJumpsWidget
from app.settings import Settings
from app.version import GIT_SHA, __version__
from app.version_checker import GetLatestVersionThread, NewVersionDialog


class Logger(logging.Handler, QObject):
    append_to_widget = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        QObject.__init__(self)
        self.widget = QPlainTextEdit()
        self.widget.setReadOnly(True)
        self.widget.setFont(QFont("Consolas"))  # Use a fixed width font
        self.widget.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.append_to_widget.connect(self.widget.appendPlainText)

    def emit(self, record):
        msg = self.format(record)
        self.append_to_widget.emit(msg)


class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grasshopper")
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setWindowIcon(get_icon("logo_32x32.png"))

        pixmap = get_pixmap("logo_256x256.png")
        # scale down
        pixmap = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio)
        label = QLabel()
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setPixmap(pixmap)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(QLabel(f"Version: {__version__}"))
        layout.addWidget(QLabel(f"SHA: {GIT_SHA}"))
        layout.addWidget(QLabel("Author: Campbell Brown"))
        github_label = QLabel(
            'GitHub: <a href="https://github.com/campbellmbrown/grasshopper">campbellmbrown/grasshopper</a>'
        )
        github_label.setOpenExternalLinks(True)
        layout.addWidget(github_label)
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Grasshopper {__version__}")
        self.resize(1000, 800)
        self.setWindowIcon(get_icon("logo_32x32.png"))

        self.settings = Settings()
        self.settings.load()
        direct_connections_widget = DirectConnectionsWidget()
        proxy_jumps_widget = ProxyJumpsWidget()
        port_forwards_widget = PortForwardsWidget()

        file_menu = QMenu("&File", self)
        preferences_menu = QMenu("&Preferences", self)
        theme_menu = QMenu("&Theme", self)
        preferences_menu.addMenu(theme_menu)

        theme_action_group = QActionGroup(self)
        theme_action_group.setExclusive(True)
        light_theme_action = theme_action_group.addAction("light")
        dark_theme_action = theme_action_group.addAction("dark")
        assert light_theme_action is not None
        assert dark_theme_action is not None
        light_theme_action.setCheckable(True)
        dark_theme_action.setCheckable(True)
        theme_menu.addAction(light_theme_action)
        theme_menu.addAction(dark_theme_action)
        dark_theme_action.triggered.connect(lambda: self._change_theme("dark"))
        light_theme_action.triggered.connect(lambda: self._change_theme("light"))

        prompt_to_download_new_version_action = preferences_menu.addAction("&Check version")
        assert prompt_to_download_new_version_action is not None
        prompt_to_download_new_version_action.setCheckable(True)
        prompt_to_download_new_version_action.setChecked(self.settings.prompt_to_download_new_version)
        prompt_to_download_new_version_action.triggered.connect(self._change_prompt_to_download_new_version)

        if self.settings.theme == "dark":
            dark_theme_action.setChecked(True)
            self._change_theme("dark")
        else:  # Default to light theme
            light_theme_action.setChecked(True)
            self._change_theme("light")

        file_menu.addAction("&Open SSH directory", self._open_ssh_directory)
        file_menu.addSeparator()
        file_menu.addMenu(preferences_menu)
        file_menu.addSeparator()
        file_menu.addAction("E&xit", self.close)

        help_menu = QMenu("&Help", self)
        help_menu.addAction("&About", self._on_about)

        menu_bar = QMenuBar()
        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(help_menu)
        self.setMenuBar(menu_bar)

        tabs = QTabWidget()
        tabs.addTab(direct_connections_widget, "Direct Connections")
        tabs.addTab(proxy_jumps_widget, "Proxy Jumps")
        tabs.addTab(port_forwards_widget, "Port Forwards")

        layout = QVBoxLayout()
        layout.addWidget(tabs)

        dock = QDockWidget("Log")
        log_handler = Logger()
        dock.setWidget(log_handler.widget)
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )

        log_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logging.getLogger().addHandler(log_handler)
        logging.getLogger().setLevel(logging.INFO)

        logging.info("v%s", __version__)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)

        self.version_check_thread = GetLatestVersionThread()
        self.version_check_thread.new_version_available.connect(self._on_new_version_available)
        self.version_check_thread.start()

    def _on_about(self):
        """Show the about dialog."""
        about_dialog = AboutDialog()
        about_dialog.exec()

    def _on_new_version_available(self, latest_version: str, url: str, publish_date: str):
        """Show a dialog to inform the user that a new version is available."""
        if self.settings.prompt_to_download_new_version:
            new_version_dialog = NewVersionDialog(self.settings, latest_version, url, publish_date)
            new_version_dialog.exec()

    def _change_theme(self, theme: str):
        """Change the application theme."""
        stylesheet = qdarktheme.load_stylesheet(theme)
        application = QApplication.instance()
        assert isinstance(application, QApplication)
        application.setStyleSheet(stylesheet)
        self.settings.set_theme(theme)

    def _change_prompt_to_download_new_version(self, checked: bool):
        """Change the setting to prompt to download new version setting.

        Args:
            checked (bool): Whether to prompt to download new versions.
        """
        self.settings.set_prompt_to_download_new_version(checked)

    def _open_ssh_directory(self) -> None:
        if platform == "win32":
            path = os.path.join(os.environ["USERPROFILE"], ".ssh")
            os.startfile(path)
        elif platform == "linux":
            path = os.path.join(os.environ["HOME"], ".ssh")
            subprocess.run(["xdg-open", path])
