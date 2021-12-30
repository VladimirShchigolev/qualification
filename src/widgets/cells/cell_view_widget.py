from PySide6.QtCore import QMargins
from PySide6.QtWidgets import QWidget, QVBoxLayout, \
    QLineEdit, QListWidget, QListWidgetItem, QLabel
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property  # snake_case enabled for Pyside6

from src.models.models import Sensor, SensorCell


class CellViewWidget(QWidget):
    """ Widget responsible for viewing a cell.
    Shows all sensors assigned to the cell.
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
        self._title_line.text = self._cell.title
        self._title_line.placeholder_text = "Title"
        self._title_line.read_only = True
        self._title_line.tool_tip = "Title can be set manually only for group of sensors."

        # create added sensors' list
        self._sensors_list_label = QLabel("Sensors:")
        self._sensors_list = QListWidget()
        self._sensors_list.alternating_row_colors = True

        # get sensors that are assigned to given cell
        cell_sensors = self._db_session.query(Sensor) \
            .join(SensorCell) \
            .filter(SensorCell.cell == self._cell) \
            .order_by(Sensor.short_name) \
            .all()

        # add found sensors to the list
        for sensor in cell_sensors:
            sensor_item = QListWidgetItem(str(sensor), self._sensors_list)
            sensor_item.set_tool_tip(f"Short Name: {sensor.short_name}\nName: {sensor.name}\n"
                                     f"Physical Value: {sensor.physical_value}\nPhysical Unit: {sensor.physical_unit}"
                                     )

        # add widgets to layout
        self._layout.add_widget(self._title_line)
        self._layout.add_widget(self._sensors_list_label)
        self._layout.add_widget(self._sensors_list)
