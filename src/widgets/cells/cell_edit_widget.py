from PySide6.QtCore import Qt, QRegularExpression, QMargins
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, \
    QLineEdit, QComboBox, QListWidget, QListWidgetItem, QMessageBox

from src.models.models import Sensor, SensorCell


class CellEditWidget(QWidget):
    """Widget for editing a cell."""

    def __init__(self, db_session, cell):
        """Create cell editing widget."""
        super().__init__()
        self._db_session = db_session
        self._cell = cell
        self._configuration = cell.tab.configuration

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """Initialize UI."""
        self.setMaximumWidth(250)
        # create a layout
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        # create title field display
        self._title_line = QLineEdit()
        self._title_line.textChanged.connect(self._update_title)
        self._title_line.setText(self._cell.title)
        self._title_line.setPlaceholderText("Title")

        # get sensors that are assigned to the cell
        cell_sensors = self._db_session.query(Sensor) \
            .join(SensorCell) \
            .filter(SensorCell.cell == self._cell) \
            .order_by(Sensor.short_name) \
            .all()

        # make title editable if cell represents a sensor group
        self._title_line.setReadOnly(len(cell_sensors) <= 1)

        self._title_line.setToolTip("Title can be set manually only for group of sensors.")

        # set validation rules to 1-30 characters in length
        self._title_line.setValidator(
            QRegularExpressionValidator(QRegularExpression(r'.{1,50}'))
        )

        # create sensor search combo box
        self._sensors_search = QComboBox()
        self._sensors_search.setEditable(True)

        # set case insensitive completion
        self._sensors_search.completer().setCaseSensitivity(Qt.CaseInsensitive)

        # set validation rules to upper and lower English letters,
        # digits and underscore, 1-10 characters in length
        self._sensors_search.setValidator(
            QRegularExpressionValidator(QRegularExpression(r'[A-Za-z0-9_]{1,10}'))
        )

        self._sensors_search.currentIndexChanged.connect(self._add_sensor)

        # create added sensors' list
        self._sensors_list = QListWidget()
        self._sensors_list.setAlternatingRowColors(True)

        self._update_lists()

        # section of buttons
        self._buttons_layout = QHBoxLayout()

        self._split_button = QPushButton("Split Cell")
        self._split_button.clicked.connect(self._split_cell)
        if self._cell.rowspan == 1 and self._cell.colspan == 1:
            self._split_button.setDisabled(True)
            self._split_button.setToolTip("This cell cannot be split.")
        self._remove_button = QPushButton("Remove Sensor")
        self._remove_button.clicked.connect(self._remove_sensor)

        self._buttons_layout.addWidget(self._split_button)
        # move view button to the right
        self._buttons_layout.addStretch(1)
        self._buttons_layout.addWidget(self._remove_button)

        # add widgets to layout
        self._layout.addWidget(self._title_line)
        self._layout.addWidget(self._sensors_search)
        self._layout.addWidget(self._sensors_list)
        self._layout.addLayout(self._buttons_layout)

    def _update_lists(self):
        """Set data to 'cell sensor' and 'search' lists."""
        # clear all items
        self._sensors_search.currentIndexChanged.disconnect(
            self._add_sensor)  # disable while editing search list
        self._sensors_list.clear()
        self._sensors_search.clear()

        # get sensors that are assigned to the cell
        cell_sensors = self._db_session.query(Sensor) \
            .join(SensorCell) \
            .filter(SensorCell.cell == self._cell) \
            .order_by(Sensor.short_name) \
            .all()

        # add found sensors to the list
        for sensor in cell_sensors:
            sensor_item = QListWidgetItem(str(sensor), self._sensors_list)
            sensor_item.setToolTip(f"Short Name: {sensor.short_name}\nName: {sensor.name}\n"
                                   f"Physical Value: {sensor.physical_value}\n"
                                   f"Physical Unit: {sensor.physical_unit}"
                                   )

        # get sensors of the configuration that are not in the cell
        unassigned_sensors = self._db_session.query(Sensor) \
            .filter(Sensor.configuration == self._configuration) \
            .except_(
            self._db_session.query(Sensor)
                .join(SensorCell)
                .filter(SensorCell.cell == self._cell)
            ) \
            .order_by(Sensor.short_name) \
            .all()

        # add found sensors to the search drop list
        for sensor in unassigned_sensors:
            self._sensors_search.addItem(str(sensor))

        self._sensors_search.setCurrentIndex(-1)
        self._sensors_search.setCurrentText("")

        self._sensors_search.currentIndexChanged.connect(
            self._add_sensor)  # enable when done editing search list

    def _update_title(self):
        """Update cell title in the grid representation."""
        if self._title_line.text() != self._cell.title:
            self._cell.title = self._title_line.text()
            self.parentWidget().update_cell_title(self._cell)

    def _add_sensor(self):
        """ Add the selected sensor to the cell """
        # get the short name of the sensor
        sensor_short_name = self._sensors_search.currentText()

        # find the sensor in the DB
        sensor = self._db_session.query(Sensor) \
            .filter(Sensor.configuration == self._configuration) \
            .filter(Sensor.short_name == sensor_short_name) \
            .one_or_none()

        # if sensor not found
        if not sensor:
            # show error message
            QMessageBox.critical(self, "Error!",
                                 "Sensor with such short name does not exist in this "
                                 "configuration!",
                                 QMessageBox.Ok, QMessageBox.Ok)

            self._update_lists()  # clear changes to search combobox
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

        # if there is a sensor assigned to the cell
        # and its' type differs from the new sensor's type
        if assigned_sensor and (assigned_sensor.physical_value != sensor.physical_value
                                or assigned_sensor.physical_unit != sensor.physical_unit):
            # show error message
            QMessageBox.critical(self, "Error!",
                                 "Only sensors with the same physical value and units can be "
                                 "assigned to the same cell!",
                                 QMessageBox.Ok, QMessageBox.Ok)
        else:
            # create a SensorCell relationship object
            SensorCell(sensor=sensor, cell=self._cell)

            # set cell title
            if assigned_sensor:
                # set title for sensor group
                self._title_line.setText(f"{sensor.physical_value} Group")

                # allow title editing
                self._title_line.setReadOnly(False)
            else:
                # set title for single sensor
                self._title_line.setText(sensor.name)

        self._update_lists()

    def _split_cell(self):
        """Split selected cell into atomic (1x1) cells."""
        self.parentWidget().split_selected_cell()

    def _remove_sensor(self):
        """Remove sensor from the cell."""
        # get selected items
        selected_items = self._sensors_list.selected_items()

        if selected_items:
            # sensor to delete is the first and only selected item
            sensor_short_name = selected_items[0].data(0)
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

            # remove sensor assignment to the cell
            if sensor_cell_to_delete:
                self._db_session.delete(sensor_cell_to_delete)

                # get sensors that are assigned to the cell
                cell_sensors = self._db_session.query(Sensor) \
                    .join(SensorCell) \
                    .filter(SensorCell.cell == self._cell) \
                    .order_by(Sensor.short_name) \
                    .all()

                # if cell represents a single sensor
                if len(cell_sensors) == 1:
                    # set cell title to sensor name
                    self._title_line.setText(cell_sensors[0].name)
                    self._title_line.setReadOnly(True)
                elif len(cell_sensors) == 0:  # if cell has no sensors
                    self._title_line.setText("")  # remove cell title

                self._update_lists()
