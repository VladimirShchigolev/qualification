from PySide6.QtCore import Qt, QMargins
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLineEdit, \
    QLabel, QHBoxLayout, QPushButton

# enable snake_case for Pyside6
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property

from src.models.models import Configuration


class ConfigurationIndexWidget(QWidget):
    """Widget responsible for showing all configurations."""

    def __init__(self, db_session):
        """Create configuration index page"""
        super().__init__()
        self._db_session = db_session

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """Initialize UI."""
        # create a layout
        self._layout = QVBoxLayout(self)
        self._layout.contents_margins = QMargins(15, 10, 15, 10)

        # create a title
        self._title = QLabel()
        self._title.text = "Configurations"
        self._title.font = QFont("Lato", 18)
        self._title.alignment = Qt.AlignCenter
        self._title.set_contents_margins(10, 10, 10, 20)

        # create a search field
        self._search_line_edit = QLineEdit()
        self._search_line_edit.placeholder_text = "Search"
        self._search_line_edit.textChanged.connect(self._search)

        # create a list widget for configurations
        self._configurations_list = QListWidget()
        self._configurations_list.alternating_row_colors = True

        # get all configurations from DB
        all_configurations = self._db_session.query(Configuration) \
            .order_by(Configuration.name).all()

        # add configurations to the list widget
        for configuration in all_configurations:
            QListWidgetItem(str(configuration), self._configurations_list)

        # show selected configuration on double click
        self._configurations_list.itemDoubleClicked.connect(self._show_list_item_configuration)

        # section of buttons
        self._buttons_layout = QHBoxLayout()

        self._new_button = QPushButton("New")
        self._new_button.clicked.connect(self._create_configuration)
        self._load_button = QPushButton("Load")
        self._view_button = QPushButton("View")
        self._view_button.clicked.connect(self._show_selected_configuration)
        self._close_button = QPushButton("Close")
        self._close_button.clicked.connect(self._close)

        self._buttons_layout.add_widget(self._new_button)
        self._buttons_layout.add_widget(self._load_button)
        self._buttons_layout.add_widget(self._view_button)

        # move close button to the right
        self._buttons_layout.add_stretch(1)

        self._buttons_layout.add_widget(self._close_button)

        # add widgets to layout
        self._layout.add_widget(self._title)
        self._layout.add_widget(self._search_line_edit)
        self._layout.add_widget(self._configurations_list)
        self._layout.add_layout(self._buttons_layout)

    def _search(self, search_string):
        """Filter configurations by the search string."""

        # get configurations which name starts with the search_string
        search_string = "{}%".format(search_string)
        filtered_configurations = self._db_session.query(Configuration).filter(
            Configuration.name.like(search_string)).order_by(Configuration.name).all()

        # clear current list and fill it with filtered configurations
        self._configurations_list.clear()
        for configuration in filtered_configurations:
            QListWidgetItem(str(configuration), self._configurations_list)

    def _create_configuration(self):
        """Open configuration creation page."""
        self.parent_widget().create_configuration()

    def _show_selected_configuration(self):
        """Open view page for the selected configuration."""
        # get selected items
        selected_items = self._configurations_list.selected_items()
        if selected_items:
            # show the first and only item
            self._show_list_item_configuration(selected_items[0])

    def _show_list_item_configuration(self, list_item):
        """Open view page for the selected/clicked configuration."""
        # get selected configuration name
        configuration_name = list_item.data(0)

        # find configuration in DB
        configuration = self._db_session.query(Configuration) \
            .where(Configuration.name == configuration_name).one_or_none()

        if configuration is not None:  # if configuration found
            self.parent_widget().view_configuration(configuration)

    def _close(self):
        """Close window."""
        self.parent_widget().close()
