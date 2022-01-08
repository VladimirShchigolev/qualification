from PySide6.QtCore import QMargins
from PySide6.QtWidgets import QWidget, QVBoxLayout, \
    QLineEdit, QListWidget, QListWidgetItem, QLabel

from src.models.models import Sensor, SensorCell


class CellViewWidget(QWidget):
    """ Widget responsible for viewing a cell."""

    def __init__(self, db_session, cell):
        """Create cell view widget."""
        super().__init__()
        self._db_session = db_session
        self._cell = cell
        self._configuration = cell.tab.configuration

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """Initialize UI."""
        self.setMaximumWidth(250)
        self.setMinimumWidth(250)
        # create a layout
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        # create title field display
        self._title_line = QLineEdit()
        self._title_line.setText(self._cell.title)
        self._title_line.setPlaceholderText("Title")
        self._title_line.setReadOnly(True)
        self._title_line.setToolTip("Title can be set manually only for group of sensors.")

        # create added sensors' list
        self._sensors_list_label = QLabel("Sensors:")
        self._sensors_list = QListWidget()
        self._sensors_list.setAlternatingRowColors(True)

        # get sensors that are assigned to given cell
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

        # add widgets to layout
        self._layout.addWidget(self._title_line)
        self._layout.addWidget(self._sensors_list_label)
        self._layout.addWidget(self._sensors_list)
