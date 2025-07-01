-- Add archived_at columns for temporal tracking
ALTER TABLE devices.sites ADD COLUMN IF NOT EXISTS archived_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE devices.floors ADD COLUMN IF NOT EXISTS archived_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE devices.rooms ADD COLUMN IF NOT EXISTS archived_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE devices.zones ADD COLUMN IF NOT EXISTS archived_at TIMESTAMP WITH TIME ZONE;

-- Add status column to device_registry if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema='devices' AND table_name='device_registry' AND column_name='status'
    ) THEN
        ALTER TABLE devices.device_registry ADD COLUMN status VARCHAR(20) DEFAULT 'ORPHAN';
    END IF;
END $$;
