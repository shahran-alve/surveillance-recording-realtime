"""Extended event-recording experiments, all on cached per-frame scores, leave-one-video-out thresholds.
E1 stride sweep; E2 adaptive stride; E3 OR-fusion of detector and motion; E4 m-of-n persistence for motion triggers;
E5 pre/post-roll ablation; E6 oracle (per-scene) vs transferred thresholds."""
import sys, json, numpy as np
sys.path.insert(0, '/root/exp')
import event_eval as EV
from event_analysis import *
KINDS = ('clean', 'illum', 'jitter', 'noise')
DK = 'DET:yolo11n'
OUT = '/root/results/more_events.json'
res = {}

def save(): json.dump(res, open(OUT, 'w'), indent=1, default=float)

def row(name, cands, kinds=KINDS):
    r, chosen = lovo(name, cands, kinds=kinds)
    out = {k: {m: float(v) for m, v in r[k][0].items() if not isinstance(v, str)} for k in kinds}
    print(name, {k: (round(out[k]['idle_kept'], 3), round(out[k]['frame_recall'], 3), round(out[k]['det_calls'], 3)) for k in kinds}, flush=True)
    return out

def adaptive(S, thr, k_idle, k_act):
    """Adaptive stride: run the detector every k_idle frames while nothing is detected, every k_act frames while an object is present."""
    s = S[DK]; n = len(s); tr = np.zeros(n, bool); i = 0; calls = 0
    while i < n:
        pos = s[i] > thr; calls += 1; k = k_act if pos else k_idle
        tr[i:i + k] = pos; i += k
    return tr, calls / n

def persist(x, m, n):
    """Fire at t only if the raw trigger fired in at least m of the last n frames."""
    c = np.convolve(x.astype(int), np.ones(n, int))[:len(x)]
    return c >= m

