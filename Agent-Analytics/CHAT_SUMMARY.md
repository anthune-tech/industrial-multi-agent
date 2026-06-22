# Agent-Analytics — Session Summary

**Date**: June 22, 2026
**Repo**: https://github.com/anthune-tech/industrial-multi-agent
**Subfolder**: `Agent-Analytics/`

---

## Phase 1 — Agent-Analytics MVP (Done)

### What was built
- Standalone Agent-Analytics subfolder with agents/, tools/, db/, ingestion/, knowledge_base/, data/ directories
- CLI (analyze, troubleshoot, seed, serve) and FastAPI server (main.py)
- Tool adapt layer (tools/adapt.py) for CrewAI 1.x compatibility
- SQLite fallback in db/connection.py (PostgreSQL optional)

### CrewAI 1.x Adaptations
- `llm` param replaces `llm_config` — uses `ollama/qwen3:4b` string format
- Hierarchical crew: agents list = [worker], manager_agent = reasoner
- Task agent must be None (not set) in hierarchical mode for delegation tools to work

### Verified Working
- Crew creation, analyze CLI, troubleshoot CLI, health endpoint
- LLM: Qwen3 4B via Ollama (localhost:11434)
- Seed data: 105 rows in data/raw.db

---

## Phase 2 — Rice Processing Pipeline (In Progress)

### Equipment & Process Flow

| Stage | Equipment | Parameters |
|---|---|---|
| **1. Intake** | Weight Bridge | Vendor ID, Transaction ID, Truck Empty/Full Weight, Material QC, Received Material Qty |
| | Rough Cleaner 1-3 | Machine status on/off (each) |
| | Fine Cleaner 1-3 | Machine status on/off (each) |
| | Tank GKP 1-2 | Status level, input gate on/off, output gate on/off (each) |
| **2. Drying** | Flow Scale 1 | Flow Weight, Totalizer Weight |
| | Dryer 1-4 | Status on/off, input gate on/off, output gate on/off |
| | Flow Scale 2 | Flow Weight, Totalizer Weight |
| | Temp Bin 1-2 | Status level, input gate, output gate |
| | Temp GKG 1-2 | Status level, input gate, output gate |
| | SILO 1-3 | Status level, input gate, output gate |
| **3. Milling** | *(pending user detail)* | |
| **4. Polishing** | *(pending user detail)* | |
| **5. Packaging** | *(pending user detail)* | |

### Flow Direction
```
Tank GKP → Flow Scale 1 → Dryer (1-4, operator selects via gate) → Flow Scale 2 → Temp Bin → Temp GKG / SILO → Milling
```

### Batch Detection (fully automated, no manual entry)
- FS1 flow starts + dryer status=on + input_gate=open → batch START + dryer ID detected
- Dryer runs → burner ON duration tracked
- FS2 flow starts + dryer output_gate=open → output phase + dryer confirmed
- FS2 flow stops → batch END
- Per batch: FS1 totalizer − FS2 totalizer = Drying Loss

### OEE Drying Formulas (from QEE Planning.docx)
- **Availability** = Burner ON time / (batch end − batch start)
- **Performance** = Standard drying time / actual drying time
  - Tstd = LoadFactor × (KA_awal − KA_target)
- **Quality** = Moisture score matrix:
  - Green (13.5%−14.5%): 100%
  - Yellow (13.0%−13.4% or 14.6%−15.0%): 80%
  - Red (<13.0% or >15.0%): 50%

### Data Source
- **PDC device** → **InfluxDB** (time-series database)
- Historical data since December 2025
- Schema: still being detailed by user

### Predictive Analytics (MVP)
- Lookup table per vendor/dryer for time prediction
- `predict_drying_time(vendor_id, tonnage, ka_awal, dryer_id)` → predicted hours + confidence
- Accuracy improves as more batches accumulate
- Separate dashboard (tech TBD — Streamlit or FastAPI/HTML)

### Rendemen Tracking (Future)
- Link vendor ID from intake → drying → milling → finished product
- `(Output Mixer / Input GKG) × 100%`

---

## To Build Next

### Code
1. `db/drying_schema.sql` — batch_history, dryer_events tables
2. `tools/oee_drying.py` — OEE Drying calculator
3. `tools/predict_drying.py` — lookup-table prediction
4. `tools/pipeline_io.py` — stage-specific DB queries
5. `pipeline/drying.py` — stages 1-2 orchestrator
6. `pipeline/report.py` — structured JSON report
7. Update seed data for realistic rice processing
8. CLI `pipeline` subcommand + API `/pipeline` endpoint
9. Stages 3-5 (milling, polishing, packaging) — pending user detail
10. Rendemen tracking per vendor
11. Prediction dashboard

### Awaiting User Input
- Detailed parameters for stages 3-5 (same format: equipment + params per block)
- InfluxDB access method (direct query or push layer)
- Dashboard tech preference
