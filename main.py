from PySide6.QtWidgets import QApplication
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.widgets.configuration.configuration_index_widget import ConfigurationIndexWidget


def main():
    """ Starts the main window """
    # connect to the database
    engine = create_engine('sqlite:///configurations.db')
    session_cls = sessionmaker(bind=engine)
    db_session = session_cls()

    app = QApplication([])

    window = ConfigurationIndexWidget(db_session)
    window.show()

    app.exec()
    db_session.close()


if __name__ == '__main__':
    main()
