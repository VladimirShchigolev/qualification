from PySide6.QtCore import Qt, QMargins, QRegularExpression
from PySide6.QtGui import QFont, QRegularExpressionValidator
from PySide6.QtWidgets import QWidget, QLabel, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QVBoxLayout, \
    QComboBox, QMessageBox
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property  # snake_case enabled for Pyside6

from src.models.models import Configuration, Tab, Sensor, Cell, SensorCell


class ConfigurationCreateCopyWidget(QWidget):
    """ Widget for creating a sensor """

    def __init__(self, db_session):
        super().__init__()
        self._db_session = db_session

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """ Initialize UI """
        # create a layout
        self._layout = QVBoxLayout(self)

        # create form layout
        self._form_layout = QFormLayout()
        self._form_layout.horizontal_spacing = 20
        self._form_layout.contents_margins = QMargins(10, 0, 10, 0)

        # create name field display
        self._name_line = QLineEdit()

        # set validation rules to 1-30 characters in length
        self._name_line.set_validator(
            QRegularExpressionValidator(QRegularExpression(r'.{1,30}'))
        )

        # create field display for configuration that gets copied
        self._source_configuration_line = QComboBox()
        self._source_configuration_line.editable = True
        # set case insensitive completion
        self._source_configuration_line.completer().case_sensitivity = Qt.CaseInsensitive
        self._source_configuration_line.current_text = ""

        # set validation rules to 1-30 characters in length
        self._source_configuration_line.set_validator(
            QRegularExpressionValidator(QRegularExpression(r'.{1,30}'))
        )

        # get all configurations
        configurations = self._db_session.query(Configuration).order_by(Configuration.name).all()

        for configuration in configurations:
            self._source_configuration_line.add_item(str(configuration))

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
        self._form_layout.add_row("Name:", self._name_line)
        self._form_layout.add_row("Source Configuration:", self._source_configuration_line)
        self._layout.add_layout(self._form_layout)

        self._layout.add_stretch(1)  # move buttons to the bottom

        # add buttons
        self._layout.add_layout(self._buttons_layout)

    def _copy_sensors(self, configuration, source_configuration):
        """ Copy all sensors from source configuration to the new configuration """

        sensors = self._db_session.query(Sensor).filter(Sensor.configuration == source_configuration).all()
        for source_sensor in sensors:
            Sensor(configuration=configuration, short_name=source_sensor.short_name, name=source_sensor.name,
                   physical_value=source_sensor.physical_value, physical_unit=source_sensor.physical_unit)

    def _copy_sensor_cells(self, cell, source_cell):
        """ Copy all data about sensors assigned to the cell from source cell to the new cell """

        sensor_cells = self._db_session.query(SensorCell).filter(SensorCell.cell == source_cell).all()

        for sensor_cell in sensor_cells:
            source_sensor = sensor_cell.sensor
            # get the same sensor from new configuration
            new_sensor = self._db_session.query(Sensor)\
                .filter(Sensor.configuration == cell.tab.configuration)\
                .filter(Sensor.short_name == source_sensor.short_name)\
                .one_or_none()

            if new_sensor:
                SensorCell(sensor=new_sensor, cell=cell)

    def _copy_cells(self, tab, source_tab):
        """ Copy all cells from source tab to the new tab """

        cells = self._db_session.query(Cell).filter(Cell.tab == source_tab).all()
        for source_cell in cells:
            cell = Cell(tab=tab, row=source_cell.row, column=source_cell.column, rowspan=source_cell.rowspan,
                        colspan=source_cell.colspan, title=source_cell.title)

            self._copy_sensor_cells(cell, source_cell)

    def _copy_tabs(self, configuration, source_configuration):
        """ Copy all tabs from source configuration to the new configuration """

        tabs = self._db_session.query(Tab).filter(Tab.configuration == source_configuration).all()
        for source_tab in tabs:
            tab = Tab(configuration=configuration, name=source_tab.name, grid_width=source_tab.grid_width,
                      grid_height=source_tab.grid_height)

            self._copy_cells(tab, source_tab)

    def _save(self):
        """ Create a new configuration based on chosen name and source configuration """

        # get data from the form
        name = self._name_line.text
        source_configuration_name = self._source_configuration_line.current_text

        # check if source configuration exists
        source_configuration = self._db_session.query(Configuration) \
            .filter(Configuration.name == source_configuration_name) \
            .one_or_none()

        if not source_configuration:
            QMessageBox.critical(self, "Error!", "Source configuration with such name does not exist",
                                 QMessageBox.Ok, QMessageBox.Ok)  # show error message
            return

        # check if data is valid
        validation_passed = False
        try:
            validation_passed = Configuration.validate(name, db_session=self._db_session,
                                                       check_for_duplicates=True)
        except ValueError as error:
            QMessageBox.critical(self, "Error!", str(error), QMessageBox.Ok, QMessageBox.Ok)  # show error message

        if validation_passed:  # if data is valid
            # create a new configuration with data copied from the source configuration
            configuration = Configuration(name=name, show_unknown_sensors=source_configuration.show_unknown_sensors)
            self._db_session.add(configuration)  # add manually, everything else gets added automatically due to FK

            self._copy_tabs(configuration, source_configuration)
            self._copy_sensors(configuration, source_configuration)

            QMessageBox.information(self, "Success!", f'Configuration {name} created successfully!',
                                    QMessageBox.Ok, QMessageBox.Ok)  # show success message

            self._db_session.commit()

            self._return_to_configurations()  # redirect to configuration index

    def _cancel(self):
        """ revert changes and open back the configuration creation/editing page """

        # revert changes
        self._db_session.rollback()

        self._return_to_configurations()

    def _return_to_configurations(self):
        """ Open configurations index page """
        self.parent_widget().index_configurations()
