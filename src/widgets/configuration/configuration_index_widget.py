from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLineEdit
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property
from src.models.configuration import Configuration


class ConfigurationIndexWidget(QWidget):
    """ Widget responsible to show all configurations.
    Allows searching, showing selected configuration and creating new configuration
    """

    def __init__(self, db_session):
        super().__init__()
        self._db_session = db_session

        self.window_title = "Configurations"
        self.resize(600, 400)
        self._init_ui()  # initialize UI

    def _init_ui(self):
        """ Initialize UI """
        # create a layout
        self.layout = QVBoxLayout(self)

        # create a search field
        self.search_line_edit = QLineEdit()
        self.search_line_edit.placeholder_text = "Search"
        self.search_line_edit.textChanged.connect(self._search)

        # create a list widget for configurations
        self.configurations_list = QListWidget()
        self.configurations_list.alternating_row_colors = True

        # get all configurations from DB
        all_configurations = self._db_session.query(Configuration)\
            .order_by(Configuration.name).all()

        # add configurations to the list widget
        for configuration in all_configurations:
            item = QListWidgetItem(str(configuration), self.configurations_list)

        # add widgets to layout
        self.layout.add_widget(self.search_line_edit)
        self.layout.add_widget(self.configurations_list)

    def _search(self, search_string):
        """ Filter configuration by the search string """

        # get configurations which name starts with the search_string
        search_string = "{}%".format(search_string)
        filtered_configurations = self._db_session.query(Configuration).filter(
            Configuration.name.like(search_string)).order_by(Configuration.name).all()

        # clear current list and fill it with filtered configurations
        self.configurations_list.clear()
        for configuration in filtered_configurations:
            item = QListWidgetItem(str(configuration), self.configurations_list)



