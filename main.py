from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

# snake_case enabled for Pyside6
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.widgets.main_window import MainWindow


def main():
    """Starts the main window."""
    # connect to the database
    engine = create_engine('sqlite:///configurations.db')
    session_cls = sessionmaker(bind=engine)

    app = QApplication([])
    app.set_font(QFont("Lato", 12, QFont.Normal))

    window = MainWindow(session_cls)
    window.show()

    app.exec()


if __name__ == '__main__':
    main()
