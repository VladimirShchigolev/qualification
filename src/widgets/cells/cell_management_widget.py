from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QScrollArea, QGridLayout
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property  # snake_case enabled for Pyside6

from src.models.models import Cell


class CellManagementWidget(QWidget):
    """ Widget responsible for showing all cells belonging to a given tab.
    Allows selecting cells and editing them.
    """

    def __init__(self, db_session, tab):
        super().__init__()
        self._db_session = db_session
        self._tab = tab
        self._configuration = tab.configuration

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """ Initialize UI """
        # create a layout
        self._layout = QHBoxLayout(self)

        # create a grid representation
        self._scroll_area = QScrollArea()
        self._grid_layout = QGridLayout()
        self._grid_widget = QWidget()
        self._grid_widget.set_layout(self._grid_layout)
        self._scroll_area.set_widget(self._grid_widget)
        self._scroll_area.widget_resizable = True
        self._fill_grid()

        # add widgets to layout
        self._layout.add_widget(self._scroll_area)

    def update_grid(self):
        """ Update grid representation. """

        self._clear_grid()  # clear the grid
        self._fill_grid()  # and fill it according to DB session data

    def _clear_grid(self):
        """ Delete all elements form grid layout. """
        for i in reversed(range(self._grid_layout.count()-1)):
            self._grid_layout.take_at(i).widget().delete_later()

    def _fill_grid(self):
        """ Fill grid with cells """

        cells = self._db_session.query(Cell).filter(Cell.tab == self._tab)\
            .order_by(Cell.row).order_by(Cell.column).all()

        for cell in cells:
            cell_button = QPushButton()
            #cell_button.set_height(100)
            self._grid_layout.add_widget(cell_button, cell.row, cell.column, cell.rowspan, cell.colspan)

        for row in range(self._grid_layout.row_count()):
            self._grid_layout.set_row_minimum_height(row, 100)

