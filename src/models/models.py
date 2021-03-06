import re

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Configuration(Base):
    """Configuration model."""
    __tablename__ = 'configuration'

    # table fields
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    show_unknown_sensors = Column(Boolean, nullable=False, default=False)
    active = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        """Create string representation of a configuration object."""
        return f'Configuration({self.name})'

    def __str__(self):
        """Create a string value of a configuration object."""
        return self.name

    @staticmethod
    def validate(name, check_for_duplicates=True, db_session=None):
        """Check if given fields are valid."""

        if check_for_duplicates:
            # check if configuration with such name exists
            configuration = db_session.query(Configuration).filter(
                Configuration.name == name).one_or_none()
            if configuration:
                raise ValueError("A configuration with such name already exists!")

        # name length
        if not 1 <= len(name) <= 30:
            raise ValueError("Name should be 1 to 30 characters long!")

        return True

    @staticmethod
    def load(db_session, name=None):
        """Load active or selected configuration from DB."""
        if name is None:
            configuration = db_session.query(Configuration) \
                .filter(Configuration.active == True).one_or_none()

            if not configuration:
                configuration = db_session.query(Configuration).filter(Configuration.name == "Default").one_or_none()
                configuration.active = True
                db_session.commit()
        else:
            configuration = db_session.query(Configuration) \
                .filter(Configuration.name == name).one_or_none()
        return configuration

    @staticmethod
    def activate(db_session, name):
        """Set selected configuration as active."""
        current_active = db_session.query(Configuration).filter(Configuration.active == True).one_or_none()
        if current_active:
            current_active.active = False

        new_active = db_session.query(Configuration).filter(Configuration.name == name).one_or_none()
        if new_active:
            new_active.active = True
            db_session.commit()

    @staticmethod
    def find(db_session, name):
        """Finds a configuration with a given name."""
        return db_session.query(Configuration).filter(Configuration.name == name).one_or_none()


class SensorCell(Base):
    """Cell and Sensors NxM relationship model."""
    __tablename__ = 'sensor_cell'

    # table fields
    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer, ForeignKey('sensor.id', ondelete='CASCADE'), nullable=False)
    cell_id = Column(Integer, ForeignKey('cell.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        """Create string representation of a CellSensor object."""
        return f'CellSensor({self.sensor_id}, {self.cell_id})'

    def __str__(self):
        """"Create string value of a CellSensor object."""
        return f'CellSensor({self.sensor_id}, {self.cell_id})'


class Sensor(Base):
    """Sensor model."""
    __tablename__ = 'sensor'

    # table fields
    id = Column(Integer, primary_key=True)
    configuration_id = Column(Integer, ForeignKey('configuration.id', ondelete='CASCADE'),
                              nullable=False)
    short_name = Column(String, nullable=False)
    name = Column(String, nullable=False)
    physical_value = Column(String, nullable=False)
    physical_unit = Column(String, nullable=False)

    configuration = relationship("Configuration", back_populates="sensors")
    cell_sensors = relationship("SensorCell", cascade="all,delete", back_populates="sensor")

    def __repr__(self):
        """Create string representation of a sensor object."""
        return f'Sensor({self.short_name}, {self.name}, {self.physical_unit})'

    def __str__(self):
        """Create a string value of a sensor object."""
        return self.short_name

    @staticmethod
    def validate(configuration, short_name, name, physical_value, physical_unit, check_for_duplicates=True,
                 db_session=None):
        """Check if given fields are valid."""

        # short name length
        if not 1 <= len(short_name) <= 10:
            raise ValueError("Short name should be 1 to 10 characters long!")

        # short name characters
        if not re.match("^[a-zA-Z0-9_]+$", short_name):
            raise ValueError(
                "Short name should consist of upper and lower English letters, digits and "
                "underscores!")

        if check_for_duplicates:
            # check if sensor with such
            # short name exists in this configuration
            sensor = db_session.query(Sensor).filter(Sensor.configuration == configuration) \
                .filter(Sensor.short_name == short_name).one_or_none()
            if sensor:
                raise ValueError(
                    "A sensor with such short name already exists in this configuration!")

        # name length
        if not 1 <= len(name) <= 30:
            raise ValueError("Name should be 1 to 30 characters long!")

        # physical value length
        if not 0 <= len(physical_value) <= 40:
            raise ValueError("Physical value should be 1 to 40 characters long!")

        # physical unit length
        if not 0 <= len(physical_unit) <= 10:
            raise ValueError("Physical unit should be 1 to 10 characters long!")

        if physical_unit and not physical_value:
            raise ValueError("Physical value cannot be empty while physical unit is set!")

        return True


Configuration.sensors = relationship("Sensor", cascade="all,delete", order_by=Sensor.short_name,
                                     back_populates="configuration")


class Tab(Base):
    """Tab model."""
    __tablename__ = 'tab'

    # table fields
    id = Column(Integer, primary_key=True)
    configuration_id = Column(Integer, ForeignKey('configuration.id', ondelete='CASCADE'),
                              nullable=False)
    name = Column(String, nullable=False)
    grid_width = Column(Integer, nullable=False, default=2)
    grid_height = Column(Integer, nullable=False, default=5)

    configuration = relationship("Configuration", back_populates="tabs")

    def __repr__(self):
        """Create string representation of a tab object."""
        return f'Tab({self.name})'

    def __str__(self):
        """Create a string value of a tab object."""
        return self.name

    @staticmethod
    def validate(configuration, name, grid_width, grid_height, check_for_duplicates=True,
                 db_session=None):
        """Check if given fields are valid."""

        # tabs = db_session.query(Tab).filter(Tab.configuration == configuration).all()
        # if len(tabs) == 10:
        #     raise ValueError("Tab limit of 10 tabs is reached for this configuration!")

        if name.lower() == 'unknown':
            raise ValueError('Tab name "Unknown" is reserved!')

        if check_for_duplicates:
            # check if a tab with such name exists in the configuration
            tab = db_session.query(Tab).filter(Tab.configuration == configuration) \
                .filter(Tab.name == name).one_or_none()
            if tab:
                raise ValueError("A tab with such name already exists in this configuration!")

        # name length
        if not 1 <= len(name) <= 30:
            raise ValueError("Name should be 1 to 30 characters long!")

        # grid width value
        if not 1 <= grid_width <= 10:
            raise ValueError("Column count should be an integer between 1 and 10!")

        # grid height value
        if not 1 <= grid_height <= 20:
            raise ValueError("Row count should be an integer between 1 and 10!")

        if int(grid_height) * int(grid_width) > 100:
            raise ValueError("Cell count should be not more than 100!")

        return True


Configuration.tabs = relationship("Tab", cascade="all,delete", order_by=Tab.name,
                                  back_populates="configuration")


class Cell(Base):
    """Cell model."""
    __tablename__ = 'cell'

    # table fields
    id = Column(Integer, primary_key=True)
    tab_id = Column(Integer, ForeignKey('tab.id', ondelete='CASCADE'), nullable=False)
    row = Column(Integer, nullable=False)
    column = Column(Integer, nullable=False)
    rowspan = Column(Integer, nullable=False, default=1)
    colspan = Column(Integer, nullable=False, default=1)
    title = Column(String, nullable=True)

    tab = relationship("Tab", back_populates="cells")
    cell_sensors = relationship("SensorCell", cascade="all,delete", back_populates="cell")

    def __repr__(self):
        """Create string representation of a cell object."""
        return f'Cell({self.row}, {self.column})'

    def __str__(self):
        """Create a string value of a cell object."""
        return f'Cell({self.row}, {self.column})'


Tab.cells = relationship("Cell", cascade="all,delete", order_by=Cell.id, back_populates="tab")

SensorCell.sensor = relationship("Sensor", back_populates="cell_sensors")
SensorCell.cell = relationship("Cell", back_populates="cell_sensors")


class Address(Base):
    """Adress model."""
    __tablename__ = 'address'

    # table fields
    id = Column(Integer, primary_key=True)
    ip_port = Column(String, nullable=False, unique=True)
    use_datetime = Column(DateTime, nullable=False)

    def __repr__(self):
        """Create string representation of an address object."""
        return f'Address({self.ip_port})'

    def __str__(self):
        """Create a string value of an address object."""
        return self.ip_port

    @staticmethod
    def validate(address):
        """Validate ip address and port."""
        if not re.match(r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}:[0-9]{1,5}$", address):
            raise ValueError("IP address is invalid (should be IPv4)!")

        ip, port = address.split(':')
        ip_numbers = [int(x) for x in ip.split('.')]
        for number in ip_numbers:
            if number < 0 or number > 255:
                raise ValueError("IP address is invalid (should be IPv4)!")

        if int(port) < 49152 or int(port) > 65535:
            raise ValueError("Port should be a private port (49152 through 65535)!")

        return True
