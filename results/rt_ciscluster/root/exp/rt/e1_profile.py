"""E1: repeated service-time profiling of the detector trigger, one fresh process per run.
The timing loop is copied verbatim from measure_det.py (same CFG order, warm-up, predict call, per-clip interleaving);
added: CPU affinity per configuration (one physical core for 1-thread configs, two physical cores for the 2-thread config,
applied to every thread of the process), /proc/stat steal-time and CPU-frequency records before/after each configuration,
and an output directory per run. The perturbed 320-px score pass of measure_det.py is NOT repeated here.
Usage: python e1_profile.py --out DIR --core 2 --core2 4 [--configs 640/1,640/2,480/1,320/1]"""
import sys, time, os, json, argparse, platform
ROOT = os.environ.get('SS_ROOT', '/root')
sys.path.insert(0, ROOT + '/exp')
ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--core', type=int, default=2); ap.add_argument('--core2', type=int, default=4)
ap.add_argument('--configs', default='640/1,640/2,480/1,320/1'); a = ap.parse_args()
def pin(cores):
    for tid in os.listdir('/proc/self/task'):
        try: os.sched_setaffinity(int(tid), cores)
        except OSError: pass
pin({a.core})                                   # before torch/cv2 are imported: all later threads inherit the mask
import numpy as np, torch, cv2
from common import VIDEOS, frames, video_info
from ultralytics import YOLO
import ultralytics.utils.torch_utils as tu; tu.NUM_THREADS = 1   # select_device() would otherwise set min(8, cpu-1) threads on the first predict
def steal():
    f = open('/proc/stat').readline().split(); return int(f[8])   # steal jiffies, all CPUs
def freq(c):
    try: return int(open(f'/sys/devices/system/cpu/cpu{c}/cpufreq/scaling_cur_freq').read()) / 1e3
    except OSError: return None
def cpustat(c):
    for l in open('/proc/stat'):
        if l.startswith(f'cpu{c} '): return [int(x) for x in l.split()[1:]]
CLS = [0, 1, 2, 3, 5, 7]
CFG = [tuple(int(x) for x in s.split('/')) for s in a.configs.split(',')]
os.makedirs(a.out, exist_ok=True)
meta = dict(host=platform.node(), pid=os.getpid(), core=a.core, core2=a.core2, torch=torch.__version__, cv2=cv2.__version__, numpy=np.__version__, python=sys.version.split()[0],
            cuda=torch.cuda.is_available(), start=time.time(), loadavg_start=open('/proc/loadavg').read().split()[:3], steal_start=steal(), freq_start=freq(a.core), cpustat_start=cpustat(a.core), per_cfg=[])
out = {}; m = YOLO(ROOT + '/data/models/yolo11n.pt')
for name in VIDEOS:
    F = list(frames(name))
    for size, th in CFG:
        pin({a.core} if th == 1 else {a.core, a.core2}); s0 = steal(); f0 = freq(a.core); c0 = cpustat(a.core); w0 = time.time()
        torch.set_num_threads(th); cv2.setNumThreads(th); ts = []; S = []
        for f in F[:5]: m.predict(f, imgsz=size, conf=0.05, classes=CLS, verbose=False)
        torch.set_num_threads(th)                 # re-apply after the warm-up (ultralytics resets the thread count on its first predict)
        for f in F:
            t0 = time.perf_counter(); r = m.predict(f, imgsz=size, conf=0.05, classes=CLS, verbose=False)[0]
            s = float(r.boxes.conf.max()) if len(r.boxes) else 0.0; ts.append(time.perf_counter() - t0); S.append(s)
        out[f'lat|{size}|{th}|{name}'] = np.array(ts); out[f'score|{size}|{th}|{name}'] = np.array(S)
        aff = sorted(os.sched_getaffinity(0)); tids = {int(t): sorted(os.sched_getaffinity(int(t))) for t in os.listdir('/proc/self/task')}
        meta['per_cfg'].append(dict(clip=name, size=size, threads=th, n=len(ts), steal_delta=steal() - s0, freq_before=f0, freq_after=freq(a.core), wall=time.time() - w0,
                                    cpustat_delta=[x - y for x, y in zip(cpustat(a.core), c0)], affinity_main=aff, n_threads=len(tids), torch_threads=torch.get_num_threads(), affinity_all=sorted({tuple(v) for v in tids.values()})))
        print(name, size, th, round(1000 * float(np.median(ts)), 1), round(1000 * float(np.percentile(ts, 99)), 1), round(1000 * float(np.max(ts)), 1), 'steal', meta['per_cfg'][-1]['steal_delta'], 'MHz', f0, meta['per_cfg'][-1]['freq_after'], 'aff', aff, 'torch_threads', torch.get_num_threads(), flush=True)
    np.savez(os.path.join(a.out, 'lat_det.npz'), **out)
meta.update(end=time.time(), loadavg_end=open('/proc/loadavg').read().split()[:3], steal_end=steal(), freq_end=freq(a.core), cpustat_end=cpustat(a.core))
json.dump(meta, open(os.path.join(a.out, 'meta_det.json'), 'w'), indent=1)
print('DONE', torch.__version__, 'steal delta total', meta['steal_end'] - meta['steal_start'])
