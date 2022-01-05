from PySide6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QScrollArea, QSizePolicy

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
        self._graph_widgets = []
        for cell in self._tab.cells:
            # if cell contains sensors create graph widget
            # otherwise use a placeholder
            if cell.cell_sensors:
                widget = GraphWidget(cell)
                size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                size_policy.setHeightForWidth(True)
                widget.setSizePolicy(size_policy)
                self._graph_widgets.append(widget)
            else:
                widget = QWidget()
                widget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

            self._grid_layout.addWidget(widget, cell.row, cell.column, cell.rowspan, cell.colspan)

        # set minimum height for rows
        for row in range(self._grid_layout.rowCount()):
            self._grid_layout.setRowMinimumHeight(row, 250)
            self._grid_layout.setRowStretch(row, 1)

        # set minimum width for columns
        for column in range(self._grid_layout.columnCount()):
            self._grid_layout.setColumnMinimumWidth(column, 375)
            self._grid_layout.setColumnStretch(column, 1)

    def get_graphs(self):
        """Get list of graph widgets for sensors."""
        graphs = {}
        for graph_widget in self._graph_widgets:
            sensors = graph_widget.get_sensor_list()
            for sensor in sensors:
                if str(sensor) in graphs:
                    graphs[str(sensor)].append(graph_widget)
                else:
                    graphs[str(sensor)] = [graph_widget]
        return graphs

    def _clear_grid(self):
        """Delete all elements from grid layout."""
        for i in range(self._grid_layout.count() - 1, -1, -1):
            self._grid_layout.takeAt(i).widget().deleteLater()

    def close(self):
        """Clear grid on closing."""
        self._clear_grid()
