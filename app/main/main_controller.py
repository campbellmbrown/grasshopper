import logging

from app.main.log_controller import LogController
from app.main.main_view import MainView
from app.version import __version__


class MainController:
    def __init__(self, view: MainView) -> None:
        view.setWindowTitle(f"Grasshopper {__version__}")

        # set up logging
        app_logger_handler = LogController(view.log_view)
        app_logger_handler.add_to_logger()
        logging.getLogger().setLevel(logging.INFO)

        logging.info("v%s", __version__)
