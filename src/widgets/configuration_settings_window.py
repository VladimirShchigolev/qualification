from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property  # snake_case enabled for Pyside6
from src.widgets.configuration.configuration_index_widget import ConfigurationIndexWidget
from src.widgets.configuration.configuration_view_widget import ConfigurationViewWidget


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
        """ Set central widget to configuration view widget """
        self._clear_window()

        # show selected configuration; set central widget to configuration view widget
        self._widget = ConfigurationViewWidget(self._db_session, configuration)
        self._layout.add_widget(self._widget)

    def index_configurations(self):
        """ Set central widget to configuration index widget """
        self._clear_window()

        # show all configurations; set central widget to configuration index widget
        self._widget = ConfigurationIndexWidget(self._db_session)
        self._layout.add_widget(self._widget)