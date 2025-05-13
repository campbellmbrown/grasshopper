"""Controller to handle log messages and display them in the view."""

import logging

from app.main.log_view import LogView


class LogController(logging.Handler):
    def __init__(self, view: LogView) -> None:
        super().__init__()
        self.view = view
        view.clear_button.clicked.connect(view.log_text.clear)

    def add_to_logger(self) -> None:
        self.setFormatter(logging.Formatter("%(asctime)s - %(levelname)-8s - %(message)s"))
        logging.getLogger().addHandler(self)

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        self.view.log_text.appendPlainText(msg)
