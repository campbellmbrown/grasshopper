import sys

from PyQt6.QtWidgets import QApplication

from app.main.main_controller import MainController
from app.main.main_view import MainView

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_view = MainView()
    main_controller = MainController(main_view)

    main_view.show()
    app.exec()
