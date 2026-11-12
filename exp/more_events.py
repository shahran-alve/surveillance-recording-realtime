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

# ---- E1 stride sweep
res['stride'] = {}
for k in (1, 2, 4, 8, 12, 16, 24, 32):
    c = [((lambda S, t=t, k=k: (trig_stride(S, DK, t, k), 1.0 / k)), t) for t in DGRID]
    res['stride'][k] = row(f'stride {k}', c); save()

# ---- E2 adaptive stride
res['adaptive'] = {}
for ki, ka in [(8, 16), (8, 32), (12, 24), (12, 48), (16, 32), (16, 64)]:
    c = [((lambda S, t=t, ki=ki, ka=ka: adaptive(S, t, ki, ka)), t) for t in DGRID]
    res['adaptive'][f'{ki}/{ka}'] = row(f'adaptive idle {ki} active {ka}', c); save()

# ---- E3 OR fusion (strided detector OR motion), thresholds chosen jointly
res['or'] = {}
for g in ('CNT', 'MOG2'):
    c = [((lambda S, gt=gt, t=t, g=g: (trig_stride(S, DK, t, 8) | (S[g] > gt), 1.0 / 8)), (gt, t)) for gt in MGRID[::3] for t in DGRID[::2]]
    res['or'][g] = row(f'stride-8 detector OR {g}', c); save()

# ---- E4 persistence filter for motion triggers
res['persist'] = {}
for key in ('FD', 'MOG2', 'CNT'):
    for m, n in [(3, 5), (6, 10)]:
        c = [((lambda S, t=t, key=key, m=m, n=n: (persist(S[key] > t, m, n), None)), t) for t in MGRID]
        res['persist'][f'{key} {m}/{n}'] = row(f'{key} persist {m}/{n}', c); save()

# ---- E5 buffer ablation (clean only)
res['buffer'] = {}
for pre, post in [(0, 0), (0, 2), (0.5, 1), (1, 1), (1, 2), (2, 3)]:
    EV.PRE, EV.POST = pre, post
    import event_analysis as EA; EA.PRE, EA.POST = pre, post
    for name, c in [('stride8', [((lambda S, t=t: (trig_stride(S, DK, t, 8), 1 / 8)), t) for t in DGRID]),
                    ('MOG2', [((lambda S, t=t: (S['MOG2'] > t, None)), t) for t in MGRID])]:
        res['buffer'][f'{name} {pre}/{post}'] = row(f'buffer {name} pre {pre} post {post}', c, kinds=('clean',))['clean']; save()
EV.PRE, EV.POST = 1.0, 2.0

# ---- E6 oracle threshold per scene vs LOVO
res['oracle'] = {}
for name, c in [('Detector (every 8th)', [((lambda S, t=t: (trig_stride(S, DK, t, 8), 1 / 8)), t) for t in DGRID]),
                ('MOG2', [((lambda S, t=t: (S['MOG2'] > t, None)), t) for t in MGRID]),
                ('CNT', [((lambda S, t=t: (S['CNT'] > t, None)), t) for t in MGRID]),
                ('FD', [((lambda S, t=t: (S['FD'] > t, None)), t) for t in MGRID])]:
    R = []
    for v in VIDS:
        fn, th = select(c, 'clean', [v], 'yolo11n')
        S = load(v, 'clean'); trig, _ = fn(S); rec = record(trig, FPS[v]); r = metrics(rec, v, FPS[v]); r['n'] = len(rec); R.append(r)
    p = pooled(R); res['oracle'][name] = {m: float(x) for m, x in p.items()}
    print('oracle', name, round(p['idle_kept'], 3), round(p['frame_recall'], 3), flush=True); save()
print('DONE')
