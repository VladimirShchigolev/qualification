from PySide6.QtWidgets import QTabWidget, QWidget

from src.widgets.graphs.graph_page_widget import GraphPageWidget


class GraphTabWidget(QTabWidget):
    """Widget for tabs of graphs."""

    def __init__(self, configuration, *args, **kwargs):
        """Create tabs for graphs."""
        super().__init__(*args, **kwargs)

        self._configuration = configuration
        self._tabs = []

        self._init_ui()

    def _init_ui(self):
        """Initialize UI."""
        for tab in self._configuration.tabs:
            new_tab = GraphPageWidget(tab)

            self._tabs.append(new_tab)
            self.addTab(new_tab, tab.name)

    def get_graphs(self):
        """Get list of graph widgets for sensors."""
        graphs = {}
        for tab in self._tabs:
            tab_graphs = tab.get_graphs()
            for sensor in tab_graphs:
                if sensor in graphs:
                    graphs[sensor] += tab_graphs[sensor]
                else:
                    graphs[sensor] = tab_graphs[sensor]

        return graphs

    def close(self):
        """Closes all tabs."""
        for tab in self._tabs:
            tab.close()
        self._tabs = []
