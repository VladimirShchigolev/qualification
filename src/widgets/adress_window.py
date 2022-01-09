import datetime

from PySide6.QtCore import Qt, QMargins, QRegularExpression
from PySide6.QtGui import QFont, QRegularExpressionValidator
from PySide6.QtWidgets import QWidget, QLabel, QFormLayout, QHBoxLayout, QPushButton, \
    QVBoxLayout, QComboBox, QMessageBox

from src.models.models import Address


class AddressWindow(QWidget):
    """Widget for setting data source IP address."""

    def __init__(self, db_session):
        """Create data source IP address setting widget"""
        super().__init__()
        self._db_session = db_session

        # set window title and size
        self.setWindowTitle("Data Source")
        self.resize(800, 600)

        # block access to other windows of application
        self.setWindowModality(Qt.ApplicationModal)

        self._init_ui()  # initialize UI

    def _init_ui(self):
        """Initialize UI."""
        # create a layout
        self._layout = QVBoxLayout(self)

        self._form_layout = QFormLayout()
        self._form_layout.setHorizontalSpacing(20)
        self._form_layout.setContentsMargins(QMargins(10, 0, 10, 0))

        # create a title
        self._title = QLabel()
        self._title.setText("Select Data Source IP Address")
        self._title.setFont(QFont("Lato", 18))
        self._title.setAlignment(Qt.AlignCenter)
        self._title.setContentsMargins(10, 10, 10, 20)

        # create address field display
        self._address_line = QComboBox()

        # fill provided values with widely last 10 used options
        addresses = self._db_session.query(Address).order_by().all()
        # add last 10 used addresses
        if len(addresses) > 10:
            addresses = addresses[-10:]
        for address in addresses[::-1]:
            self._address_line.addItem(str(address))

        self._address_line.setEditable(True)
        self._address_line.setCurrentText(str(addresses[-1]))

        # set validation rules for IP address and port
        self._address_line.setValidator(
            QRegularExpressionValidator(
                QRegularExpression(r'[0-9]{0,3}\.[0-9]{0,3}\.[0-9]{0,3}\.[0-9]{0,3}:[0-9]{5}')
            )
        )

        # section of buttons
        self._buttons_layout = QHBoxLayout()
        self._buttons_layout.setContentsMargins(QMargins(10, 0, 10, 0))

        self._save_button = QPushButton("Save")
        self._save_button.clicked.connect(self._save)
        self._cancel_button = QPushButton("Cancel")
        self._cancel_button.clicked.connect(self.close)

        self._buttons_layout.addWidget(self._save_button)

        # move cancel button to the right
        self._buttons_layout.addStretch(1)

        self._buttons_layout.addWidget(self._cancel_button)

        # add widgets to layout

        # add configuration data
        self._form_layout.addRow(self._title)
        self._form_layout.addRow("IP address:port", self._address_line)
        self._layout.addLayout(self._form_layout)

        self._layout.addStretch(1)  # move buttons to the bottom

        # add buttons
        self._layout.addLayout(self._buttons_layout)

    def _save(self):
        """Create a sensor from data in the form."""
        # get data from the form
        new_address = self._address_line.currentText()

        # check if data is valid
        validation_passed = False
        try:
            validation_passed = Address.validate(new_address)
        except ValueError as error:
            # show error message
            QMessageBox.critical(self, "Error!", str(error), QMessageBox.Ok,
                                 QMessageBox.Ok)

        if validation_passed:  # if data is valid
            # if exists, update it's use time. Otherwise create new
            address = self._db_session.query(Address).filter(Address.ip_port == new_address).one_or_none()
            if address:
                address.use_datetime = datetime.datetime.now()
            else:
                self._db_session.add(Address(ip_port=new_address, use_datetime=datetime.datetime.now()))

            self._db_session.commit()  # save changes

            QMessageBox.information(self, "Success!", "IP address is set!", QMessageBox.Ok, QMessageBox.Ok)

            # close the window
            self.close()
