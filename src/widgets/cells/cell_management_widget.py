from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QScrollArea, QGridLayout, QSizePolicy, QMessageBox
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property  # snake_case enabled for Pyside6

from src.models.models import Cell
from src.widgets.cells.cell_edit_widget import CellEditWidget


class CellManagementWidget(QWidget):
    """ Widget responsible for showing all cells belonging to a given tab.
    Allows selecting cells and editing them.
    """

    def __init__(self, db_session, tab):
        super().__init__()
        self._db_session = db_session
        self._tab = tab
        self._configuration = tab.configuration

        self._selected_cells = set()  # set of selected cells
        self._cells = {}  # dictionary for buttons

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

        # create a placeholder for cell editing widget
        self._right_widget = QWidget()
        self._right_widget.minimum_width = 250
        self._right_widget.maximum_width = 250

        # add widgets to layout
        self._layout.add_widget(self._scroll_area)
        self._layout.add_widget(self._right_widget)

    def update_grid(self):
        """ Update grid representation. """

        self._clear_grid()  # clear the grid
        self._fill_grid()  # and fill it according to DB session data

    def _clear_grid(self):
        """ Delete all elements form grid layout. """
        self._cells.clear()
        self._selected_cells = set()
        for i in range(self._grid_layout.count()-1, -1, -1):
            self._grid_layout.take_at(i).widget().delete_later()

    def _fill_grid(self):
        """ Fill grid with cells """

        cells = self._db_session.query(Cell).filter(Cell.tab == self._tab)\
            .order_by(Cell.row).order_by(Cell.column).all()

        print(cells)

        for cell in cells:
            cell_button = QPushButton()
            cell_button.checkable = True
            self._cells[(cell.row, cell.column)] = (cell_button, cell)

            cell_button.size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            cell_button.minimum_height = 40
            cell_button.minimum_width = 80
            self._grid_layout.add_widget(cell_button, cell.row, cell.column, cell.rowspan, cell.colspan)

            # add cell selection management on button click
            cell_button.toggled.connect(
                (
                    lambda cell_row, cell_column: lambda: self._press_cell_button(cell_row, cell_column)
                )(cell.row, cell.column)
            )

        # set minimum height for rows
        for row in range(self._grid_layout.row_count()):
            self._grid_layout.set_row_minimum_height(row, 40)

    def _press_cell_button(self, row, column):
        """ Manages cell selection when pressing cell buttons """

        # enable (if not enabled) or disable (if enabled) cell selection
        if (row, column) in self._selected_cells:
            self._selected_cells.remove((row, column))
        else:
            self._selected_cells.add((row, column))

        # set right widget according to selected cells
        self._layout.remove_widget(self._right_widget)  # remove old widget
        self._right_widget.deleteLater()

        if len(self._selected_cells) == 0:  # if no cells selected
            # set a placeholder widget
            self._right_widget = QWidget()

        elif len(self._selected_cells) == 1:  # if exactly one cell is selected
            # set a cell editing widget
            self._right_widget = CellEditWidget(self._db_session, self._cells[(row, column)][1])
        else:
            # set a cell merging widget
            self._set_cell_merging_widget()

        self._right_widget.minimum_width = 250
        self._layout.add_widget(self._right_widget)

    def _set_cell_merging_widget(self):
        """ Set right widget to cell merging widget """
        self._right_widget = QWidget()
        inner_layout = QHBoxLayout(self._right_widget)

        self._merge_button = QPushButton("Merge Cells")
        self._merge_button.minimum_height = 40
        inner_layout.add_widget(self._merge_button)

        self._merge_button.clicked.connect(self._merge_selected_cells)

    def _merge_selected_cells(self):
        """ Merge selected cells if they are forming a rectangle """

        if len(self._selected_cells) < 2:
            # show error message
            QMessageBox.critical(self, "Error!", "Can merge only two or more cells", QMessageBox.Ok, QMessageBox.Ok)
            return

        def is_rectangular_selection(selected_cells, all_cells, grid_size):
            """ Check if selected cells form a rectangle """
            # create empty grid selection
            grid = [[False for column in range(grid_size[1])] for row in range(grid_size[0])]

            def fill_cell(row, column, rowspan, colspan):
                """ Fill atomic cells (1x1) of a given cell (N x M) as selected """
                for i in range(row, row + rowspan):
                    for j in range(column, column + colspan):
                        grid[i][j] = True

            def is_spanning_rectangle(grid, upper_left_cell, lower_right_cell):
                """ Check if selected cells of the grid create a rectangle
                with given left upper and right lower corners"""

                spanning_rectangle = True
                for row in range(len(grid)):
                    for column in range(len(grid[0])):
                        # if cell is inside the spanning rectangle
                        if upper_left_cell[0] <= row <= lower_right_cell[0]\
                                and upper_left_cell[1] <= column <= lower_right_cell[1]:

                            spanning_rectangle &= grid[row][column]  # it should be marked as selected
                        else:  # if it's outside the spanning rectangle
                            spanning_rectangle &= not grid[row][column]  # it should be marked as not selected
                # if contradiction was found, selection does not form a rectangle
                return spanning_rectangle

            # fill the grid of atomic cells (1 x 1) - are these cells in selection or not
            for cell_position in selected_cells:
                cell = all_cells[cell_position][1]
                fill_cell(cell.row, cell.column, cell.rowspan, cell.colspan)

            # find upper left atomic (1x1) cell
            upper_left_corners = sorted(selected_cells)
            upper_left_cell = upper_left_corners[0]

            # find lower right atomic (1x1) cell
            lower_right_corners = []
            for cell_position in selected_cells:
                cell = self._cells[cell_position][1]
                # append lower right corner of each cell
                lower_right_corners.append((cell.row + cell.rowspan, cell.column + cell.colspan))
            lower_right_corners.sort()
            lower_right_cell = lower_right_corners[-1]  # corner by 1 further from selection in each direction
            lower_right_cell = lower_right_cell[0] - 1, lower_right_cell[1] - 1  # selected corner

            print(grid)
            print(upper_left_cell, lower_right_cell)

            return is_spanning_rectangle(grid, upper_left_cell, lower_right_cell)

        if is_rectangular_selection(self._selected_cells, self._cells, (self._tab.grid_height, self._tab.grid_width)):
            print("Yes")
        else:
            print("No")

