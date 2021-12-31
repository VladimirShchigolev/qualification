from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLineEdit, QLabel, QHBoxLayout, \
    QPushButton
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property  # snake_case enabled for Pyside6

from src.models.models import Sensor


class SensorIndexWidget(QWidget):
    """ Widget responsible for showing all sensors belonging to given configuration.
    Allows searching, showing selected sensors and creating new sensors
    """

    def __init__(self, db_session, configuration, configuration_page="view"):
        super().__init__()
        self._db_session = db_session
        self._configuration = configuration

        self._configuration_page = configuration_page  # from what page this page was open (where to return later)

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """ Initialize UI """
        # create a layout
        self._layout = QVBoxLayout(self)

        # create a title
        self._title = QLabel()
        self._title.text = "Sensors"
        self._title.font = QFont("Lato", 14)
        self._title.alignment = Qt.AlignCenter

        # create a search field
        self._search_line_edit = QLineEdit()
        self._search_line_edit.placeholder_text = "Search"
        self._search_line_edit.textChanged.connect(self._search)

        # create a list widget for sensors
        self._sensors_list = QListWidget()
        self._sensors_list.alternating_row_colors = True

        # get all configuration sensors from DB
        all_sensors = self._db_session.query(Sensor).filter(Sensor.configuration == self._configuration)\
            .order_by(Sensor.short_name).all()

        # add sensors to the list widget
        for sensor in all_sensors:
            QListWidgetItem(str(sensor), self._sensors_list)

        # show selected sensor on double click
        self._sensors_list.itemDoubleClicked.connect(self._show_list_item_sensor)

        # section of buttons
        self._buttons_layout = QHBoxLayout()

        self._new_button = QPushButton("New")
        self._new_button.clicked.connect(self._create_sensor)
        self._view_button = QPushButton("View")
        self._view_button.clicked.connect(self._show_selected_sensor)

        self._buttons_layout.add_widget(self._new_button)
        self._buttons_layout.add_stretch(1)  # move view button to the right
        self._buttons_layout.add_widget(self._view_button)

        # add widgets to layout
        self._layout.add_widget(self._title)
        self._layout.add_widget(self._search_line_edit)
        self._layout.add_widget(self._sensors_list)
        self._layout.add_layout(self._buttons_layout)

    def _search(self, search_string):
        """ Filter configuration by the search string """

        # get sensors which name starts with the search_string from current configuration
        search_string = "{}%".format(search_string)
        filtered_sensors = self._db_session.query(Sensor).filter(Sensor.configuration == self._configuration).filter(
            Sensor.short_name.like(search_string)).order_by(Sensor.short_name).all()

        # clear current list and fill it with filtered sensors
        self._sensors_list.clear()
        for sensor in filtered_sensors:
            QListWidgetItem(str(sensor), self._sensors_list)

    def _show_selected_sensor(self):
        """ open view page for the selected sensor """
        # get selected items
        selected_items = self._sensors_list.selected_items()
        if selected_items:
            self._show_list_item_sensor(selected_items[0])  # show the first and only item

    def _show_list_item_sensor(self, list_item):
        """ open view page for the selected/clicked sensor """
        sensor_short_name = list_item.data(0)  # get selected sensor short name

        # find sensor in DB
        sensor = self._db_session.query(Sensor).where(Sensor.configuration == self._configuration)\
            .where(Sensor.short_name == sensor_short_name).one_or_none()

        if sensor is not None:  # if sensor found
            self.parent_widget().parent_widget().view_sensor(sensor, self._configuration_page)

    def _create_sensor(self):
        """ open a sensor creating page """
        self.parent_widget().parent_widget().create_sensor(self._configuration, self._configuration_page)
