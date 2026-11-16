"""Reverse adaptive stride: sparse while idle, dense while active (so clips end promptly)."""
import sys, json
sys.path.insert(0, '/root/exp')
from more_events_lib import *
res = json.load(open(OUT))
res['adaptive_rev'] = {}
for ki, ka in [(16, 4), (16, 8), (24, 4), (24, 8), (32, 8), (12, 4)]:
    c = [((lambda S, t=t, ki=ki, ka=ka: adaptive(S, t, ki, ka)), t) for t in DGRID]
    res['adaptive_rev'][f'{ki}/{ka}'] = row(f'adaptive idle {ki} active {ka}', c); json.dump(res, open(OUT, 'w'), indent=1, default=float)
print('DONE')
