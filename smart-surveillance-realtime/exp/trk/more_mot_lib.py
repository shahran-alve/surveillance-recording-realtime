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

