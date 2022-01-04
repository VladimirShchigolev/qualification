from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QScrollArea, QGridLayout, \
    QSizePolicy

from src.models.models import Cell
from src.widgets.cells.cell_view_widget import CellViewWidget


class CellGridViewWidget(QWidget):
    """ Widget responsible for showing all cells of the tab."""

    def __init__(self, db_session, tab):
        """Create grid view widget."""
        super().__init__()
        self._db_session = db_session
        self._tab = tab
        self._configuration = tab.configuration

        self._selected_cells = set()  # set of selected cells
        self._cells = {}  # dictionary for buttons

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """Initialize UI."""
        # create a layout
        self._layout = QHBoxLayout(self)

        # create a grid representation
        self._scroll_area = QScrollArea()
        self._grid_layout = QGridLayout()
        self._grid_widget = QWidget()
        self._grid_widget.setLayout(self._grid_layout)
        self._scroll_area.setWidget(self._grid_widget)
        self._scroll_area.setWidgetResizable(True)
        self._fill_grid()

        # create a placeholder for cell view widget
        self._right_widget = QWidget()
        self._right_widget.setMinimumWidth(250)
        self._right_widget.setMaximumWidth(250)

        # add widgets to layout
        self._layout.addWidget(self._scroll_area)
        self._layout.addWidget(self._right_widget)

    def update_grid(self):
        """Update grid representation."""
        self._clear_grid()  # clear the grid
        self._fill_grid()  # and fill it according to DB session data

    def _clear_grid(self):
        """Delete all elements from grid layout."""
        self._cells.clear()
        self._selected_cells = set()
        for i in range(self._grid_layout.count() - 1, -1, -1):
            self._grid_layout.takeAt(i).widget().deleteLater()

    def _fill_grid(self):
        """Fill grid with cells."""
        cells = self._db_session.query(Cell).filter(Cell.tab == self._tab) \
            .order_by(Cell.row).order_by(Cell.column).all()

        for cell in cells:
            cell_button = QPushButton()
            cell_button.setText(cell.title)
            self._cells[(cell.row, cell.column)] = (cell_button, cell)

            cell_button.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
            cell_button.setMinimumSize(40, 80)
            self._grid_layout.addWidget(cell_button, cell.row, cell.column, cell.rowspan,
                                        cell.colspan)

            # add cell selection management on button click
            cell_button.clicked.connect(
                (
                    lambda cell_row, cell_column: lambda: self._press_cell_button(cell_row,
                                                                                  cell_column)
                )(cell.row, cell.column)
            )

        # set minimum height for rows
        for row in range(self._grid_layout.rowCount()):
            self._grid_layout.setRowMinimumHeight(row, 40)
            self._grid_layout.setRowStretch(row, 1)
        for column in range(self._grid_layout.columnCount()):
            self._grid_layout.setColumnStretch(column, 1)

    def _press_cell_button(self, row, column):
        """Manages cell selection when pressing cell buttons."""
        # set right widget according to the selected cell

        # remove old widget
        self._layout.removeWidget(self._right_widget)
        self._right_widget.deleteLater()

        # set a cell editing widget
        self._right_widget = CellViewWidget(self._db_session, self._cells[(row, column)][1])

        self._right_widget.setMinimumWidth(250)
        self._right_widget.setMaximumWidth(250)
        self._layout.addWidget(self._right_widget)
