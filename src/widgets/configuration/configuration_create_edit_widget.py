from PySide6.QtCore import Qt, QMargins, QRegularExpression
from PySide6.QtGui import QFont, QRegularExpressionValidator
from PySide6.QtWidgets import QWidget, QLabel, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QVBoxLayout, \
    QComboBox, QMessageBox, QCheckBox, QSizePolicy
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property  # snake_case enabled for Pyside6

from src.models.models import Configuration, Tab, Cell, SensorCell
from src.widgets.cells.cell_grid_management_widget import CellGridManagementWidget
from src.widgets.sensors.sensor_index_widget import SensorIndexWidget
from src.widgets.tabs.tab_index_widget import TabIndexWidget


class ConfigurationCreateEditWidget(QWidget):
    """ Widget for creating (manually) or editing a configuration """

    def __init__(self, db_session, configuration=None, returned_to_creation=False):
        super().__init__()
        self._db_session = db_session

        # set to true if returned to the creation page after creating/editing sensors or tabs
        self._returned_to_creation = returned_to_creation

        print("configuration:", configuration)

        # define if configuration is being created or edited
        if configuration:
            self._configuration = configuration
            self._edit_mode = True
        else:
            # create a new configuration to edit it later
            print("configuration created")
            self._configuration = Configuration(name="", show_unknown_sensors=False)
            self._db_session.add(self._configuration)
            self._edit_mode = False

        print("created: ", self._configuration.id)

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """ Initialize UI """
        # create a layout
        self._layout = QVBoxLayout(self)

        self._form_layout = QFormLayout()
        self._form_layout.horizontal_spacing = 20
        self._form_layout.vertical_spacing = 20
        self._form_layout.contents_margins = QMargins(10, 0, 10, 0)

        # create a title
        if self._edit_mode and not self._returned_to_creation:
            self._title = QLabel()
            self._title.text = f'Edit Configuration {self._configuration.name}'
            self._title.font = QFont("Lato", 18)
            self._title.alignment = Qt.AlignCenter
            self._title.set_contents_margins(10, 10, 10, 20)

            self._form_layout.add_row(self._title)

        # create name field display
        self._name_line = QLineEdit()
        self._name_line.text = self._configuration.name

        # set validation rules to 1-30 characters in length
        self._name_line.set_validator(
            QRegularExpressionValidator(QRegularExpression(r'.{1,30}'))
        )
        self._name_line.textChanged.connect(self._update_name)

        self._show_unknown_sensors = QCheckBox()
        print("check: ", self._configuration.show_unknown_sensors)
        self._show_unknown_sensors.checked = self._configuration.show_unknown_sensors
        self._show_unknown_sensors.clicked.connect(self._update_showing_unknown_sensors)

        # create sensors and tabs display
        if self._edit_mode and not self._returned_to_creation:
            page = "edit"
        else:
            page = "create"

        self._sensors_and_tabs_layout = QHBoxLayout()

        self._sensors_widget = SensorIndexWidget(self._db_session, self._configuration, configuration_page=page)
        self._sensors_and_tabs_layout.add_widget(self._sensors_widget)

        self._tabs_widget = TabIndexWidget(self._db_session, self._configuration, configuration_page=page)
        self._sensors_and_tabs_layout.add_widget(self._tabs_widget)

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
        self._form_layout.add_row("Name:", self._name_line)
        self._form_layout.add_row("Show unknown sensors:", self._show_unknown_sensors)
        self._layout.add_layout(self._form_layout)
        self._layout.add_layout(self._sensors_and_tabs_layout)

        # add buttons
        self._layout.add_layout(self._buttons_layout)

    def _update_name(self):
        """ Updates configuration name when it changes """
        name = self._name_line.text
        self._configuration.name = name

    def _update_showing_unknown_sensors(self):
        """ Updates option of showing unknown sensors when it changes """
        show = self._show_unknown_sensors.checked
        self._configuration.show_unknown_sensors = show

    def _save(self):
        """ Save configuration from data in the form """

        # get data from the form
        name = self._name_line.text
        include_unknown_sensor_tab = self._show_unknown_sensors.checked

        # determine if check for duplicates is needed
        check_for_duplicates = name != self._configuration.name  # needed only when configuration name gets changed

        # check if data is valid
        validation_passed = False
        try:
            validation_passed = Configuration.validate(name, db_session=self._db_session,
                                                       check_for_duplicates=check_for_duplicates)
        except ValueError as error:
            QMessageBox.critical(self, "Error!", str(error), QMessageBox.Ok, QMessageBox.Ok)  # show error message

        if validation_passed:  # if data is valid
            # set data to created/edited configuration object
            self._configuration.name = name
            self._configuration.show_unknown_sensors = include_unknown_sensor_tab

            # set message according to selected mode (create or edit)
            if self._edit_mode:
                message = f'Configuration {self._configuration.name} updated successfully!'
            else:
                message = f'Configuration {self._configuration.name} created successfully!'

            QMessageBox.information(self, "Success!", message,
                                    QMessageBox.Ok, QMessageBox.Ok)  # show success message

            self._db_session.commit()

            self._return_to_configurations()  # redirect to configuration index

    def _cancel(self):
        """ Revert changes and open back the configuration index/view page """

        # revert changes
        self._db_session.rollback()

        self._return_to_configurations()

    def _return_to_configurations(self):
        """ Open configurations index page """
        self.parent_widget().index_configurations()
