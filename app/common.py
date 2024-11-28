from PyQt5.QtWidgets import QTableView


class ViewBase(QTableView):
    """Base class for all table views in the application."""

    def __init__(self):
        super().__init__()
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setSortingEnabled(True)
