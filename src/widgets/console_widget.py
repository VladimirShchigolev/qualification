from PySide6.QtWidgets import QWidget, QGridLayout, QTextEdit


class ConsoleWidget(QWidget):
    """Console window."""

    def __init__(self):
        """Create console window."""
        super().__init__()

        # set window title and size
        self.setWindowTitle("Console")
        self.resize(800, 600)

        self._init_ui()

    def _init_ui(self):
        """Initialize UI."""
        self.grid_layout = QGridLayout(self)

        self.serialTextEdit = QTextEdit()
        self.serialTextEdit.setReadOnly(True)
        self.serialTextEdit.setFontPointSize(12)

        self.grid_layout.addWidget(self.serialTextEdit, 0, 0, 1, 1)

    def clear(self):
        """Clear console."""
        self.serialTextEdit.clear()

    def print(self, data_string, warning=False):
        """Print new data (or warning) to the console."""
        if warning:
            self.serialTextEdit.append('<p style="color:red"><b>' + data_string + '</b></p>')
        else:
            self.serialTextEdit.append('<p style="color:blue">' + data_string + '</p>')

