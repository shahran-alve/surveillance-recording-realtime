"""Per-frame service times and scores of the detector trigger (YOLO11n, PyTorch CPU) for several input sizes and thread counts."""
import sys, time, os, numpy as np, torch, cv2
sys.path.insert(0, '/root/exp')
from common import VIDEOS, frames, video_info
from perturb import make_perturber
from ultralytics import YOLO
CLS = [0, 1, 2, 3, 5, 7]
CFG = [(640, 1), (640, 2), (480, 1), (320, 1)]
out = {}; m = YOLO('/root/data/models/yolo11n.pt')
for name in VIDEOS:
    F = list(frames(name))
    for size, th in CFG:
        torch.set_num_threads(th); cv2.setNumThreads(th); ts = []; S = []
        for f in F[:5]: m.predict(f, imgsz=size, conf=0.05, classes=CLS, verbose=False)
        for f in F:
            t0 = time.perf_counter(); r = m.predict(f, imgsz=size, conf=0.05, classes=CLS, verbose=False)[0]
            s = float(r.boxes.conf.max()) if len(r.boxes) else 0.0; ts.append(time.perf_counter() - t0); S.append(s)
        out[f'lat|{size}|{th}|{name}'] = np.array(ts); out[f'score|{size}|{th}|{name}'] = np.array(S)
        if th == 1 and size != 640: np.save(f'/root/results/det_scores/yolo11n{size}_{name}_clean.npy', np.array(S))
        print(name, size, th, round(1000 * float(np.median(ts)), 1), round(1000 * float(np.percentile(ts, 99)), 1), flush=True)
    np.savez('/root/results/rt/lat_det.npz', **out)
# scores for the 320-px detector under perturbation (no timing)
torch.set_num_threads(2)
for kind in ['illum', 'jitter']:
    for name in VIDEOS:
        fps, n = video_info(name); P = make_perturber(kind, n, seed=sum(map(ord, name))); S = []
        for t, f in enumerate(frames(name)):
            r = m.predict(P(t, f), imgsz=320, conf=0.05, classes=CLS, verbose=False)[0]; S.append(float(r.boxes.conf.max()) if len(r.boxes) else 0.0)
        np.save(f'/root/results/det_scores/yolo11n320_{name}_{kind}.npy', np.array(S)); print('scores', kind, name, flush=True)
print('DONE', torch.__version__)
