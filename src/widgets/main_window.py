from PySide6.QtCore import QSize
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QMenuBar, QMenu, QStatusBar, QWidget, QMessageBox

# enable snake_case for Pyside6
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property

from sqlalchemy.exc import SQLAlchemyError

from src.models.models import Configuration
from src.widgets.graphs.graph_tab_widget import GraphTabWidget


class MainWindow(QMainWindow):
    """Main window of the application."""

    def __init__(self, session_maker):
        """Create main window."""
        super().__init__()

        self._session_maker = session_maker

        # set window title
        self.window_title = "Sensor Measurement Data Visualization"

        # set window size
        self.minimum_size = QSize(800, 600)
        self.showMaximized()

        self._init_ui()

        # load active configuration
        self._load_configuration()

    def _init_ui(self):
        """Initialize UI."""
        # create menu bar
        self._menu_bar = QMenuBar(self)

        self._menu_file = QMenu(self._menu_bar)
        self._menu_file.title = "File"

        self._menu_settings = QMenu(self._menu_bar)
        self._menu_settings.title = "Settings"

        self.set_menu_bar(self._menu_bar)

        # create status bar
        self._status_bar = QStatusBar(self)
        self.set_status_bar(self._status_bar)

        # create actions
        self._action_new = QAction(self)
        self._action_new.text = "New Session"

        self._action_open = QAction(self)
        self._action_open.text = "Open Recording"

        self._action_record = QAction(self)
        self._action_record.text = "Start Recording"

        self._action_configurations = QAction(self)
        self._action_configurations.text = "Configurations"

        # add actions to the menu
        self._menu_file.add_action(self._action_new)
        self._menu_file.add_action(self._action_open)
        self._menu_file.add_action(self._action_record)
        self._menu_bar.add_action(self._menu_file.menu_action())

        self._menu_settings.add_action(self._action_configurations)
        self._menu_bar.add_action(self._menu_settings.menu_action())

        # self.actionNew.triggered.connect(self.start_new_session)
        # self.actionOpen.triggered.connect(self.open_record)
        # self.actionRecord.triggered.connect(self.record)
        # self.actionSettings.triggered.connect(self.open_settings)

        self._tabs = QWidget()
        self.set_central_widget(self._tabs)

    def _init_visualization(self, configuration):
        """Initialize graph page and console"""
        # remove old widget
        self._tabs.delete_later()

        # create new graph tabs page
        self._tabs = GraphTabWidget(configuration)
        self.set_central_widget(self._tabs)

    def _load_configuration(self):
        """Loads active configuration and updates ui"""
        db_session = self._session_maker()
        try:
            configuration = Configuration.load(db_session)
        except SQLAlchemyError as e:
            print(e)
            configuration = None
            # show error message
            QMessageBox.critical(self, "Error!", "Cannot load the configuration!", QMessageBox.Ok,
                                 QMessageBox.Ok)
            raise

        print(configuration)
        if configuration:
            self._init_visualization(configuration)

        db_session.close()

    def close_event(self, event):
        """Finish work with resources before closing"""
        event.accept()
