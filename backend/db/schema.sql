CREATE TABLE IF NOT EXISTS oee_snapshots (
  id SERIAL PRIMARY KEY,
  machine_id TEXT NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL,
  shift TEXT,
  availability FLOAT,
  performance FLOAT,
  quality FLOAT,
  oee FLOAT,
  run_minutes INT,
  downtime_minutes INT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_oee_machine_time ON oee_snapshots (machine_id, timestamp DESC);

CREATE TABLE IF NOT EXISTS machine_status (
  machine_id TEXT PRIMARY KEY,
  status TEXT CHECK (status IN ('running','idle','down','maintenance')),
  last_seen TIMESTAMPTZ,
  error_code TEXT,
  oee_current FLOAT,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS analytics_results (
  id SERIAL PRIMARY KEY,
  query_type TEXT,
  machine_id TEXT,
  parameters JSONB,
  result JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS alarms (
  id SERIAL PRIMARY KEY,
  machine_id TEXT,
  severity TEXT CHECK (severity IN ('info','warning','critical')),
  message TEXT,
  details JSONB,
  triggered_at TIMESTAMPTZ,
  acknowledged BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_alarms_machine ON alarms (machine_id, triggered_at DESC);

CREATE TABLE IF NOT EXISTS troubleshoot_sessions (
  id SERIAL PRIMARY KEY,
  machine_id TEXT,
  problem TEXT,
  diagnosis TEXT,
  resolution TEXT,
  confidence FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO machine_status (machine_id, status, last_seen, oee_current)
VALUES
  ('LINE-01', 'running', NOW(), 0.85),
  ('LINE-02', 'running', NOW(), 0.72),
  ('LINE-03', 'down', NOW() - INTERVAL '30 minutes', 0.45),
  ('LINE-04', 'idle', NOW() - INTERVAL '5 minutes', 0.91),
  ('LINE-05', 'running', NOW(), 0.78)
ON CONFLICT (machine_id) DO NOTHING;
