import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QDockWidget,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.direct_connection_page import DirectConnectionsWidget
from app.version import GIT_SHA, __version__
from app.version_checker import GetLatestVersionThread, NewVersionDialog


class Logger(logging.Handler):
    def __init__(self, widget: QTextEdit):
        super().__init__()
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)


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

        direct_connections_widget = DirectConnectionsWidget()

        help_menu = QMenu("&Help", self)
        help_menu.addAction("&About", self._on_about)

        menu_bar = QMenuBar()
        menu_bar.addMenu(help_menu)
        self.setMenuBar(menu_bar)

        tabs = QTabWidget()
        tabs.addTab(direct_connections_widget, "Direct Connections")

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

    def _on_about(self):
        """Show the about dialog."""
        about_dialog = AboutDialog()
        about_dialog.exec_()

    def _on_new_version_available(self, latest_version: str, url: str, publish_date: str):
        """Show a dialog to inform the user that a new version is available."""
        new_version_dialog = NewVersionDialog(latest_version, url, publish_date)
        new_version_dialog.exec_()
