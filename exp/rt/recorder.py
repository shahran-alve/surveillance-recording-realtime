"""E3: end-to-end event-triggered recorder for one camera (capture thread, ring buffer, detector worker, writer thread).
 capture:  decodes the clip with cv2.VideoCapture, applies the frame step and 768-px resize of common.frames(); frame t is due at
           t0 + t*T (T = 1/fps). At its due time the frame is decoded+resized (timed) and pushed into the ring buffer; lateness =
           push time - due time (includes decode, resize and wake-up jitter).
 ring:     the last p + ceil(R_max*fps) frames, p = round(pre_roll*fps), R_max = pooled C_max of Phase 1 (seconds, --rmax).
 detector: 1 torch thread; samples frame i, decision pos = score > theta (analysis.json 'theta'), held for k frames
           (k = k_act if pos else k_idle), next sample i + k (identical to sample_plan()/trig_from_plan() in analyze.py).
 writer:   on a positive decision for sample i it must store frames [i - round(pre*fps), i + k - 1 + round(post*fps)] (the union of
           record() windows of the k trigger frames); it writes the pre-roll from the ring buffer, then frames as they arrive, with
           cv2.VideoWriter (MJPG, one file per contiguous segment); every written frame index and its write time are logged.
           A frame that is needed but no longer in the ring buffer is logged as lost.
Usage: python recorder.py --policy "Fixed stride 8" --rmax 0.0xx --cores 2 [--cores 2,4] --outdir DIR --viddir DIR [--clips a,b]"""
import sys, os, time, json, argparse, threading, collections, platform, math
ROOT = os.environ.get('SS_ROOT', '/root')
sys.path.insert(0, ROOT + '/exp')
ap = argparse.ArgumentParser(); ap.add_argument('--policy', required=True); ap.add_argument('--rmax', type=float, required=True); ap.add_argument('--cores', default='2')
ap.add_argument('--outdir', required=True); ap.add_argument('--viddir', required=True); ap.add_argument('--clips', default=''); ap.add_argument('--pre', type=float, default=1.0); ap.add_argument('--post', type=float, default=2.0)
ap.add_argument('--imgsz', type=int, default=640); ap.add_argument('--tag', default=''); a = ap.parse_args()
CORES = {int(c) for c in a.cores.split(',')}; os.sched_setaffinity(0, CORES)
import numpy as np, cv2, torch
import ultralytics.utils.torch_utils as tu; tu.NUM_THREADS = 1
from common import VIDEOS, VID_DIR, WIDTH, video_info
from ultralytics import YOLO
torch.set_num_threads(1); cv2.setNumThreads(1); CLS = [0, 1, 2, 3, 5, 7]
A = json.load(open(ROOT + '/results/rt/analysis.json')); TH = A['theta']
def kidle_rt(fps, pre=1.0): return max(1, int(np.floor(pre * fps + 1e-9)))
POL = {'Fixed stride 8': lambda fps: (8, 8), 'Adaptive 16/8': lambda fps: (16, 8), 'Adaptive, deadline-aware': lambda fps: (kidle_rt(fps), min(8, kidle_rt(fps)))}
pf = POL[a.policy]; os.makedirs(a.outdir, exist_ok=True); os.makedirs(a.viddir, exist_ok=True)
m = YOLO(ROOT + '/data/models/yolo11n.pt')
def steal(): return int(open('/proc/stat').readline().split()[8])

class Recorder:
    def __init__(self, name):
        self.name = name; self.file, self.step = VIDEOS[name]; self.fps, self.n = video_info(name); self.T = 1 / self.fps
        self.p = int(round(a.pre * self.fps)); self.post = int(round(a.post * self.fps)); self.cap_n = self.p + math.ceil(a.rmax * self.fps)
        self.ki, self.ka = pf(self.fps); self.thr = TH[name]
        self.ring = collections.OrderedDict(); self.lock = threading.Condition(); self.newest = -1; self.done = False
        self.need = set(); self.done_idx = set(); self.need_hi = -1; self.cap_log = []; self.det_log = []; self.wr_log = []; self.lost = []; self.det_lost = []; self.segments = []

    # ---- capture thread
    def capture(self):
        c = cv2.VideoCapture(os.path.join(VID_DIR, self.file)); raw = 0; t = 0
        while True:
            due = self.t0 + t * self.T; now = time.perf_counter()
            if now < due: time.sleep(due - now)
            d0 = time.perf_counter(); fr = None
            while True:                                  # decode up to and including the next kept frame (frame step as in common.frames())
                ok, f = c.read()
                if not ok: break
                keep = raw % self.step == 0; raw += 1
                if keep: fr = f; break
            if fr is None: break
            h = int(round(fr.shape[0] * WIDTH / fr.shape[1]))
            if fr.shape[1] != WIDTH: fr = cv2.resize(fr, (WIDTH, h), interpolation=cv2.INTER_AREA)
            d1 = time.perf_counter()
            with self.lock:
                self.ring[t] = fr
                while len(self.ring) > self.cap_n: self.ring.popitem(last=False)
                self.newest = t; self.lock.notify_all()
            self.cap_log.append((t, due - self.t0, 1e3 * (d1 - d0), d1 - self.t0, d1 - due)); t += 1
        with self.lock: self.done = True; self.lock.notify_all()

    # ---- detector worker
    def detector(self):
        i = 0
        while i < self.n:
            with self.lock:
                while self.newest < i and not self.done: self.lock.wait()
                if self.newest < i: break
                fr = self.ring.get(i); rel = self.cap_log[i][3]
                if fr is None:                            # frame already evicted (detector far behind): resample at the oldest available frame
                    self.det_lost.append(i); i = next(iter(self.ring)); fr = self.ring[i]; rel = self.cap_log[i][3]
            s0 = time.perf_counter(); r = m.predict(fr, imgsz=a.imgsz, conf=0.05, classes=CLS, verbose=False)[0]; s = float(r.boxes.conf.max()) if len(r.boxes) else 0.0; s1 = time.perf_counter()
            pos = s > self.thr; k = self.ka if pos else self.ki
            self.det_log.append(dict(frame=i, release=rel, start=s0 - self.t0, finish=s1 - self.t0, service=s1 - s0, score=s, pos=bool(pos), k=k))
            if pos:
                lo, hi = max(0, i - self.p), min(self.n - 1, i + k - 1 + self.post)
                with self.lock: self.need.update(j for j in range(lo, hi + 1) if j not in self.done_idx); self.need_hi = max(self.need_hi, hi); self.lock.notify_all()
            i += k
        with self.lock: self.det_done = True; self.lock.notify_all()

    # ---- writer thread
    def writer(self):
        vw = None; last = -2; seg = None
        while True:
            with self.lock:
                while True:
                    ready = sorted(j for j in self.need if j <= self.newest)
                    if ready or (self.done and getattr(self, 'det_done', False)): break
                    self.lock.wait()
                if not ready and self.done and getattr(self, 'det_done', False): break
                frames = [(j, self.ring.get(j)) for j in ready]
                for j in ready: self.need.discard(j); self.done_idx.add(j)
            for j, fr in frames:
                if fr is None: self.lost.append(j); continue
                if j != last + 1 or vw is None:
                    if vw is not None: vw.release()
                    seg = os.path.join(a.viddir, f'{self.name}_{a.policy.replace(" ", "_").replace(",", "").replace("/", "")}_{j:05d}.avi'); self.segments.append(seg)
                    vw = cv2.VideoWriter(seg, cv2.VideoWriter_fourcc(*'MJPG'), self.fps, (fr.shape[1], fr.shape[0]))
                w0 = time.perf_counter(); vw.write(fr); w1 = time.perf_counter()
                self.wr_log.append((j, 1e3 * (w1 - w0), w1 - self.t0, len(self.segments) - 1)); last = j
        if vw is not None: vw.release()

    def run(self):
        self.det_done = False
        for _ in range(3): m.predict(np.zeros((432, 768, 3), np.uint8), imgsz=a.imgsz, conf=0.05, classes=CLS, verbose=False)
        torch.set_num_threads(1)
        self.t0 = time.perf_counter() + 0.5
        th = [threading.Thread(target=f, daemon=True) for f in (self.capture, self.detector, self.writer)]
        for t in th: t.start()
        for t in th: t.join()
        return dict(clip=self.name, fps=self.fps, n=self.n, p=self.p, post=self.post, ring_capacity=self.cap_n, k_idle=self.ki, k_act=self.ka, theta=self.thr,
                    capture=self.cap_log, detector=self.det_log, written=self.wr_log, lost=self.lost, det_lost=self.det_lost, segments=self.segments,
                    n_captured=len(self.cap_log), n_written=len(self.wr_log))

meta = dict(host=platform.node(), policy=a.policy, rmax=a.rmax, cores=sorted(CORES), affinity=sorted(os.sched_getaffinity(0)), imgsz=a.imgsz, torch=torch.__version__, cv2=cv2.__version__, tag=a.tag,
            pre=a.pre, post=a.post, loadavg_start=open('/proc/loadavg').read().split()[:3], steal_start=steal(), t_start=time.time(), torch_threads=torch.get_num_threads(), viddir=a.viddir)
out = dict(meta=meta, clips={})
for name in (a.clips.split(',') if a.clips else list(VIDEOS)):
    r = Recorder(name).run(); out['clips'][name] = r
    sv = np.array([d['service'] for d in r['detector']]); dec = np.array([c[2] for c in r['capture']]); late = np.array([c[4] for c in r['capture']]); wr = np.array([w[1] for w in r['written']]) if r['written'] else np.zeros(1)
    print(name, a.policy, 'captured', r['n_captured'], 'det jobs', len(sv), 'written', r['n_written'], 'lost', len(r['lost']), 'det_lost', len(r['det_lost']),
          'service ms mean/max', round(1e3 * sv.mean(), 1), round(1e3 * sv.max(), 1), 'decode ms mean/max', round(dec.mean(), 2), round(dec.max(), 2), 'late ms mean/max', round(1e3 * late.mean(), 2), round(1e3 * late.max(), 2),
          'write ms mean/max', round(wr.mean(), 2), round(wr.max(), 2), 'segments', len(r['segments']), flush=True)
meta.update(t_end=time.time(), loadavg_end=open('/proc/loadavg').read().split()[:3], steal_end=steal(), torch_threads_end=torch.get_num_threads())
fn = os.path.join(a.outdir, f'recorder_{a.policy.replace(" ", "_").replace(",", "").replace("/", "")}_cores{"-".join(map(str, sorted(CORES)))}{a.tag}.json')
json.dump(out, open(fn, 'w'), default=float); print('DONE', fn)
