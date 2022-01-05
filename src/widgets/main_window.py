from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QMenuBar, QMenu, QStatusBar, QWidget, QMessageBox

from sqlalchemy.exc import SQLAlchemyError

from src.models.models import Configuration
from src.widgets.configuration_settings_window import ConfigurationSettingsWindow
from src.widgets.graphs.graph_tab_widget import GraphTabWidget


class MainWindow(QMainWindow):
    """Main window of the application."""

    def __init__(self, session_maker):
        """Create main window."""
        super().__init__()

        self._session_maker = session_maker

        # set window title
        self.setWindowTitle("Sensor Measurement Data Visualization")

        # set window size
        self.setMinimumSize(800, 600)
        #self.showMaximized()

        self._init_ui()

        # load active configuration
        self._load_configuration()

    def _init_ui(self):
        """Initialize UI."""
        # create menu bar
        self._menu_bar = QMenuBar(self)

        self._menu_file = QMenu(self._menu_bar)
        self._menu_file.setTitle("File")

        self._menu_settings = QMenu(self._menu_bar)
        self._menu_settings.setTitle("Settings")

        self.setMenuBar(self._menu_bar)

        # create actions
        self._action_new = QAction(self)
        self._action_new.setText("New Session")

        self._action_open = QAction(self)
        self._action_open.setText("Open Recording")

        self._action_record = QAction(self)
        self._action_record.setText("Start Recording")

        self._action_configurations = QAction(self)
        self._action_configurations.setText("Configurations")

        # add actions to the menu
        self._menu_file.addActions(
            [self._action_new,
             self._action_open,
             self._action_record]
        )
        self._menu_bar.addAction(self._menu_file.menuAction())

        self._menu_settings.addAction(self._action_configurations)
        self._menu_bar.addAction(self._menu_settings.menuAction())

        # self.actionNew.triggered.connect(self.start_new_session)
        # self.actionOpen.triggered.connect(self.open_record)
        # self.actionRecord.triggered.connect(self.record)
        self._action_configurations.triggered.connect(self._open_configurations)

        self._tabs = QWidget()
        self.setCentralWidget(self._tabs)

    def _init_visualization(self, configuration):
        """Initialize graph page and console"""
        # remove old widget
        self._tabs.deleteLater()

        # create new graph tabs page
        self._tabs = GraphTabWidget(configuration)
        self._graphs = self._tabs.get_graphs()
        print(self._graphs)
        self.setCentralWidget(self._tabs)

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

    def _open_configurations(self):
        """Open configuration settings window."""

        self._configurations_window = ConfigurationSettingsWindow(self._session_maker)
        self._configurations_window.show()
        print("lol")

    def close_event(self, event):
        """Finish work with resources before closing."""
        self._tabs.close()
        event.accept()
