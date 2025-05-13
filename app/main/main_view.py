from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QActionGroup
from PyQt6.QtWidgets import QDockWidget, QMainWindow, QMenu, QMenuBar, QTabWidget, QVBoxLayout, QWidget

from app.direct_connection_page import DirectConnectionsWidget
from app.icons import get_icon
from app.main.log_view import LogView
from app.port_forward_page import PortForwardsWidget
from app.proxy_jump_page import ProxyJumpsWidget


class MainView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(get_icon("logo_32x32.png"))
        self.resize(1000, 800)
        self._set_up_dock()
        direct_connections_widget = DirectConnectionsWidget()
        proxy_jumps_widget = ProxyJumpsWidget()
        port_forwards_widget = PortForwardsWidget()

        file_menu = QMenu("&File", self)
        preferences_menu = QMenu("&Preferences", self)
        theme_menu = QMenu("&Theme", self)
        preferences_menu.addMenu(theme_menu)

        self.open_ssh_directory_action = QAction("&Open SSH directory")
        self.light_theme_action = QAction("Light")
        self.dark_theme_action = QAction("Dark")
        self.about_action = QAction("&About")
        self.prompt_to_download_new_version_action = QAction("&Check version")

        theme_action_group = QActionGroup(self)
        theme_action_group.setExclusive(True)
        self.light_theme_action.setCheckable(True)
        self.dark_theme_action.setCheckable(True)
        theme_menu.addAction(self.light_theme_action)
        theme_menu.addAction(self.dark_theme_action)

        self.prompt_to_download_new_version_action.setCheckable(True)

        file_menu.addAction(self.open_ssh_directory_action)
        file_menu.addSeparator()
        file_menu.addMenu(preferences_menu)
        file_menu.addSeparator()
        file_menu.addAction("E&xit", self.close)

        preferences_menu.addAction(self.prompt_to_download_new_version_action)

        help_menu = QMenu("&Help", self)
        help_menu.addAction(self.about_action)

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

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def _set_up_dock(self) -> None:
        self.log_view = LogView()
        dock = QDockWidget("Log")
        dock.setWidget(self.log_view)
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)
