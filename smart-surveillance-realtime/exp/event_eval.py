import sys, numpy as np, json, itertools
sys.path.insert(0, '/root/exp')
from common import VIDEOS, video_info
from gt_events import frame_labels, EVENTS
MS = '/root/results/motion_scores/{}_{}.npz'; DS = '/root/results/det_scores/{}_{}_{}.npy'
PRE, POST, WARM = 1.0, 2.0, 2.0
MOTION = ['FD', 'FLOW', 'MOG2', 'KNN', 'CNT', 'GSOC']

def load(name, kind, det='yolo11n'):
    z = np.load(MS.format(name, kind)); S = {k: z[k] for k in MOTION}
    try: S['DET:'+det] = np.load(DS.format(det, name, kind))
    except FileNotFoundError: pass
    return S

def record(trig, fps):
    n = len(trig); rec = np.zeros(n, bool); idx = np.where(trig)[0]
    a, b = int(round(POST*fps)), int(round(PRE*fps))
    for u in idx: rec[max(0, u-b):min(n, u+a+1)] = True
    return rec

def metrics(rec, name, fps):
    n = len(rec); lab, valid = frame_labels(name, fps, n)
    valid = valid & (np.arange(n) >= WARM*fps)
    t = np.arange(n)/fps; ev = []
    for a, b in EVENTS[name]:
        m = (t >= a-0.5) & (t <= b+0.5) & valid
        ev.append(rec[m].mean() if m.any() else 1.0)
    return dict(stored=rec.mean(), frame_recall=rec[lab & valid].mean() if (lab & valid).any() else np.nan,
                idle_kept=rec[~lab & valid].mean() if (~lab & valid).any() else np.nan,
                ev_cov=np.array(ev), n_active=(lab & valid).sum(), n_idle=(~lab & valid).sum(), active_frac=lab.mean())

def trig_single(S, key, thr, fps):
    return S[key] > thr
def trig_hybrid(S, gkey, gthr, dkey, dthr, fps):
    gate = S[gkey] > gthr
    return gate & (S[dkey] > dthr), gate.mean()
def trig_stride(S, dkey, dthr, k):
    s = S[dkey]; tr = np.zeros(len(s), bool)
    for i in range(0, len(s), k): tr[i:i+k] = s[i] > dthr
    return tr

def pooled(results):
    """Pool frame-level metrics across videos (weighted by frames)."""
    stored = sum(r['stored']*r['n'] for r in results)/sum(r['n'] for r in results)
    fr = sum(r['frame_recall']*r['n_active'] for r in results if r['n_active'])/sum(r['n_active'] for r in results)
    idle = sum(r['idle_kept']*r['n_idle'] for r in results if r['n_idle'])/sum(r['n_idle'] for r in results)
    cov = np.concatenate([r['ev_cov'] for r in results])
    return dict(stored=stored, frame_recall=fr, idle_kept=idle, ev_full=(cov >= 0.9).mean(), ev_hit=(cov > 0).mean(), n_events=len(cov))
