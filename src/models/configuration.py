from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base


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
