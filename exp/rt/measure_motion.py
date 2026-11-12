"""Per-frame service times of the motion triggers on all seven clips (clean), single thread. Decode excluded (frame already in memory)."""
import sys, time, numpy as np, cv2, platform
sys.path.insert(0, '/root/exp')
from common import VIDEOS, frames
cv2.setNumThreads(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
K = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)); out = {}
for name in VIDEOS:
    F = list(frames(name)); T = {}
    prev = None; ts = []
    for f in F:
        t0 = time.perf_counter()
        g = cv2.GaussianBlur(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), (5, 5), 0)
        if prev is not None: cv2.morphologyEx((cv2.absdiff(g, prev) > 25).astype(np.uint8), cv2.MORPH_OPEN, K).mean()
        prev = g; ts.append(time.perf_counter() - t0)
    T['FD'] = ts
    prev = None; ts = []
    for f in F:
        t0 = time.perf_counter()
        g = cv2.GaussianBlur(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), (5, 5), 0); g = cv2.resize(g, (g.shape[1] // 2, g.shape[0] // 2))
        if prev is not None: (np.linalg.norm(cv2.calcOpticalFlowFarneback(prev, g, None, 0.5, 3, 15, 3, 5, 1.2, 0), axis=2) > 1.0).mean()
        prev = g; ts.append(time.perf_counter() - t0)
    T['FLOW'] = ts
    for k, mk in [('MOG2', lambda: cv2.createBackgroundSubtractorMOG2(detectShadows=True)), ('KNN', lambda: cv2.createBackgroundSubtractorKNN(detectShadows=True)),
                  ('CNT', lambda: cv2.bgsegm.createBackgroundSubtractorCNT()), ('GSOC', lambda: cv2.bgsegm.createBackgroundSubtractorGSOC())]:
        s = mk(); ts = []
        for f in F:
            t0 = time.perf_counter(); cv2.morphologyEx((s.apply(f) == 255).astype(np.uint8), cv2.MORPH_OPEN, K).mean(); ts.append(time.perf_counter() - t0)
        T[k] = ts
    for k, v in T.items(): out[f'{k}|{name}'] = np.array(v)
    print(name, {k: round(1000 * float(np.median(v)), 2) for k, v in T.items()}, flush=True)
np.savez('/root/results/rt/lat_motion.npz', **out); print('DONE', cv2.__version__, platform.processor())
