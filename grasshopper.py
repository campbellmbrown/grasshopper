import sys

from PySide6.QtWidgets import QApplication

from app.dialogs.exception_view import ExceptionView
from app.main.main_controller import MainController
from app.main.main_view import MainView
from app.model.model import Model

if __name__ == "__main__":
    sys.excepthook = ExceptionView.show_exception_dialog
    app = QApplication(sys.argv)

    model = Model()
    main_view = MainView()
    main_controller = MainController(main_view, model)

    main_view.show()
    sys.exit(app.exec())
