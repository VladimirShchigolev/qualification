from PySide6.QtCore import Qt, QMargins
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QLabel, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, \
    QVBoxLayout, QMessageBox

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
        self._form_layout.setHorizontalSpacing(20)
        self._form_layout.setContentsMargins(10, 0, 10, 0)

        # create a title
        self._title = QLabel()
        self._title.setText("View Sensor")
        self._title.setFont(QFont("Lato", 18))
        self._title.setAlignment(Qt.AlignCenter)
        self._title.setContentsMargins(10, 10, 10, 20)

        # create short name field display
        self._short_name_line = QLineEdit()
        self._short_name_line.setText(self._sensor.short_name)
        self._short_name_line.setReadOnly(True)

        # create name field display
        self._name_line = QLineEdit()
        self._name_line.setText(self._sensor.name)
        self._name_line.setReadOnly(True)

        # create physical value field display
        self._physical_value_line = QLineEdit()
        self._physical_value_line.setText(self._sensor.physical_value)
        self._physical_value_line.setReadOnly(True)

        # create physical unit field display
        self._physical_unit_line = QLineEdit()
        self._physical_unit_line.setText(self._sensor.physical_unit)
        self._physical_unit_line.setReadOnly(True)

        # section of buttons
        self._buttons_layout = QHBoxLayout()
        self._buttons_layout.setContentsMargins(10, 0, 10, 0)

        self._edit_button = QPushButton("Edit")
        self._edit_button.clicked.connect(self._edit_sensor)

        self._delete_button = QPushButton("Delete")
        self._delete_button.clicked.connect(self._delete)

        self._back_button = QPushButton("Back To Configuration")
        self._back_button.clicked.connect(self._return_to_configuration)

        self._buttons_layout.addWidget(self._edit_button)
        self._buttons_layout.addWidget(self._delete_button)

        # move back button to the right
        self._buttons_layout.addStretch(1)

        self._buttons_layout.addWidget(self._back_button)

        # add widgets to layout

        # add configuration data
        self._form_layout.addRow(self._title)
        self._form_layout.addRow("Short Name:", self._short_name_line)
        self._form_layout.addRow("Name:", self._name_line)
        self._form_layout.addRow("Physical Value:", self._physical_value_line)
        self._form_layout.addRow("Physical Unit:", self._physical_unit_line)
        self._layout.addLayout(self._form_layout)

        self._layout.addStretch(1)  # move buttons to the bottom

        # add buttons
        self._layout.addLayout(self._buttons_layout)

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
        self.parentWidget().edit_sensor(self._sensor)

    def _return_to_configuration(self):
        """Open back the configuration creation/editing/view page."""
        if self._configuration_page == "edit":
            self.parentWidget().edit_configuration(self._sensor.configuration)
        elif self._configuration_page == "create":
            self.parentWidget().create_configuration(self._sensor.configuration)
        else:
            self.parentWidget().view_configuration(self._sensor.configuration)
