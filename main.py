from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property  # snake_case enabled for Pyside6
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.widgets.configuration_settings_window import ConfigurationSettingsWindow


def main():
    """ Starts the main window """
    # connect to the database
    engine = create_engine('sqlite:///configurations.db')
    session_cls = sessionmaker(bind=engine)
    db_session = session_cls()

    app = QApplication([])
    app.set_font(QFont("Lato", 12, QFont.Normal))

    window = ConfigurationSettingsWindow(db_session)
    window.show()

    app.exec()
    db_session.close()


if __name__ == '__main__':
    main()
