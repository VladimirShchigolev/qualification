from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QScrollArea, QGridLayout, \
    QSizePolicy, QMessageBox

from src.models.models import Cell, SensorCell
from src.widgets.cells.cell_edit_widget import CellEditWidget


class CellGridManagementWidget(QWidget):
    """Widget responsible for showing all cells belonging to a tab."""

    def __init__(self, db_session, tab):
        """Create grid management widget."""
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

        # create a placeholder for cell editing widget
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
        self._grid_layout.deleteLater()
        self._grid_widget.deleteLater()

        self._grid_layout = QGridLayout()
        self._grid_widget = QWidget()
        self._grid_widget.setLayout(self._grid_layout)
        self._scroll_area.setWidget(self._grid_widget)

    def _fill_grid(self):
        """Fill grid with cells."""
        cells = self._db_session.query(Cell).filter(Cell.tab == self._tab) \
            .order_by(Cell.row).order_by(Cell.column).all()

        for cell in cells:
            cell_button = QPushButton()
            cell_button.setText(cell.title)
            cell_button.setCheckable(True)
            self._cells[(cell.row, cell.column)] = (cell_button, cell)

            cell_button.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
            cell_button.setMinimumSize(80, 40)
            self._grid_layout.addWidget(cell_button, cell.row, cell.column, cell.rowspan,
                                        cell.colspan)

            # add cell selection management on button click
            cell_button.toggled.connect(
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
        # enable (if not enabled) or disable (otherwise) cell selection
        if (row, column) in self._selected_cells:
            self._selected_cells.remove((row, column))
        else:
            self._selected_cells.add((row, column))

        # set right widget according to selected cells

        # remove old widget
        self._layout.removeWidget(self._right_widget)
        self._right_widget.deleteLater()

        if len(self._selected_cells) == 0:  # if no cells selected
            # set a placeholder widget
            self._right_widget = QWidget()

        elif len(self._selected_cells) == 1:
            # if exactly one cell is selected set a cell editing widget

            # get selected cell's coordinates
            row, column = next(iter(self._selected_cells))
            self._right_widget = CellEditWidget(self._db_session, self._cells[(row, column)][1])
        else:
            # set a cell merging widget
            self._set_cell_merging_widget()

        self._right_widget.setMinimumWidth(250)
        self._right_widget.setMaximumWidth(250)
        self._layout.addWidget(self._right_widget)

    def _set_cell_merging_widget(self):
        """Set right widget to cell merging widget."""
        self._right_widget = QWidget()
        inner_layout = QHBoxLayout(self._right_widget)

        self._merge_button = QPushButton("Merge Cells")
        self._merge_button.setMinimumHeight(40)
        inner_layout.addWidget(self._merge_button)

        self._merge_button.clicked.connect(self._merge_selected_cells)

    def _merge_selected_cells(self):
        """Merge selected cells if they are forming a rectangle."""

        def is_rectangular_selection(selected_cells, all_cells, grid_size):
            """Check if selected cells form a rectangle."""
            # create empty grid selection
            grid = [[False for column in range(grid_size[1])] for row in range(grid_size[0])]

            def fill_cell(row, column, rowspan, colspan):
                """Fill grid with selected cell as atomic cells."""
                for i in range(row, row + rowspan):
                    for j in range(column, column + colspan):
                        grid[i][j] = True

            def is_spanning_rectangle(grid, upper_left_cell, lower_right_cell):
                """Check if selected cells create a rectangle
                with given left upper and right lower corners."""
                spanning_rectangle = True
                for row in range(len(grid)):
                    for column in range(len(grid[0])):
                        # if cell is inside the spanning rectangle
                        if upper_left_cell[0] <= row <= lower_right_cell[0] \
                                and upper_left_cell[1] <= column <= lower_right_cell[1]:

                            # it should be marked as selected
                            # otherwise it's not a spanning rectangle
                            if not grid[row][column]:
                                spanning_rectangle = False
                                break
                        else:  # if it's outside the spanning rectangle
                            # it should be marked as not selected
                            # otherwise it's not a spanning rectangle
                            if grid[row][column]:
                                spanning_rectangle = False
                                break

                    if not spanning_rectangle:
                        break  # stop if contradiction was found

                return spanning_rectangle

            # fill the grid of atomic cells (1 x 1) -
            # are these cells in selection or not
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

            # corner by 1 further from selection in each direction
            lower_right_cell = lower_right_corners[-1]

            # selected corner
            lower_right_cell = lower_right_cell[0] - 1, lower_right_cell[1] - 1

            return is_spanning_rectangle(grid, upper_left_cell, lower_right_cell)

        if len(self._selected_cells) < 2:
            # show error message
            QMessageBox.critical(self, "Error!", "Can merge only two or more cells!",
                                 QMessageBox.Ok, QMessageBox.Ok)
            return

        if is_rectangular_selection(self._selected_cells, self._cells,
                                    (self._tab.grid_height, self._tab.grid_width)):
            self._merge_cell_rectangle()
        else:
            QMessageBox.critical(self, "Error!", "Can merge only cells that form a rectangle!",
                                 QMessageBox.Ok, QMessageBox.Ok)

    def _merge_cell_rectangle(self):
        """Merge selected rectangle of cells into one cell."""
        selected_cells = sorted(self._selected_cells)

        # select a cell to be the one after merging (main cell)
        for cell_coordinates in selected_cells:
            cell = self._cells[cell_coordinates][1]
            # check if cell contains sensors
            has_sensor_assigned = self._db_session.query(SensorCell) \
                .filter(SensorCell.cell == cell) \
                .first()

            # set the upper left cell with sensors as the main cell
            if has_sensor_assigned:
                main_cell = cell
                break
        else:  # if no such main cell is found,
            # set left upper selected cell to be main cell
            main_cell = self._cells[selected_cells[0]][1]

        # calculate new (main) cell coordinates and span
        upper_left_cell_coordinates = selected_cells[0]

        # calculate lower right corner of the selection
        lower_right_borders = []
        for cell_coordinates in selected_cells:
            cell = self._cells[cell_coordinates][1]
            lower_right_borders.append((cell.row + cell.rowspan, cell.column + cell.colspan))
        lower_right_borders.sort()

        lower_right_border = lower_right_borders[-1]

        rowspan = lower_right_border[0] - upper_left_cell_coordinates[0]
        colspan = lower_right_border[1] - upper_left_cell_coordinates[1]

        # set main cell to span over all selected cells
        main_cell.row = upper_left_cell_coordinates[0]
        main_cell.column = upper_left_cell_coordinates[1]
        main_cell.rowspan = rowspan
        main_cell.colspan = colspan

        # delete all selected cells except the main cell
        self._db_session.query(Cell) \
            .filter(Cell.tab == self._tab) \
            .filter(Cell.row >= main_cell.row) \
            .filter(Cell.row < main_cell.row + main_cell.rowspan) \
            .filter(Cell.column >= main_cell.column) \
            .filter(Cell.column < main_cell.column + main_cell.colspan) \
            .filter(Cell.id != main_cell.id) \
            .delete()

        self.update_grid()
        self._cells[main_cell.row, main_cell.column][0].toggle()

    def split_selected_cell(self):
        """Split selected cell into atomic (1x1) cells."""
        # check if only one cell is selected
        if len(self._selected_cells) > 1:
            # show error message
            QMessageBox.critical(self, "Error!", "Can split only one cell!", QMessageBox.Ok,
                                 QMessageBox.Ok)
            return

        # check if selected cell can be split (is not atomic 1x1 cell)

        # get the only selected cell
        cell = self._cells[next(iter(self._selected_cells))][1]

        if cell.rowspan == 1 and cell.colspan == 1:
            # show error message
            QMessageBox.critical(self, "Error!", "Selected cell cannot be split!", QMessageBox.Ok,
                                 QMessageBox.Ok)
            return

        # create all others atomic cells
        for row in range(cell.row, cell.row + cell.rowspan):
            for column in range(cell.column, cell.column + cell.colspan):
                if row != cell.row or column != cell.column:
                    # create an atomic cell
                    Cell(tab=self._tab, row=row, column=column)

        # set upper left cell's rowspan and colspan to 1
        cell.rowspan = 1
        cell.colspan = 1

        # remove cell selection
        self._cells[cell.row, cell.column][0].toggle()

        self.update_grid()

    def update_cell_title(self, cell):
        """Update cell title in it's grid representation."""
        self._cells[cell.row, cell.column][0].setText(cell.title)
