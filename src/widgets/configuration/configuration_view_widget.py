from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QLabel, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QVBoxLayout
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property  # snake_case enabled for Pyside6


class ConfigurationViewWidget(QWidget):
    """ Widget for viewing a certain configuration """

    def __init__(self, db_session, configuration):
        super().__init__()
        self._db_session = db_session
        self._configuration = configuration

        self._init_ui()  # initialize UI

    def _init_ui(self):
        # create a layout
        self._layout = QVBoxLayout(self)

        self._form_layout = QFormLayout()

        # create a title
        self._title = QLabel()
        self._title.text = "View Configuration"
        self._title.font = QFont("Lato", 18)
        self._title.alignment = Qt.AlignCenter

        # create name field display
        self._name_line = QLineEdit()
        self._name_line.text = self._configuration.name
        self._name_line.read_only = True

        # create buttons
        self._button_layout = QHBoxLayout()

        self._load_button = QPushButton("Load")
        self._edit_button = QPushButton("Edit")
        self._back_button = QPushButton("All Configurations")
        self._back_button.clicked.connect(self._index_configurations)

        self._button_layout.add_stretch(1)  # move buttons to the right
        self._button_layout.add_widget(self._load_button)
        self._button_layout.add_widget(self._edit_button)
        self._button_layout.add_widget(self._back_button)

        # add widgets to layout
        # add configuration data
        self._form_layout.add_row(self._title)
        self._form_layout.add_row("Name:", self._name_line)
        self._layout.add_layout(self._form_layout)
        self._layout.add_stretch(1)

        # add buttons
        self._layout.add_layout(self._button_layout)

    def _index_configurations(self):
        self.parent_widget().index_configurations()