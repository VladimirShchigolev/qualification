from PySide6.QtCore import Qt, QRegularExpression, QMargins
from PySide6.QtGui import QFont, QRegularExpressionValidator
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QScrollArea, QGridLayout, QSizePolicy, QVBoxLayout, \
    QLineEdit, QComboBox, QListWidget, QListWidgetItem
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property  # snake_case enabled for Pyside6

from src.models.models import Cell, Sensor


class CellEditWidget(QWidget):
    """ Widget responsible for editing a cell.
    Allows selecting and removing sensors for the cell
    and editing the name of the cell if more than one sensor is used.
    """

    def __init__(self, db_session, cell):
        super().__init__()
        self._db_session = db_session
        self._cell = cell
        self._configuration = cell.tab.configuration

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """ Initialize UI """
        self.maximum_width = 250
        # create a layout
        self._layout = QVBoxLayout(self)
        self._layout.contents_margins = QMargins(0, 0, 0, 0)

        # create title field display
        self._title_line = QLineEdit()
        self._title_line.text = ""
        self._title_line.placeholder_text = "Title"
        self._title_line.read_only = True

        # create sensor search combo box
        self._sensors_search = QComboBox()
        self._sensors_search.editable = True
        self._sensors_search.completer().case_sensitivity = Qt.CaseInsensitive  # set case insensitive completion
        self._sensors_search.current_text = ""
        self._sensors_search.placeholder_text = "Add Sensor"

        # set validation rules to upper and lower English letters, digits and underscore, 1-10 characters in length
        self._sensors_search.set_validator(
            QRegularExpressionValidator(QRegularExpression(r'[A-Za-z0-9_]{1,10}'))
        )

        # get all configuration sensors from DB
        all_sensors = self._db_session.query(Sensor).filter(Sensor.configuration == self._configuration) \
            .order_by(Sensor.short_name).all()

        for sensor in all_sensors:
            self._sensors_search.add_item(str(sensor))

        # create added sensors' list
        self._sensors_list = QListWidget()
        self._sensors_list.alternating_row_colors = True

        # add cell's sensors to the sensors' list
        # for sensor in all_sensors:
        #     QListWidgetItem(str(sensor), self._sensors_list)

        # add widgets to layout
        self._layout.add_widget(self._title_line)
        self._layout.add_widget(self._sensors_search)
        self._layout.add_widget(self._sensors_list)
