from PySide6.QtCore import QSize
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QMenuBar, QMenu, QStatusBar, QTabWidget

# enable snake_case for Pyside6
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property


class MainWindow(QMainWindow):
    """Main window of the application"""

    def __init__(self, *args, **kwargs):
        """Create main window"""
        super(MainWindow, self).__init__(*args, **kwargs)
        self.window_title = "Sensor Measurement Data Visualization"

        # create menu bar
        self._menu_bar = QMenuBar(self)

        self._menu_file = QMenu(self._menu_bar)
        self._menu_file.title = "File"

        self._menu_settings = QMenu(self._menu_bar)
        self._menu_settings.title = "Settings"

        self.set_menu_bar(self._menu_bar)

        # create status bar
        self._status_bar = QStatusBar(self)
        self.set_status_bar(self._status_bar)

        # create actions
        self._action_new = QAction(self)
        self._action_new.text = "New Session"

        self._action_open = QAction(self)
        self._action_open.text = "Open Recording"

        self._action_record = QAction(self)
        self._action_record.text = "Start Recording"

        self._action_configurations = QAction(self)
        self._action_configurations.text = "Configurations"

        # add actions to the menu
        self._menu_file.add_action(self._action_new)
        self._menu_file.add_action(self._action_open)
        self._menu_file.add_action(self._action_record)
        self._menu_bar.add_action(self._menu_file.menu_action())

        self._menu_settings.add_action(self._action_configurations)
        self._menu_bar.add_action(self._menu_settings.menu_action())

        # self.actionNew.triggered.connect(self.start_new_session)
        # self.actionOpen.triggered.connect(self.open_record)
        # self.actionRecord.triggered.connect(self.record)
        # self.actionSettings.triggered.connect(self.open_settings)

        self._tabs = QTabWidget()

        self.set_central_widget(self._tabs)

        self.init_ui()

        self.minimum_size = QSize(800, 600)
        self.showMaximized()

    def init_ui(self):
        pass

    def closeEvent(self, event):
        event.accept()

