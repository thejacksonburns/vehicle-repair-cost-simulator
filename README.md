# Vehicle Repair & Cost Simulator

A local data analytics and simulation project that explores how maintenance staffing, spare-parts inventory, and delivery delays affect a fictional vehicle fleet's operational readiness and cost.

## Business Problem

A fictional operations manager needs to decide whether additional maintenance capacity or spare-parts inventory produces enough improvement in equipment availability to justify the added cost.

## What the Project Does

- Runs repeated vehicle-readiness simulations in Python
- Models random failures, repair queues, crew capacity, spare-parts inventory, and delivery delays
- Stores scenario assumptions and results in SQLite
- Uses SQL queries to compare saved scenarios and operational metrics
- Provides an interactive HTML dashboard for changing assumptions and reviewing results
- Exports trial-level and daily results to CSV
- Uses deterministic random seeds so identical settings can reproduce the same results

## Tools

**Python • SQL • SQLite • HTML/CSS • JavaScript**

The Python simulation uses the standard library and runs locally without external packages.

## Example Analysis

A 100-trial comparison used a fictional fleet of 40 vehicles over 60 days.

| Metric | Baseline: 3 crews, 8 spares | Enhanced: 5 crews, 16 spares |
| --- | ---: | ---: |
| Average readiness | 89.02% | 92.75% |
| Average modeled cost | $84,010 | $126,305 |
| Average queue vehicle-days | 109.72 | 6.92 |
| Cost per ready vehicle-day | $39.32 | $56.74 |

Under these assumptions, the enhanced policy increased average readiness by **3.73 percentage points** while increasing modeled cost by about **50.3%**. Waiting decreased by about **93.7%**. These results are simulated and are not a real-world operational recommendation.

## Run Locally

1. Clone or download this repository.
2. Open Terminal in the project folder.
3. Run:

```bash
python3 server.py
```

4. Open `http://127.0.0.1:8765` if the dashboard does not open automatically.
5. Change the scenario inputs and run simulations from the dashboard.

Running scenarios creates a local `readiness.sqlite` database for saved results.

## Repository Structure

- `model.py` — simulation logic and input validation
- `server.py` — local HTTP server and API endpoints
- `storage.py` — SQLite schema and persistence
- `queries.sql` — example SQL analysis
- `dashboard.html` — interactive dashboard
- `tests/test_model.py` — model and storage tests
- `sample-results/` — CSV outputs from example scenarios
- `PROJECT_GUIDE.md` — methodology, data dictionary, findings, and interview notes
- `VALIDATION.md` — validation and testing summary

## Validation

The project includes tests for fleet conservation, crew limits, deterministic runs, repair and delivery timing, cost calculations, input validation, and SQLite round trips. Additional checks cover scenario execution, saved-result retrieval, CSV exports, and dashboard interactions.

## Skills Demonstrated

Python programming, SQL, relational databases, data analysis, simulation, scenario analysis, data visualization, testing, and translating operational questions into measurable business tradeoffs.

## Important Note

This project uses **fictional assumptions and synthetic simulation data**. No real operational, proprietary, or sensitive data is included.
