"""E1 extension (section 8B): e1_profile.py restricted to 640 px / 1 thread, with (1) a discarded warm-up of --warmup seconds of back-to-back
inference cycling through all seven clips before any timing, and (2) the clip order rotated by --rotate positions. All clips are pre-decoded
once at the start (the warm-up needs every clip); the timed loop is otherwise the one of measure_det.py / e1_profile.py (5 warm-up frames per
clip, then every frame timed). Same guards: affinity to --core for every thread, ultralytics NUM_THREADS patched, set_num_threads(1) re-applied.
Usage: python e1_profile2.py --out DIR --core 2 --warmup 120 --rotate k"""
import sys, time, os, json, argparse, platform
ROOT = os.environ.get('SS_ROOT', '/root')
sys.path.insert(0, ROOT + '/exp')
ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--core', type=int, default=2); ap.add_argument('--warmup', type=float, default=120.0); ap.add_argument('--rotate', type=int, default=0)
ap.add_argument('--size', type=int, default=640); ap.add_argument('--thp-disable', action='store_true', help='prctl(PR_SET_THP_DISABLE, 1) before importing torch'); a = ap.parse_args()
THP_RC = None
if a.thp_disable:
    import ctypes; libc = ctypes.CDLL(None, use_errno=True); THP_RC = libc.prctl(41, 1, 0, 0, 0)   # PR_SET_THP_DISABLE = 41
    if THP_RC != 0: raise SystemExit(f'prctl(PR_SET_THP_DISABLE) failed errno={ctypes.get_errno()}')
def pin(cores):
    for tid in os.listdir('/proc/self/task'):
        try: os.sched_setaffinity(int(tid), cores)
        except OSError: pass
pin({a.core})
import numpy as np, torch, cv2
from common import VIDEOS, frames, video_info
from ultralytics import YOLO
import ultralytics.utils.torch_utils as tu; tu.NUM_THREADS = 1
def steal(): return int(open('/proc/stat').readline().split()[8])
def freq(c):
    try: return int(open(f'/sys/devices/system/cpu/cpu{c}/cpufreq/scaling_cur_freq').read()) / 1e3
    except OSError: return None
def minflt(): return int(open('/proc/self/stat').read().rsplit(')', 1)[1].split()[7])   # field 10 = minflt
def thp_status():
    try: return [l.strip() for l in open('/proc/self/status') if l.startswith('THP')]
    except OSError: return []
def smaps():
    try: return {l.split(':')[0]: int(l.split()[1]) for l in open('/proc/self/smaps_rollup') if l.split(':')[0] in ('Rss', 'Anonymous', 'AnonHugePages')}
    except OSError: return {}
def cpustat(c):
    for l in open('/proc/stat'):
        if l.startswith(f'cpu{c} '): return [int(x) for x in l.split()[1:]]
CLS = [0, 1, 2, 3, 5, 7]; th = 1; size = a.size
os.makedirs(a.out, exist_ok=True)
order = list(VIDEOS); order = order[a.rotate % len(order):] + order[:a.rotate % len(order)]
meta = dict(host=platform.node(), pid=os.getpid(), core=a.core, size=size, threads=th, warmup_s=a.warmup, rotate=a.rotate, order=order, torch=torch.__version__, cv2=cv2.__version__, python=sys.version.split()[0],
            thp_disable=a.thp_disable, thp_prctl_rc=THP_RC, thp_status=thp_status(), malloc_env={k: v for k, v in os.environ.items() if k.startswith('MALLOC_')}, minflt_start=minflt(), start=time.time(), loadavg_start=open('/proc/loadavg').read().split()[:3], steal_start=steal(), freq_start=freq(a.core), cpustat_start=cpustat(a.core), per_cfg=[])
m = YOLO(ROOT + '/data/models/yolo11n.pt'); torch.set_num_threads(th); cv2.setNumThreads(th)
FR = {name: list(frames(name)) for name in VIDEOS}; ALL = [f for name in VIDEOS for f in FR[name]]
# ---- discarded warm-up: back-to-back inference over all clips for --warmup seconds
m.predict(ALL[0], imgsz=size, conf=0.05, classes=CLS, verbose=False); torch.set_num_threads(th)
w0 = time.perf_counter(); c0 = cpustat(a.core); mf0 = minflt(); j = 0; wts = []
while time.perf_counter() - w0 < a.warmup:
    t0 = time.perf_counter(); m.predict(ALL[j % len(ALL)], imgsz=size, conf=0.05, classes=CLS, verbose=False); wts.append(time.perf_counter() - t0); j += 1
wts = np.array(wts); meta['warmup'] = dict(jobs=j, mean_ms=1e3 * wts.mean(), max_ms=1e3 * wts.max(), first10_ms=(1e3 * wts[:10]).tolist(), cpustat_delta=[x - y for x, y in zip(cpustat(a.core), c0)], torch_threads=torch.get_num_threads(), minflt=minflt() - mf0, minflt_per_s=(minflt() - mf0) / (time.perf_counter() - w0), smaps_kb=smaps())
print('warmup', j, 'jobs', round(1e3 * wts.mean(), 1), 'ms mean', round(1e3 * wts.max(), 1), 'max', 'sys jiffies', meta['warmup']['cpustat_delta'][2], flush=True)
out = {}
for name in order:
    F = FR[name]
    pin({a.core}); s0 = steal(); f0 = freq(a.core); c0 = cpustat(a.core); mf0 = minflt(); w0 = time.time()
    torch.set_num_threads(th); cv2.setNumThreads(th); ts = []; S = []
    for f in F[:5]: m.predict(f, imgsz=size, conf=0.05, classes=CLS, verbose=False)
    torch.set_num_threads(th)
    for f in F:
        t0 = time.perf_counter(); r = m.predict(f, imgsz=size, conf=0.05, classes=CLS, verbose=False)[0]
        s = float(r.boxes.conf.max()) if len(r.boxes) else 0.0; ts.append(time.perf_counter() - t0); S.append(s)
    out[f'lat|{size}|{th}|{name}'] = np.array(ts); out[f'score|{size}|{th}|{name}'] = np.array(S)
    aff = sorted(os.sched_getaffinity(0)); cd = [x - y for x, y in zip(cpustat(a.core), c0)]; mfd = minflt() - mf0
    meta['per_cfg'].append(dict(clip=name, size=size, threads=th, n=len(ts), steal_delta=steal() - s0, freq_before=f0, freq_after=freq(a.core), wall=time.time() - w0, cpustat_delta=cd, sys_share=cd[2] / max(1, cd[0] + cd[2]), minflt=mfd, minflt_per_s=mfd / (time.time() - w0), smaps_kb=smaps(), affinity_main=aff, torch_threads=torch.get_num_threads()))
    print(name, size, th, round(1000 * float(np.median(ts)), 1), round(1000 * float(np.percentile(ts, 99)), 1), round(1000 * float(np.max(ts)), 1), 'sys share %.3f' % meta['per_cfg'][-1]['sys_share'], 'minflt/s %.0f' % meta['per_cfg'][-1]['minflt_per_s'], 'steal', meta['per_cfg'][-1]['steal_delta'], 'aff', aff, 'torch_threads', torch.get_num_threads(), flush=True)
    np.savez(os.path.join(a.out, 'lat_det.npz'), **out)
meta.update(minflt_end=minflt(), end=time.time(), loadavg_end=open('/proc/loadavg').read().split()[:3], steal_end=steal(), freq_end=freq(a.core), cpustat_end=cpustat(a.core))
json.dump(meta, open(os.path.join(a.out, 'meta_det.json'), 'w'), indent=1)
print('DONE', torch.__version__, 'steal delta total', meta['steal_end'] - meta['steal_start'])
