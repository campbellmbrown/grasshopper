import logging

from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QDialog,
    QDockWidget,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPlainTextEdit,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.direct_connection_page import DirectConnectionsWidget
from app.icons import get_icon
from app.port_forward_page import PortForwardsWidget
from app.proxy_jump_page import ProxyJumpsWidget
from app.settings import Settings, SettingsDialog
from app.version import GIT_SHA, __version__
from app.version_checker import GetLatestVersionThread, NewVersionDialog


class Logger(logging.Handler, QObject):
    append_to_widget = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        QObject.__init__(self)
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)
        self.append_to_widget.connect(self.widget.appendPlainText)

    def emit(self, record):
        msg = self.format(record)
        self.append_to_widget.emit(msg)


class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StaSSH")
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Version: {__version__}"))
        layout.addWidget(QLabel(f"SHA: {GIT_SHA}"))
        layout.addWidget(QLabel("Author: Campbell Brown"))
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"StaSSH {__version__}")
        self.resize(1000, 800)

        self.settings = Settings()
        self.settings.load()
        direct_connections_widget = DirectConnectionsWidget()
        proxy_jumps_widget = ProxyJumpsWidget()
        port_forwards_widget = PortForwardsWidget()

        file_menu = QMenu("&File", self)
        file_menu.addAction(get_icon("gear.png"), "&Settings", self._on_open_settings)
        file_menu.addSeparator()
        file_menu.addAction(get_icon("exit.png"), "E&xit", self.close)

        help_menu = QMenu("&Help", self)
        help_menu.addAction(get_icon("question.png"), "&About", self._on_about)

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
        log_text = QTextEdit()
        log_text.setReadOnly(True)
        log_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        log_text.setFontFamily("Consolas")  # Use a fixed width font
        log_handler = Logger(log_text)
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

    def _on_open_settings(self):
        """Show the settings dialog."""
        settings_dialog = SettingsDialog(self.settings)
        result = settings_dialog.exec_()
        if result == QDialog.DialogCode.Accepted:
            self.settings = settings_dialog.to_settings()
            self.settings.save()

    def _on_about(self):
        """Show the about dialog."""
        about_dialog = AboutDialog()
        about_dialog.exec_()

    def _on_new_version_available(self, latest_version: str, url: str, publish_date: str):
        """Show a dialog to inform the user that a new version is available."""
        if self.settings.prompt_to_download_new_version:
            new_version_dialog = NewVersionDialog(self.settings, latest_version, url, publish_date)
            new_version_dialog.exec_()
