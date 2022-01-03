from PySide6.QtWidgets import QTabWidget, QWidget

# enable snake_case for Pyside6
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property


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
            new_tab = QWidget()

            self._tabs.append(new_tab)
            self.add_tab(new_tab, tab.name)

