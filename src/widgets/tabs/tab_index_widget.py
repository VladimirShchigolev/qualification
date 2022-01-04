from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLineEdit, \
    QLabel, QHBoxLayout, QPushButton

from src.models.models import Tab


class TabIndexWidget(QWidget):
    """ Widget for showing tabs of the configurations."""

    def __init__(self, db_session, configuration, configuration_page="view", read_only=False):
        """Create tab index widget."""
        super().__init__()
        self._db_session = db_session
        self._configuration = configuration

        # True if creating new tabs is allowed
        self._read_only = read_only

        # from what page this page was open (where to return later)
        self._configuration_page = configuration_page

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """Initialize UI."""
        # create a layout
        self._layout = QVBoxLayout(self)

        # create a title
        self._title = QLabel()
        self._title.setText("Tabs")
        self._title.setFont(QFont("Lato", 14))
        self._title.setAlignment(Qt.AlignCenter)

        # create a search field
        self._search_line_edit = QLineEdit()
        self._search_line_edit.setPlaceholderText("Search")
        self._search_line_edit.textChanged.connect(self._search)

        # create a list widget for tabs
        self._tabs_list = QListWidget()
        self._tabs_list.setAlternatingRowColors(True)

        # get all configurations tabs from DB
        all_tabs = self._db_session.query(Tab).filter(
            Tab.configuration == self._configuration).order_by(Tab.name).all()

        # add tabs to the list widget
        for tab in all_tabs:
            QListWidgetItem(str(tab), self._tabs_list)

        # show selected tab on double click
        self._tabs_list.itemDoubleClicked.connect(self._show_list_item_tab)

        # section of buttons
        self._buttons_layout = QHBoxLayout()

        if not self._read_only:
            self._new_button = QPushButton("New")
            self._new_button.clicked.connect(self._create_tab)

            self._buttons_layout.addWidget(self._new_button)

        self._view_button = QPushButton("View")
        self._view_button.clicked.connect(self._show_selected_tab)

        # move view button to the right
        self._buttons_layout.addStretch(1)

        self._buttons_layout.addWidget(self._view_button)

        # add widgets to layout
        self._layout.addWidget(self._title)
        self._layout.addWidget(self._search_line_edit)
        self._layout.addWidget(self._tabs_list)
        self._layout.addLayout(self._buttons_layout)

    def _search(self, search_string):
        """Filter tab by the search string."""
        # get tabs which name starts with the
        # search_string from current configurations
        search_string = "{}%".format(search_string)
        filtered_tabs = self._db_session.query(Tab) \
            .filter(Tab.configuration == self._configuration) \
            .filter(Tab.name.like(search_string)) \
            .order_by(Tab.name) \
            .all()

        # clear current list and fill it with filtered tabs
        self._tabs_list.clear()
        for tab in filtered_tabs:
            QListWidgetItem(str(tab), self._tabs_list)

    def _show_selected_tab(self):
        """Open view page for the selected tab."""
        # get selected items
        selected_items = self._tabs_list.selectedItems()
        if selected_items:
            # show the first and only item
            self._show_list_item_tab(selected_items[0])

    def _show_list_item_tab(self, list_item):
        """Open view page for the selected/clicked tab."""
        tab_name = list_item.data(0)  # get selected tab short name

        # find tab in DB
        tab = self._db_session.query(Tab) \
            .where(Tab.configuration == self._configuration) \
            .where(Tab.name == tab_name) \
            .one_or_none()

        if tab is not None:  # if tab found
            self.parentWidget().parentWidget().view_tab(tab, self._configuration_page)

    def _create_tab(self):
        """Open a tab creating page."""
        self.parentWidget().parentWidget().create_tab(self._configuration,
                                                      self._configuration_page)
