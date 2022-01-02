from PySide6.QtCore import Qt, QMargins, QRegularExpression
from PySide6.QtGui import QFont, QRegularExpressionValidator
from PySide6.QtWidgets import QWidget, QLabel, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QVBoxLayout, \
    QComboBox, QMessageBox, QRadioButton, QButtonGroup, QSizePolicy
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property  # snake_case enabled for Pyside6

from src.models.models import Configuration, Tab, Sensor, Cell, SensorCell
from src.widgets.configuration.configuration_create_copy_widget import ConfigurationCreateCopyWidget
from src.widgets.configuration.configuration_create_edit_widget import ConfigurationCreateEditWidget


class ConfigurationCreateWidget(QWidget):
    """ Widget for creating a configuration providing option to create manually
    or create by copying other configuration"""

    def __init__(self, db_session, configuration=None):
        super().__init__()
        self._db_session = db_session

        # define if returned back to configuration creation from sensor/tab editing or creation
        if configuration:
            self._returned_to_creation = True
        else:
            self._returned_to_creation = False

        self._configuration = configuration

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """ Initialize UI """
        # create a layout
        self._layout = QVBoxLayout(self)
        self._layout.contents_margins = QMargins(0, 0, 0, 0)

        # create form layout
        self._form_layout = QFormLayout()
        self._form_layout.horizontal_spacing = 20
        self._form_layout.vertical_spacing = 20
        self._form_layout.contents_margins = QMargins(19, 0, 19, 0)

        # create a title
        self._title = QLabel()
        self._title.text = f'Create Configuration'
        self._title.font = QFont("Lato", 18)
        self._title.alignment = Qt.AlignCenter
        self._title.set_contents_margins(10, 10, 10, 20)

        # create mode selection radio buttons
        self._create_from_other_configuration = QRadioButton()
        self._create_manually = QRadioButton()

        self._mode_selection = QButtonGroup()
        self._mode_selection.add_button(self._create_from_other_configuration)
        self._mode_selection.add_button(self._create_manually)

        # if configuration creation is started already, choose manual mode automatically
        if self._returned_to_creation:
            self._create_manually.checked = True

        self._mode_selection.exclusive = True
        self._mode_selection.buttonClicked.connect(self._change_mode)

        # create main widget for creation
        if self._returned_to_creation:  # if creation in process, set manual mode and fill it with configuration data
            self._creation_widget = ConfigurationCreateEditWidget(self._db_session, configuration=self._configuration,
                                                                  returned_to_creation=self._returned_to_creation)
        else:
            self._creation_widget = QWidget()  # create a placeholder
        self._creation_widget.size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # create cancel button for case when no creation mode is selected
        if not self._returned_to_creation:
            self._buttons_layout = QHBoxLayout()
            self._buttons_layout.contents_margins = QMargins(0, 0, 20, 10)

            self._cancel_button = QPushButton("Cancel")
            self._cancel_button.clicked.connect(self.index_configurations)

            self._buttons_layout.add_stretch(1)
            self._buttons_layout.add_widget(self._cancel_button)

        # add widgets to the layout
        self._form_layout.add_row("Create from other configuration: ", self._create_from_other_configuration)
        self._form_layout.add_row("Create manually: ", self._create_manually)

        self._layout.add_widget(self._title)
        self._layout.add_layout(self._form_layout)
        self._layout.add_widget(self._creation_widget)
        if not self._returned_to_creation:
            self._layout.add_layout(self._buttons_layout)

    def _clear_creation_widget(self):
        """ Remove current creation widget from page """
        self._layout.remove_widget(self._creation_widget)
        self._creation_widget.delete_later()

        if self._cancel_button:
            self._buttons_layout.delete_later()
            self._cancel_button.delete_later()
            self._cancel_button = None

    def _change_mode(self, button):
        """ Change configuration creation mode to manual or by copying """

        self._clear_creation_widget()
        self._db_session.rollback()

        if button == self._create_manually:
            self._creation_widget = ConfigurationCreateEditWidget(self._db_session, configuration=self._configuration,
                                                                  returned_to_creation=self._returned_to_creation)
        else:
            self._creation_widget = ConfigurationCreateCopyWidget(self._db_session)

        self._creation_widget.size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._layout.add_widget(self._creation_widget)
        print(self._layout.children())
        print(self.children())

    def index_configurations(self):
        """ Open configurations index page """
        self.parent_widget().index_configurations()

    def create_sensor(self, configuration, configuration_page="view"):
        """ open sensor creation page """
        self.parent_widget().create_sensor(configuration, configuration_page)

    def view_sensor(self, sensor, configuration_page="view"):
        """ Show the given sensor """
        self.parent_widget().view_sensor(sensor, configuration_page)

    def create_tab(self, configuration, configuration_page="view"):
        """ open tab creation page """
        self.parent_widget().create_tab(configuration, configuration_page)

    def view_tab(self, tab, configuration_page="view"):
        """ Show the given tab """
        self.parent_widget().view_tab(tab, configuration_page)
