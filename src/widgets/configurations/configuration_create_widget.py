from PySide6.QtCore import Qt, QMargins
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QLabel, QFormLayout, QHBoxLayout, QPushButton, QVBoxLayout, \
    QRadioButton, QButtonGroup, QSizePolicy

from src.widgets.configurations.configuration_create_copy_widget import \
    ConfigurationCreateCopyWidget
from src.widgets.configurations.configuration_create_edit_widget import \
    ConfigurationCreateEditWidget


class ConfigurationCreateWidget(QWidget):
    """Widget for creating a configuration with option to create manually
    or by copying other configuration."""

    def __init__(self, db_session, configuration=None):
        super().__init__()
        self._db_session = db_session

        # define if returned back to configuration
        # creation from sensor/tab viewing/editing/creation
        if configuration:
            self._returned_to_creation = True
        else:
            self._returned_to_creation = False

        self._configuration = configuration

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """Initialize UI."""
        # create a layout
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        # create form layout
        self._form_layout = QFormLayout()
        self._form_layout.setHorizontalSpacing(20)
        self._form_layout.setVerticalSpacing(20)
        self._form_layout.setContentsMargins(19, 0, 19, 0)

        # create a title
        self._title = QLabel()
        self._title.setText(f'Create Configuration')
        self._title.setFont(QFont("Lato", 18))
        self._title.setAlignment(Qt.AlignCenter)
        self._title.setContentsMargins(10, 10, 10, 20)

        # create mode selection radio buttons
        self._create_from_other_configuration = QRadioButton()
        self._create_manually = QRadioButton()

        self._mode_selection = QButtonGroup()
        self._mode_selection.addButton(self._create_from_other_configuration)
        self._mode_selection.addButton(self._create_manually)

        # if configuration creation is started already,
        # choose manual mode automatically
        if self._returned_to_creation:
            self._create_manually.setChecked(True)

        self._mode_selection.setExclusive(True)
        self._mode_selection.buttonClicked.connect(self._change_mode)

        # create main widget for creation
        if self._returned_to_creation:
            # if creation in process, set manual mode
            # and fill it with configuration data
            self._creation_widget = ConfigurationCreateEditWidget(
                self._db_session,
                configuration=self._configuration,
                returned_to_creation=self._returned_to_creation
            )
        else:
            self._creation_widget = QWidget()  # create a placeholder
        self._creation_widget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,
                                                        QSizePolicy.Expanding))

        # create cancel button in case no creation mode is selected
        if not self._returned_to_creation:
            self._buttons_layout = QHBoxLayout()
            self._buttons_layout.setContentsMargins(0, 0, 20, 10)

            self._cancel_button = QPushButton("Cancel")
            self._cancel_button.clicked.connect(self.index_configurations)

            self._buttons_layout.addStretch(1)
            self._buttons_layout.addWidget(self._cancel_button)

        # add widgets to the layout
        self._form_layout.addRow("Create from other configuration: ",
                                  self._create_from_other_configuration)
        self._form_layout.addRow("Create manually: ", self._create_manually)

        self._layout.addWidget(self._title)
        self._layout.addLayout(self._form_layout)
        self._layout.addWidget(self._creation_widget)
        if not self._returned_to_creation:
            self._layout.addLayout(self._buttons_layout)

    def _clear_creation_widget(self):
        """Remove current creation widget from page."""
        self._layout.removeWidget(self._creation_widget)
        self._creation_widget.deleteLater()

        if self._cancel_button:
            self._buttons_layout.deleteLater()
            self._cancel_button.deleteLater()
            self._cancel_button = None

    def _change_mode(self, button):
        """Change configuration creation mode to manual or copying."""

        self._clear_creation_widget()
        self._db_session.rollback()

        if button == self._create_manually:
            self._creation_widget = ConfigurationCreateEditWidget(
                self._db_session,
                configuration=self._configuration,
                returned_to_creation=self._returned_to_creation
            )
        else:
            self._creation_widget = ConfigurationCreateCopyWidget(self._db_session)

        self._creation_widget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,
                                                        QSizePolicy.Expanding))
        self._layout.addWidget(self._creation_widget)

    def index_configurations(self):
        """Open configurations index page."""
        self.parentWidget().index_configurations()

    def create_sensor(self, configuration, configuration_page="view"):
        """Open sensor creation page."""
        self.parentWidget().create_sensor(configuration, configuration_page)

    def view_sensor(self, sensor, configuration_page="view"):
        """Show the given sensor."""
        self.parentWidget().view_sensor(sensor, configuration_page)

    def create_tab(self, configuration, configuration_page="view"):
        """Open tab creation page."""
        self.parentWidget().create_tab(configuration, configuration_page)

    def view_tab(self, tab, configuration_page="view"):
        """Show the given tab."""
        self.parentWidget().view_tab(tab, configuration_page)
