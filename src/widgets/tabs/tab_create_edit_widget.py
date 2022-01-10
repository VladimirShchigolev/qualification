from PySide6.QtCore import Qt, QMargins, QRegularExpression
from PySide6.QtGui import QFont, QRegularExpressionValidator
from PySide6.QtWidgets import QWidget, QLabel, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, \
    QVBoxLayout, QComboBox, QMessageBox

from src.models.models import Tab, Cell, SensorCell
from src.widgets.cells.cell_grid_management_widget import CellGridManagementWidget
from src.widgets.cells.cell_grid_view_widget import CellGridViewWidget


class TabCreateEditWidget(QWidget):
    """Widget for creating or editing a tab."""

    def __init__(self, db_session, configuration=None, tab=None, configuration_page="view"):
        """Create tab creation/editing widget."""
        super().__init__()
        self._db_session = db_session

        # from what page this page was open (where to return later)
        self._configuration_page = configuration_page

        # define if tab is being created or edited
        if tab:
            self._tab = tab
            self._configuration = tab.configuration
            self._edit_mode = True
            self._create_backup()
        else:
            # create a new tab to edit it later
            self._tab = Tab(configuration=configuration, name="", grid_width=2, grid_height=5)
            self._configuration = configuration
            self._edit_mode = False

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """Initialize UI."""
        # create a layout
        self._layout = QVBoxLayout(self)

        self._form_layout = QFormLayout()
        self._form_layout.setHorizontalSpacing(20)
        self._form_layout.setContentsMargins(10, 0, 10, 0)

        # create a title
        self._title = QLabel()
        if self._edit_mode:
            self._title.setText(f'Edit Tab {self._tab.name}')
        else:
            self._title.setText("Create Tab")
        self._title.setFont(QFont("Lato", 18))
        self._title.setAlignment(Qt.AlignCenter)
        self._title.setContentsMargins(10, 10, 10, 20)

        # create name field display
        self._name_line = QLineEdit()
        self._name_line.setText(self._tab.name)

        # set validation rules to 1-30 characters in length
        self._name_line.setValidator(
            QRegularExpressionValidator(QRegularExpression(r'.{1,30}'))
        )

        # create a grid display
        self._grid = CellGridManagementWidget(self._db_session, self._tab)

        # if a new tab is created, set grid to default
        if not self._edit_mode:
            self._resize(0, 0, 2, 5)

        # create grid width field display
        self._grid_width_line = QComboBox()

        # fill it with width from 1 to 10
        self._grid_width_line.addItems(
            [str(number) for number in range(1, 11)]
        )
        self._grid_width_line.setCurrentText(str(self._tab.grid_width))

        # change height combobox options on width change;
        # resize grid on width change
        self._grid_width_line.currentTextChanged.connect(self._update_possible_heights)

        # create grid height field display
        self._grid_height_line = QComboBox()

        # fill it with height from 1 to 20
        self._grid_height_line.addItems(
            [str(number) for number in range(1, 21)]
        )

        self._grid_height_line.setCurrentText(str(self._tab.grid_height))

        # resize grid on height change
        self._grid_height_line.currentTextChanged.connect(self._update_height)

        # set provided height according to the chosen width
        self._update_possible_heights()

        # section of buttons
        self._buttons_layout = QHBoxLayout()
        self._buttons_layout.setContentsMargins(10, 0, 10, 0)

        self._save_button = QPushButton("Save")
        self._save_button.clicked.connect(self._save)
        self._cancel_button = QPushButton("Cancel")
        self._cancel_button.clicked.connect(self._cancel)

        self._buttons_layout.addWidget(self._save_button)

        # move cancel button to the right
        self._buttons_layout.addStretch(1)

        self._buttons_layout.addWidget(self._cancel_button)

        # add widgets to layout

        # add configurations data
        self._form_layout.addRow(self._title)
        self._form_layout.addRow("Name:", self._name_line)
        self._form_layout.addRow("Column count:", self._grid_width_line)
        self._form_layout.addRow("Row count:", self._grid_height_line)
        self._layout.addLayout(self._form_layout)
        self._layout.addWidget(self._grid)

        # add buttons
        self._layout.addLayout(self._buttons_layout)

    def _update_possible_heights(self):
        """Update provided grid height to match grid width value."""
        # get chosen value
        width = int(self._grid_width_line.currentText())

        # save current height
        current_height = int(self._grid_height_line.currentText())

        # remove onTextChange event handler while editing
        self._grid_height_line.currentTextChanged.disconnect(self._update_height)
        self._grid_height_line.clear()  # clear all units

        # maximal cell count per tab is 100 and maximal height is 20
        maximal_height = min(20, 100 // width)

        # add height values for chosen width
        self._grid_height_line.addItems(
            [str(possible_height) for possible_height in range(1, maximal_height + 1)]
        )

        # if current height is no longer possible,
        # change it to maximal possible
        if current_height > maximal_height:
            self._grid_height_line.setCurrentText(str(maximal_height))
        else:  # otherwise set to previous value
            self._grid_height_line.setCurrentText(str(current_height))

        # add event handler back when editing is finished
        self._grid_height_line.currentTextChanged.connect(self._update_height)

        # resize grid
        self._resize(self._tab.grid_width, self._tab.grid_height, width, self._tab.grid_height)

    def _update_height(self):
        """Resize the grid on height change."""
        # get chosen value
        height = int(self._grid_height_line.currentText())

        self._resize(self._tab.grid_width, self._tab.grid_height, self._tab.grid_width,
                     height)  # resize the grid

    def _resize(self, old_width, old_height, new_width, new_height):
        """Resize the grid.
        Resize the grid by deleting old cells if new height
        or new width are smaller than the old ones. Create new
        cells if new width or new height are greater than the old ones.
        If resizing splits a cell in half -
        split this cell into atomic cells.
        """
        def split_cell(cell):
            """Split cell into atomic cells."""
            # create all others atomic cells
            for row in range(cell.row, cell.row + cell.rowspan):
                for column in range(cell.column, cell.column + cell.colspan):
                    if row != cell.row or column != cell.column:
                        # create an atomic cell
                        Cell(tab=self._tab, row=row, column=column)

            # set upper left cell's rowspan and colspan to 1
            cell.rowspan = 1
            cell.colspan = 1

        cells = self._db_session.query(Cell).filter(Cell.tab == self._tab).all()
        for cell in cells:
            if cell.row < new_height < cell.row + cell.rowspan \
                    or cell.column < new_width < cell.column + cell.colspan:
                split_cell(cell)

        # delete cells that are beyond new grid size
        self._db_session.query(Cell).filter(Cell.tab == self._tab) \
            .filter(Cell.column >= new_width).delete(synchronize_session=False)

        self._db_session.query(Cell).filter(Cell.tab == self._tab) \
            .filter(Cell.row >= new_height).delete(synchronize_session=False)

        # create new cells to fill grid up to the new size
        for column in range(old_width, new_width):
            for row in range(new_height):
                Cell(tab=self._tab, row=row, column=column)

        for row in range(old_height, new_height):
            for column in range(min(new_width, old_width)):
                Cell(tab=self._tab, row=row, column=column)

        # update the tab data
        self._tab.grid_width = new_width
        self._tab.grid_height = new_height
        self._grid.update_grid()

    def _create_backup(self):
        """Create a backup for reverting changes later if needed."""
        # create a backup tab
        self._backup_tab = Tab(configuration=self._configuration, name="",
                               grid_width=self._tab.grid_width,
                               grid_height=self._tab.grid_height)

        # get all the cells of the tab and create their backups
        cells = self._db_session.query(Cell).filter(Cell.tab == self._tab).all()
        for cell in cells:
            Cell(tab=self._backup_tab, row=cell.row, column=cell.column, rowspan=cell.rowspan,
                 colspan=cell.colspan,
                 title=cell.title)

        # get all the sensor-cell records and create their backups
        sensor_cells = self._db_session.query(SensorCell) \
            .join(Cell) \
            .filter(Cell.tab == self._tab) \
            .all()

        for sensor_cell in sensor_cells:
            # find the backup of the cell
            cell = self._db_session.query(Cell) \
                .filter(Cell.tab == self._backup_tab) \
                .filter(Cell.row == sensor_cell.cell.row) \
                .filter(Cell.column == sensor_cell.cell.column) \
                .one_or_none()

            if cell:
                SensorCell(cell=cell, sensor=sensor_cell.sensor)

    def _save(self):
        """Save tab from data in the form."""
        # get data from the form
        name = self._name_line.text()
        grid_width = int(self._grid_width_line.currentText())
        grid_height = int(self._grid_height_line.currentText())

        # check for duplicates is needed
        # only when tab name gets changed
        check_for_duplicates = name != self._tab.name

        # check if data is valid
        validation_passed = False
        try:
            validation_passed = Tab.validate(self._configuration, name, grid_width, grid_height,
                                             db_session=self._db_session,
                                             check_for_duplicates=check_for_duplicates)
        except ValueError as error:
            QMessageBox.critical(self, "Error!", str(error), QMessageBox.Ok,
                                 QMessageBox.Ok)  # show error message

        if validation_passed:  # if data is valid
            # set data to created/edited tab object
            self._tab.configuration = self._configuration
            self._tab.name = name
            self._tab.grid_width = grid_width
            self._tab.grid_height = grid_height

            # remove the backup tab if in editing mode
            if self._edit_mode:
                self._db_session.delete(self._backup_tab)

            # set message according to selected mode (create or edit)
            if self._edit_mode:
                message = f'Tab {self._tab.name} updated successfully!'
            else:
                message = f'Tab {self._tab.name} created successfully!'

            # show success message
            QMessageBox.information(self, "Success!", message,
                                    QMessageBox.Ok, QMessageBox.Ok)

            # redirect to configurations
            self._return_to_configuration()

    def _cancel(self):
        """Revert changes and open back
        the configurations creation/editing page."""
        # revert changes
        if self._edit_mode:
            tab_name = self._tab.name
            self._db_session.delete(self._tab)
            self._backup_tab.name = tab_name
        else:
            self._db_session.delete(self._tab)  # remove created tab

        self._return_to_configuration()

    def _return_to_configuration(self):
        """Open back the configurations creation/editing/view page."""
        if self._configuration_page == "edit":
            self.parentWidget().edit_configuration(self._configuration)
        elif self._configuration_page == "create":
            self.parentWidget().create_configuration(self._configuration)
        else:
            self.parentWidget().view_configuration(self._configuration)
