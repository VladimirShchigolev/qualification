from PySide6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QScrollArea, QSizePolicy

# enable snake_case for Pyside6
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property

from src.widgets.graphs.graph_widget import GraphWidget


class GraphPageWidget(QWidget):
    """Visual representation of a tab."""

    def __init__(self, tab):
        """Create graph page (tab)."""
        super().__init__()

        self._tab = tab

        self.init_ui()

    def init_ui(self):
        """Initialize UI."""

        self._scroll_area = QScrollArea()
        main_layout = QHBoxLayout(self)
        self.setLayout(main_layout)
        main_layout.addWidget(self._scroll_area)
        self._grid_layout = QGridLayout()
        widget = QWidget()
        widget.setLayout(self._grid_layout)
        self._scroll_area.setWidget(widget)
        self._scroll_area.setWidgetResizable(True)

        self._fill_grid()

    def _fill_grid(self):
        """Fill grid with graph widgets."""
        for cell in self._tab.cells:
            widget = GraphWidget(cell)
            widget.size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            widget.minimum_height = 150
            widget.minimum_width = 300

            self._grid_layout.add_widget(widget, cell.row, cell.column, cell.rowspan, cell.colspan)

        # set minimum height for rows
        for row in range(self._grid_layout.row_count()):
            self._grid_layout.set_row_minimum_height(row, 150)
            self._grid_layout.set_row_stretch(row, 1)

        # set minimum width for columns
        for column in range(self._grid_layout.column_count()):
            self._grid_layout.set_column_minimum_width(column, 300)
            self._grid_layout.set_column_stretch(column, 1)
