from PySide6.QtCore import Qt, QRegularExpression, QMargins
from PySide6.QtGui import QFont, QRegularExpressionValidator
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QScrollArea, QGridLayout, QSizePolicy, QVBoxLayout, \
    QLineEdit, QComboBox, QListWidget, QListWidgetItem, QMessageBox, QToolTip
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property  # snake_case enabled for Pyside6

from src.models.models import Cell, Sensor, SensorCell


class CellEditWidget(QWidget):
    """ Widget responsible for editing a cell.
    Allows selecting and removing sensors for the cell
    and editing the name of the cell if more than one sensor is used.
    """

    def __init__(self, db_session, cell):
        super().__init__()
        self._db_session = db_session
        self._cell = cell
        self._configuration = cell.tab.configuration

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """ Initialize UI """
        self.maximum_width = 250
        # create a layout
        self._layout = QVBoxLayout(self)
        self._layout.contents_margins = QMargins(0, 0, 0, 0)

        # create title field display
        self._title_line = QLineEdit()
        self._title_line.text = ""
        self._title_line.placeholder_text = "Title"
        self._title_line.read_only = True
        self._title_line.tool_tip = "Title can be set manually only for group of sensors."

        # create sensor search combo box
        self._sensors_search = QComboBox()
        self._sensors_search.editable = True
        self._sensors_search.completer().case_sensitivity = Qt.CaseInsensitive  # set case insensitive completion

        # set validation rules to upper and lower English letters, digits and underscore, 1-10 characters in length
        self._sensors_search.set_validator(
            QRegularExpressionValidator(QRegularExpression(r'[A-Za-z0-9_]{1,10}'))
        )

        self._sensors_search.currentIndexChanged.connect(self._add_sensor)

        # create added sensors' list
        self._sensors_list = QListWidget()
        self._sensors_list.alternating_row_colors = True

        self._update_lists()

        # section of buttons
        self._buttons_layout = QHBoxLayout()

        self._split_button = QPushButton("Split")
        self._split_button.clicked.connect(self._split_cell)
        if self._cell.rowspan == 1 and self._cell.colspan == 1:
            self._split_button.set_disabled(True)
            self._split_button.tool_tip = "This cell cannot be split."
        self._remove_button = QPushButton("Remove")
        self._remove_button.clicked.connect(self._remove_sensor)

        self._buttons_layout.add_widget(self._split_button)
        self._buttons_layout.add_stretch(1)  # move view button to the right
        self._buttons_layout.add_widget(self._remove_button)

        # add widgets to layout
        self._layout.add_widget(self._title_line)
        self._layout.add_widget(self._sensors_search)
        self._layout.add_widget(self._sensors_list)
        self._layout.add_layout(self._buttons_layout)

    def _update_lists(self):
        """ Set cell list of sensors and search list of sensors according to DB data """
        # clear all items
        self._sensors_search.currentIndexChanged.disconnect(self._add_sensor)  # disable while editing search list
        self._sensors_list.clear()
        self._sensors_search.clear()

        # get sensors that are assign to given cell
        cell_sensors = self._db_session.query(Sensor) \
            .join(SensorCell) \
            .filter(SensorCell.cell == self._cell) \
            .order_by(Sensor.short_name) \
            .all()

        # add found sensors to the list
        for sensor in cell_sensors:
            QListWidgetItem(str(sensor), self._sensors_list)

        # get sensors of the configuration that are not added to the cell
        unassigned_sensors = self._db_session.query(Sensor) \
            .outerjoin(SensorCell) \
            .filter(Sensor.configuration == self._configuration) \
            .filter(SensorCell.cell != self._cell)\
            .order_by(Sensor.short_name) \
            .all()

        # add found sensors to the search drop list
        for sensor in unassigned_sensors:
            self._sensors_search.add_item(str(sensor))

        self._sensors_search.current_text = ""

        self._sensors_search.currentIndexChanged.connect(self._add_sensor)  # enable when done editing search list

    def _add_sensor(self):
        """ Add the selected sensor to the cell """

        sensor_short_name = self._sensors_search.current_text  # get the short name of the sensor

        # find the sensor in the DB
        sensor = self._db_session.query(Sensor).filter(Sensor.configuration == self._configuration) \
            .filter(Sensor.short_name == sensor_short_name).one_or_none()

        # if sensor not found
        if not sensor:
            # show error message
            QMessageBox.critical(self, "Error!", "Sensor with such short name does not exist in this configuration!",
                                 QMessageBox.Ok, QMessageBox.Ok)
            return

        # check if sensor is already assigned to the cell
        assigned = self._db_session.query(SensorCell).filter(SensorCell.cell == self._cell) \
            .filter(SensorCell.sensor == sensor).one_or_none()

        if assigned:
            # show error message
            QMessageBox.critical(self, "Error!", "This sensor is already assigned to this cell!",
                                 QMessageBox.Ok, QMessageBox.Ok)
            return

        # check if sensor type conforms already assigned sensors
        assigned_sensor = self._db_session.query(Sensor) \
            .join(SensorCell) \
            .filter(SensorCell.cell == self._cell) \
            .first()

        # if there is a sensor assigned to the cell and its' type differs from the new sensor's type
        if assigned_sensor and (assigned_sensor.physical_value != sensor.physical_value
                                or assigned_sensor.physical_unit != sensor.physical_unit):
            # show error message
            QMessageBox.critical(self, "Error!", "Only sensors with the same physical value and units can be "
                                                 "assigned to the same cell!",
                                 QMessageBox.Ok, QMessageBox.Ok)
            return

        # create a SensorCell relationship object
        SensorCell(sensor=sensor, cell=self._cell)

        self._update_lists()

    def _split_cell(self):
        """ Split selected cell into atomic (1x1) cells """
        self.parent_widget().split_selected_cell()

    def _remove_sensor(self):
        """ Remove sensor from the cell """
        # get selected items
        selected_items = self._sensors_list.selected_items()

        if len(selected_items):
            sensor_short_name = selected_items[0].data(0)  # sensor to delete is the first and only selected item
            # get the sensor that is being removed
            sensor = self._db_session.query(Sensor) \
                .filter(Sensor.configuration == self._configuration) \
                .filter(Sensor.short_name == sensor_short_name) \
                .one_or_none()

            # find SensorCell object to remove
            sensor_cell_to_delete = self._db_session.query(SensorCell) \
                .filter(SensorCell.cell == self._cell) \
                .filter(SensorCell.sensor == sensor) \
                .one_or_none()

            # remove SensorCell object - remove sensor assignment to the cell
            if sensor_cell_to_delete:
                self._db_session.delete(sensor_cell_to_delete)

                self._update_lists()
