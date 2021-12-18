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


Configuration.sensors = relationship("Sensor", order_by=Sensor.short_name, back_populates="configuration")
