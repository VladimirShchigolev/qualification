from PySide6.QtCore import Qt, QMargins, QRegularExpression
from PySide6.QtGui import QFont, QRegularExpressionValidator
from PySide6.QtWidgets import QWidget, QLabel, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, \
    QVBoxLayout, QComboBox, QMessageBox

# enable snake_case for Pyside6
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property

from src.models.models import Sensor


class SensorCreateEditWidget(QWidget):
    """Widget for creating/editing a sensor."""

    def __init__(self, db_session, configuration=None, sensor=None, configuration_page="view"):
        """Create sensor creating/editing widget"""
        super().__init__()
        self._db_session = db_session

        # define mode - edit or create
        if sensor:
            self._edit_mode = True
            self._sensor = sensor
            self._configuration = sensor.configuration
        else:
            self._edit_mode = False
            self._configuration = configuration
            self._sensor = Sensor(configuration=configuration, short_name="", name="",
                                  physical_value="", physical_unit="")

        # from what page this page was open (where to return later)
        self._configuration_page = configuration_page

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """Initialize UI."""
        # create a layout
        self._layout = QVBoxLayout(self)

        self._form_layout = QFormLayout()
        self._form_layout.horizontal_spacing = 20
        self._form_layout.contents_margins = QMargins(10, 0, 10, 0)

        # create a title
        self._title = QLabel()

        if self._edit_mode:
            self._title.text = f'Update Sensor {self._sensor.short_name}'
        else:
            self._title.text = "Create Sensor"
        self._title.font = QFont("Lato", 18)
        self._title.alignment = Qt.AlignCenter
        self._title.set_contents_margins(10, 10, 10, 20)

        # create short name field display
        self._short_name_line = QLineEdit()
        self._short_name_line.text = self._sensor.short_name

        # set validation rules to upper and lower English letters,
        # digits and underscore, 1-10 characters in length
        self._short_name_line.set_validator(
            QRegularExpressionValidator(QRegularExpression(r'[A-Za-z0-9_]{1,10}'))
        )

        # create name field display
        self._name_line = QLineEdit()
        self._name_line.text = self._sensor.name

        # set validation rules to 1-30 characters in length
        self._name_line.set_validator(
            QRegularExpressionValidator(QRegularExpression(r'.{1,30}'))
        )

        # create physical value field display
        self._physical_value_line = QComboBox()

        # fill provided values with widely used options
        self._physical_value_line.add_items(
            sorted(["-", "Temperature", "Voltage", "Resistance", "Electric Current", "Pressure"])
        )
        self._physical_value_line.editable = True
        self._physical_value_line.current_text = self._sensor.physical_value

        # update provided units on value change
        self._physical_value_line.editTextChanged.connect(self._update_units)

        # set validation rules to 0-40 characters in length
        self._physical_value_line.set_validator(
            QRegularExpressionValidator(QRegularExpression(r'.{0,40}'))
        )

        # create physical unit field display
        self._physical_unit_line = QComboBox()
        self._update_units()
        self._physical_unit_line.editable = True

        # set case sensitive completion
        self._physical_unit_line.completer().case_sensitivity = Qt.CaseSensitive

        self._physical_unit_line.current_text = self._sensor.physical_unit

        # set validation rules to 0-10 characters in length
        self._physical_unit_line.set_validator(
            QRegularExpressionValidator(QRegularExpression(r'.{0,10}'))
        )

        # section of buttons
        self._buttons_layout = QHBoxLayout()
        self._buttons_layout.contents_margins = QMargins(10, 0, 10, 0)

        self._save_button = QPushButton("Save")
        self._save_button.clicked.connect(self._save)
        self._cancel_button = QPushButton("Cancel")
        self._cancel_button.clicked.connect(self._return_to_configuration)

        self._buttons_layout.add_widget(self._save_button)

        # move cancel button to the right
        self._buttons_layout.add_stretch(1)

        self._buttons_layout.add_widget(self._cancel_button)

        # add widgets to layout

        # add configuration data
        self._form_layout.add_row(self._title)
        self._form_layout.add_row("Short Name:", self._short_name_line)
        self._form_layout.add_row("Name:", self._name_line)
        self._form_layout.add_row("Physical Value:", self._physical_value_line)
        self._form_layout.add_row("Physical Unit:", self._physical_unit_line)
        self._layout.add_layout(self._form_layout)

        self._layout.add_stretch(1)  # move buttons to the bottom

        # add buttons
        self._layout.add_layout(self._buttons_layout)

    def _update_units(self):
        """Update provided physical units to match physical value."""
        # define widely used units for values
        units = {
            "Temperature": ["K", "°C", "°F"],
            "Pressure": ["mbar", "bar", "Pa", "kPa"],
            "Voltage": ["μV", "mV", "V"],
            "Resistance": ["mΩ", "Ω", "kΩ", "MΩ"],
            "Electric Current": ["μA", "mA", "A"]
        }

        # get chosen value
        value = self._physical_value_line.current_text

        # save current units
        current_units = self._physical_unit_line.current_text

        self._physical_unit_line.clear()  # clear all units

        # add units for chosen value
        if value in units:
            self._physical_unit_line.add_items(["-"] + units[value])
        else:
            self._physical_unit_line.add_item("-")

        # set to earlier chosen units
        self._physical_unit_line.current_text = current_units

    def _save(self):
        """Create a sensor from data in the form."""
        # get data from the form
        short_name = self._short_name_line.text
        name = self._name_line.text
        physical_value = self._physical_value_line.current_text
        physical_unit = self._physical_unit_line.current_text

        # if short name gets changed, check for duplicates
        check_for_duplicates = self._sensor.short_name != short_name

        # check if data is valid
        validation_passed = False
        try:
            validation_passed = Sensor.validate(self._sensor.configuration, short_name, name,
                                                physical_value,
                                                physical_unit,
                                                check_for_duplicates=check_for_duplicates,
                                                db_session=self._db_session)
        except ValueError as error:
            # show error message
            QMessageBox.critical(self, "Error!", str(error), QMessageBox.Ok,
                                 QMessageBox.Ok)

        if validation_passed:  # if data is valid
            # update sensor object
            self._sensor.short_name = short_name
            self._sensor.name = name
            self._sensor.physical_value = physical_value
            self._sensor.physical_unit = physical_unit

            # show success message
            if self._edit_mode:
                message = f'Sensor {self._sensor.short_name} updated successfully!'
            else:
                message = f'Sensor {self._sensor.short_name} created successfully!'
            QMessageBox.information(self, "Success!", message, QMessageBox.Ok, QMessageBox.Ok)

            # redirect to configuration
            self._return_to_configuration()

    def _return_to_configuration(self):
        """Open back the configuration creation/editing/view page."""
        if self._configuration_page == "edit":
            self.parent_widget().edit_configuration(self._sensor.configuration)
        elif self._configuration_page == "create":
            self.parent_widget().create_configuration(self._sensor.configuration)
        else:
            self.parent_widget().view_configuration(self._sensor.configuration)