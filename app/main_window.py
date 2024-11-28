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
from app.version import __version__


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

    def _on_about(self):
        about_dialog = AboutDialog()
        about_dialog.exec_()
