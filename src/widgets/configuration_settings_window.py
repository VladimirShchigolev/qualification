from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property  # snake_case enabled for Pyside6
from src.widgets.configuration.configuration_index_widget import ConfigurationIndexWidget
from src.widgets.configuration.configuration_view_widget import ConfigurationViewWidget
from src.widgets.sensors.sensor_view_widget import SensorViewWidget


class ConfigurationSettingsWindow(QWidget):
    """ Window for all configurations settings (configurations, tabs, cells, sensors) """

    def __init__(self, db_session):
        super().__init__()
        self._db_session = db_session

        # set window title and size
        self.window_title = "Configurations"
        self.resize(800, 600)

        self.window_modality = Qt.ApplicationModal  # block access to other windows of application

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """ Initialize UI """
        # create layout
        self._layout = QVBoxLayout(self)

        # create central widget
        self._widget = ConfigurationIndexWidget(self._db_session)

        # add widget to layout
        self._layout.add_widget(self._widget)

    def _clear_window(self):
        """ Clear window (remove current central widget) """
        self._layout.remove_widget(self._widget)
        self._widget.deleteLater()

    def view_configuration(self, configuration):
        """ Show the given configuration """
        self._clear_window()

        # show selected configuration; set central widget to configuration view widget
        self._widget = ConfigurationViewWidget(self._db_session, configuration)
        self._layout.add_widget(self._widget)

    def index_configurations(self):
        """ Show all the configurations """
        self._clear_window()

        # show all configurations; set central widget to configuration index widget
        self._widget = ConfigurationIndexWidget(self._db_session)
        self._layout.add_widget(self._widget)

    def view_sensor(self, sensor):
        """ Show the given sensor """
        self._clear_window()

        # show selected sensor; set central widget to senosor view widget
        self._widget = SensorViewWidget(self._db_session, sensor)
        self._layout.add_widget(self._widget)
