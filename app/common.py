from PyQt6.QtCore import QItemSelectionModel, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QContextMenuEvent, QKeyEvent
from PyQt6.QtWidgets import QMenu, QTableView

from app.utility.resource_provider import get_icon


class StyleSheets:
    TRANSPARENT_TOOLBUTTON = """
        QToolButton {
            background-color: transparent;
            padding: 5px;
            border: none;
        }
        QToolButton:hover {
            background-color: rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(0, 0, 0, 0.3);
        }
    """


class ViewBase(QTableView):
    """Base class for all table views in the application."""

    item_activated = pyqtSignal(int)
    new_item = pyqtSignal()
    edit_item = pyqtSignal(int)
    duplicate_item = pyqtSignal(int)
    delete_item = pyqtSignal(int)
    copy_command = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setSortingEnabled(False)

        self.new_action = QAction(get_icon("new.png"), "New")
        self.edit_action = QAction(get_icon("pencil.png"), "Edit")
        self.duplicate_action = QAction(get_icon("duplicate.png"), "Duplicate")
        self.delete_action = QAction(get_icon("x.png"), "Delete")
        self.copy_command_action = QAction(get_icon("copy-command.png"), "Copy Command")
        self.menu = QMenu(self)
        self.menu.addAction(self.new_action)
        self.menu.addAction(self.edit_action)
        self.menu.addAction(self.duplicate_action)
        self.menu.addAction(self.delete_action)
        self.menu.addSeparator()
        self.menu.addAction(self.copy_command_action)

        self.doubleClicked.connect(lambda: self.item_activated.emit(self.currentIndex().row()))
        self.new_action.triggered.connect(self.new_item)
        self.edit_action.triggered.connect(lambda: self.edit_item.emit(self.currentIndex().row()))
        self.duplicate_action.triggered.connect(lambda: self.duplicate_item.emit(self.currentIndex().row()))
        self.delete_action.triggered.connect(lambda: self.delete_item.emit(self.currentIndex().row()))
        self.copy_command_action.triggered.connect(lambda: self.copy_command.emit(self.currentIndex().row()))

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        index = self.indexAt(event.pos())
        is_valid = index.isValid()
        self.edit_action.setEnabled(is_valid)
        self.duplicate_action.setEnabled(is_valid)
        self.delete_action.setEnabled(is_valid)
        self.copy_command_action.setEnabled(is_valid)
        self.menu.exec(event.globalPos())

    def keyPressEvent(self, event: QKeyEvent):
        if self.currentIndex().isValid():
            if event.key() == Qt.Key.Key_Delete:
                self.delete_item.emit(self.currentIndex().row())
            elif event.key() == Qt.Key.Key_Return:
                self.item_activated.emit(self.currentIndex().row())
            elif event.key() == Qt.Key.Key_Escape:
                selection_model = self.selectionModel()
                assert isinstance(selection_model, QItemSelectionModel)
                selection_model.clearSelection()
                selection_model.clearCurrentIndex()
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)
