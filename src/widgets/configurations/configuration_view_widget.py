from PySide6.QtCore import Qt, QMargins
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QLabel, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, \
    QVBoxLayout

from src.widgets.sensors.sensor_index_widget import SensorIndexWidget
from src.widgets.tabs.tab_index_widget import TabIndexWidget


class ConfigurationViewWidget(QWidget):
    """Widget for viewing a certain configuration."""

    def __init__(self, db_session, configuration):
        """Create configuration view page"""
        super().__init__()
        self._db_session = db_session
        self._configuration = configuration

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """Initialize UI."""
        # create a layout
        self._layout = QVBoxLayout(self)

        self._form_layout = QFormLayout()
        self._form_layout.setHorizontalSpacing(20)
        self._form_layout.setContentsMargins(10, 0, 10, 0)

        # create a title
        self._title = QLabel()
        self._title.setText("View Configuration")
        self._title.setFont(QFont("Lato", 18))
        self._title.setAlignment(Qt.AlignCenter)
        self._title.setContentsMargins(10, 10, 10, 20)

        # create name field display
        self._name_line = QLineEdit()
        self._name_line.setText(self._configuration.name)
        self._name_line.setReadOnly(True)

        # create sensors and tabs display
        self._sensors_and_tabs_layout = QHBoxLayout()

        self._sensors_widget = SensorIndexWidget(self._db_session, self._configuration,
                                                 configuration_page="view", read_only=True)
        self._sensors_and_tabs_layout.addWidget(self._sensors_widget)

        self._tabs_widget = TabIndexWidget(self._db_session, self._configuration,
                                           configuration_page="view", read_only=True)
        self._sensors_and_tabs_layout.addWidget(self._tabs_widget)

        # section of buttons
        self._buttons_layout = QHBoxLayout()
        self._buttons_layout.setContentsMargins(10, 0, 10, 0)

        self._load_button = QPushButton("Load")
        self._edit_button = QPushButton("Edit")
        self._edit_button.clicked.connect(self._edit_configuration)
        self._back_button = QPushButton("Back To Configurations")
        self._back_button.clicked.connect(self._return_to_configurations)

        self._buttons_layout.addWidget(self._load_button)
        self._buttons_layout.addWidget(self._edit_button)

        # move back button to the right
        self._buttons_layout.addStretch(1)

        self._buttons_layout.addWidget(self._back_button)

        # add widgets to layout
        # add configuration data
        self._form_layout.addRow(self._title)
        self._form_layout.addRow("Name:", self._name_line)
        self._layout.addLayout(self._form_layout)
        self._layout.addLayout(self._sensors_and_tabs_layout)

        self._layout.addStretch(1)  # move buttons to the bottom

        # add buttons
        self._layout.addLayout(self._buttons_layout)

    def _edit_configuration(self):
        """Open configuration editing page."""
        self.parentWidget().edit_configuration(self._configuration)

    def _return_to_configurations(self):
        """Open configurations index page."""
        self.parentWidget().index_configurations()
