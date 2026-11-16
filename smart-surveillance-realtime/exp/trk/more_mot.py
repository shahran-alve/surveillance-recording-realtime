"""Tracking with sparse or unreliable detections (MOT15 TUD-Campus + TUD-Stadtmitte, public detections).
T1: detections only every k-th frame (strided detector); the tracker predicts in between.
T2: each detection dropped independently with probability p (5 seeds), simulating detector misses.
Kalman motion model vs. last-box (no motion) prediction; track memory fixed at 15 frames."""
import sys, json, math, numpy as np
np.asfarray = lambda a, dtype=float: np.asarray(a, dtype=dtype)
import motmetrics as mm
sys.path.insert(0, '/root/exp/trk')
from sortcore import KalmanBoxTracker, associate_detections_to_trackers
from run_mot import load_dets, evaluate, SEQS, NoMotionTracker

def track(seq, k=1, drop=0.0, seed=0, motion=True, memory=15, min_hits=3, iou_thr=0.3, coast=0):
    dets, nF = load_dets(seq); rng = np.random.default_rng(seed)
    T = KalmanBoxTracker if motion else NoMotionTracker; KalmanBoxTracker.count = 0
    tracks, rows = [], []
    rounds = max(1, math.ceil(memory / k))
    for f in range(1, nF + 1):
        pred = [t.predict()[0] for t in tracks]
        if (f - 1) % k == 0:
            D = dets.get(f, np.empty((0, 5)))
            if drop > 0 and len(D): D = D[rng.random(len(D)) >= drop]
            P = np.array([[*p[:4], 0] for p in pred]) if pred else np.empty((0, 5))
            m, ud, ut = associate_detections_to_trackers(D, P, iou_thr)
            for di, ti in m: tracks[ti].update(D[di]); tracks[ti].missed = 0
            for ti in ut: tracks[ti].missed = getattr(tracks[ti], 'missed', 0) + 1
            for di in ud:
                t = T(D[di]); t.missed = 0; t.hits = 1; tracks.append(t)
            tracks = [t for t in tracks if t.missed <= rounds]
        for t in tracks:
            if t.hits >= min_hits and t.missed <= coast:
                x1, y1, x2, y2 = t.get_state()[0][:4]; rows.append([f, t.id + 1, x1, y1, x2 - x1, y2 - y1])
    return rows

mh = mm.metrics.create(); M = ['mota', 'idf1', 'num_switches', 'num_false_positives', 'num_misses', 'num_fragmentations']
def score(**kw):
    accs, ex = [], []
    for s in SEQS:
        a, e = evaluate(s, track(s, **kw)); accs.append(a); ex.append(e)
    r = mh.compute_many(accs, names=SEQS, metrics=M, generate_overall=True).loc['OVERALL']
    no = sum(e['n_occ'] for e in ex); nv = sum(e['n_vis'] for e in ex)
    d = {m: float(r[m]) for m in M}
    d['recall_occ'] = sum(e['recall_occ'] * e['n_occ'] for e in ex) / no; d['recall_vis'] = sum(e['recall_vis'] * e['n_vis'] for e in ex) / nv
    return d

if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'coast':
    res = json.load(open('/root/results/mot/more_mot.json')); res['dropout_coast'] = {}
    for p in (0.0, 0.1, 0.2, 0.3, 0.5):
        for motion in (True, False):
            rs = [score(drop=p, seed=s, motion=motion, coast=3) for s in range(5 if p > 0 else 1)]
            agg = {m: [float(np.mean([r[m] for r in rs])), float(np.std([r[m] for r in rs]))] for m in rs[0]}
            res['dropout_coast'][f'{p}|{"kalman" if motion else "none"}'] = agg
            print('coast drop', p, motion, {a: round(b[0], 3) for a, b in agg.items()}, flush=True)
    json.dump(res, open('/root/results/mot/more_mot.json', 'w'), indent=1); sys.exit()
res = {'stride': {}, 'dropout': {}}
for k in (1, 2, 4, 8):
    for motion in (True, False):
        r = score(k=k, motion=motion); res['stride'][f'{k}|{"kalman" if motion else "none"}'] = r
        print('stride', k, motion, {a: round(b, 3) for a, b in r.items()}, flush=True)
for p in (0.0, 0.1, 0.2, 0.3, 0.5):
    for motion in (True, False):
        rs = [score(drop=p, seed=s, motion=motion) for s in range(5 if p > 0 else 1)]
        agg = {m: [float(np.mean([r[m] for r in rs])), float(np.std([r[m] for r in rs]))] for m in rs[0]}
        res['dropout'][f'{p}|{"kalman" if motion else "none"}'] = agg
        print('drop', p, motion, {a: round(b[0], 3) for a, b in agg.items()}, flush=True)
json.dump(res, open('/root/results/mot/more_mot.json', 'w'), indent=1)
print('DONE')
