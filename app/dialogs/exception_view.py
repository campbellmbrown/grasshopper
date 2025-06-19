import sys
import traceback
from types import TracebackType

from PySide6.QtWidgets import QApplication, QMessageBox

from app.utility.resource_provider import get_icon


class ExceptionView(QMessageBox):
    def __init__(self, exc_type: type[BaseException], exc_value: BaseException, exc_tb: TracebackType | None) -> None:
        super().__init__()
        self.setIcon(QMessageBox.Icon.Critical)
        try:
            self.setWindowIcon(get_icon("logo_32x32.png"))
        except Exception:
            pass
        self.setWindowTitle("Unhandled Exception")
        self.setText(f"An unhandled exception occurred: {exc_value}")

        exception_details = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        self.setDetailedText(exception_details)

    @staticmethod
    def show_exception_dialog(
        exc_type: type[BaseException], exc_value: BaseException, exc_tb: TracebackType | None
    ) -> None:
        # Let the exception propagate to the default handler so code editors can show the traceback.
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        dialog = ExceptionView(exc_type, exc_value, exc_tb)
        dialog.raise_()
        dialog.exec()
        QApplication.exit(1)
