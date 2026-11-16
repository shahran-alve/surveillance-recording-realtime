import sys, time, json, numpy as np, cv2
sys.path.insert(0, '/root/exp')
from common import frames
F = [f for i, f in zip(range(300), frames('one-by-one'))]
K = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)); res = {}
def bench(name, fn, warm=20):
    ts = []
    for i, f in enumerate(F):
        t0 = time.perf_counter(); fn(f); dt = time.perf_counter()-t0
        if i >= warm: ts.append(dt)
    res[name] = 1000*float(np.median(ts)); print(name, round(res[name], 2), flush=True)
st = {'prev': None}
def fd(f):
    g = cv2.GaussianBlur(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), (5, 5), 0)
    if st['prev'] is not None: m = cv2.morphologyEx((cv2.absdiff(g, st['prev']) > 25).astype(np.uint8), cv2.MORPH_OPEN, K); m.mean()
    st['prev'] = g
bench('FD', fd); st['prev'] = None
def flow(f):
    g = cv2.resize(cv2.GaussianBlur(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), (5, 5), 0), (384, 216))
    if st['prev'] is not None: fl = cv2.calcOpticalFlowFarneback(st['prev'], g, None, 0.5, 3, 15, 3, 5, 1.2, 0); (np.linalg.norm(fl, axis=2) > 1).mean()
    st['prev'] = g
bench('FLOW', flow)
for name, s in [('MOG2', cv2.createBackgroundSubtractorMOG2(detectShadows=True)), ('KNN', cv2.createBackgroundSubtractorKNN(detectShadows=True)),
                ('CNT', cv2.bgsegm.createBackgroundSubtractorCNT()), ('GSOC', cv2.bgsegm.createBackgroundSubtractorGSOC())]:
    bench(name, lambda f, s=s: cv2.morphologyEx((s.apply(f) == 255).astype(np.uint8), cv2.MORPH_OPEN, K).mean())
json.dump(res, open('/root/results/latency_motion.json', 'w'), indent=1)
