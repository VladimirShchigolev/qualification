import re

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Configuration(Base):
    """ Configuration model """
    __tablename__ = 'configuration'

    # table fields
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    show_unknown_sensors = Column(Boolean, nullable=False)
    show_model = Column(Boolean, nullable=False)
    model_chamber_text = Column(String)
    model_control_text = Column(String)

    def __repr__(self):
        """ Create string representation of a configuration object """
        return f'Configuration({self.name})'

    def __str__(self):
        """ Create a string value of a configuration object"""
        return self.name


class Sensor(Base):
    """ Sensor model """
    __tablename__ = 'sensor'

    # table fields
    id = Column(Integer, primary_key=True)
    configuration_id = Column(Integer, ForeignKey('configuration.id'),nullable=False)
    short_name = Column(String, nullable=False)
    name = Column(String, nullable=False)
    physical_value = Column(String, nullable=False)
    physical_unit = Column(String, nullable=False)

    configuration = relationship("Configuration", back_populates="sensors")

    def __repr__(self):
        """ Create string representation of a sensor object """
        return f'Sensor({self.short_name}, {self.name}, {self.physical_unit})'

    def __str__(self):
        """ Create a string value of a sensor object"""
        return self.short_name

    @staticmethod
    def validate(configuration, short_name, name, physical_value, physical_unit):
        """ Check if given fields are valid """

        # short name length
        if not 0 < len(short_name) < 10:
            raise ValueError("Short name should be 1 to 10 characters long!")

        # short name characters
        if not re.match("^[a-zA-Z0-9_]+$", short_name):
            raise ValueError("Short name should consist of upper and lower English letters, digits and underscores!")

        # check if sensor with such short name exists in this configuration
        exists = False
        for sensor in configuration.sensors:
            if sensor.short_name == short_name:
                exists = True
                break
        if exists:
            raise ValueError("A sensor with such short name already exists in this configuration")

        # name length
        if not 0 < len(name) < 30:
            raise ValueError("Name should be 1 to 30 characters long!")

        # physical value length
        if not 0 < len(physical_value) < 40:
            raise ValueError("Physical value should be 1 to 40 characters long!")

        # physical unit length
        if not 0 < len(physical_unit) < 10:
            raise ValueError("Physical unit should be 1 to 10 characters long!")

        return True


Configuration.sensors = relationship("Sensor", order_by=Sensor.short_name, back_populates="configuration")
