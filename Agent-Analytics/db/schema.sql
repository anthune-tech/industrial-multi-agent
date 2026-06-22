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

INSERT INTO oee_snapshots (machine_id, timestamp, shift, availability, performance, quality, oee, run_minutes, downtime_minutes)
SELECT m, t, s, a, p, q, a*p*q, r, d FROM (VALUES
  ('LINE-01', NOW() - INTERVAL '6 days', 'morning', 0.95, 0.88, 0.97, 420, 30),
  ('LINE-01', NOW() - INTERVAL '5 days', 'morning', 0.92, 0.85, 0.96, 400, 50),
  ('LINE-01', NOW() - INTERVAL '4 days', 'morning', 0.88, 0.82, 0.95, 380, 70),
  ('LINE-01', NOW() - INTERVAL '3 days', 'morning', 0.85, 0.80, 0.94, 360, 90),
  ('LINE-01', NOW() - INTERVAL '2 days', 'morning', 0.90, 0.86, 0.96, 390, 60),
  ('LINE-01', NOW() - INTERVAL '1 days', 'morning', 0.93, 0.87, 0.97, 410, 40),
  ('LINE-02', NOW() - INTERVAL '6 days', 'morning', 0.88, 0.82, 0.94, 380, 70),
  ('LINE-02', NOW() - INTERVAL '5 days', 'morning', 0.85, 0.80, 0.93, 360, 90),
  ('LINE-02', NOW() - INTERVAL '4 days', 'morning', 0.90, 0.84, 0.95, 390, 60),
  ('LINE-02', NOW() - INTERVAL '3 days', 'morning', 0.92, 0.86, 0.96, 400, 50),
  ('LINE-02', NOW() - INTERVAL '2 days', 'morning', 0.78, 0.75, 0.90, 320, 130),
  ('LINE-02', NOW() - INTERVAL '1 days', 'morning', 0.82, 0.78, 0.92, 340, 110),
  ('LINE-03', NOW() - INTERVAL '6 days', 'morning', 0.75, 0.72, 0.88, 300, 150),
  ('LINE-03', NOW() - INTERVAL '5 days', 'morning', 0.70, 0.68, 0.85, 280, 170),
  ('LINE-03', NOW() - INTERVAL '4 days', 'morning', 0.65, 0.62, 0.82, 250, 200),
  ('LINE-03', NOW() - INTERVAL '3 days', 'morning', 0.60, 0.58, 0.80, 220, 230),
  ('LINE-03', NOW() - INTERVAL '2 days', 'morning', 0.55, 0.52, 0.78, 200, 250),
  ('LINE-03', NOW() - INTERVAL '1 days', 'morning', 0.50, 0.48, 0.75, 180, 270),
  ('LINE-04', NOW() - INTERVAL '6 days', 'morning', 0.98, 0.95, 0.99, 440, 10),
  ('LINE-04', NOW() - INTERVAL '5 days', 'morning', 0.97, 0.94, 0.99, 430, 20),
  ('LINE-04', NOW() - INTERVAL '4 days', 'morning', 0.96, 0.93, 0.98, 420, 30),
  ('LINE-04', NOW() - INTERVAL '3 days', 'morning', 0.95, 0.92, 0.98, 410, 40),
  ('LINE-04', NOW() - INTERVAL '2 days', 'morning', 0.94, 0.91, 0.97, 400, 50),
  ('LINE-04', NOW() - INTERVAL '1 days', 'morning', 0.93, 0.90, 0.97, 390, 60),
  ('LINE-05', NOW() - INTERVAL '6 days', 'morning', 0.91, 0.87, 0.96, 400, 50),
  ('LINE-05', NOW() - INTERVAL '5 days', 'morning', 0.89, 0.85, 0.95, 380, 70),
  ('LINE-05', NOW() - INTERVAL '4 days', 'morning', 0.87, 0.83, 0.94, 360, 90),
  ('LINE-05', NOW() - INTERVAL '3 days', 'morning', 0.86, 0.82, 0.94, 350, 100),
  ('LINE-05', NOW() - INTERVAL '2 days', 'morning', 0.84, 0.80, 0.93, 340, 110),
  ('LINE-05', NOW() - INTERVAL '1 days', 'morning', 0.83, 0.79, 0.92, 330, 120)
) AS t(m, t, s, a, p, q, r, d);

INSERT INTO alarms (machine_id, severity, message, details, triggered_at)
VALUES
  ('LINE-03', 'critical', 'Conveyor belt motor over temperature', '{"temp": 95, "threshold": 85}', NOW() - INTERVAL '2 hours'),
  ('LINE-03', 'critical', 'Emergency stop activated', '{"reason": "overheat_protection"}', NOW() - INTERVAL '1 hour'),
  ('LINE-02', 'warning', 'Cycle time exceeded threshold', '{"actual": 55, "threshold": 50}', NOW() - INTERVAL '4 hours'),
  ('LINE-05', 'warning', 'Quality rate dropping below 90%', '{"actual_quality": 87.5}', NOW() - INTERVAL '6 hours'),
  ('LINE-02', 'warning', 'Vibration sensor spike detected', '{"sensor": "bearing_1", "value": 12.3}', NOW() - INTERVAL '8 hours'),
  ('LINE-01', 'info', 'Scheduled maintenance due in 2 days', '{"days_until_maintenance": 2}', NOW() - INTERVAL '1 day'),
  ('LINE-04', 'info', 'Production target achieved for shift', '{"achieved": 112, "target": 100}', NOW() - INTERVAL '12 hours');

INSERT INTO analytics_results (query_type, machine_id, parameters, result)
VALUES
  ('oee_trend', 'LINE-01', '{"days": 7}', '{"trend": "declining", "avg_oee": 0.88}'),
  ('oee_trend', 'LINE-02', '{"days": 7}', '{"trend": "stable", "avg_oee": 0.85}'),
  ('oee_trend', 'LINE-03', '{"days": 7}', '{"trend": "declining", "avg_oee": 0.65}'),
  ('oee_trend', 'LINE-04', '{"days": 7}', '{"trend": "slight_decline", "avg_oee": 0.95}'),
  ('oee_trend', 'LINE-05', '{"days": 7}', '{"trend": "stable", "avg_oee": 0.86}');
