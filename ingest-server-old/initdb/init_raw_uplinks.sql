CREATE TABLE IF NOT EXISTS public.raw_uplinks (
    id SERIAL PRIMARY KEY,
    deveui TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    payload JSONB,
    received_at TIMESTAMPTZ
);
