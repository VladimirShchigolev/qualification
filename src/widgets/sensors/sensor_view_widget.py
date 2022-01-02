from PySide6.QtCore import Qt, QMargins
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QLabel, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, \
    QVBoxLayout, QMessageBox

# enable snake_case for Pyside6
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property


class SensorViewWidget(QWidget):
    """Widget for viewing a certain sensor."""

    def __init__(self, db_session, sensor, configuration_page="view"):
        """Create sensor viewing widget."""
        super().__init__()
        self._db_session = db_session
        self._sensor = sensor

        # from what page this page was open (where to return later)
        self._configuration_page = configuration_page

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """Initialize UI."""
        # create a layout
        self._layout = QVBoxLayout(self)

        self._form_layout = QFormLayout()
        self._form_layout.horizontal_spacing = 20
        self._form_layout.contents_margins = QMargins(10, 0, 10, 0)

        # create a title
        self._title = QLabel()
        self._title.text = "View Sensor"
        self._title.font = QFont("Lato", 18)
        self._title.alignment = Qt.AlignCenter
        self._title.set_contents_margins(10, 10, 10, 20)

        # create short name field display
        self._short_name_line = QLineEdit()
        self._short_name_line.text = self._sensor.short_name
        self._short_name_line.read_only = True

        # create name field display
        self._name_line = QLineEdit()
        self._name_line.text = self._sensor.name
        self._name_line.read_only = True

        # create physical value field display
        self._physical_value_line = QLineEdit()
        self._physical_value_line.text = self._sensor.physical_value
        self._physical_value_line.read_only = True

        # create physical unit field display
        self._physical_unit_line = QLineEdit()
        self._physical_unit_line.text = self._sensor.physical_unit
        self._physical_unit_line.read_only = True

        # section of buttons
        self._buttons_layout = QHBoxLayout()
        self._buttons_layout.contents_margins = QMargins(10, 0, 10, 0)

        self._edit_button = QPushButton("Edit")
        self._edit_button.clicked.connect(self._edit_sensor)

        self._delete_button = QPushButton("Delete")
        self._delete_button.clicked.connect(self._delete)

        self._back_button = QPushButton("Back To Configuration")
        self._back_button.clicked.connect(self._return_to_configuration)

        self._buttons_layout.add_widget(self._edit_button)
        self._buttons_layout.add_widget(self._delete_button)

        # move back button to the right
        self._buttons_layout.add_stretch(1)

        self._buttons_layout.add_widget(self._back_button)

        # add widgets to layout

        # add configuration data
        self._form_layout.add_row(self._title)
        self._form_layout.add_row("Short Name:", self._short_name_line)
        self._form_layout.add_row("Name:", self._name_line)
        self._form_layout.add_row("Physical Value:", self._physical_value_line)
        self._form_layout.add_row("Physical Unit:", self._physical_unit_line)
        self._layout.add_layout(self._form_layout)

        self._layout.add_stretch(1)  # move buttons to the bottom

        # add buttons
        self._layout.add_layout(self._buttons_layout)

    def _delete(self):
        """Removes the sensor from database."""
        # ask for confirmation
        confirmation = QMessageBox.question(
            self, "Delete", f'Are you sure you want to delete sensor {self._sensor.short_name}?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        # if confirmed, remove sensor and redirect to configuration
        if confirmation == QMessageBox.Yes:
            self._db_session.delete(self._sensor)

            self._return_to_configuration()

    def _edit_sensor(self):
        """Open sensor editing page."""
        self.parent_widget().edit_sensor(self._sensor)

    def _return_to_configuration(self):
        """Open back the configuration creation/editing/view page."""
        if self._configuration_page == "edit":
            self.parent_widget().edit_configuration(self._sensor.configuration)
        elif self._configuration_page == "create":
            self.parent_widget().create_configuration(self._sensor.configuration)
        else:
            self.parent_widget().view_configuration(self._sensor.configuration)
