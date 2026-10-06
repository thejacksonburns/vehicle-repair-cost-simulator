import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
DB=Path(__file__).parent/'readiness.sqlite'
SCHEMA='''
CREATE TABLE IF NOT EXISTS scenarios(id INTEGER PRIMARY KEY, created TEXT, name TEXT, config_json TEXT, result_json TEXT);
CREATE TABLE IF NOT EXISTS trial_results(scenario_id INTEGER REFERENCES scenarios(id), trial INTEGER, readiness REAL, cost REAL, failures INTEGER, completed INTEGER, waiting_vehicle_days INTEGER, parts_ordered INTEGER, PRIMARY KEY(scenario_id,trial));
CREATE TABLE IF NOT EXISTS daily_results(scenario_id INTEGER REFERENCES scenarios(id), day INTEGER, mean REAL, p10 REAL, p90 REAL, PRIMARY KEY(scenario_id,day));
CREATE TABLE IF NOT EXISTS sample_events(scenario_id INTEGER REFERENCES scenarios(id), day INTEGER, event TEXT, vehicle INTEGER, quantity INTEGER);
CREATE VIEW IF NOT EXISTS scenario_summary AS SELECT s.id,s.name,COUNT(t.trial) AS trials,AVG(t.readiness) AS average_readiness,AVG(t.cost) AS average_cost,AVG(t.waiting_vehicle_days) AS average_waiting_vehicle_days FROM scenarios s JOIN trial_results t ON s.id=t.scenario_id GROUP BY s.id,s.name;
'''
def connect():
    db=sqlite3.connect(DB); db.execute('PRAGMA foreign_keys=ON'); db.executescript(SCHEMA); return db

def save(name,result):
    with connect() as db:
        cur=db.execute('INSERT INTO scenarios(created,name,config_json,result_json) VALUES(?,?,?,?)',
            (datetime.now(timezone.utc).isoformat(),name,json.dumps(result['config']),json.dumps(result)))
        sid=cur.lastrowid
        db.executemany('INSERT INTO trial_results VALUES(?,?,?,?,?,?,?,?)',[(sid,t['trial'],t['readiness'],t['cost'],t['failures'],t['completed'],t['waiting_vehicle_days'],t['parts_ordered']) for t in result['trials']])
        db.executemany('INSERT INTO daily_results VALUES(?,?,?,?,?)',[(sid,r['day'],r['mean'],r['p10'],r['p90']) for r in result['daily']])
        db.executemany('INSERT INTO sample_events VALUES(?,?,?,?,?)',[(sid,*e) for e in result['sample_events']])
    return sid

def history():
    with connect() as db:
        return [dict(zip(('id','created','name'),row)) for row in db.execute('SELECT id,created,name FROM scenarios ORDER BY id DESC LIMIT 30')]

def load(sid):
    with connect() as db: row=db.execute('SELECT result_json FROM scenarios WHERE id=?',(sid,)).fetchone()
    if not row: raise ValueError('Scenario not found')
    return json.loads(row[0])
