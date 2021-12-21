from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLineEdit, QLabel, QHBoxLayout, \
    QPushButton
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property  # snake_case enabled for Pyside6

from src.models.models import Tab


class TabIndexWidget(QWidget):
    """ Widget responsible for showing all tabs belonging to given configuration.
    Allows searching, showing selected tabs and creating new tabs
    """

    def __init__(self, db_session, configuration):
        super().__init__()
        self._db_session = db_session
        self._configuration = configuration

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """ Initialize UI """
        # create a layout
        self._layout = QVBoxLayout(self)

        # create a title
        self._title = QLabel()
        self._title.text = "Tabs"
        self._title.font = QFont("Lato", 14)
        self._title.alignment = Qt.AlignCenter

        # create a search field
        self._search_line_edit = QLineEdit()
        self._search_line_edit.placeholder_text = "Search"
        self._search_line_edit.textChanged.connect(self._search)

        # create a list widget for tabs
        self._tabs_list = QListWidget()
        self._tabs_list.alternating_row_colors = True

        # get all configuration tabs from DB
        all_tabs = self._configuration.tabs

        # add tabs to the list widget
        for tab in all_tabs:
            QListWidgetItem(str(tab), self._tabs_list)

        # show selected tab on double click
        self._tabs_list.itemDoubleClicked.connect(self._show_list_item_tab)

        # section of buttons
        self._buttons_layout = QHBoxLayout()

        self._new_button = QPushButton("New")
        self._new_button.clicked.connect(self._create_tab)
        self._view_button = QPushButton("View")
        self._view_button.clicked.connect(self._show_selected_tab)

        self._buttons_layout.add_widget(self._new_button)
        self._buttons_layout.add_stretch(1)  # move view button to the right
        self._buttons_layout.add_widget(self._view_button)

        # add widgets to layout
        self._layout.add_widget(self._title)
        self._layout.add_widget(self._search_line_edit)
        self._layout.add_widget(self._tabs_list)
        self._layout.add_layout(self._buttons_layout)

    def _search(self, search_string):
        """ Filter configuration by the search string """

        # get tabs which name starts with the search_string from current configuration
        search_string = "{}%".format(search_string)
        filtered_tabs = self._db_session.query(Tab).filter(Tab.configuration == self._configuration).filter(
            Tab.name.like(search_string)).order_by(Tab.name).all()

        # clear current list and fill it with filtered tabs
        self._tabs_list.clear()
        for tab in filtered_tabs:
            QListWidgetItem(str(tab), self._tabs_list)

    def _show_selected_tab(self):
        """ open view page for the selected tab """
        # get selected items
        selected_items = self._tabs_list.selected_items()
        if len(selected_items):
            self._show_list_item_tab(selected_items[0])  # show the first and only item

    def _show_list_item_tab(self, list_item):
        """ open view page for the selected/clicked tab """
        tab_name = list_item.data(0)  # get selected tab short name

        # find tab in DB
        tab = self._db_session.query(Tab).where(Tab.configuration == self._configuration)\
            .where(Tab.name == tab_name).one_or_none()

        if tab is not None:  # if tab found
            self.parent_widget().parent_widget().view_tab(tab)

    def _create_tab(self):
        """ open a tab creating page """
        self.parent_widget().parent_widget().create_tab(self._configuration)
