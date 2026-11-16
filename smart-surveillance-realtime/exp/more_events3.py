"""R1 recall-target sensitivity (90/95/99%); R2 onset delay of each trigger (LOVO thresholds); R3 per-scene idle storage."""
import sys, json, numpy as np
sys.path.insert(0, '/root/exp')
import event_analysis as EA
from more_events_lib import *
from gt_events import EVENTS
OUT3 = '/root/results/more_events3.json'; res = {}
def C_stride(k): return [((lambda S, t=t, k=k: (trig_stride(S, DK, t, k), 1.0 / k)), t) for t in DGRID]
def C_adapt(ki, ka): return [((lambda S, t=t: adaptive(S, t, ki, ka)), t) for t in DGRID]
def C_mot(key): return [((lambda S, t=t, key=key: (S[key] > t, None)), t) for t in MGRID]
M = {'Detector, every frame': C_stride(1), 'Detector, every 8th': C_stride(8), 'Detector, every 16th': C_stride(16), 'Adaptive 16/8': C_adapt(16, 8),
     'FD': C_mot('FD'), 'MOG2': C_mot('MOG2'), 'CNT': C_mot('CNT'), 'GSOC': C_mot('GSOC'), 'Optical flow': C_mot('FLOW')}

# R1
res['target'] = {}
for tgt in (0.90, 0.95, 0.99):
    EA.TARGET = tgt
    for name in ['Detector, every 8th', 'Adaptive 16/8', 'MOG2', 'CNT', 'FD']:
        r, _ = EA.lovo(name, M[name], kinds=('clean',)); p = r['clean'][0]
        res['target'][f'{tgt}|{name}'] = {k: float(v) for k, v in p.items() if not isinstance(v, str)}
        print('target', tgt, name, round(p['idle_kept'], 3), round(p['frame_recall'], 3), round(p['ev_full'], 3), flush=True)
EA.TARGET = 0.95
json.dump(res, open(OUT3, 'w'), indent=1)

# R2 onset delay + R3 per-scene
res['onset'] = {}; res['scene'] = {}
for name, cands in M.items():
    delays, covered = [], []; per = {}
    for v in VIDS:
        fn, th = EA.select(cands, 'clean', [u for u in VIDS if u != v], 'yolo11n')
        S = load(v, 'clean'); trig, _ = fn(S); fps = FPS[v]; rec = record(trig, fps)
        r = metrics(rec, v, fps); per[v] = float(r['idle_kept'])
        t = np.arange(len(trig)) / fps
        for a, b in EVENTS[v]:
            if a < 2.0: continue  # background warm-up
            idx = np.where(trig & (t >= a - 0.5) & (t <= b + 0.5))[0]
            d = (t[idx[0]] - (a - 0.5)) if len(idx) else np.nan
            delays.append(d)
            i0 = int(round((a + 0.5) * fps))  # 1 s into the event (outside the annotation tolerance)
            covered.append(bool(rec[min(i0, len(rec) - 1)]))
    d = np.array(delays, float)
    res['onset'][name] = dict(n=len(d), missed=int(np.isnan(d).sum()), median=float(np.nanmedian(d)), p90=float(np.nanpercentile(d, 90)),
                              mean=float(np.nanmean(d)), within_preroll=float(np.mean(np.nan_to_num(d, nan=99) <= 1.0)), start_recorded=float(np.mean(covered)))
    res['scene'][name] = per
    print('onset', name, {k: round(x, 3) if isinstance(x, float) else x for k, x in res['onset'][name].items()}, {k: round(x, 2) for k, x in per.items()}, flush=True)
    json.dump(res, open(OUT3, 'w'), indent=1)
print('DONE')
