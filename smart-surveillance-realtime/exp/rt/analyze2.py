"""Second-stage real-time analysis: (1) load of motion-gated hybrids vs. strided detector, (2) wall-clock validation summary."""
import sys, json, re, numpy as np
sys.path.insert(0, '/root/exp')
import event_eval as EV, event_analysis as EA
from event_analysis import VIDS, FPS, load
R = '/root/results/rt/'; A = json.load(open(R + 'analysis.json')); TH = A['theta']
LM = np.load(R + 'lat_motion.npz'); LD = np.load(R + 'lat_det.npz'); out = {}
def fifo(release, service):
    fin = np.empty(len(release)); t = 0.0
    for i in range(len(release)):
        t = max(t, release[i]) + service[i]; fin[i] = t
    return fin - release
# ---- 1  hybrids: per-frame job = gate (+ detector if the gate is open); deadline T
THR = json.load(open('/root/results/event_thresholds.json'))
def parse(s): return [float(x) for x in re.findall(r'float64\(([^)]+)\)', s)]
out['hybrid'] = {}
for g in ['MOG2', 'CNT', 'FD']:
    th = {v: parse(s) for v, s in THR[f'Hybrid: {g} gate + detector']}
    for kind in ['clean', 'jitter', 'illum']:
        miss = []; srv_all = []; open_all = []; burst = 0
        for v in VIDS:
            S = load(v, kind); n = min(len(S[g]), len(LD[f'lat|640|1|{v}'])); gate = S[g][:n] > th[v][0]
            srv = LM[f'{g}|{v}'][:n] + gate * LD[f'lat|640|1|{v}'][:n]; T = 1 / FPS[v]; r = fifo(np.arange(n) * T, srv)
            miss.append(r[10:] > T); srv_all.append(srv[10:]); open_all.append(gate)
            run = 0
            for x in gate:
                run = run + 1 if x else 0; burst = max(burst, run)
        s = np.concatenate(srv_all)
        out['hybrid'][f'{g}|{kind}'] = dict(miss=100 * float(np.concatenate(miss).mean()), mean_ms=1e3 * s.mean(), p99_ms=1e3 * np.percentile(s, 99), max_ms=1e3 * s.max(),
                                            gate_open=100 * float(np.concatenate(open_all).mean()), longest_open_run=int(burst), util=float(np.mean([s.mean() * 12])))
        print('hybrid', g, kind, {k: round(x, 2) for k, x in out['hybrid'][f'{g}|{kind}'].items()}, flush=True)
# every-frame detector and per-frame motion triggers at the clips' native rates (10-12.5 fps)
out['native'] = {}
for name, key in [('Detector 640 px', lambda v: LD[f'lat|640|1|{v}']), ('Detector 640 px, 2 threads', lambda v: LD[f'lat|640|2|{v}']), ('Detector 320 px', lambda v: LD[f'lat|320|1|{v}'])] + [(m, (lambda v, m=m: LM[f'{m}|{v}'])) for m in ['FD', 'CNT', 'MOG2', 'KNN', 'FLOW', 'GSOC']]:
    miss = np.concatenate([(fifo(np.arange(len(key(v))) / FPS[v], key(v)) > 1 / FPS[v])[10:] for v in VIDS]); out['native'][name] = 100 * float(miss.mean())
print('native', {k: round(x, 2) for k, x in out['native'].items()})
# ---- 2  wall-clock validation
try: L = json.load(open(R + 'live.json'))
except FileNotFoundError: L = None
if L:
    def summ(rec):
        x = np.array([r['resp'] for r in rec]); s = np.array([r['service'] for r in rec])
        return dict(jobs=len(rec), miss=100 * float(np.mean([r['miss'] for r in rec])), resp_mean=1e3 * x.mean(), resp_p50=1e3 * np.percentile(x, 50), resp_p95=1e3 * np.percentile(x, 95),
                    resp_p99=1e3 * np.percentile(x, 99), resp_max=1e3 * x.max(), service_mean=1e3 * s.mean(), service_p99=1e3 * np.percentile(s, 99), service_max=1e3 * s.max(),
                    min_slack_ms=1e3 * float(min(r['deadline'] - r['resp'] for r in rec)))
    out['live_single'] = {}; CMAX = max(LD[f'lat|640|1|{v}'].max() for v in VIDS)
    def kidle_rt(fps, pre=1.0): return max(1, int(np.floor(pre * fps + 1e-9)))
    KI = {'Fixed stride 8': lambda fps: 8, 'Adaptive 16/8': lambda fps: 16, 'Adaptive, deadline-aware': kidle_rt}
    KA = {'Fixed stride 8': lambda fps: 8, 'Adaptive 16/8': lambda fps: 8, 'Adaptive, deadline-aware': lambda fps: min(8, kidle_rt(fps))}
    def onsets(s, thr, fps):
        on = s > thr; W = int(round(fps)); o = []
        for j in range(max(W, int(2 * fps)), len(s) - 16):
            if on[j] and not on[j - W:j].any() and on[j:j + 16].all(): o.append(j)
        return o
    for pname, rec in L['single'].items():
        d = summ(rec); agree = []; delays = []; bounds = []; stored = []
        for v in VIDS:
            s = load(v, 'clean')['DET:yolo11n']; fps = FPS[v]; T = 1 / fps; rv = [r for r in rec if r['clip'] == v]
            agree += [bool(r['pos']) == bool(s[r['frame']] > TH[v]) for r in rv]
            # trace plan must visit the same frames
            for j in onsets(s, TH[v], fps):
                c = [r for r in rv if r['frame'] >= j and r['pos']]
                if not c: continue
                r0 = c[0]; delays.append(r0['finish'] - (r0['release'] - (r0['frame'] - j) * T)); bounds.append((KI[pname](fps) - 1) * T + CMAX); stored.append(r0['frame'] - j <= int(round(1.0 * fps)))
        d.update(agree=100 * float(np.mean(agree)), onsets=len(delays), delay_median=float(np.median(delays)), delay_max=float(np.max(delays)), bound_max=float(np.max(bounds)),
                 within_bound=100 * float(np.mean(np.array(delays) <= np.array(bounds))), onset_stored=100 * float(np.mean(stored)),
                 calls=100 * len(rec) / sum(len(load(v, 'clean')['DET:yolo11n']) for v in VIDS))
        out['live_single'][pname] = d; print('live', pname, {k: (round(x, 2) if isinstance(x, float) else x) for k, x in d.items()}, flush=True)
    out['live_multi'] = {k: summ(v['rec']) | dict(util=v['summary']['util']) for k, v in L['multi'].items()}
    for k, v in out['live_multi'].items(): print('live multi', k, {a: round(b, 2) for a, b in v.items()})
    out['cmax_profile_ms'] = 1e3 * float(CMAX)
json.dump(out, open(R + 'analysis2.json', 'w'), indent=1, default=float); print('DONE')
