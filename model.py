"""Fictional fleet readiness simulation. Standard library only."""
import random
import math
import statistics
from dataclasses import dataclass, asdict

@dataclass
class Config:
    fleet: int = 40
    days: int = 60
    trials: int = 100
    failure_rate: float = 0.025
    repair_days: int = 3
    crews: int = 3
    initial_spares: int = 8
    stock_target: int = 8
    lead_days: int = 7
    seed: int = 42
    crew_daily_cost: float = 300
    spare_cost: float = 500

    def validate(self):
        bounds = {'fleet':(1,150), 'days':(1,180), 'trials':(1,300),
                  'repair_days':(1,20), 'crews':(0,30), 'initial_spares':(0,200),
                  'stock_target':(0,200), 'lead_days':(1,60), 'seed':(0,2147483647)}
        for name,(lo,hi) in bounds.items():
            value = getattr(self,name)
            if type(value) is not int or not lo <= value <= hi:
                raise ValueError(f'{name} must be an integer between {lo} and {hi}')
        for name,lo,hi in [('failure_rate',0,1),('crew_daily_cost',0,10000),('spare_cost',0,100000)]:
            value=getattr(self,name)
            if type(value) not in (int,float) or not math.isfinite(value) or not lo<=value<=hi:
                raise ValueError(f'{name} must be between {lo} and {hi}')
        if self.fleet*self.days*self.trials>4000000:
            raise ValueError('Reduce fleet, days, or trials; maximum is 4 million vehicle-days.')

def percentile(values,q):
    values=sorted(values)
    pos=(len(values)-1)*q
    a=int(pos); b=min(a+1,len(values)-1)
    return values[a]+(values[b]-values[a])*(pos-a)

def trial(c,index):
    # Fixed draws per vehicle/day keep comparable configurations paired.
    rng=random.Random(c.seed+index*100003)
    state=['ready']*c.fleet
    queue=[]; active={}; stock=c.initial_spares; orders=[]; rows=[]; events=[]
    bought=0; failures=0; completed=0; waiting_vehicle_days=0
    for day in range(1,c.days+1):
        for arrival,quantity in orders[:]:
            if arrival==day:
                stock+=quantity; orders.remove((arrival,quantity))
                if index==0: events.append((day,'parts_arrived',None,quantity))
        # Completed repairs return at the start of the next day.
        for v in list(active):
            if active[v]==0:
                del active[v]; state[v]='ready'; completed+=1
                if index==0: events.append((day,'repair_completed',v+1,1))
        for v in range(c.fleet):
            fail_draw=rng.random(); duration_draw=rng.random()
            if state[v]=='ready' and fail_draw<c.failure_rate:
                state[v]='waiting'; failures+=1
                duration=max(1,c.repair_days+int(duration_draw*3)-1)
                queue.append((v,duration))
                if index==0: events.append((day,'failure',v+1,duration))
        while queue and len(active)<c.crews and stock>0:
            v,duration=queue.pop(0); stock-=1; state[v]='repair'; active[v]=duration
            if index==0: events.append((day,'repair_started',v+1,duration))
        # Daily base-stock policy includes outstanding replenishment orders.
        quantity=max(0,c.stock_target-stock-sum(q for _,q in orders))
        if quantity:
            orders.append((day+c.lead_days,quantity)); bought+=quantity
            if index==0: events.append((day,'parts_ordered',None,quantity))
        ready=state.count('ready'); waiting=len(queue); repairing=len(active)
        waiting_vehicle_days+=waiting
        rows.append({'day':day,'ready':ready,'waiting':waiting,'repairing':repairing,
                     'stock':stock,'on_order':sum(q for _,q in orders),
                     'readiness':100*ready/c.fleet})
        for v in active: active[v]-=1
    cost=c.crews*c.crew_daily_cost*c.days+(c.initial_spares+bought)*c.spare_cost
    return {'trial':index,'readiness':statistics.mean(r['readiness'] for r in rows),
            'cost':cost,'failures':failures,'completed':completed,
            'waiting_vehicle_days':waiting_vehicle_days,'parts_ordered':bought,
            'daily':rows,'events':events}

def simulate(c):
    c.validate()
    runs=[trial(c,i) for i in range(c.trials)]
    daily=[]
    for j in range(c.days):
        values=[t['daily'][j]['readiness'] for t in runs]
        daily.append({'day':j+1,'mean':statistics.mean(values),
                      'p10':percentile(values,.1),'p90':percentile(values,.9)})
    values=[t['readiness'] for t in runs]
    summaries=[{k:v for k,v in t.items() if k not in ('daily','events')} for t in runs]
    ready_days=sum(t['readiness']/100*c.fleet*c.days for t in runs)
    summary={'readiness':statistics.mean(values),'p10':percentile(values,.1),
             'p90':percentile(values,.9),'cost':statistics.mean(t['cost'] for t in runs),
             'failures':statistics.mean(t['failures'] for t in runs),
             'waiting_vehicle_days':statistics.mean(t['waiting_vehicle_days'] for t in runs),
             'cost_per_ready_day':sum(t['cost'] for t in runs)/ready_days if ready_days else None}
    return {'config':asdict(c),'summary':summary,'daily':daily,
            'sample_daily':runs[0]['daily'],'sample_events':runs[0]['events'],
            'trials':summaries}
