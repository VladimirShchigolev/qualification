from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLineEdit, \
    QLabel, QHBoxLayout, QPushButton, QMessageBox

from src.models.models import Sensor


class SensorIndexWidget(QWidget):
    """ Widget for showing sensors of the configuration."""

    def __init__(self, db_session, configuration, configuration_page="view", read_only=False):
        """Create sensor index widget."""
        super().__init__()
        self._db_session = db_session
        self._configuration = configuration

        # True if creating new tabs is allowed
        self._read_only = read_only

        # from what page this page was open (where to return later)
        self._configuration_page = configuration_page

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """Initialize UI."""
        # create a layout
        self._layout = QVBoxLayout(self)

        # create a title
        self._title = QLabel()
        self._title.setText("Sensors")
        self._title.setFont(QFont("Lato", 14))
        self._title.setAlignment(Qt.AlignCenter)

        # create a search field
        self._search_line_edit = QLineEdit()
        self._search_line_edit.setPlaceholderText("Search")
        self._search_line_edit.textChanged.connect(self._search)

        # create a list widget for sensors
        self._sensors_list = QListWidget()
        self._sensors_list.setAlternatingRowColors(True)

        # get all configuration sensors from DB
        all_sensors = self._db_session.query(Sensor).filter(
            Sensor.configuration == self._configuration) \
            .order_by(Sensor.short_name).all()

        # add sensors to the list widget
        for sensor in all_sensors:
            QListWidgetItem(str(sensor), self._sensors_list)

        # show selected sensor on double click
        self._sensors_list.itemDoubleClicked.connect(self._show_list_item_sensor)

        # section of buttons
        self._buttons_layout = QHBoxLayout()

        if not self._read_only:
            self._new_button = QPushButton("New")
            self._new_button.clicked.connect(self._create_sensor)

            self._buttons_layout.addWidget(self._new_button)

        self._view_button = QPushButton("View")
        self._view_button.clicked.connect(self._show_selected_sensor)

        # move view button to the right
        self._buttons_layout.addStretch(1)

        self._buttons_layout.addWidget(self._view_button)

        # add widgets to layout
        self._layout.addWidget(self._title)
        self._layout.addWidget(self._search_line_edit)
        self._layout.addWidget(self._sensors_list)
        self._layout.addLayout(self._buttons_layout)

    def _search(self, search_string):
        """Filter sensors by the search string."""
        # get sensors which name starts with
        # the search_string from current configuration
        search_string = "{}%".format(search_string)
        filtered_sensors = self._db_session.query(Sensor) \
            .filter(Sensor.configuration == self._configuration) \
            .filter(Sensor.short_name.like(search_string)) \
            .order_by(Sensor.short_name) \
            .all()

        # clear current list and fill it with filtered sensors
        self._sensors_list.clear()
        for sensor in filtered_sensors:
            QListWidgetItem(str(sensor), self._sensors_list)

    def _show_selected_sensor(self):
        """Open view page for the selected sensor."""
        # get selected items
        selected_items = self._sensors_list.selectedItems()
        if selected_items:
            # show the first and only item
            self._show_list_item_sensor(selected_items[0])

    def _show_list_item_sensor(self, list_item):
        """Open view page for the selected/clicked sensor."""
        # get selected sensor short name
        sensor_short_name = list_item.data(0)

        # find sensor in DB
        sensor = self._db_session.query(Sensor) \
            .where(Sensor.configuration == self._configuration) \
            .where(Sensor.short_name == sensor_short_name) \
            .one_or_none()

        if sensor is not None:  # if sensor found
            self.parentWidget().parentWidget().view_sensor(sensor, self._configuration_page)

    def _create_sensor(self):
        """Open a sensor creating page."""
        sensors = self._db_session.query(Sensor).filter(Sensor.configuration == self._configuration).all()
        if len(sensors) == 100:
            QMessageBox.critical(self, "Error!", "Sensor limit of 100 sensors is reached for this configuration!",
                                 QMessageBox.Ok, QMessageBox.Ok)
        else:
            self.parentWidget().parentWidget().create_sensor(self._configuration,
                                                             self._configuration_page)
