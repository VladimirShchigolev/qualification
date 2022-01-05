import json
import re

from PySide6.QtGui import QAction
from PySide6.QtNetwork import QTcpSocket, QHostAddress
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

        # set up TCP socket
        self._socket = QTcpSocket(self)
        self._socket.readyRead.connect(self._read_from_socket)
        self._socket.errorOccurred.connect(self._show_socket_error)
        self._connect()

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

    def _connect(self):
        """Connect to data source."""
        self._socket.connectToHost("127.0.0.1", 64363)

    def _read_from_socket(self):
        """Reads data from socket when new data arrives."""
        if self._socket.canReadLine():
            # convert from QBytearray to str
            line = str(self._socket.readLine())[2:-3].strip()
            self._process_data(line)

    def _process_data(self, line):
        """Process the data in the given string."""
        def check_correctness(data):
            correct_format = True
            # check if obligatory fields are in data
            if correct_format and ("timestamp" not in data or "sensors" not in data
                                   or not isinstance(data["sensors"], dict)):
                correct_format = False

            print("uno", correct_format)
            # check if timestamp format is correct
            if not re.match('^[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}$', data["timestamp"]):
                correct_format = False
            print("duo", correct_format)
            # check if values of sensors are numbers
            if correct_format:
                for sensor_value in data["sensors"].values():
                    print(sensor_value)
                    if not (isinstance(sensor_value, int) or isinstance(sensor_value, float)):
                        correct_format = False
                        break

            return correct_format

        if len(line) > 6000:
            print("Line is too long: " + line[:6000] + "...")
        else:
            correct_format = True
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                data = None
                correct_format = False

            if correct_format:
                correct_format = check_correctness(data)

            if correct_format:
                self._update_graphs(data)
                print(line)
            else:
                print("Wrong format: " + line)

    def _update_graphs(self, data):
        """Add new points to the graphs."""
        def timestamp_to_seconds(timestamp):
            """Turns string timestamp into seconds"""
            # timestamp format:
            # HH:MM:SS.mmm
            h, m, s_and_ms = timestamp.split(":")
            s, ms = s_and_ms.split(".")
            return int(h)*3600 + int(m)*60 + int(s) + int(ms) / 1000

        seconds = timestamp_to_seconds(data["timestamp"])
        for sensor, value in data["sensors"].items():
            if sensor in self._graphs:
                for graph in self._graphs[sensor]:
                    graph.update_data(seconds, value, line=sensor)

    def _show_socket_error(self, error):
        """Show socket error when it occurs."""
        print(error)

    def close_event(self, event):
        """Finish work with resources before closing."""
        self._tabs.close()
        event.accept()
