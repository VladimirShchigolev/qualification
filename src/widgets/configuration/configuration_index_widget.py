from PySide6.QtCore import Qt, QMargins
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLineEdit, QLabel
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property  # snake_case enabled for Pyside6
from src.models.models import Configuration


class ConfigurationIndexWidget(QWidget):
    """ Widget responsible for showing all configurations.
    Allows searching, showing selected configuration and creating new configurations
    """

    def __init__(self, db_session):
        super().__init__()
        self._db_session = db_session

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """ Initialize UI """
        # create a layout
        self._layout = QVBoxLayout(self)

        # create a title
        self._title = QLabel()
        self._title.text = "Configurations"
        self._title.font = QFont("Lato", 18)
        self._title.alignment = Qt.AlignCenter
        self._title.contents_margins = QMargins(10, 10, 10, 20)

        # create a search field
        self._search_line_edit = QLineEdit()
        self._search_line_edit.placeholder_text = "Search"
        self._search_line_edit.textChanged.connect(self._search)

        # create a list widget for configurations
        self._configurations_list = QListWidget()
        self._configurations_list.alternating_row_colors = True

        # get all configurations from DB
        all_configurations = self._db_session.query(Configuration)\
            .order_by(Configuration.name).all()

        # add configurations to the list widget
        for configuration in all_configurations:
            QListWidgetItem(str(configuration), self._configurations_list)

        # show selected configuration on double click
        self._configurations_list.itemDoubleClicked.connect(self._show_selected_configuration)

        # add widgets to layout
        self._layout.add_widget(self._title)
        self._layout.add_widget(self._search_line_edit)
        self._layout.add_widget(self._configurations_list)

    def _search(self, search_string):
        """ Filter configuration by the search string """

        # get configurations which name starts with the search_string
        search_string = "{}%".format(search_string)
        filtered_configurations = self._db_session.query(Configuration).filter(
            Configuration.name.like(search_string)).order_by(Configuration.name).all()

        # clear current list and fill it with filtered configurations
        self._configurations_list.clear()
        for configuration in filtered_configurations:
            QListWidgetItem(str(configuration), self._configurations_list)

    def _show_selected_configuration(self, list_item):
        configuration_name = list_item.data(0)  # get selected configuration name

        # find configuration in DB
        configuration = self._db_session.query(Configuration)\
            .where(Configuration.name == configuration_name).one_or_none()

        if configuration is not None:  # if configuration found
            self.parent_widget().view_configuration(configuration)

