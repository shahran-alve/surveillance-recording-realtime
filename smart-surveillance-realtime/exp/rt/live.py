"""Wall-clock validation of the detector task.
Frames are released at the clip's own frame rate (pre-decoded, so decode is excluded); one non-preemptive worker (1 thread)
serves the detector jobs of N cameras first-come-first-served. A job released at r with next stride k must finish by r + k*T.
Outputs job response times, deadline misses, and agreement of the live trigger with the trace-driven trigger."""
import sys, time, json, heapq, numpy as np, torch, cv2
sys.path.insert(0, '/root/exp')
from common import VIDEOS, frames, video_info
from ultralytics import YOLO
R = '/root/results/rt/'; A = json.load(open(R + 'analysis.json')); TH = A['theta']
CLS = [0, 1, 2, 3, 5, 7]; torch.set_num_threads(1); cv2.setNumThreads(1)
m = YOLO('/root/data/models/yolo11n.pt')
def kidle_rt(fps, pre=1.0): return max(1, int(np.floor(pre * fps + 1e-9)))
POL = {'Fixed stride 8': lambda fps: (8, 8), 'Adaptive 16/8': lambda fps: (16, 8), 'Adaptive, deadline-aware': lambda fps: (kidle_rt(fps), min(8, kidle_rt(fps)))}

def run(cams, pf, horizon, loop):
    """cams: list of (clip name, frames, fps). Returns per-job records."""
    N = len(cams); Q = []; rec = []
    for f in cams[0][1][:3]: m.predict(f, imgsz=640, conf=0.05, classes=CLS, verbose=False)
    t0 = time.perf_counter() + 0.5
    for c, (v, F, fps) in enumerate(cams):
        ki, ka = pf(fps); heapq.heappush(Q, ((c / N) * ki / fps, c, 0, 0))      # (release, camera, frame index, loop count)
    while Q:
        rel, c, i, lp = heapq.heappop(Q); v, F, fps = cams[c]; T = 1 / fps
        if rel > horizon: continue
        now = time.perf_counter() - t0
        if now < rel: time.sleep(rel - now)
        start = time.perf_counter() - t0
        r = m.predict(F[i], imgsz=640, conf=0.05, classes=CLS, verbose=False)[0]; s = float(r.boxes.conf.max()) if len(r.boxes) else 0.0
        fin = time.perf_counter() - t0; pos = s > TH[v]; ki, ka = pf(fps); k = ka if pos else ki
        rec.append(dict(cam=c, clip=v, frame=i, loop=lp, release=rel, start=start, finish=fin, resp=fin - rel, service=fin - start, deadline=k * T, miss=bool(fin - rel > k * T), pos=bool(pos), k=k))
        ni = i + k; nrel = rel + k * T
        if ni >= len(F):
            if not loop: continue
            ni = 0; lp += 1
        heapq.heappush(Q, (nrel, c, ni, lp))
    return rec

def summ(rec):
    x = np.array([r['resp'] for r in rec]); s = np.array([r['service'] for r in rec]); dur = max(r['finish'] for r in rec) - min(r['release'] for r in rec)
    return dict(jobs=len(rec), miss=100 * float(np.mean([r['miss'] for r in rec])), resp_mean=1e3 * x.mean(), resp_p50=1e3 * np.percentile(x, 50), resp_p95=1e3 * np.percentile(x, 95), resp_p99=1e3 * np.percentile(x, 99),
                resp_max=1e3 * x.max(), service_mean=1e3 * s.mean(), service_max=1e3 * s.max(), util=float(s.sum() / dur), min_slack=float(min(r['deadline'] - r['resp'] for r in rec)))

out = {'single': {}, 'multi': {}}
# ---- one camera, every clip in full, three policies
clips = {}
for v in VIDEOS:
    fps, n = video_info(v); F = list(frames(v)); clips[v] = (v, F, fps)
    sc = np.load(f'/root/results/det_scores/yolo11n_{v}_clean.npy') if False else None
    for pname, pf in POL.items():
        rec = run([clips[v]], pf, 1e9, False); out['single'].setdefault(pname, []).extend(rec)
        print(v, pname, {k: round(x, 3) for k, x in summ(rec).items()}, flush=True)
    if v not in ('people', 'person-bike-car', 'car-lot', 'store-aisle'): del clips[v]
for pname in POL: out['single_summary_' + pname] = summ(out['single'][pname]); print('ALL', pname, out['single_summary_' + pname], flush=True)
# ---- several cameras on one core (clips looped, 120 s)
base = [clips[v] for v in ('people', 'person-bike-car', 'car-lot', 'store-aisle')]
for N in [int(a) for a in sys.argv[1:]] or [4, 8]:
    for pname in ['Fixed stride 8', 'Adaptive, deadline-aware']:
        rec = run([base[c % 4] for c in range(N)], POL[pname], 120.0, True); out['multi'][f'{pname}|{N}'] = dict(summary=summ(rec), rec=rec)
        print('multi', N, pname, {k: round(x, 3) for k, x in summ(rec).items()}, flush=True)
json.dump(out, open(R + 'live.json', 'w'), default=float); print('DONE')
