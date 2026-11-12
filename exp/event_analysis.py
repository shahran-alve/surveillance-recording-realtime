import sys, json, numpy as np, pandas as pd
sys.path.insert(0, '/root/exp')
from event_eval import *
VIDS = list(VIDEOS); TARGET = 0.95
MGRID = np.concatenate([[0], np.logspace(-5, -0.5, 46)]); DGRID = np.round(np.arange(0.05, 0.96, 0.05), 2)
FPS = {v: video_info(v)[0] for v in VIDS}
def methods(det='yolo11n'):
    M = {}
    for k in MOTION: M[k] = [((lambda S, k=k, t=t: (S[k] > t, None)), t) for t in MGRID]
    dk = 'DET:'+det
    M['Detector (every frame)'] = [((lambda S, t=t: (S[dk] > t, 1.0)), t) for t in DGRID]
    for k in (2, 4, 8):
        M[f'Detector (every {k}th frame)'] = [((lambda S, t=t, k=k: (trig_stride(S, dk, t, k), 1.0/k)), t) for t in DGRID]
    for g in ('MOG2', 'CNT', 'FD'):
        M[f'Hybrid: {g} gate + detector'] = [((lambda S, gt=gt, t=t, g=g: ((S[g] > gt) & (S[dk] > t), (S[g] > gt).mean())), (gt, t))
                                    for gt in MGRID[::2] for t in DGRID[::2]]
    return M
def evaluate_cfg(fn, kind, vids, det='yolo11n'):
    R = []; calls = []
    for v in vids:
        S = load(v, kind, det); trig, c = fn(S); rec = record(trig, FPS[v])
        r = metrics(rec, v, FPS[v]); r['n'] = len(rec); R.append(r); calls.append((c if c is not None else 0.0, len(rec)))
    p = pooled(R); p['det_calls'] = sum(c*n for c, n in calls)/sum(n for _, n in calls); return p, R
def select(cands, kind, vids, det):
    best = None
    for fn, th in cands:
        p, R = evaluate_cfg(fn, kind, vids, det)
        worst = min(r['frame_recall'] for r in R)  # every training scene must reach the recall target
        key = (worst >= TARGET, -p['stored'] if worst >= TARGET else worst)
        if best is None or key > best[0]: best = (key, fn, th)
    return best[1], best[2]
def lovo(name, cands, det='yolo11n', kinds=('clean',)):
    """Leave-one-video-out: threshold chosen on the other 6 clean videos, applied to the held-out video."""
    out = {k: [] for k in kinds}; chosen = []; calls = {k: [] for k in kinds}
    for v in VIDS:
        train = [u for u in VIDS if u != v]
        fn, th = select(cands, 'clean', train, det); chosen.append((v, th))
        for k in kinds:
            S = load(v, k, det); trig, c = fn(S); rec = record(trig, FPS[v]); r = metrics(rec, v, FPS[v]); r['n'] = len(rec); r['video'] = v
            out[k].append(r); calls[k].append((c if c is not None else 0.0, len(rec)))
    res = {}
    for k in kinds:
        p = pooled(out[k]); p['det_calls'] = sum(c*n for c, n in calls[k])/sum(n for _, n in calls[k]); p['method'] = name; p['kind'] = k; res[k] = (p, out[k])
    return res, chosen
if __name__ == '__main__':
    kinds = tuple(sys.argv[1].split(',')) if len(sys.argv) > 1 else ('clean',)
    rows, per_video, thresholds = [], [], {}
    for name, cands in methods().items():
        res, chosen = lovo(name, cands, kinds=kinds); thresholds[name] = [(v, str(t)) for v, t in chosen]
        for k, (p, R) in res.items():
            rows.append(p)
            for r in R: per_video.append(dict(method=name, kind=k, video=r['video'], stored=r['stored'], frame_recall=r['frame_recall'], idle_kept=r['idle_kept'], ev_full=(r['ev_cov'] >= 0.9).mean()))
        print(name, {k: {m: round(float(x), 3) for m, x in p.items() if not isinstance(x, str)} for k, (p, _) in res.items()}, flush=True)
    pd.DataFrame(rows).to_csv('/root/results/event_lovo.csv', index=False)
    pd.DataFrame(per_video).to_csv('/root/results/event_lovo_per_video.csv', index=False)
    json.dump(thresholds, open('/root/results/event_thresholds.json', 'w'), indent=1)
