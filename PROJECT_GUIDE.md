# Project guide: equipment readiness and resource tradeoffs

## Business problem
A fictional operations manager needs to decide whether additional maintenance capacity or spare-parts inventory produces sufficient equipment availability to justify the cost.

## Requirements and acceptance criteria
1. Users can change fleet size, time horizon, failure probability, repair capacity, inventory policy, delivery delay, and costs.
2. Identical settings and seeds reproduce the same results.
3. Every daily snapshot conserves fleet size: ready + waiting + repairing = fleet.
4. Repairs cannot exceed crew capacity or use unavailable spare parts.
5. Inputs are validated; overly large studies are rejected.
6. Users can compare scenarios, revisit saved results, and export raw trial and daily data.
7. Stored records support SQL analysis and retain the exact assumptions.
8. Costs and uncertainty have clear definitions.

## Architecture
Browser controls submit JSON to POST /api/simulate. Python validates the configuration and runs the simulations. SQLite persists assumptions, results, daily distributions, and an event trace from trial zero. The browser renders the returned data. GET endpoints support history, scenario retrieval, and CSV exports. Everything runs locally.

## Data dictionary
| Table | Main fields | Grain |
|---|---|---|
| scenarios | id, created, name, config_json, result_json | One saved scenario |
| trial_results | scenario_id, trial, readiness, cost, failures, completed, waiting_vehicle_days, parts_ordered | One trial |
| daily_results | scenario_id, day, mean, p10, p90 | One aggregated day |
| sample_events | scenario_id, day, event, vehicle, quantity | One event from trial zero |

Event quantity stores a part count for orders/arrivals, duration in days for failures/repair starts, and one completion for repair completions. Vehicle numbers start at one. No personal or sensitive data is used.

## Verified sample findings
Settings: 40 vehicles, 60 days, 100 trials, seed 42, daily failure probability 0.025, typical repair duration 3 days, 7-day deliveries, $300 per crew-day, $500 per part.

| Metric | Baseline: 3 crews, 8 spares | Enhanced: 5 crews, 16 spares |
|---|---:|---:|
| Average readiness | 89.02% | 92.75% |
| Average modeled cost | $84,010 | $126,305 |
| Average queue vehicle-days | 109.72 | 6.92 |
| Cost per ready vehicle-day | $39.32 | $56.74 |

The enhanced policy gains 3.73 percentage points in readiness for $42,295 more modeled cost, a 50.3% cost increase. Waiting decreases about 93.7%. These are simulated results under fictional assumptions, not realized savings or an operational recommendation. The next useful study separates extra crews from extra inventory and defines a readiness target and budget.

## Experiments for you to own
1. Baseline versus extra crews only.
2. Baseline versus extra spares only.
3. Same inventory policy with 3-, 7-, and 14-day delivery delays.
4. A higher failure probability to represent stressed equipment.
5. Three different seeds and a larger trial count to check stability.
6. Identify the lowest-cost scenario meeting an explicit readiness target, then discuss uncertainty and assumptions.

## A short interview explanation
“I built an AI-assisted logistics simulator to understand how repair staffing and spare inventory affect equipment availability. Python runs repeated scenarios, SQL stores the data, and the dashboard compares readiness with cost. In a fictional 100-trial study, adding crews and spares raised readiness by about 3.7 percentage points but increased modeled cost by about 50%, so I would test each resource change separately before recommending an investment.”

## Questions to be ready for
- Why did you choose these assumptions? They make a tractable prototype; real deployment would require historical data and domain validation.
- Why simulate? A single average cannot capture queues, delayed arrivals, and random failures over time.
- What did SQL contribute? Structured history, relational data, aggregate comparisons, and auditable inputs.
- How did you test it? Boundary cases, fleet conservation, capacity limits, timing, deterministic runs, cost calculations, database round trips, and API/CSV checks.
- What would you change next? Calibrate assumptions, add multiple equipment and part types, and optimize policies against an agreed target.

## Resume bullet after you review and demo it
Developed an AI-assisted Python and SQL logistics simulator with an interactive dashboard to evaluate fleet readiness, maintenance capacity, and spare-parts policies across 100-trial scenario studies.

Add Power BI to the bullet only after you create and can demonstrate a Power BI report yourself.
