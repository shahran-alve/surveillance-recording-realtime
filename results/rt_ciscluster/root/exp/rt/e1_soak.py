"""E1 soak test of the detector trigger (YOLO11n, PyTorch CPU, 1 thread), process pinned to one physical core.
mode 'b2b':   back-to-back inference for --minutes, cycling through all seven clips (pre-decoded frames, decode excluded)
mode 'paced': one job every --period seconds (default 8/12 s = stride 8 at 12 fps), same frame order
Per job: clip, frame index, service time, release/start time. Output: npz + meta json.
Usage: python e1_soak.py --mode b2b --imgsz 640 --minutes 20 --core 2 --out FILE.npz"""
import sys, time, os, json, argparse, platform
ROOT = os.environ.get('SS_ROOT', '/root')
sys.path.insert(0, ROOT + '/exp')
ap = argparse.ArgumentParser(); ap.add_argument('--mode', choices=['b2b', 'paced'], required=True); ap.add_argument('--imgsz', type=int, default=640); ap.add_argument('--minutes', type=float, default=20)
ap.add_argument('--period', type=float, default=8 / 12); ap.add_argument('--core', type=int, default=2); ap.add_argument('--threads', type=int, default=1); ap.add_argument('--out', required=True); a = ap.parse_args()
os.sched_setaffinity(0, {a.core})
import numpy as np, torch, cv2
from common import VIDEOS, frames
from ultralytics import YOLO
import ultralytics.utils.torch_utils as tu; tu.NUM_THREADS = a.threads   # neutralise select_device()'s thread reset
torch.set_num_threads(a.threads); cv2.setNumThreads(a.threads); CLS = [0, 1, 2, 3, 5, 7]
def steal(): return int(open('/proc/stat').readline().split()[8])
def freq(c):
    try: return int(open(f'/sys/devices/system/cpu/cpu{c}/cpufreq/scaling_cur_freq').read()) / 1e3
    except OSError: return None
F = []; ids = []
for v in VIDEOS:
    for i, f in enumerate(frames(v)): F.append(f); ids.append((v, i))
m = YOLO(ROOT + '/data/models/yolo11n.pt')
for f in F[:5]: m.predict(f, imgsz=a.imgsz, conf=0.05, classes=CLS, verbose=False)
torch.set_num_threads(a.threads)
meta = dict(host=platform.node(), mode=a.mode, imgsz=a.imgsz, threads=a.threads, core=a.core, period=a.period, minutes=a.minutes, torch=torch.__version__, cv2=cv2.__version__,
            loadavg_start=open('/proc/loadavg').read().split()[:3], steal_start=steal(), freq_start=freq(a.core), affinity=sorted(os.sched_getaffinity(0)), t_start=time.time(), torch_threads=torch.get_num_threads())
ts, rel, st, clip, frame, sc = [], [], [], [], [], []
t0 = time.perf_counter(); horizon = 60 * a.minutes; j = 0; maxf = []
while True:
    r_ = j * a.period if a.mode == 'paced' else None
    if a.mode == 'paced':
        now = time.perf_counter() - t0
        if r_ > horizon: break
        if now < r_: time.sleep(r_ - now)
    elif time.perf_counter() - t0 > horizon: break
    k = j % len(F); s0 = time.perf_counter(); r = m.predict(F[k], imgsz=a.imgsz, conf=0.05, classes=CLS, verbose=False)[0]; s1 = time.perf_counter()
    sc.append(float(r.boxes.conf.max()) if len(r.boxes) else 0.0); ts.append(s1 - s0); st.append(s0 - t0); rel.append(r_ if r_ is not None else s0 - t0); clip.append(ids[k][0]); frame.append(ids[k][1]); j += 1
    if j % 2000 == 0:
        x = np.array(ts); print(j, 'mean', round(1e3 * x.mean(), 1), 'p99', round(1e3 * np.percentile(x, 99), 1), 'max', round(1e3 * x.max(), 1), 'MHz', freq(a.core), 'steal', steal() - meta['steal_start'], flush=True)
meta.update(t_end=time.time(), jobs=j, loadavg_end=open('/proc/loadavg').read().split()[:3], steal_end=steal(), freq_end=freq(a.core))
np.savez(a.out, service=np.array(ts), start=np.array(st), release=np.array(rel), clip=np.array(clip), frame=np.array(frame), score=np.array(sc))
json.dump(meta, open(a.out.replace('.npz', '_meta.json'), 'w'), indent=1)
x = np.array(ts); print('DONE', a.mode, a.imgsz, 'jobs', j, 'mean', round(1e3 * x.mean(), 2), 'p99', round(1e3 * np.percentile(x, 99), 2), 'p99.9', round(1e3 * np.percentile(x, 99.9), 2), 'max', round(1e3 * x.max(), 2), 'steal', meta['steal_end'] - meta['steal_start'])
