"""Real-time analysis from measured per-frame service times (measure_motion.py, measure_det.py).
A  latency distributions and per-frame deadline misses (FIFO, single worker)
B  schedulability of the strided / adaptive detector task and CPU utilisation per camera
C  timing guarantee: alert-delay bound and onset coverage, checked on detectable onsets
D  cameras per core (trace-driven FIFO simulation)
E  lower-resolution detector as trigger (storage / recall, LOVO)"""
import sys, json, numpy as np
import os; ROOT = os.environ.get('SS_ROOT', '/root')
sys.path.insert(0, ROOT + '/exp')
import event_eval as EV, event_analysis as EA
from event_analysis import VIDS, FPS, DGRID, load, record, metrics, pooled, trig_stride
from gt_events import EVENTS
R = ROOT + '/results/rt/'; res = {}
LM = np.load(R + 'lat_motion.npz'); LD = np.load(R + 'lat_det.npz')
WARM = 10
def pool(key_fn): return np.concatenate([key_fn(v)[WARM:] for v in VIDS])
COMP = {'FD': lambda v: LM[f'FD|{v}'], 'CNT': lambda v: LM[f'CNT|{v}'], 'MOG2': lambda v: LM[f'MOG2|{v}'], 'KNN': lambda v: LM[f'KNN|{v}'],
        'Optical flow': lambda v: LM[f'FLOW|{v}'], 'GSOC': lambda v: LM[f'GSOC|{v}'],
        'Detector 320 px': lambda v: LD[f'lat|320|1|{v}'], 'Detector 480 px': lambda v: LD[f'lat|480|1|{v}'],
        'Detector 640 px': lambda v: LD[f'lat|640|1|{v}'], 'Detector 640 px, 2 threads': lambda v: LD[f'lat|640|2|{v}']}

def fifo(release, service):
    """Single non-preemptive worker, FIFO. Returns response times."""
    fin = np.empty(len(release)); t = 0.0
    for i in range(len(release)):
        t = max(t, release[i]) + service[i]; fin[i] = t
    return fin - release

# ---------------- A
res['latency'] = {}
for name, fn in COMP.items():
    x = pool(fn); r = dict(n=len(x), mean=1e3 * x.mean(), p50=1e3 * np.percentile(x, 50), p95=1e3 * np.percentile(x, 95), p99=1e3 * np.percentile(x, 99), max=1e3 * x.max())
    for fps in (12, 15, 30):
        T = 1.0 / fps; miss = []; over = []
        for v in VIDS:
            s = fn(v)[WARM:]; resp = fifo(np.arange(len(s)) * T, s); miss.append(resp > T); over.append(s > T)
        r[f'miss{fps}'] = 100 * float(np.concatenate(miss).mean()); r[f'over{fps}'] = 100 * float(np.concatenate(over).mean()); r[f'util{fps}'] = float(x.mean() * fps)
    res['latency'][name] = r
    print(name, {k: round(v, 2) for k, v in r.items()}, flush=True)

# ---------------- B  strided detector as a periodic task with period k*T
res['sched'] = {}
for name in ['Detector 320 px', 'Detector 480 px', 'Detector 640 px', 'Detector 640 px, 2 threads']:
    x = pool(COMP[name]); r = {}
    for fps in (12, 15, 30):
        r[f'kmin{fps}'] = int(np.ceil(x.max() * fps)); r[f'kmin_p99_{fps}'] = int(np.ceil(np.percentile(x, 99) * fps))
        for k in (1, 2, 4, 8, 16): r[f'util{fps}_k{k}'] = float(x.mean() * fps / k)
    res['sched'][name] = r; print('sched', name, r, flush=True)

# ---------------- thresholds (LOVO, fixed stride 8) reused for the timing analysis
DK = 'DET:yolo11n'
C8 = [((lambda S, t=t: (trig_stride(S, DK, t, 8), 1 / 8)), t) for t in DGRID]
TH = {v: EA.select(C8, 'clean', [u for u in VIDS if u != v], 'yolo11n')[1] for v in VIDS}
res['theta'] = {v: float(t) for v, t in TH.items()}

def sample_plan(s, thr, k_idle, k_act):
    """Frames on which the detector runs and its decisions (adaptive stride; fixed stride when k_idle == k_act)."""
    idx, pos, nxt = [], [], []; i = 0; n = len(s)
    while i < n:
        p = bool(s[i] > thr); k = k_act if p else k_idle; idx.append(i); pos.append(p); nxt.append(k); i += k
    return np.array(idx), np.array(pos), np.array(nxt)

def trig_from_plan(n, idx, pos, nxt):
    tr = np.zeros(n, bool)
    for i, p, k in zip(idx, pos, nxt): tr[i:i + k] = p
    return tr

def kidle_rt(fps, pre): return max(1, int(np.floor(pre * fps + 1e-9)))

# ---------------- C  timing guarantee on detectable onsets
P_PERSIST = 16
def onsets(s, thr, fps):
    on = s > thr; W = int(round(fps)); out = []
    for j in range(max(W, int(2 * fps)), len(s) - P_PERSIST):
        if on[j] and not on[j - W:j].any() and on[j:j + P_PERSIST].all(): out.append(j)
    return out
POL = {'Fixed stride 8': lambda fps, pre: (8, 8), 'Fixed stride 16': lambda fps, pre: (16, 16), 'Adaptive 16/8': lambda fps, pre: (16, 8),
       'Adaptive, deadline-aware': lambda fps, pre: (kidle_rt(fps, pre), min(8, kidle_rt(fps, pre))), 'Every frame': lambda fps, pre: (1, 1)}
res['timing'] = {}
for pre in (1.0, 1.5):
    for pname, pf in POL.items():
        D, cov, bound_ok, bounds, slack = [], [], [], [], []
        for v in VIDS:
            fps = FPS[v]; T = 1 / fps; S = load(v, 'clean'); s = S[DK]; lat = LD[f'lat|640|1|{v}']; n = min(len(s), len(lat)); s = s[:n]
            ki, ka = pf(fps, pre); idx, pos, nxt = sample_plan(s, TH[v], ki, ka); tr = trig_from_plan(n, idx, pos, nxt)
            EV.PRE = pre; EA.PRE = pre; rec = record(tr, fps); EV.PRE = 1.0
            Rmax = lat[idx].max(); B = (ki - 1) * T + Rmax
            for j in onsets(s, TH[v], fps):
                m = np.where((idx >= j) & pos)[0]
                if not len(m): continue
                i = idx[m[0]]; d = (i - j) * T + lat[i]; D.append(d); cov.append(bool(rec[j])); bound_ok.append(d <= B + 1e-9); bounds.append(B); slack.append(B - d)
        D = np.array(D)
        res['timing'][f'{pname}|{pre}'] = dict(n=len(D), median=float(np.median(D)), p95=float(np.percentile(D, 95)), max=float(D.max()), onset_stored=100 * float(np.mean(cov)),
                                               within_bound=100 * float(np.mean(bound_ok)), bound_max=float(np.max(bounds)), bound_min=float(np.min(bounds)), delays=D.tolist())
        print('timing', pname, pre, {k: (round(x, 3) if isinstance(x, float) else x) for k, x in res['timing'][f'{pname}|{pre}'].items() if k != 'delays'}, flush=True)

# storage / recall / detector calls of the policies (LOVO thresholds chosen per policy, clean + perturbed)
def lovo_policy(pf, pre=1.0, det='yolo11n', kinds=('clean', 'jitter', 'illum')):
    dk = 'DET:' + det; out = {}
    def mk(t):
        def fn(S, t=t):
            v = S['_v']; ki, ka = pf(FPS[v], pre); idx, pos, nxt = sample_plan(S[dk], t, ki, ka); return trig_from_plan(len(S[dk]), idx, pos, nxt), len(idx) / len(S[dk])
        return fn
    cands = [(mk(t), t) for t in DGRID]
    def ev(fn, kind, vids):
        Rr, calls = [], []
        for v in vids:
            S = load(v, kind, det); S['_v'] = v; tr, c = fn(S); EV.PRE = pre; rec = record(tr, FPS[v]); EV.PRE = 1.0
            r = metrics(rec, v, FPS[v]); r['n'] = len(rec); Rr.append(r); calls.append((c, len(rec)))
        return Rr, calls
    chosen = {}
    for v in VIDS:
        best = None
        for fn, t in cands:
            Rr, _ = ev(fn, 'clean', [u for u in VIDS if u != v]); p = pooled(Rr); worst = min(r['frame_recall'] for r in Rr)
            key = (worst >= 0.95, -p['stored'] if worst >= 0.95 else worst)
            if best is None or key > best[0]: best = (key, fn, t)
        chosen[v] = best[1]
    for kind in kinds:
        Rr, calls = [], []
        for v in VIDS:
            try: a, b = ev(chosen[v], kind, [v])
            except (FileNotFoundError, KeyError): Rr = None; break
            Rr += a; calls += b
        if Rr is None: continue
        p = pooled(Rr); out[kind] = dict(stored=100 * p['stored'], recall=100 * p['frame_recall'], idle=100 * p['idle_kept'], events=int(round(p['ev_full'] * p['n_events'])),
                                         calls=100 * sum(c * n for c, n in calls) / sum(n for _, n in calls))
    return out
res['policy'] = {}
for pname, pf in POL.items():
    for pre in ((1.0, 1.5) if pname == 'Adaptive 16/8' else (1.0,)):
        res['policy'][f'{pname}|{pre}'] = lovo_policy(pf, pre); print('policy', pname, pre, {k: {a: round(b, 1) for a, b in v.items()} for k, v in res['policy'][f'{pname}|{pre}'].items()}, flush=True)

# ---------------- E  lower-resolution detector as trigger (fixed stride 8)
res['lowres'] = {}
for det in ['yolo11n320', 'yolo11n480']:
    res['lowres'][det] = lovo_policy(POL['Fixed stride 8'], 1.0, det); print('lowres', det, res['lowres'][det], flush=True)
    res['lowres'][det + '|da'] = lovo_policy(POL['Adaptive, deadline-aware'], 1.0, det); print('lowres da', det, res['lowres'][det + '|da'], flush=True)


# ---------------- F  annotated-event onset delay for the policies (threshold: LOVO stride-8 threshold TH), incl. measured response time
res['onset_events'] = {}
for pre in (1.0, 1.5):
    for pname, pf in POL.items():
        delays, covered = [], []
        for v in VIDS:
            fps = FPS[v]; s = load(v, 'clean')[DK]; lat = LD[f'lat|640|1|{v}']; n = min(len(s), len(lat)); ki, ka = pf(fps, pre)
            idx, pos, nxt = sample_plan(s[:n], TH[v], ki, ka); tr = trig_from_plan(n, idx, pos, nxt); EV.PRE = pre; rec = record(tr, fps); EV.PRE = 1.0; t = np.arange(n) / fps
            for a, b in EVENTS[v]:
                if a < 2.0: continue
                m = np.where(pos & (t[idx] >= a - 0.5) & (t[idx] <= b + 0.5))[0]
                delays.append((t[idx[m[0]]] - (a - 0.5) + lat[idx[m[0]]]) if len(m) else np.nan)
                covered.append(bool(rec[min(int(round((a + 0.5) * fps)), n - 1)]))
        d = np.array(delays, float)
        res['onset_events'][f'{pname}|{pre}'] = dict(n=len(d), missed=int(np.isnan(d).sum()), median=float(np.nanmedian(d)), p90=float(np.nanpercentile(d, 90)), max=float(np.nanmax(d)),
                                                    within_pre=100 * float(np.mean(np.nan_to_num(d, nan=99) <= pre)), start_recorded=100 * float(np.mean(covered)))
        print('onset_events', pname, pre, res['onset_events'][f'{pname}|{pre}'], flush=True)

# ---------------- G  sensitivity to the sampling phase (fixed thresholds TH; the first sample falls on frame o)
res['phase'] = {}
for pname, pf in POL.items():
    if pname == 'Every frame': continue
    rows = []
    for o in range(8):
        Rr = []; calls = 0; tot = 0
        for v in VIDS:
            fps = FPS[v]; s = load(v, 'clean')[DK]; n = len(s); ki, ka = pf(fps, 1.0); idx, pos, nxt = sample_plan(s[o:], TH[v], ki, ka)
            tr = np.zeros(n, bool); tr[o:] = trig_from_plan(n - o, idx, pos, nxt); rec = record(tr, fps); r = metrics(rec, v, fps); r['n'] = n; Rr.append(r); calls += len(idx); tot += n
        p = pooled(Rr); rows.append((100 * p['frame_recall'], 100 * p['idle_kept'], 100 * p['stored'], round(p['ev_full'] * p['n_events']), 100 * calls / tot))
    a = np.array(rows, float); res['phase'][pname] = dict(mean=a.mean(0).tolist(), min=a.min(0).tolist(), max=a.max(0).tolist())
    print('phase', pname, np.round(a.mean(0), 1), np.round(a.min(0), 1), np.round(a.max(0), 1), flush=True)

# ---------------- D  cameras per core: trace-driven FIFO simulation, cameras cycle through the clips with staggered phases
THD = {'yolo11n': TH}
for det in ['yolo11n320', 'yolo11n480']:
    Cd = [((lambda S, t=t, det=det: (trig_stride(S, 'DET:' + det, t, 8), 1 / 8)), t) for t in DGRID]
    THD[det] = {v: EA.select(Cd, 'clean', [u for u in VIDS if u != v], det)[1] for v in VIDS}
res['theta_lowres'] = {d: {v: float(t) for v, t in x.items()} for d, x in THD.items()}
def jobs_for_camera(c, N, pf, latkey, horizon, det='yolo11n'):
    v = VIDS[c % len(VIDS)]; fps = FPS[v]; T = 1 / fps; s = load(v, 'clean', det)['DET:' + det]; lat = LD[f'{latkey}|{v}']; n = min(len(s), len(lat))
    ki, ka = pf(fps, 1.0); idx, pos, nxt = sample_plan(s[:n], THD[det][v], ki, ka)
    rel, srv, ddl = [], [], []; t0 = (c / N) * ki * T; loop = 0
    while t0 + loop * n * T < horizon:
        base = t0 + loop * n * T
        rel += list(base + idx * T); srv += list(lat[idx]); ddl += list(nxt * T); loop += 1
    return np.array(rel), np.array(srv), np.array(ddl)
def cams(pf, latkey, horizon=600.0, nmax=60, det='yolo11n'):
    best = 0; detail = {}
    for N in range(1, nmax + 1):
        J = [jobs_for_camera(c, N, pf, latkey, horizon, det) for c in range(N)]
        rel = np.concatenate([j[0] for j in J]); srv = np.concatenate([j[1] for j in J]); ddl = np.concatenate([j[2] for j in J])
        o = np.argsort(rel, kind='stable'); rel, srv, ddl = rel[o], srv[o], ddl[o]; m = rel < horizon; rel, srv, ddl = rel[m], srv[m], ddl[m]
        resp = fifo(rel, srv); miss = float((resp > ddl).mean()); util = float(srv.sum() / horizon)
        detail[N] = dict(util=util, miss=100 * miss, resp_max=float(resp.max()), resp_p99=float(np.percentile(resp, 99)))
        if miss == 0: best = N
        if util > 1.2: break
    return best, detail
res['cameras'] = {}
for latkey, lname, det in [('lat|640|1', '640 px, 1 thread', 'yolo11n'), ('lat|640|2', '640 px, 2 threads', 'yolo11n'), ('lat|480|1', '480 px, 1 thread', 'yolo11n480'), ('lat|320|1', '320 px, 1 thread', 'yolo11n320')]:
    for pname in ['Every frame', 'Fixed stride 8', 'Adaptive 16/8', 'Adaptive, deadline-aware']:
        b, d = cams(POL[pname], latkey, det=det); res['cameras'][f'{pname}|{lname}'] = dict(nmax=b, at=d.get(b, {}), next=d.get(b + 1, {}), curve={str(n): x for n, x in d.items()})
        print('cameras', pname, lname, b, d.get(b), flush=True)
# per-frame motion triggers at 15 and 30 fps (every camera at the same rate)
def cams_motion(key, fps, horizon=60.0, nmax=200):
    T = 1 / fps; best = 0; lo, hi = 1, nmax
    S = np.concatenate([LM[f'{key}|{v}'][WARM:] for v in VIDS]); n = int(horizon * fps)
    def ok(N):
        rel = np.concatenate([np.arange(n) * T + (c / N) * T for c in range(N)]); srv = np.concatenate([np.roll(S, 997 * c)[:n] for c in range(N)])
        o = np.argsort(rel, kind='stable'); return bool((fifo(rel[o], srv[o]) <= T).all())
    while lo <= hi:
        mid = (lo + hi) // 2
        if ok(mid): best = mid; lo = mid + 1
        else: hi = mid - 1
    return best
res['cameras_motion'] = {f'{k}|{fps}': cams_motion(k, fps) for k in ['FD', 'CNT', 'MOG2', 'KNN'] for fps in (15, 30)}
print(res['cameras_motion'])
json.dump(res, open(R + 'analysis.json', 'w'), indent=1, default=float); print('DONE')
