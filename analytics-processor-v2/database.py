""
SenseMy IoT Platform: Analytics Layer Database Models
Version: 20250629
Last Updated: 2025-06-29 14:30:00 UTC
Authors: SenseMy IoT Team

Changelog:
- Initial implementation of SQLAlchemy database models
- Added comprehensive table definitions for analytics layer
- Implemented relationships and constraints
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Numeric, JSON, ForeignKey, Text, UniqueConstraint, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# Rest of the existing database model code remains the same

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Numeric, JSON, ForeignKey, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class LocationHierarchy(Base):
    __tablename__ = 'location_hierarchy'
    
    id = Column(Integer, primary_key=True)
    deveui = Column(String(16), nullable=False)
    site_id = Column(Integer)
    floor_id = Column(Integer)
    room_id = Column(Integer)
    zone_id = Column(Integer)
    
    valid_from = Column(DateTime(timezone=True), default=datetime.utcnow)
    valid_to = Column(DateTime(timezone=True))
    is_current = Column(Boolean, default=True)
    
    change_reason = Column(Text)
    changed_by = Column(String(255))
    
    __table_args__ = (
        UniqueConstraint('deveui', 'valid_from'),
    )

class DeviceConfigurationHistory(Base):
    __tablename__ = 'device_configuration_history'
    
    id = Column(Integer, primary_key=True)
    deveui = Column(String(16), nullable=False)
    
    device_type_id = Column(Integer)
    unpacker_module_name = Column(String(255))
    unpacker_function_name = Column(String(255))
    unpacker_version = Column(String(50))
    
    status = Column(String(50))
    
    configured_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    decommissioned_at = Column(DateTime(timezone=True))
    recommissioned_at = Column(DateTime(timezone=True))
    
    change_reason = Column(Text)
    changed_by = Column(String(255))
    
    is_current = Column(Boolean, default=True)
    
    __table_args__ = (
        UniqueConstraint('deveui', 'configured_at'),
    )

class HourlyMeasurements(Base):
    __tablename__ = 'hourly_measurements'
    
    id = Column(Integer, primary_key=True)
    deveui = Column(String(16), nullable=False)
    device_type_id = Column(Integer, nullable=False)
    measurement_type = Column(String(50), nullable=False)
    
    measurement_hour = Column(DateTime(timezone=True), nullable=False)
    
    mean_value = Column(Numeric(10, 2))
    median_value = Column(Numeric(10, 2))
    min_value = Column(Numeric(10, 2))
    max_value = Column(Numeric(10, 2))
    
    sample_count = Column(Integer)
    unique_uplinks = Column(Integer)
    
    interpolation_method = Column(String(50))
    interpolation_confidence = Column(Numeric(5, 2))
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('deveui', 'device_type_id', 'measurement_type', 'measurement_hour'),
    )

class BatteryHealthHistory(Base):
    __tablename__ = 'battery_health_history'
    
    id = Column(Integer, primary_key=True)
    deveui = Column(String(16), nullable=False)
    
    hourly_mean_voltage = Column(Numeric(5, 2))
    hourly_min_voltage = Column(Numeric(5, 2))
    hourly_max_voltage = Column(Numeric(5, 2))
    
    hourly_mean_percentage = Column(Numeric(5, 2))
    hourly_min_percentage = Column(Numeric(5, 2))
    hourly_max_percentage = Column(Numeric(5, 2))
    
    measurement_hour = Column(DateTime(timezone=True), nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('deveui', 'measurement_hour'),
    )

class NetworkPerformanceHistory(Base):
    __tablename__ = 'network_performance_history'
    
    id = Column(Integer, primary_key=True)
    deveui = Column(String(16), nullable=False)
    
    hourly_mean_rssi = Column(Numeric(6, 2))
    hourly_min_rssi = Column(Numeric(6, 2))
    hourly_max_rssi = Column(Numeric(6, 2))
    
    hourly_mean_snr = Column(Numeric(6, 2))
    hourly_min_snr = Column(Numeric(6, 2))
    hourly_max_snr = Column(Numeric(6, 2))
    
    packets_sent = Column(Integer)
    packets_received = Column(Integer)
    packet_loss_rate = Column(Numeric(5, 2))
    
    measurement_hour = Column(DateTime(timezone=True), nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('deveui', 'measurement_hour'),
    )

class DeviceHealthAlerts(Base):
    __tablename__ = 'device_health_alerts'
    
    id = Column(Integer, primary_key=True)
    deveui = Column(String(16), nullable=False)
    
    alert_type = Column(String(50), 
        CheckConstraint("alert_type IN ('LOW_BATTERY', 'CRITICAL_BATTERY', 'NETWORK_DEGRADATION', 'NO_COMMUNICATION', 'FIRMWARE_ISSUE')")
    )
    
    severity = Column(String(20), 
        CheckConstraint("severity IN ('INFO', 'WARNING', 'CRITICAL')")
    )
    
    alert_description = Column(Text)
    current_value = Column(Numeric(10, 2))
    threshold_value = Column(Numeric(10, 2))
    
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True))
    resolution_notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
