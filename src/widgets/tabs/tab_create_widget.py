from PySide6.QtCore import Qt, QMargins, QRegularExpression
from PySide6.QtGui import QFont, QRegularExpressionValidator
from PySide6.QtWidgets import QWidget, QLabel, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QVBoxLayout, \
    QComboBox, QMessageBox
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property  # snake_case enabled for Pyside6

from src.models.models import Tab


class TabCreateWidget(QWidget):
    """ Widget for creating a tab """

    def __init__(self, db_session, configuration):
        super().__init__()
        self._db_session = db_session
        self._configuration = configuration

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
        self._title.text = "Create Tab"
        self._title.font = QFont("Lato", 18)
        self._title.alignment = Qt.AlignCenter
        self._title.set_contents_margins(10, 10, 10, 20)

        # create name field display
        self._name_line = QLineEdit()

        # set validation rules to 1-30 characters in length
        self._name_line.set_validator(
            QRegularExpressionValidator(QRegularExpression(r'.{1,30}'))
        )

        # create grid width field display
        self._grid_width_line = QComboBox()
        self._grid_width_line.add_items(  # fill it with integers from 1 to 10
            [str(number) for number in range(1, 11)]
        )
        self._grid_width_line.current_text = "2"

        self._grid_width_line.currentTextChanged.connect(self._update_possible_heights)

        # create grid height field display
        self._grid_height_line = QComboBox()
        self._grid_height_line.add_items(  # fill it with integers from 1 to 20
            [str(number) for number in range(1, 21)]
        )
        self._grid_height_line.current_text = "5"

        # section of buttons
        self._buttons_layout = QHBoxLayout()
        self._buttons_layout.contents_margins = QMargins(10, 0, 10, 0)

        self._save_button = QPushButton("Save")
        self._save_button.clicked.connect(self._save)
        self._cancel_button = QPushButton("Cancel")
        self._cancel_button.clicked.connect(self._return_to_configuration)

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

        self._layout.add_stretch(1)  # move buttons to the bottom

        # add buttons
        self._layout.add_layout(self._buttons_layout)

    def _update_possible_heights(self):
        """ update provided grid height values according to chosen grid width value """

        width = int(self._grid_width_line.current_text)  # get chosen value

        current_height = int(self._grid_height_line.current_text)  # save current height
        self._grid_height_line.clear()  # clear all units

        maximal_height = min(20, 100 // width)  # maximal cell count per tab is 100 and maximal height is 20

        # add height values for chosen width
        self._grid_height_line.add_items(
            [str(possible_height) for possible_height in range(1, maximal_height+1)]
        )

        # if current height is no longer possible, change it to maximal possible
        if current_height > maximal_height:
            self._grid_height_line.current_text = str(maximal_height)
        else:  # otherwise set to previous value
            self._grid_height_line.current_text = str(current_height)

    def _save(self):
        """ Create a tab from data in the form """

        # get data from the form
        name = self._name_line.text
        grid_width = self._grid_width_line.current_text
        grid_height = self._grid_height_line.current_text

        # check if data is valid
        validation_passed = False
        try:
            validation_passed = Tab.validate(self._configuration, name, grid_width, grid_height,
                                             db_session=self._db_session)
        except ValueError as error:
            QMessageBox.critical(self, "Error!", str(error), QMessageBox.Ok, QMessageBox.Ok)  # show error message

        if validation_passed:  # if data is valid
            # create a new tab object
            tab = Tab(configuration=self._configuration, name=name, grid_width=grid_width, grid_height=grid_height)

            QMessageBox.information(self, "Success!", f'Tab {tab.name} created successfully!',
                                    QMessageBox.Ok, QMessageBox.Ok)  # show success message

            self._return_to_configuration()  # redirect to configuration

    def _return_to_configuration(self):
        """ open back the configuration creation/view/editing page """
        self.parent_widget().view_configuration(self._configuration)
