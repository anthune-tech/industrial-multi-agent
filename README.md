# Industrial Multi-Agent Plant Management System

## Architecture

```
┌──────────────────┐     ┌─────────────────────────────┐
│  Raw Plant Data  │────▶│      Data Ingestion          │
│  (CSV/Excel/DB)  │     │  (cron every 5 min)          │
└──────────────────┘     └─────────────┬───────────────┘
                                       ▼ Raw DB (SQLite)
┌──────────────────────────────────────────────────────────┐
│                Multi-Agent System (CrewAI)                │
│                                                          │
│  ┌────────────────────┐  tool calls  ┌────────────────┐ │
│  │  REASONING AGENT   │─────────────▶│  TASK AGENT    │ │
│  │  (Claude / GPT-4o) │◀────────────│  (GPT-4o-mini) │ │
│  │                    │   results    │  + 9 tools     │ │
│  │  •  Plans & routes │              └────────────────┘ │
│  │  •  Troubleshoots  │                                 │
│  │  •  Synthesizes    │   ┌──────────────────────────┐  │
│  │  •  Maintains mem  │   │  VECTOR DB (ChromaDB)    │  │
│  └────────────────────┘   │  SOPs, manuals, history  │  │
│                           └──────────────────────────┘  │
└───────────────────────────┬──────────────────────────────┘
                            ▼ writes results
┌──────────────────────────────────────────────────────────┐
│              Results Database (PostgreSQL)                │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ oee_snapshots│  │machine_status│  │analytics_res. │  │
│  └──────────────┘  └──────────────┘  └───────────────┘  │
│  ┌──────────────┐  ┌──────────────┐                     │
│  │   alarms     │  │troubleshoot_ │                     │
│  │              │  │   sessions   │                     │
│  └──────────────┘  └──────────────┘                     │
└───────────────────────────┬──────────────────────────────┘
                            │ dashboard polls every 30s
                            ▼
┌──────────────────────────────────────────────────────────┐
│            React Dashboard (Vite + TypeScript)            │
│                                                          │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────┐ ┌──────┐  │
│  │ OEE         │ │ Machine     │ │ Analytics│ │Troub-│  │
│  │ Dashboard   │ │ Overview    │ │          │ │lesh. │  │
│  └─────────────┘ └─────────────┘ └──────────┘ └──────┘  │
└──────────────────────────────────────────────────────────┘
```

## Agents

| Agent | LLM | Role |
|---|---|---|
| **Reasoning Agent** (Supervisor) | Claude 4 / GPT-4o | Planner, troubleshooter, answer synthesizer |
| **Task Agent** (Worker) | GPT-4o-mini | Executes all data/tool operations |

## Tools (Task Agent)

| # | Tool | What it does |
|---|---|---|
| 1 | `read_plant_data(machine, date_range)` | Read raw sensor/production data |
| 2 | `calculate_oee(machine, shift, date)` | A×P×Q computation |
| 3 | `analyze_trend(machine, metric, period)` | Stats, trend, anomaly detection |
| 4 | `query_results_db(query)` | Read historical results from PostgreSQL |
| 5 | `save_to_results_db(table, data)` | Write results to PostgreSQL |
| 6 | `query_knowledge_base(question)` | RAG over SOPs/manuals (ChromaDB) |
| 7 | `detect_anomalies(machine, metric)` | Statistical outlier detection |
| 8 | `generate_report(machine, period)` | Structured JSON summary |
| 9 | `save_troubleshoot_session(...)` | Log troubleshooting sessions to DB |

## Database Schema (PostgreSQL)

### oee_snapshots
Stores OEE calculations per machine per shift.

| Column | Type | Description |
|---|---|---|
| id | SERIAL | Primary key |
| machine_id | TEXT | Machine identifier |
| timestamp | TIMESTAMPTZ | Snapshot time |
| shift | TEXT | Shift label |
| availability | FLOAT | 0-1 |
| performance | FLOAT | 0-1 |
| quality | FLOAT | 0-1 |
| oee | FLOAT | 0-1 |
| run_minutes | INT | Total run time |
| downtime_minutes | INT | Total downtime |

### machine_status
Latest known state of each machine.

| Column | Type | Description |
|---|---|---|
| machine_id | TEXT | Primary key |
| status | TEXT | running/idle/down/maintenance |
| last_seen | TIMESTAMPTZ | Last heartbeat |
| error_code | TEXT | Current error if any |
| oee_current | FLOAT | Latest OEE |
| updated_at | TIMESTAMPTZ | Last update |

### analytics_results
Ad-hoc analysis query results.

| Column | Type | Description |
|---|---|---|
| id | SERIAL | Primary key |
| query_type | TEXT | Type of analysis |
| machine_id | TEXT | Target machine |
| parameters | JSONB | Query params |
| result | JSONB | Result data |
| created_at | TIMESTAMPTZ | Creation time |

### alarms
Detected anomalies and alerts.

| Column | Type | Description |
|---|---|---|
| id | SERIAL | Primary key |
| machine_id | TEXT | Affected machine |
| severity | TEXT | info/warning/critical |
| message | TEXT | Alarm message |
| details | JSONB | Additional context |
| triggered_at | TIMESTAMPTZ | When triggered |
| acknowledged | BOOLEAN | Acknowledged flag |

### troubleshoot_sessions
Troubleshooting history.

| Column | Type | Description |
|---|---|---|
| id | SERIAL | Primary key |
| machine_id | TEXT | Affected machine |
| problem | TEXT | User-described issue |
| diagnosis | TEXT | Agent's diagnosis |
| resolution | TEXT | Recommended action |
| confidence | FLOAT | Confidence score |
| created_at | TIMESTAMPTZ | Creation time |

## Dashboard — 4 Tabs

| Tab | Components | Data Source |
|---|---|---|
| **OEE Dashboard** | Gauge (OEE %), 3 sub-gauges (A/P/Q), 24h trend, shift comparison | oee_snapshots |
| **Machine Overview** | Cards per machine: status badge, OEE, last seen, error code | machine_status |
| **Data Analytics** | Selectors + chart, "Run Analysis" triggers agent | analytics_results + agent API |
| **Troubleshooting** | Chat UI, user types problem → agent returns diagnosis + resolution | agent API + troubleshoot_sessions |

## Tech Stack

| Layer | Technology |
|---|---|
| Agent framework | CrewAI |
| Backend API | FastAPI (Python) |
| Results DB | PostgreSQL (via Docker) |
| Vector DB | ChromaDB |
| LLMs | Claude 4, GPT-4o-mini, text-embedding-3-small |
| Dashboard | React + Vite + TypeScript |
| Charts | Recharts |
| Deployment | docker-compose |

## Project Structure

```
plant-mgmt/
├── docker-compose.yml
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── agents/
│   │   ├── reasoner.py
│   │   └── worker.py
│   ├── tools/
│   │   ├── oee.py
│   │   ├── analytics.py
│   │   ├── data_io.py
│   │   ├── knowledge.py
│   │   └── troubleshoot.py
│   ├── db/
│   │   ├── schema.sql
│   │   ├── models.py
│   │   └── connection.py
│   ├── ingestion/
│   │   └── ingest.py
│   ├── api/
│   │   ├── routes_agent.py
│   │   └── routes_data.py
│   ├── scheduler/
│   │   └── jobs.py
│   └── knowledge_base/
├── dashboard/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── api/client.ts
│   │   ├── hooks/usePoll.ts
│   │   ├── views/
│   │   │   ├── OEEDashboard.tsx
│   │   │   ├── MachineOverview.tsx
│   │   │   ├── DataAnalytics.tsx
│   │   │   └── Troubleshooting.tsx
│   │   └── components/
│   │       ├── Gauge.tsx
│   │       ├── StatusCard.tsx
│   │       ├── TrendChart.tsx
│   │       └── ChatBubble.tsx
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## Implementation Phases

| Phase | What | Est. time |
|---|---|---|
| P1 | docker-compose, PostgreSQL schema, data ingestion | 2 days |
| P2 | CrewAI agents + 9 tools + ChromaDB knowledge base | 4 days |
| P3 | FastAPI routes + scheduler | 2 days |
| P4 | React dashboard — OEE + Machine Overview | 3 days |
| P5 | Analytics tab + Troubleshooting tab | 3 days |
| P6 | Integration testing, seed data, polish | 2 days |
