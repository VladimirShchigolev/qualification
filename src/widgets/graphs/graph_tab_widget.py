from PySide6.QtWidgets import QTabWidget

from src.widgets.graphs.graph_page_widget import GraphPageWidget
from src.widgets.graphs.unknown_graph_page_widget import UnknownGraphPageWidget


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

        if self._configuration.show_unknown_sensors:
            self._unknown_tab = UnknownGraphPageWidget()

            self._tabs.append(self._unknown_tab)
            self.addTab(self._unknown_tab, "Unknown")

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

    def add_unknown_sensor(self, sensor):
        """Add a sensor graph to unknown sensor page."""
        if self._configuration.show_unknown_sensors:
            return self._unknown_tab.add_graph(sensor)
        else:
            return None

    def close(self):
        """Closes all tabs."""
        for tab in self._tabs:
            tab.close()
        self._tabs = []
