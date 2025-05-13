import sys

from PyQt6.QtWidgets import QApplication

from app.main.main_controller import MainController
from app.main.main_view import MainView
from app.ssh_model import SshModel

if __name__ == "__main__":
    app = QApplication(sys.argv)

    ssh_model = SshModel()
    main_view = MainView()
    main_controller = MainController(main_view, ssh_model)

    main_view.show()
    app.exec()
