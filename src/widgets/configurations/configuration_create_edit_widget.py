from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QFont, QRegularExpressionValidator
from PySide6.QtWidgets import QWidget, QLabel, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, \
    QVBoxLayout, QMessageBox, QCheckBox

from src.models.models import Configuration, Tab, Sensor
from src.widgets.sensors.sensor_index_widget import SensorIndexWidget
from src.widgets.tabs.tab_index_widget import TabIndexWidget


class ConfigurationCreateEditWidget(QWidget):
    """Widget for creating (manually) or editing a configuration."""

    def __init__(self, db_session, configuration=None, returned_to_creation=False):
        """Create configuration creating/editing widget"""
        super().__init__()
        self._db_session = db_session

        # set to true if returned to the creation
        # page after creating/editing/viewing sensors or tabs
        self._returned_to_creation = returned_to_creation

        # define if configuration is being created or edited
        if configuration:
            self._configuration = configuration
            self._edit_mode = True
        else:
            # create a new configuration to edit it later
            self._configuration = Configuration(name="", show_unknown_sensors=False)
            self._db_session.add(self._configuration)
            self._edit_mode = False

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """Initialize UI."""
        # create a layout
        self._layout = QVBoxLayout(self)

        self._form_layout = QFormLayout()
        self._form_layout.setHorizontalSpacing(20)
        self._form_layout.setVerticalSpacing(20)
        self._form_layout.setContentsMargins(10, 0, 10, 0)

        # create a title
        if self._edit_mode and not self._returned_to_creation:
            self._title = QLabel()
            self._title.setText(f'Edit Configuration {self._configuration.name}')
            self._title.setFont(QFont("Lato", 18))
            self._title.setAlignment(Qt.AlignCenter)
            self._title.setContentsMargins(10, 10, 10, 20)

            self._form_layout.addRow(self._title)

        # create name field display
        self._name_line = QLineEdit()
        self._name_line.setText(self._configuration.name)

        # set validation rules to 1-30 characters in length
        self._name_line.setValidator(
            QRegularExpressionValidator(QRegularExpression(r'.{1,30}'))
        )
        self._name_line.textChanged.connect(self._update_name)

        self._show_unknown_sensors = QCheckBox()
        self._show_unknown_sensors.setChecked(self._configuration.show_unknown_sensors)

        self._show_unknown_sensors.clicked.connect(self._update_showing_unknown_sensors)

        # create sensors and tabs display
        if self._edit_mode and not self._returned_to_creation:
            page = "edit"
        else:
            page = "create"

        self._sensors_and_tabs_layout = QHBoxLayout()

        self._sensors_widget = SensorIndexWidget(self._db_session, self._configuration,
                                                 configuration_page=page)
        self._sensors_and_tabs_layout.addWidget(self._sensors_widget)

        self._tabs_widget = TabIndexWidget(self._db_session, self._configuration,
                                           configuration_page=page)
        self._sensors_and_tabs_layout.addWidget(self._tabs_widget)

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
        self._form_layout.addRow("Name:", self._name_line)
        self._form_layout.addRow("Show unknown sensors:", self._show_unknown_sensors)
        self._layout.addLayout(self._form_layout)
        self._layout.addLayout(self._sensors_and_tabs_layout)

        # add buttons
        self._layout.addLayout(self._buttons_layout)

    def _update_name(self):
        """Update configuration name."""
        name = self._name_line.text()
        self._configuration.name = name

    def _update_showing_unknown_sensors(self):
        """Update option of showing unknown sensors."""
        show = self._show_unknown_sensors.isChecked()
        self._configuration.show_unknown_sensors = show

    def _save(self):
        """Save configuration from data in the form."""
        # get data from the form
        name = self._name_line.text()
        include_unknown_sensor_tab = self._show_unknown_sensors.isChecked()

        # check for duplicates is needed
        # only when configuration name gets changed
        check_for_duplicates = name != self._configuration.name

        # check if data is valid
        validation_passed = False
        try:
            validation_passed = Configuration.validate(name, db_session=self._db_session,
                                                       check_for_duplicates=check_for_duplicates)
        except ValueError as error:
            QMessageBox.critical(self, "Error!", str(error), QMessageBox.Ok,
                                 QMessageBox.Ok)  # show error message

        if validation_passed:
            tabs = self._db_session.query(Tab).filter(Tab.configuration == self._configuration).all()
            if not tabs and not include_unknown_sensor_tab:
                # show error message
                QMessageBox.critical(self, "Error!", "Number of tabs cannot be zero", QMessageBox.Ok,
                                     QMessageBox.Ok)
                validation_passed = False

        if validation_passed:
            sensors = self._db_session.query(Sensor).filter(Sensor.configuration == self._configuration).all()
            if not sensors:
                confirmation = QMessageBox.warning(self, "Warning", "Number of sensors is zero!",
                                                   QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
                validation_passed = confirmation == QMessageBox.Ok

        if validation_passed:  # if data is valid
            # set data to created/edited configuration object
            self._configuration.name = name
            self._configuration.show_unknown_sensors = include_unknown_sensor_tab

            # set message according to selected mode (create or edit)
            if self._edit_mode and not self._returned_to_creation:
                message = f'Configuration {self._configuration.name} updated successfully!'
            else:
                message = f'Configuration {self._configuration.name} created successfully!'

            # show success message
            QMessageBox.information(self, "Success!", message,
                                    QMessageBox.Ok, QMessageBox.Ok)

            self._db_session.commit()

            # redirect to configuration index
            self._return_to_configurations()

    def _cancel(self):
        """Revert changes and open back
        the configuration index/view page."""
        # revert changes
        self._db_session.rollback()

        self._return_to_configurations()

    def _return_to_configurations(self):
        """Open configurations index page."""
        self.parentWidget().index_configurations()
