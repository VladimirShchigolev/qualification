from PySide6.QtCore import Qt, QMargins
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QLabel, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, \
    QVBoxLayout, QMessageBox

from src.widgets.cells.cell_grid_view_widget import CellGridViewWidget


class TabViewWidget(QWidget):
    """Widget for viewing a certain tab."""

    def __init__(self, db_session, tab, configuration_page="view"):
        """Create tab viewing widget"""
        super().__init__()
        self._db_session = db_session
        self._tab = tab

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
        self._title.setText("View Tab")
        self._title.setFont(QFont("Lato", 18))
        self._title.setAlignment(Qt.AlignCenter)
        self._title.setContentsMargins(10, 10, 10, 20)

        # create name field display
        self._name_line = QLineEdit()
        self._name_line.setText(self._tab.name)
        self._name_line.setReadOnly(True)

        # create grid width field display
        self._grid_width_line = QLineEdit()
        self._grid_width_line.setText(str(self._tab.grid_width))
        self._grid_width_line.setReadOnly(True)

        # create grid height field display
        self._grid_height_line = QLineEdit()
        self._grid_height_line.setText(str(self._tab.grid_height))
        self._grid_height_line.setReadOnly(True)

        # create grid display
        self._grid = CellGridViewWidget(self._db_session, self._tab)

        # section of buttons
        self._buttons_layout = QHBoxLayout()
        self._buttons_layout.setContentsMargins(10, 0, 10, 0)

        self._edit_button = QPushButton("Edit")
        self._edit_button.clicked.connect(self._edit_tab)

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
        self._form_layout.addRow(self._title)
        self._form_layout.addRow("Name:", self._name_line)
        self._form_layout.addRow("Column count:", self._grid_width_line)
        self._form_layout.addRow("Row count:", self._grid_height_line)
        self._layout.addLayout(self._form_layout)
        self._layout.addWidget(self._grid)

        # add buttons
        self._layout.addLayout(self._buttons_layout)

    def _delete(self):
        """Removes the tab from database."""
        # ask for confirmation
        confirmation = QMessageBox.question(
            self, "Delete",
            f'Are you sure you want to delete tab {self._tab.name}?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        # if confirmed, remove sensor and redirect to configurations
        if confirmation == QMessageBox.Yes:
            self._db_session.delete(self._tab)

            self._return_to_configuration()

    def _edit_tab(self):
        """Open tab editing page."""
        self.parentWidget().edit_tab(self._tab)

    def _return_to_configuration(self):
        """Open back the configurations creation/editing/view page."""
        if self._configuration_page == "edit":
            self.parentWidget().edit_configuration(self._tab.configuration)
        elif self._configuration_page == "create":
            self.parentWidget().create_configuration(self._tab.configuration)
        else:
            self.parentWidget().view_configuration(self._tab.configuration)
