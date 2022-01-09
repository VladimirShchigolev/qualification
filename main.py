import os
import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QMessageBox, QMainWindow
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.widgets.main_window import MainWindow


def main():
    """Starts the main window."""
    app = QApplication([])

    # check if database exists
    if not os.path.isfile('configurations.db'):
        window = QMainWindow()  # window needed for a message box
        window.resize(1, 1)
        window.show()
        QMessageBox.critical(window,
                             "Error", "Critical Error!\nFailed to open configurations database!",
                             QMessageBox.Ok, QMessageBox.Ok)
        window.close()
        return

    # connect to the database
    engine = create_engine('sqlite:///configurations.db')
    session_cls = sessionmaker(bind=engine)

    app.setFont(QFont("Lato", 12, QFont.Normal))

    window = MainWindow(session_cls)
    window.show()

    app.exec()


def excepthook(cls, exception, traceback):
    """Ignores TypeError thrown by pyqtgraph bug"""
    if not (cls is TypeError
            and str(exception).strip().endswith("native Qt signal is not callable")):
        raise exception


sys.excepthook = excepthook

if __name__ == '__main__':
    main()
