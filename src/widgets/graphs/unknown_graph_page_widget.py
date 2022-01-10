from PySide6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QScrollArea, QSizePolicy

from src.widgets.graphs.graph_widget import GraphWidget


class UnknownGraphPageWidget(QWidget):
    """Visual representation of an unkown sensor tab."""

    def __init__(self):
        """Create unknown graph page (tab)."""
        super().__init__()

        self._count = 0

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

    def add_graph(self, unknown_sensor):
        """Add unknown sensor graph widget."""
        if self._count < 100:
            widget = GraphWidget(cell=None, unknown_sensor=unknown_sensor)
            size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            size_policy.setHeightForWidth(True)
            widget.setSizePolicy(size_policy)
            row = self._count // 5
            column = self._count % 5
            self._grid_layout.addWidget(widget, row, column, 1, 1)

            # set minimum height for the row
            self._grid_layout.setRowMinimumHeight(row, 250)
            self._grid_layout.setRowStretch(column, 1)

            # set minimum width for the column
            self._grid_layout.setColumnMinimumWidth(column, 375)
            self._grid_layout.setColumnStretch(column, 1)

            self._count += 1

            return widget
        else:
            return None

    def get_graphs(self):
        return []

    def _clear_grid(self):
        """Delete all elements from grid layout."""
        for i in range(self._grid_layout.count() - 1, -1, -1):
            self._grid_layout.takeAt(i).widget().deleteLater()

    def close(self):
        """Clear grid on closing."""
        self._clear_grid()
