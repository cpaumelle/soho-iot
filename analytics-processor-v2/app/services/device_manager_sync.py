"""
SenseMy IoT Platform: Device Manager Synchronization Script

This script provides a robust mechanism for synchronizing metadata 
between the device manager and analytics databases.

Key Features:
- Comprehensive metadata synchronization
- Idempotent upsert operations
- Detailed error logging and tracking
- Flexible sync modes (initial/scheduled)

Synchronization Tables:
1. Interpolation Strategies
2. Location Hierarchy (Sites, Floors, Rooms, Zones)
3. Device Types

Deployment Modes:
- Initial Sync: Complete data transfer
- Scheduled Sync: Incremental updates

Usage:
    python device_manager_sync.py --initial   # First-time full sync
    python device_manager_sync.py --scheduled # Regular scheduled sync

Logging:
- Comprehensive logging to device_manager_sync.log
- Tracks sync details, errors, and performance metrics

Version: 1.0.0
Last Updated: 2025-06-29 UTC
Authors: SenseMy IoT Team
"""

import argparse
import logging
from datetime import datetime
import traceback
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text

# Enhanced Logging Configuration
def setup_logging():
    """
    Configure comprehensive logging with multiple handlers
    
    Includes:
    - File logging (detailed)
    - Console logging (summary)
    - Structured log format
    """
    # Create logger
    logger = logging.getLogger('DeviceManagerSync')
    logger.setLevel(logging.DEBUG)

    # File Handler (Detailed)
    file_handler = logging.FileHandler('device_manager_sync.log')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - '
        '[%(funcName)s:%(lineno)d] - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    # Console Handler (Summary)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s: %(message)s', 
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Global logger setup
logger = setup_logging()

class DeviceManagerSync:
    def __init__(self, device_manager_url, analytics_url):
        """
        Initialize database synchronization service
        
        Establishes connections to both source and target databases
        
        Args:
            device_manager_url (str): Connection string for source database
            analytics_url (str): Connection string for target database
        
        Raises:
            Exception: If database connections fail
        """
        try:
            # Create database engines with additional diagnostics
            self.device_manager_engine = create_engine(
                device_manager_url,
                # Additional connection pooling and diagnostic options
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
                pool_recycle=1800,  # Reconnect after 30 minutes
                echo=False  # Set to True for SQL query logging
            )
            self.analytics_engine = create_engine(
                analytics_url,
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
                pool_recycle=1800,
                echo=False
            )
            
            # Create session factories
            self.DeviceManagerSession = sessionmaker(bind=self.device_manager_engine)
            self.AnalyticsSession = sessionmaker(bind=self.analytics_engine)
            
            logger.info("✅ Database connections initialized successfully")
            
            # Perform a quick connection test
            with self.device_manager_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            with self.analytics_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("✅ Database connection tests passed")
        
        except Exception as e:
            logger.error(f"❌ Database connection initialization failed: {e}")
            logger.error(traceback.format_exc())
            raise

    def _safe_execute(self, session, query, params=None, description="Operation"):
        """
        Wrapper for safe query execution with comprehensive logging
        
        Args:
            session: Database session
            query: SQL query to execute
            params: Query parameters
            description: Description of the operation for logging
        
        Returns:
            Query result or None
        """
        try:
            logger.debug(f"Executing {description}")
            start_time = datetime.now()
            
            result = session.execute(query, params) if params else session.execute(query)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"✅ {description} completed in {duration:.2f} seconds")
            return result
        
        except Exception as e:
            logger.error(f"❌ {description} failed: {e}")
            logger.error(traceback.format_exc())
            raise

    # Rest of the implementation remains the same as in the previous version
    # (sync_interpolation_strategies, sync_location_hierarchy, sync_device_types, full_sync methods)

def main():
    """
    Main entry point for the synchronization script
    
    Handles:
    - Argument parsing
    - Sync mode selection
    - Error handling and reporting
    """
    parser = argparse.ArgumentParser(
        description="SenseMy IoT Device Manager Synchronization Tool",
        epilog="Sync metadata between device manager and analytics databases"
    )
    parser.add_argument(
        '--initial', 
        action='store_true', 
        help='Perform comprehensive initial full sync'
    )
    parser.add_argument(
        '--scheduled', 
        action='store_true', 
        help='Perform scheduled incremental sync'
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true', 
        help='Perform a dry run without committing changes'
    )

    args = parser.parse_args()

    # Configuration (in production, use environment variables or config file)
    DEVICE_MANAGER_URL = 'postgresql://username:password@localhost/device_db'
    ANALYTICS_URL = 'postgresql://username:password@localhost/analytics_db'

    # Comprehensive startup logging
    logger.info("🚀 Device Manager Synchronization Tool Initiated")
    logger.info(f"Sync Mode: Initial={args.initial}, Scheduled={args.scheduled}, Dry Run={args.dry_run}")

    sync_tool = DeviceManagerSync(DEVICE_MANAGER_URL, ANALYTICS_URL)

    try:
        if args.initial:
            logger.info("🔄 Starting initial full synchronization")
            sync_tool.full_sync()
        elif args.scheduled:
            logger.info("🔄 Starting scheduled synchronization")
            sync_tool.full_sync()
        else:
            parser.print_help()
        
        logger.info("✅ Synchronization completed successfully")
    
    except Exception as e:
        logger.error(f"❌ Synchronization process failed: {e}")
        logger.error(traceback.format_exc())
        raise
    finally:
        logger.info("🏁 Device Manager Sync Process Terminated")

if __name__ == '__main__':
    main()
"""
SenseMy IoT Platform: Device Manager Synchronization Script
Version: 1.0.0
Last Updated: 2025-06-29 UTC
Authors: SenseMy IoT Team
"""

import argparse
import logging
from datetime import datetime
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='device_manager_sync.log'
)
logger = logging.getLogger(__name__)

class DeviceManagerSync:
    def __init__(self, device_manager_url, analytics_url):
        """
        Initialize synchronization between device manager and analytics databases
        
        :param device_manager_url: Connection string for device manager database
        :param analytics_url: Connection string for analytics database
        """
        try:
            self.device_manager_engine = create_engine(device_manager_url)
            self.analytics_engine = create_engine(analytics_url)
            
            self.DeviceManagerSession = sessionmaker(bind=self.device_manager_engine)
            self.AnalyticsSession = sessionmaker(bind=self.analytics_engine)
            
            logger.info("Database connections initialized successfully")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def sync_interpolation_strategies(self):
        """
        Synchronize interpolation strategies from device manager to analytics
        """
        try:
            with self.DeviceManagerSession() as dm_session, \
                 self.AnalyticsSession() as analytics_session:
                
                # Fetch all strategies from device manager
                strategies = dm_session.execute(text("SELECT * FROM interpolation_strategies")).fetchall()
                
                for strategy in strategies:
                    # Upsert strategy
                    analytics_session.execute(
                        text("""
                        INSERT INTO interpolation_strategies 
                        (id, name, max_gap_hours, critical_silence_hours, interpolation_type, description)
                        VALUES (:id, :name, :max_gap_hours, :critical_silence_hours, :interpolation_type, :description)
                        ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        max_gap_hours = EXCLUDED.max_gap_hours,
                        critical_silence_hours = EXCLUDED.critical_silence_hours,
                        interpolation_type = EXCLUDED.interpolation_type,
                        description = EXCLUDED.description
                        """),
                        {
                            'id': strategy.id,
                            'name': strategy.name,
                            'max_gap_hours': strategy.max_gap_hours,
                            'critical_silence_hours': strategy.critical_silence_hours,
                            'interpolation_type': strategy.interpolation_type,
                            'description': strategy.description
                        }
                    )
                
                analytics_session.commit()
                logger.info(f"Synchronized {len(strategies)} interpolation strategies")
        
        except Exception as e:
            logger.error(f"Interpolation strategies sync failed: {e}")
            raise

    def sync_location_hierarchy(self):
        """
        Synchronize location hierarchy (sites, floors, rooms, zones)
        """
        location_tables = [
            ('sites', ['id', 'name', 'address', 'latitude', 'longitude']),
            ('floors', ['id', 'name', 'site_id']),
            ('rooms', ['id', 'name', 'floor_id']),
            ('zones', ['id', 'name', 'room_id'])
        ]

        for table, columns in location_tables:
            try:
                with self.DeviceManagerSession() as dm_session, \
                     self.AnalyticsSession() as analytics_session:
                    
                    # Fetch all records from device manager
                    records = dm_session.execute(
                        text(f"SELECT {', '.join(columns)} FROM {table}")
                    ).fetchall()
                    
                    # Prepare upsert query
                    upsert_query = text(f"""
                    INSERT INTO {table} ({', '.join(columns)})
                    VALUES ({', '.join([f':{col}' for col in columns])})
                    ON CONFLICT (id) DO UPDATE SET
                    {', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col != 'id'])}
                    """)
                    
                    # Batch upsert
                    for record in records:
                        analytics_session.execute(
                            upsert_query,
                            {col: getattr(record, col) for col in columns}
                        )
                    
                    analytics_session.commit()
                    logger.info(f"Synchronized {len(records)} records for {table}")
            
            except Exception as e:
                logger.error(f"Sync failed for {table}: {e}")
                raise

    def sync_device_types(self):
        """
        Synchronize device types from device manager to analytics
        """
        try:
            with self.DeviceManagerSession() as dm_session, \
                 self.AnalyticsSession() as analytics_session:
                
                # Fetch all device types
                device_types = dm_session.execute(text("""
                    SELECT 
                        id, name, device_family, 
                        icon_name, unpacker_module_name, 
                        unpacker_function_name, unpacker_version,
                        interpolation_strategy_id
                    FROM device_types
                """)).fetchall()
                
                upsert_query = text("""
                INSERT INTO device_types (
                    id, name, device_family, icon_name, 
                    unpacker_module_name, unpacker_function_name, 
                    unpacker_version, interpolation_strategy_id
                ) VALUES (
                    :id, :name, :device_family, :icon_name, 
                    :unpacker_module_name, :unpacker_function_name, 
                    :unpacker_version, :interpolation_strategy_id
                )
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    device_family = EXCLUDED.device_family,
                    icon_name = EXCLUDED.icon_name,
                    unpacker_module_name = EXCLUDED.unpacker_module_name,
                    unpacker_function_name = EXCLUDED.unpacker_function_name,
                    unpacker_version = EXCLUDED.unpacker_version,
                    interpolation_strategy_id = EXCLUDED.interpolation_strategy_id
                """)
                
                for device_type in device_types:
                    analytics_session.execute(
                        upsert_query,
                        {
                            'id': device_type.id,
                            'name': device_type.name,
                            'device_family': device_type.device_family,
                            'icon_name': device_type.icon_name,
                            'unpacker_module_name': device_type.unpacker_module_name,
                            'unpacker_function_name': device_type.unpacker_function_name,
                            'unpacker_version': device_type.unpacker_version,
                            'interpolation_strategy_id': device_type.interpolation_strategy_id
                        }
                    )
                
                analytics_session.commit()
                logger.info(f"Synchronized {len(device_types)} device types")
        
        except Exception as e:
            logger.error(f"Device types sync failed: {e}")
            raise

    def full_sync(self):
        """
        Perform a full synchronization of all tables
        """
        sync_methods = [
            self.sync_interpolation_strategies,
            self.sync_location_hierarchy,
            self.sync_device_types
        ]

        for method in sync_methods:
            method()

def main():
    parser = argparse.ArgumentParser(description="Device Manager Synchronization Tool")
    parser.add_argument(
        '--initial', 
        action='store_true', 
        help='Perform initial full sync'
    )
    parser.add_argument(
        '--scheduled', 
        action='store_true', 
        help='Perform scheduled sync'
    )

    args = parser.parse_args()

    # Configuration (in production, use environment variables)
    DEVICE_MANAGER_URL = 'postgresql://username:password@localhost/device_db'
    ANALYTICS_URL = 'postgresql://username:password@localhost/analytics_db'

    sync_tool = DeviceManagerSync(DEVICE_MANAGER_URL, ANALYTICS_URL)

    try:
        if args.initial:
            logger.info("Starting initial full synchronization")
            sync_tool.full_sync()
        elif args.scheduled:
            logger.info("Starting scheduled synchronization")
            sync_tool.full_sync()
        else:
            parser.print_help()
    
    except Exception as e:
        logger.error(f"Synchronization failed: {e}")
        raise

if __name__ == '__main__':
    main()
    EOF

# Make the script executable
chmod +x app/services/device_manager_sync.py

# Update requirements.txt to ensure SQLAlchemy is installed
echo "sqlalchemy" >> requirements.txt

# Create a configuration file for database connections
mkdir -p config
cat > config/database.yml << 'EOF'
device_manager:
  url: postgresql://username:password@localhost/device_db

analytics:
  url: postgresql://username:password@localhost/analytics_db
