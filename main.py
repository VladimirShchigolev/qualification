import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.widgets.main_window import MainWindow


def main():
    """Starts the main window."""
    # connect to the database
    engine = create_engine('sqlite:///configurations.db')
    session_cls = sessionmaker(bind=engine)

    app = QApplication([])
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
