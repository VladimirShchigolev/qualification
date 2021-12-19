from PySide6.QtCore import Qt, QMargins
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QLabel, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QVBoxLayout
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property  # snake_case enabled for Pyside6

from src.widgets.sensors.sensor_index_widget import SensorIndexWidget


class ConfigurationViewWidget(QWidget):
    """ Widget for viewing a certain configuration """

    def __init__(self, db_session, configuration):
        super().__init__()
        self._db_session = db_session
        self._configuration = configuration

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """ Initialize UI """
        # create a layout
        self._layout = QVBoxLayout(self)

        self._form_layout = QFormLayout()
        self._form_layout.horizontal_spacing = 20
        self._form_layout.contents_margins = QMargins(10, 0, 10, 0)

        # create a title
        self._title = QLabel()
        self._title.text = "View Configuration"
        self._title.font = QFont("Lato", 18)
        self._title.alignment = Qt.AlignCenter
        self._title.set_contents_margins(10, 10, 10, 20)

        # create name field display
        self._name_line = QLineEdit()
        self._name_line.text = self._configuration.name
        self._name_line.read_only = True

        # create sensors and tabs display
        self._sensors_and_tabs_layout = QHBoxLayout()

        self._sensors_widget = SensorIndexWidget(self._db_session, self._configuration)
        self._sensors_and_tabs_layout.add_widget(self._sensors_widget)

        # create buttons
        self._buttons_layout = QHBoxLayout()
        self._buttons_layout.contents_margins = QMargins(10, 0, 10, 0)

        self._load_button = QPushButton("Load")
        self._edit_button = QPushButton("Edit")
        self._back_button = QPushButton("Back To Configurations")
        self._back_button.clicked.connect(self._index_configurations)

        self._buttons_layout.add_widget(self._load_button)
        self._buttons_layout.add_widget(self._edit_button)
        self._buttons_layout.add_stretch(1)  # move back button to the right
        self._buttons_layout.add_widget(self._back_button)

        # add widgets to layout
        # add configuration data
        self._form_layout.add_row(self._title)
        self._form_layout.add_row("Name:", self._name_line)
        self._layout.add_layout(self._form_layout)
        self._layout.add_layout(self._sensors_and_tabs_layout)

        self._layout.add_stretch(1)  # move buttons to the bottom

        # add buttons
        self._layout.add_layout(self._buttons_layout)

    def _index_configurations(self):
        self.parent_widget().index_configurations()
