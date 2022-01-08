from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout

from src.widgets.configurations.configuration_create_edit_widget import \
    ConfigurationCreateEditWidget
from src.widgets.configurations.configuration_create_widget import ConfigurationCreateWidget
from src.widgets.configurations.configuration_index_widget import ConfigurationIndexWidget
from src.widgets.configurations.configuration_view_widget import ConfigurationViewWidget
from src.widgets.sensors.sensor_create_edit_widget import SensorCreateEditWidget
from src.widgets.sensors.sensor_view_widget import SensorViewWidget
from src.widgets.tabs.tab_create_edit_widget import TabCreateEditWidget
from src.widgets.tabs.tab_view_widget import TabViewWidget


class ConfigurationSettingsWindow(QWidget):
    """Window for all configurations settings."""

    def __init__(self, session_maker):
        """Create configuration settings window."""
        super().__init__()
        self._db_session = session_maker()

        # set window title and size
        self.setWindowTitle("Configurations")
        self.resize(800, 600)

        # block access to other windows of application
        self.setWindowModality(Qt.ApplicationModal)

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """Initialize UI."""
        # create layout
        self._layout = QVBoxLayout(self)

        # create central widget
        self._widget = ConfigurationIndexWidget(self._db_session)

        # add widget to layout
        self._layout.addWidget(self._widget)

    def _clear_window(self):
        """Clear window (remove current central widget)."""
        self._layout.removeWidget(self._widget)
        self._widget.deleteLater()

    def create_configuration(self, configuration=None):
        """Open configuration editing page."""
        self._clear_window()

        # open editing page; set central widget to sensor edit widget
        self._widget = ConfigurationCreateWidget(self._db_session, configuration)
        self._layout.addWidget(self._widget)

    def view_configuration(self, configuration):
        """Show the given configuration."""
        self._clear_window()

        # show selected configuration;
        # set central widget to configuration view widget
        self._widget = ConfigurationViewWidget(self._db_session, configuration)
        self._layout.addWidget(self._widget)

    def edit_configuration(self, configuration):
        """Open configuration editing page."""
        self._clear_window()

        # open editing page; set central widget to sensor edit widget
        self._widget = ConfigurationCreateEditWidget(self._db_session, configuration)
        self._layout.addWidget(self._widget)

    def index_configurations(self):
        """Show all the configurations."""
        self._clear_window()

        # show all configurations;
        # set central widget to configuration index widget
        self._widget = ConfigurationIndexWidget(self._db_session)
        self._layout.addWidget(self._widget)

    def create_sensor(self, configuration, configuration_page="view"):
        """Open sensor creation page."""
        self._clear_window()

        # open sensor creation;
        # set central widget to sensor create widget
        self._widget = SensorCreateEditWidget(self._db_session, configuration=configuration,
                                              configuration_page=configuration_page)
        self._layout.addWidget(self._widget)

    def view_sensor(self, sensor, configuration_page="view"):
        """Show the given sensor."""
        self._clear_window()

        # show selected sensor;
        # set central widget to sensor view widget
        self._widget = SensorViewWidget(self._db_session, sensor,
                                        configuration_page=configuration_page)
        self._layout.addWidget(self._widget)

    def edit_sensor(self, sensor, configuration_page="view"):
        """Open sensor editing page."""
        self._clear_window()

        # open editing page; set central widget to sensor edit widget
        self._widget = SensorCreateEditWidget(self._db_session, sensor=sensor,
                                              configuration_page=configuration_page)
        self._layout.addWidget(self._widget)

    def create_tab(self, configuration, configuration_page="view"):
        """Open tab creation page."""
        self._clear_window()

        # open tab creation;
        # set central widget to tab create/edit widget in create mode
        self._widget = TabCreateEditWidget(self._db_session, configuration=configuration,
                                           configuration_page=configuration_page)
        self._layout.addWidget(self._widget)

    def view_tab(self, tab, configuration_page="view"):
        """Show the given tab."""
        self._clear_window()

        # show selected tab; set central widget to tab view widget
        self._widget = TabViewWidget(self._db_session, tab, configuration_page=configuration_page)
        self._layout.addWidget(self._widget)

    def edit_tab(self, tab, configuration_page="view"):
        """Open tab creation page."""
        self._clear_window()

        # open tab editing; set central widget to tab create/edit widget in edit mode
        self._widget = TabCreateEditWidget(self._db_session, tab=tab,
                                           configuration_page=configuration_page)
        self._layout.addWidget(self._widget)

    def close_event(self, event):
        """Finish working with resources before closing."""
        self._db_session.close()
        event.accept()
