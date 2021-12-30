from PySide6.QtCore import Qt, QMargins
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QLabel, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QVBoxLayout, \
    QMessageBox
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property  # snake_case enabled for Pyside6

from src.widgets.cells.cell_grid_view_widget import CellGridViewWidget


class TabViewWidget(QWidget):
    """ Widget for viewing a certain tab """

    def __init__(self, db_session, tab, configuration_page="view"):
        super().__init__()
        self._db_session = db_session
        self._tab = tab

        self._configuration_page = configuration_page  # from what page this page was open (where to return later)

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """ Initialize UI """
        # create a layout
        self._layout = QVBoxLayout(self)

        self._form_layout = QFormLayout()
        self._form_layout.horizontal_spacing = 20
        self._form_layout.contents_margins = QMargins(10, 0, 10, 0)

        # create a title
        self._title = QLabel()
        self._title.text = "View Tab"
        self._title.font = QFont("Lato", 18)
        self._title.alignment = Qt.AlignCenter
        self._title.set_contents_margins(10, 10, 10, 20)

        # create name field display
        self._name_line = QLineEdit()
        self._name_line.text = self._tab.name
        self._name_line.read_only = True

        # create grid width field display
        self._grid_width_line = QLineEdit()
        self._grid_width_line.text = str(self._tab.grid_width)
        self._grid_width_line.read_only = True

        # create grid height field display
        self._grid_height_line = QLineEdit()
        self._grid_height_line.text = str(self._tab.grid_height)
        self._grid_height_line.read_only = True

        # create grid display
        self._grid = CellGridViewWidget(self._db_session, self._tab)

        # section of buttons
        self._buttons_layout = QHBoxLayout()
        self._buttons_layout.contents_margins = QMargins(10, 0, 10, 0)

        self._edit_button = QPushButton("Edit")
        self._edit_button.clicked.connect(self._edit_tab)

        self._delete_button = QPushButton("Delete")
        self._delete_button.clicked.connect(self._delete)

        self._back_button = QPushButton("Back To Configuration")
        self._back_button.clicked.connect(self._return_to_configuration)

        self._buttons_layout.add_widget(self._edit_button)
        self._buttons_layout.add_widget(self._delete_button)
        self._buttons_layout.add_stretch(1)  # move back button to the right
        self._buttons_layout.add_widget(self._back_button)

        # add widgets to layout
        self._form_layout.add_row(self._title)
        self._form_layout.add_row("Name:", self._name_line)
        self._form_layout.add_row("Column count:", self._grid_width_line)
        self._form_layout.add_row("Row count:", self._grid_height_line)
        self._layout.add_layout(self._form_layout)
        self._layout.add_widget(self._grid)

        # add buttons
        self._layout.add_layout(self._buttons_layout)

    def _delete(self):
        """ Removes the tab from database """
        # ask for confirmation
        confirmation = QMessageBox.question(self, "Delete",
                                            f'Are you sure you want to delete tab {self._tab.name}?',
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        # if confirmed, remove sensor and redirect to configuration
        if confirmation == QMessageBox.Yes:
            self._db_session.delete(self._tab)

            self._return_to_configuration()

    def _edit_tab(self):
        """ open tab editing page """
        self.parent_widget().edit_tab(self._tab)

    def _return_to_configuration(self):
        """ Open back the configuration creation/editing/view page """
        if self._configuration_page == "edit":
            self.parent_widget().edit_configuration(self._tab.configuration)
        elif self._configuration_page == "create":
            self.parent_widget().create_configuration(self._tab.configuration)
        else:
            self.parent_widget().view_configuration(self._tab.configuration)
