import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import unittest
from model import Config,simulate
import storage
import tempfile

class ModelTests(unittest.TestCase):
    def test_no_failures(self):
        r=simulate(Config(failure_rate=0,crews=0,trials=3))
        self.assertEqual(r['summary']['readiness'],100)
        self.assertEqual(r['summary']['failures'],0)
    def test_no_crews_eventually_all_down(self):
        r=simulate(Config(failure_rate=1,crews=0,days=5,trials=2))
        self.assertEqual(r['summary']['readiness'],0)
        self.assertEqual(r['summary']['waiting_vehicle_days'],40*5)
    def test_no_parts_no_repairs(self):
        r=simulate(Config(initial_spares=0,stock_target=0,failure_rate=1,days=4,trials=2))
        self.assertEqual(r['trials'][0]['completed'],0)
        self.assertTrue(all(row['repairing']==0 for row in r['sample_daily']))
    def test_conservation_and_capacity(self):
        c=Config(trials=10);r=simulate(c)
        for row in r['sample_daily']:
            self.assertEqual(row['ready']+row['waiting']+row['repairing'],c.fleet)
            self.assertLessEqual(row['repairing'],c.crews)
            self.assertGreaterEqual(row['stock'],0)
        for row in r['daily']:
            self.assertTrue(0<=row['p10']<=row['mean']<=row['p90']<=100)
    def test_determinism(self):
        c=Config(trials=3,days=12)
        self.assertEqual(simulate(c),simulate(c))
    def test_arrival_delay_and_repair_boundary(self):
        c=Config(fleet=1,days=5,trials=1,failure_rate=1,repair_days=2,initial_spares=0,stock_target=1,lead_days=2,crews=1)
        r=simulate(c)
        events=r['sample_events']
        self.assertEqual(next(e[0] for e in events if e[1]=='parts_arrived'),3)
        self.assertEqual(next(e[0] for e in events if e[1]=='repair_started'),3)
        duration=next(e[3] for e in events if e[1]=='repair_started')
        completed=[e[0] for e in events if e[1]=='repair_completed']
        if completed:self.assertEqual(completed[0],3+duration)
    def test_cost_accounting(self):
        c=Config(days=4,trials=1,failure_rate=0,crews=2,initial_spares=3,stock_target=5,lead_days=10)
        r=simulate(c)
        self.assertEqual(r['summary']['cost'],2*300*4+5*500)
    def test_bad_input(self):
        for c in [Config(fleet=0),Config(trials=301),Config(failure_rate=float('nan')),Config(crews=1.5)]:
            with self.assertRaises(ValueError):simulate(c)
    def test_database_round_trip(self):
        old=storage.DB
        try:
            with tempfile.TemporaryDirectory() as tmp:
                storage.DB=Path(tmp)/'test.sqlite';r=simulate(Config(trials=2,days=5))
                sid=storage.save('Test',r);self.assertEqual(storage.load(sid),__import__('json').loads(__import__('json').dumps(r)))
                with storage.connect() as db:
                    self.assertEqual(db.execute('SELECT COUNT(*) FROM trial_results').fetchone()[0],2)
                    self.assertEqual(db.execute('SELECT COUNT(*) FROM daily_results').fetchone()[0],5)
                    self.assertEqual(db.execute('SELECT trials FROM scenario_summary').fetchone()[0],2)
        finally:storage.DB=old
if __name__=='__main__':unittest.main()
