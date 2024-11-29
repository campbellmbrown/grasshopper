from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QContextMenuEvent, QIcon
from PyQt5.QtWidgets import QAction, QMenu, QTableView


class ViewBase(QTableView):
    """Base class for all table views in the application."""

    new_item = pyqtSignal()
    edit_item = pyqtSignal(int)
    duplicate_item = pyqtSignal(int)
    delete_item = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setSortingEnabled(True)

        self.new_action = QAction(QIcon("resources/new.png"), "New")
        self.edit_action = QAction(QIcon("resources/pencil.png"), "Edit")
        self.duplicate_action = QAction(QIcon("resources/duplicate.png"), "Duplicate")
        self.delete_action = QAction(QIcon("resources/x.png"), "Delete")
        self.menu = QMenu(self)
        self.menu.addAction(self.new_action)
        self.menu.addAction(self.edit_action)
        self.menu.addAction(self.duplicate_action)
        self.menu.addAction(self.delete_action)

        self.new_action.triggered.connect(self.new_item)
        self.edit_action.triggered.connect(lambda: self.edit_item.emit(self.currentIndex().row()))
        self.duplicate_action.triggered.connect(lambda: self.duplicate_item.emit(self.currentIndex().row()))
        self.delete_action.triggered.connect(lambda: self.delete_item.emit(self.currentIndex().row()))

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        index = self.indexAt(event.pos())
        is_valid = index.isValid()
        self.edit_action.setEnabled(is_valid)
        self.duplicate_action.setEnabled(is_valid)
        self.delete_action.setEnabled(is_valid)
        self.menu.exec_(event.globalPos())
