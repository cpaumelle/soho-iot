-- Create the 'devices' schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS devices;

-- Set the search path to include the 'devices' schema
SET search_path TO devices, public;

-- Table: device_types - Master list of device models
CREATE TABLE IF NOT EXISTS device_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

-- Table: sites - Top-level location hierarchy
CREATE TABLE IF NOT EXISTS sites (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

-- Table: floors - Linked to sites
CREATE TABLE IF NOT EXISTS floors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    site_id INTEGER NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    UNIQUE (name, site_id)
);

-- Table: rooms - Linked to floors
CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    floor_id INTEGER NOT NULL REFERENCES floors(id) ON DELETE CASCADE,
    UNIQUE (name, floor_id)
);

-- Table: zones - Linked to rooms
CREATE TABLE IF NOT EXISTS zones (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    room_id INTEGER NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    UNIQUE (name, room_id)
);

-- Table: devices - For individual devices, linked to device_types and zones
-- Implied by "devices.devices" schema usage and "uplinks (via deveui) -> devices" relationship
CREATE TABLE IF NOT EXISTS devices (
    deveui VARCHAR(16) PRIMARY KEY, -- Device EUI as primary key
    name VARCHAR(255),
    device_type_id INTEGER REFERENCES device_types(id) ON DELETE SET NULL,
    zone_id INTEGER REFERENCES zones(id) ON DELETE SET NULL -- Location link
);

-- Table: uplinks - Processed uplink data, linked to devices
CREATE TABLE IF NOT EXISTS uplinks (
    id SERIAL PRIMARY KEY,
    deveui VARCHAR(16) NOT NULL REFERENCES devices(deveui) ON DELETE CASCADE,
    received_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    payload JSONB
);
