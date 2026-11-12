"""Parameter sweeps for the Kalman tracker on clean MOT15 public detections: coasting window, IoU gate, confirmation hits."""
import sys, json
sys.path.insert(0, '/root/exp/trk')
from more_mot_lib import score
res = {'coast': {}, 'iou': {}, 'hits': {}}
for c in (0, 1, 3, 5, 10):
    res['coast'][c] = score(coast=c); print('coast', c, {k: round(v, 3) for k, v in res['coast'][c].items()}, flush=True)
for t in (0.1, 0.2, 0.3, 0.5):
    res['iou'][t] = score(iou_thr=t, coast=3); print('iou', t, {k: round(v, 3) for k, v in res['iou'][t].items()}, flush=True)
for h in (1, 2, 3, 5):
    res['hits'][h] = score(min_hits=h, coast=3); print('hits', h, {k: round(v, 3) for k, v in res['hits'][h].items()}, flush=True)
json.dump(res, open('/root/results/mot/more_mot2.json', 'w'), indent=1)
print('DONE')
