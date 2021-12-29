from PySide6.QtCore import Qt, QMargins, QRegularExpression
from PySide6.QtGui import QFont, QRegularExpressionValidator
from PySide6.QtWidgets import QWidget, QLabel, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QVBoxLayout, \
    QComboBox, QMessageBox
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property  # snake_case enabled for Pyside6

from src.models.models import Tab, Cell, SensorCell
from src.widgets.cells.cell_grid_management_widget import CellGridManagementWidget


class TabCreateEditWidget(QWidget):
    """ Widget for creating or editing a tab """

    def __init__(self, db_session, configuration=None, tab=None):
        super().__init__()
        self._db_session = db_session

        # define if tab is being created or edited
        if tab:
            self._tab = tab
            self._configuration = configuration
            self._edit_mode = True
        else:
            # create a new tab to edit it later
            self._tab = Tab(configuration=configuration, name="", grid_width=2, grid_height=5)
            self._configuration = configuration
            self._edit_mode = False

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """ Initialize UI """
        # create a layout
        self._layout = QVBoxLayout(self)

        self._form_layout = QFormLayout()
        self._form_layout.horizontal_spacing = 20
        self._form_layout.contents_margins = QMargins(10, 0, 10, 0)

        # create a title
        self._title = QLabel()
        if self._edit_mode:
            self._title.text = f'Edit tab {self._tab.name}'
        else:
            self._title.text = "Create Tab"
        self._title.font = QFont("Lato", 18)
        self._title.alignment = Qt.AlignCenter
        self._title.set_contents_margins(10, 10, 10, 20)

        # create name field display
        self._name_line = QLineEdit()
        self._name_line.text = self._tab.name

        # set validation rules to 1-30 characters in length
        self._name_line.set_validator(
            QRegularExpressionValidator(QRegularExpression(r'.{1,30}'))
        )

        # create a grid display
        self._grid = CellGridManagementWidget(self._db_session, self._tab)
        if not self._edit_mode:
            self._resize(0, 0, 2, 5)  # if a new tab is created, set grid to default

        # create grid width field display
        self._grid_width_line = QComboBox()
        self._grid_width_line.add_items(  # fill it with integers from 1 to 10
            [str(number) for number in range(1, 11)]
        )
        self._grid_width_line.current_text = str(self._tab.grid_width)

        # change height combobox options on width change; resize grid on width change
        self._grid_width_line.currentTextChanged.connect(self._update_possible_heights)

        # create grid height field display
        self._grid_height_line = QComboBox()
        self._grid_height_line.add_items(  # fill it with integers from 1 to 20
            [str(number) for number in range(1, 21)]
        )
        self._grid_height_line.current_text = str(self._tab.grid_height)
        # resize grid on height change
        self._grid_height_line.currentTextChanged.connect(self._update_height)

        self._update_possible_heights()  # set provided height according to the chosen width

        # section of buttons
        self._buttons_layout = QHBoxLayout()
        self._buttons_layout.contents_margins = QMargins(10, 0, 10, 0)

        self._save_button = QPushButton("Save")
        self._save_button.clicked.connect(self._save)
        self._cancel_button = QPushButton("Cancel")
        self._cancel_button.clicked.connect(self._cancel)

        self._buttons_layout.add_widget(self._save_button)
        self._buttons_layout.add_stretch(1)  # move cancel button to the right
        self._buttons_layout.add_widget(self._cancel_button)

        # add widgets to layout
        # add configuration data
        self._form_layout.add_row(self._title)
        self._form_layout.add_row("Name:", self._name_line)
        self._form_layout.add_row("Column count:", self._grid_width_line)
        self._form_layout.add_row("Row count:", self._grid_height_line)
        self._layout.add_layout(self._form_layout)
        self._layout.add_widget(self._grid)

        # add buttons
        self._layout.add_layout(self._buttons_layout)

    def _update_possible_heights(self):
        """ update provided grid height values according to chosen grid width value """

        width = int(self._grid_width_line.current_text)  # get chosen value

        current_height = int(self._grid_height_line.current_text)  # save current height

        # remove onTextChange event handler while editing
        self._grid_height_line.currentTextChanged.disconnect(self._update_height)
        self._grid_height_line.clear()  # clear all units

        maximal_height = min(20, 100 // width)  # maximal cell count per tab is 100 and maximal height is 20

        # add height values for chosen width
        self._grid_height_line.add_items(
            [str(possible_height) for possible_height in range(1, maximal_height + 1)]
        )

        # if current height is no longer possible, change it to maximal possible
        if current_height > maximal_height:
            self._grid_height_line.current_text = str(maximal_height)
        else:  # otherwise set to previous value
            self._grid_height_line.current_text = str(current_height)

        # add event handler back when editing is finished
        self._grid_height_line.currentTextChanged.connect(self._update_height)

        # resize grid
        self._resize(self._tab.grid_width, self._tab.grid_height, width, self._tab.grid_height)

    def _update_height(self):
        """ Resize the grid on height change """

        height = int(self._grid_height_line.current_text)  # get chosen value

        self._resize(self._tab.grid_width, self._tab.grid_height, self._tab.grid_width, height)  # resize the grid

    def _resize(self, old_width, old_height, new_width, new_height):
        """ Resize the grid
        Resize the grid by deleting old cells if new height or new width are smaller than the old ones. Create new
        cells if new width or new height are greater than the old ones.
        """

        # delete cells that are beyond new grid size
        self._db_session.query(Cell).filter(Cell.tab == self._tab) \
            .filter(Cell.column >= new_width).delete(synchronize_session=False)

        self._db_session.query(Cell).filter(Cell.tab == self._tab) \
            .filter(Cell.row >= new_height).delete(synchronize_session=False)

        # create new cells to fill grid up to the new size
        for column in range(old_width, new_width):
            for row in range(new_height):
                print(row, column)
                Cell(tab=self._tab, row=row, column=column)

        for row in range(old_height, new_height):
            for column in range(min(new_width, old_width)):
                print(row, column)
                Cell(tab=self._tab, row=row, column=column)

        self._tab.grid_width = new_width
        self._tab.grid_height = new_height
        self._grid.update_grid()

    def _save(self):
        """ Create a tab from data in the form """

        # get data from the form
        name = self._name_line.text
        grid_width = self._grid_width_line.current_text
        grid_height = self._grid_height_line.current_text

        # determine if check for duplicates is needed
        check_for_duplicates = name != self._tab.name  # needed only when tab name gets changed

        # check if data is valid
        validation_passed = False
        try:
            validation_passed = Tab.validate(self._configuration, name, grid_width, grid_height,
                                             db_session=self._db_session, check_for_duplicates=check_for_duplicates)
        except ValueError as error:
            QMessageBox.critical(self, "Error!", str(error), QMessageBox.Ok, QMessageBox.Ok)  # show error message

        if validation_passed:  # if data is valid
            # set data to created/edited tab object
            self._tab.configuration = self._configuration
            self._tab.name = name
            self._tab.grid_width = grid_width
            self._tab.grid_height = grid_height

            # set message according to selected mode (create or edit)
            if self._edit_mode:
                message = f'Tab {self._tab.name} updated successfully!'
            else:
                message = f'Tab {self._tab.name} created successfully!'

            QMessageBox.information(self, "Success!", message,
                                    QMessageBox.Ok, QMessageBox.Ok)  # show success message

            self._return_to_configuration()  # redirect to configuration

    def _cancel(self):
        """ revert changes and open back the configuration creation/editing page """

        # revert changes
        if self._edit_mode:
            pass
        else:
            self._db_session.delete(self._tab)  # remove created tab

        self._return_to_configuration()

    def _return_to_configuration(self):
        """ revert changes and open back the configuration creation/editing page """
        self.parent_widget().view_configuration(self._configuration)
