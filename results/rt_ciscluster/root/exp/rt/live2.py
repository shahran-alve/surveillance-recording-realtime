"""E2: wall-clock validation of the detector task with N cameras that cycle through ALL seven clips.
Extends live.py (which is kept unchanged): cameras use the same clip order (camera c -> VIDS[c % 7]), phase stagger
t0 = (c/N) * k_idle * T and loop restart (loop L starts at t0 + L*n*T, frame 0) as jobs_for_camera() in analyze.py, so a live run
and the trace-driven simulation release the same job sequence when the decisions agree. All three policies are supported.
Frames are pre-decoded (decode excluded); one non-preemptive worker (1 torch thread) serves jobs first-come-first-served;
a job released at r with next stride k must finish by r + k*T. The process is pinned to --core before torch/cv2 are imported.
ultralytics' thread reset (select_device -> torch.set_num_threads(min(8, cpu-1))) is neutralised: NUM_THREADS is patched and
torch.set_num_threads(--threads) is re-applied after the first (warm-up) predict.
Usage: multi:  python live2.py --policy "Fixed stride 8" --N 10 --horizon 600 --imgsz 640 --threads 1 --core 2 --out FILE.json
       single: python live2.py --single --imgsz 640 --threads 1 --core 2 --out FILE.json   (one camera, every clip once, 3 policies)"""
import sys, time, json, heapq, os, argparse, platform
ROOT = os.environ.get('SS_ROOT', '/root')
sys.path.insert(0, ROOT + '/exp')
ap = argparse.ArgumentParser(); ap.add_argument('--policy', default='Fixed stride 8'); ap.add_argument('--N', type=int, default=4); ap.add_argument('--horizon', type=float, default=600.0)
ap.add_argument('--imgsz', type=int, default=640); ap.add_argument('--threads', type=int, default=1); ap.add_argument('--core', type=int, default=2); ap.add_argument('--core2', type=int, default=4)
ap.add_argument('--single', action='store_true'); ap.add_argument('--out', required=True); ap.add_argument('--tag', default=''); a = ap.parse_args()
os.sched_setaffinity(0, {a.core} if a.threads == 1 else {a.core, a.core2})
import numpy as np, torch, cv2
import ultralytics.utils.torch_utils as tu; tu.NUM_THREADS = a.threads
from common import VIDEOS, frames, video_info
from ultralytics import YOLO
R = ROOT + '/results/rt/'; A = json.load(open(R + 'analysis.json')); TH = A['theta'] if a.imgsz == 640 else A['theta_lowres'][f'yolo11n{a.imgsz}']
DET = 'yolo11n' if a.imgsz == 640 else f'yolo11n{a.imgsz}'
CLS = [0, 1, 2, 3, 5, 7]; torch.set_num_threads(a.threads); cv2.setNumThreads(a.threads)
m = YOLO(ROOT + '/data/models/yolo11n.pt')
def kidle_rt(fps, pre=1.0): return max(1, int(np.floor(pre * fps + 1e-9)))
POL = {'Fixed stride 8': lambda fps: (8, 8), 'Adaptive 16/8': lambda fps: (16, 8), 'Adaptive, deadline-aware': lambda fps: (kidle_rt(fps), min(8, kidle_rt(fps)))}
VIDS = list(VIDEOS)
def steal(): return int(open('/proc/stat').readline().split()[8])
def freq(c):
    try: return int(open(f'/sys/devices/system/cpu/cpu{c}/cpufreq/scaling_cur_freq').read()) / 1e3
    except OSError: return None

def run(cams, pf, horizon, loop):
    """cams: list of (clip name, frames, fps). Returns per-job records. Loop restarts follow jobs_for_camera(): loop L starts at t0 + L*n*T."""
    N = len(cams); Q = []; rec = []
    for f in cams[0][1][:3]: m.predict(f, imgsz=a.imgsz, conf=0.05, classes=CLS, verbose=False)
    torch.set_num_threads(a.threads)                       # undo ultralytics' reset on the first predict (belt and braces)
    t0 = time.perf_counter() + 0.5
    for c, (v, F, fps) in enumerate(cams):
        ki, ka = pf(fps); heapq.heappush(Q, ((c / N) * ki / fps, c, 0, 0))      # (release, camera, frame index, loop count)
    while Q:
        rel, c, i, lp = heapq.heappop(Q); v, F, fps = cams[c]; T = 1 / fps; n = len(F)
        if rel >= horizon: continue
        now = time.perf_counter() - t0
        if now < rel: time.sleep(rel - now)
        start = time.perf_counter() - t0
        r = m.predict(F[i], imgsz=a.imgsz, conf=0.05, classes=CLS, verbose=False)[0]; s = float(r.boxes.conf.max()) if len(r.boxes) else 0.0
        fin = time.perf_counter() - t0; pos = s > TH[v]; ki, ka = pf(fps); k = ka if pos else ki
        rec.append(dict(cam=c, clip=v, frame=i, loop=lp, release=rel, start=start, finish=fin, resp=fin - rel, service=fin - start, deadline=k * T, miss=bool(fin - rel > k * T), pos=bool(pos), k=k, score=s))
        ni = i + k; nrel = rel + k * T
        if ni >= n:
            if not loop: continue
            lp += 1; ni = 0; nrel = (c / N) * ki * T + lp * n * T
        heapq.heappush(Q, (nrel, c, ni, lp))
    return rec

def summ(rec):
    x = np.array([r['resp'] for r in rec]); s = np.array([r['service'] for r in rec]); dur = max(r['finish'] for r in rec) - min(r['release'] for r in rec)
    return dict(jobs=len(rec), miss=100 * float(np.mean([r['miss'] for r in rec])), n_miss=int(sum(r['miss'] for r in rec)), resp_mean=1e3 * x.mean(), resp_p50=1e3 * np.percentile(x, 50), resp_p95=1e3 * np.percentile(x, 95),
                resp_p99=1e3 * np.percentile(x, 99), resp_max=1e3 * x.max(), service_mean=1e3 * s.mean(), service_p99=1e3 * np.percentile(s, 99), service_max=1e3 * s.max(), util=float(s.sum() / dur),
                min_slack=float(min(r['deadline'] - r['resp'] for r in rec)))

def agreement(rec):
    """Share of live decisions equal to the offline (trace) decision on the same frame, and max |score difference|."""
    off = {v: np.load(f'{ROOT}/results/det_scores/{DET}_{v}_clean.npy') for v in VIDS}; ag = []; dmax = 0.0
    for r in rec:
        so = float(off[r['clip']][r['frame']]); ag.append(bool(r['pos']) == bool(so > TH[r['clip']])); dmax = max(dmax, abs(so - r['score']))
    return dict(agree=100 * float(np.mean(ag)), n_disagree=int(len(ag) - sum(ag)), max_abs_score_diff=dmax)

meta = dict(host=platform.node(), imgsz=a.imgsz, threads=a.threads, core=a.core, affinity=sorted(os.sched_getaffinity(0)), torch=torch.__version__, cv2=cv2.__version__, tag=a.tag,
            theta=TH, loadavg_start=open('/proc/loadavg').read().split()[:3], steal_start=steal(), freq_start=freq(a.core), t_start=time.time(), torch_threads=torch.get_num_threads())
clips = {}
for v in VIDS:
    fps, n = video_info(v); clips[v] = (v, list(frames(v)), fps)
out = dict(meta=meta)
if a.single:
    out['single'] = {}
    for v in VIDS:
        for pname, pf in POL.items():
            rec = run([clips[v]], pf, 1e9, False); out['single'].setdefault(pname, []).extend(rec)
            print(v, pname, {k: round(x, 3) for k, x in summ(rec).items()}, flush=True)
    out['single_summary'] = {p: summ(rec) | agreement(rec) for p, rec in out['single'].items()}
    for p, d in out['single_summary'].items(): print('ALL', p, {k: round(x, 3) for k, x in d.items()}, flush=True)
else:
    N = a.N; pf = POL[a.policy]; cams = [clips[VIDS[c % len(VIDS)]] for c in range(N)]
    rec = run(cams, pf, a.horizon, True); out['multi'] = dict(policy=a.policy, N=N, horizon=a.horizon, summary=summ(rec) | agreement(rec), rec=rec)
    print('multi', a.policy, N, {k: round(x, 3) for k, x in out['multi']['summary'].items()}, flush=True)
meta.update(t_end=time.time(), loadavg_end=open('/proc/loadavg').read().split()[:3], steal_end=steal(), freq_end=freq(a.core), torch_threads_end=torch.get_num_threads())
json.dump(out, open(a.out, 'w'), default=float); print('DONE')
