# version: 0.1.0 - 2025-06-30  (initial minimal model for analytics_processor)

from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DeviceConfigurationHistory(Base):
    __tablename__ = 'device_configuration_history'
    id = Column(Integer, primary_key=True)
    deveui = Column(String)
    configuration_key = Column(String)
    configuration_value = Column(String)
    timestamp = Column(DateTime)

class HourlyMeasurements(Base):
    __tablename__ = 'hourly_measurements'
    id = Column(Integer, primary_key=True)
    deveui = Column(String)
    measurement_type = Column(String)
    measurement_value = Column(Float)
    timestamp = Column(DateTime)

class LocationHierarchy(Base):
    __tablename__ = 'location_hierarchy'
    id = Column(Integer, primary_key=True)
    site = Column(String)
    floor = Column(String)
    room = Column(String)
    zone = Column(String)
    deveui = Column(String)
