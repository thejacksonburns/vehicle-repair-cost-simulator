-- Run against readiness.sqlite after running scenarios.
-- Management comparison across saved scenarios.
SELECT * FROM scenario_summary ORDER BY average_readiness DESC;

-- Days below an 80% readiness target.
SELECT scenario_id, COUNT(*) AS days_below_target
FROM daily_results WHERE mean < 80 GROUP BY scenario_id;

-- First-trial failure counts by vehicle (synthetic data).
SELECT scenario_id,vehicle,COUNT(*) AS failures
FROM sample_events WHERE event='failure'
GROUP BY scenario_id,vehicle ORDER BY failures DESC;

-- Queue burden and cost efficiency.
SELECT s.name, AVG(t.waiting_vehicle_days) AS queue_days,
       AVG(t.cost) AS cost, AVG(t.readiness) AS readiness
FROM scenarios s JOIN trial_results t ON s.id=t.scenario_id GROUP BY s.id;
