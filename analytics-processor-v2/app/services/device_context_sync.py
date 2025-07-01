import os
import sys
import logging
from datetime import datetime, timedelta

import psycopg2
from sqlalchemy import create_engine

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.connections import get_device_manager_connection_string, get_analytics_connection_string

class DeviceContextSynchronizer:
    def __init__(self, device_manager_dsn, analytics_dsn):
        """
        Initialize database connections using SQLAlchemy engines
        """
        self.device_manager_engine = create_engine(device_manager_dsn)
        self.analytics_engine = create_engine(analytics_dsn)
        self.logger = logging.getLogger(__name__)
    
    def get_modified_devices(self, last_sync_timestamp=None):
        """
        Fetch devices modified since last sync
        """
        with self.device_manager_engine.connect() as connection:
            # If no last sync timestamp, fetch devices from last 30 days
            if not last_sync_timestamp:
                last_sync_timestamp = datetime.now() - timedelta(days=30)
            
            query = """
            SELECT 
                deveui, 
                device_type_id, 
                zone_id, 
                first_seen, 
                last_seen, 
                status
            FROM 
                device_registry
            WHERE 
                updated_at > :last_sync
            """
            
            result = connection.execute(
                query, 
                {'last_sync': last_sync_timestamp}
            )
            
            return [dict(row) for row in result]
    
    def upsert_device_context(self, devices):
        """
        Upsert device contexts into analytics database
        """
        with self.analytics_engine.connect() as connection:
            for device in devices:
                upsert_query = """
                INSERT INTO device_context 
                (deveui, device_type_id, zone_id, first_seen, last_seen, status, updated_at)
                VALUES (:deveui, :device_type_id, :zone_id, :first_seen, :last_seen, :status, NOW())
                ON CONFLICT (deveui) DO UPDATE SET
                    device_type_id = EXCLUDED.device_type_id,
                    zone_id = EXCLUDED.zone_id,
                    first_seen = LEAST(device_context.first_seen, EXCLUDED.first_seen),
                    last_seen = GREATEST(device_context.last_seen, EXCLUDED.last_seen),
                    status = EXCLUDED.status,
                    updated_at = NOW()
                """
                
                connection.execute(upsert_query, device)
            
            connection.commit()
    
    def sync(self, last_sync_timestamp=None):
        """
        Synchronize device contexts
        """
        try:
            # Fetch modified devices
            devices = self.get_modified_devices(last_sync_timestamp)
            
            # Upsert devices
            self.upsert_device_context(devices)
            
            self.logger.info(f"Synchronized {len(devices)} devices")
            return len(devices)
        
        except Exception as e:
            self.logger.error(f"Synchronization failed: {e}")
            raise

def run_device_context_sync():
    """
    Main function to run device context synchronization
    """
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    device_manager_dsn = get_device_manager_connection_string()
    analytics_dsn = get_analytics_connection_string()
    
    synchronizer = DeviceContextSynchronizer(
        device_manager_dsn, 
        analytics_dsn
    )
    
    synchronizer.sync()

if __name__ == '__main__':
    run_device_context_sync()
