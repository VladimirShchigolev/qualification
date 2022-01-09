import json
import os
import re

from PySide6.QtGui import QAction
from PySide6.QtNetwork import QTcpSocket, QHostAddress
from PySide6.QtWidgets import QMainWindow, QMenuBar, QMenu, QStatusBar, QWidget, QMessageBox, \
    QFileDialog

from sqlalchemy.exc import SQLAlchemyError

from src.models.models import Configuration
from src.widgets.adress_window import AddressWindow
from src.widgets.configuration_settings_window import ConfigurationSettingsWindow
from src.widgets.console_widget import ConsoleWidget
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
        self.showMaximized()

        self._init_ui()
        self._console = ConsoleWidget()

        # load active configuration
        self._configuration = None
        self._load_configuration()

        # set up recording control
        self._recording = False
        self._record_file = None

        # set up TCP socket
        self._socket = QTcpSocket(self)
        self._socket.readyRead.connect(self._read_from_socket)
        self._socket.errorOccurred.connect(self._show_socket_error)

        # set state
        self._active_session = False
        self._opened_file = False

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

        self._action_close = QAction(self)
        self._action_close.setText("Close Session")
        self._action_close.setDisabled(True)

        self._action_record = QAction(self)
        self._action_record.setText("Start Recording")

        self._action_configurations = QAction(self)
        self._action_configurations.setText("Configurations")

        self._action_data_source = QAction(self)
        self._action_data_source.setText("Data Source")

        self._action_console = QAction(self)
        self._action_console.setText("Console")

        # add actions to the menu
        self._menu_file.addActions(
            [self._action_new,
             self._action_open,
             self._action_record]
        )
        self._menu_file.addAction(self._action_new)
        self._menu_file.addAction(self._action_open)
        self._menu_file.addSeparator()
        self._menu_file.addAction(self._action_close)
        self._menu_file.addSeparator()
        self._menu_file.addAction(self._action_record)

        self._menu_bar.addAction(self._menu_file.menuAction())

        self._menu_settings.addAction(self._action_configurations)
        self._menu_settings.addAction(self._action_data_source)
        self._menu_bar.addAction(self._menu_settings.menuAction())

        self._menu_bar.addAction(self._action_console)

        # connect actions to methods
        self._action_new.triggered.connect(self._start_new_session)
        self._action_open.triggered.connect(self._open_record)
        self._action_close.triggered.connect(self._stop_session)
        self._action_record.triggered.connect(self._record)
        self._action_configurations.triggered.connect(self._open_configurations)
        self._action_data_source.triggered.connect(self._open_data_source_settings)
        self._action_console.triggered.connect(self._open_console)

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

    def _open_console(self):
        """Opens console window."""
        if not self._console.isVisible():
            self._console.show()
        self._console.activateWindow()  # bring to front

    def _load_configuration(self, name=None):
        """Loads configuration and updates ui"""
        db_session = self._session_maker()
        try:
            configuration = Configuration.load(db_session, name=name)
        except SQLAlchemyError as e:
            configuration = None
            # show error message
            QMessageBox.critical(self, "Error!", "Cannot load the configuration!", QMessageBox.Ok,
                                 QMessageBox.Ok)
            raise

        if configuration:
            self._configuration = configuration
            self._init_visualization(configuration)

        db_session.close()

    def _open_configurations(self):
        """Open configuration settings window."""
        self._configurations_window = ConfigurationSettingsWindow(self._session_maker)
        self._configurations_window.show()

    def _open_data_source_settings(self):
        """Open data source settings window."""
        db_session = self._session_maker()
        self._data_source_settings_window = AddressWindow(db_session)
        self._data_source_settings_window.show()
        db_session.close()

    def _record(self):
        """Enables or disables recording."""
        if self._recording:
            try:
                self._record_file.close()
            except (OSError, IOError):
                QMessageBox.critical(self, "Error!", f'Error while closing file',
                                     QMessageBox.Ok, QMessageBox.Ok)
            finally:
                self._recording = False
                self._action_record.setText("Start Recording")
        else:
            filename, _ = QFileDialog.getSaveFileName(self, filter="Text files (*.txt)")
            if filename:
                # open the file and handle possible exceptions
                try:
                    self._record_file = open(filename, 'w')
                except (OSError, IOError):
                    QMessageBox.critical(self, "Error!", f'Unable to create file!',
                                         QMessageBox.Ok, QMessageBox.Ok)
                    self._record_file = None

                # start recording if file created successfully
                if self._record_file:
                    self._recording = True
                    self._action_record.setText("Stop Recording")
                    self._record_file.write(
                        f'{"configuration": "{self._configuration.name}"}')

    def _open_record(self):
        """Open record file."""
        self._stop_session()

        filename, _ = QFileDialog.getOpenFileName(self, "Open recording",
                                                  filter="Text files (*.txt)")
        try:
            file = open(filename, 'r')
        except FileNotFoundError:
            QMessageBox.critical(self, "Error!", f'File {filename} not found!',
                                 QMessageBox.Ok, QMessageBox.Ok)
            file = None
        except (IOError, OSError):
            QMessageBox.critical(self, "Error!", f'Unable to open the file!',
                                 QMessageBox.Ok, QMessageBox.Ok)
            file = None

        if file:
            # check if file format is OK
            if '\n' not in file.read(10000):
                QMessageBox.critical(self, "Error!", f'Wrong file format!',
                                     QMessageBox.Ok, QMessageBox.Ok)
                self._stop_session()
                return
            file.seek(0)

            first_line = file.readline()
            try:
                configuration_suggestion = json.loads(first_line.strip())
            except json.JSONDecodeError:
                configuration_suggestion = None

            if configuration_suggestion and "configuration" in configuration_suggestion:
                configuration = Configuration.find(configuration_suggestion["configuration"])
                if configuration is not None:
                    confirmation = QMessageBox.question(
                        self, "Select configuration",
                        f'Configuration {configuration.name} is suggested. Load it?',
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
                    )
                    if confirmation == QMessageBox.Yes:
                        self._load_configuration(configuration)

                line = file.readline()
            else:
                line = first_line

            # process the data in file
            while line:
                self._process_data(line)
                line = file.readline()

            file.close()
            self._action_close.setDisabled(False)

    def _stop_session(self):
        """Stop active session of file reading session."""
        if self._active_session:
            self._socket.disconnectFromHost()
            self._active_session = False
        self._load_configuration()
        self._opened_file = False

        self._action_close.setDisabled(True)

    def _start_new_session(self):
        """Start new active session."""
        self._stop_session()
        self._active_session = True
        self._action_close.setDisabled(False)
        self._connect()

    def _connect(self):
        """Connect to data source."""
        self._active_session = True
        self._socket.abort()
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
            correct = True
            # check if obligatory fields are in data
            if correct and ("timestamp" not in data or "sensors" not in data
                            or not isinstance(data["sensors"], dict)):
                correct = False

            # check if timestamp format is correct
            if not re.match('^[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}$', data["timestamp"]):
                correct = False

            # check if values of sensors are numbers
            if correct:
                for sensor_value in data["sensors"].values():
                    if not (isinstance(sensor_value, int) or isinstance(sensor_value, float)):
                        correct = False
                        break

            return correct

        # save to file if recording is enabled
        if self._recording:
            try:
                self._record_file.write(line+"\n")
                # save changes to the file
                self._record_file.flush()
                os.fsync(self._record_file.fileno())
            except (OSError, IOError):
                QMessageBox.critical(self, "Error!",
                                     'Unable to write to file! Recording stopped!',
                                     QMessageBox.Ok, QMessageBox.Ok)
                # stop recording
                self._record()

        if len(line) > 6000:
            self._console.print("Line is too long: " + line[:6000] + "...", warning=True)
        else:
            # check if data format is correct
            correct_format = True
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                data = None
                correct_format = False

            if correct_format:
                correct_format = check_correctness(data)

            if correct_format:
                # show new data on graphs and in the console
                self._update_graphs(data)
                self._console.print(line)
            else:
                self._console.print("Wrong format: " + line, warning=True)

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
