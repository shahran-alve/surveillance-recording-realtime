import sys, os, time, numpy as np, cv2
ROOT = os.environ.get('SS_ROOT', '/root')
sys.path.insert(0, ROOT + '/exp')
from common import VIDEOS, frames, video_info
from perturb import make_perturber
K = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
def run(args):
    name, kind = args
    out = f'{ROOT}/results/motion_scores/{name}_{kind}.npz'
    if os.path.exists(out): return out
    fps, n = video_info(name)
    P = make_perturber(kind, n, seed=abs(hash(name)) % 1000 if False else sum(map(ord, name)))
    subs = {'MOG2': cv2.createBackgroundSubtractorMOG2(detectShadows=True),
            'KNN': cv2.createBackgroundSubtractorKNN(detectShadows=True),
            'CNT': cv2.bgsegm.createBackgroundSubtractorCNT(),
            'GSOC': cv2.bgsegm.createBackgroundSubtractorGSOC()}
    S = {k: [] for k in ['FD', 'FLOW', *subs]}; T = {k: 0.0 for k in S}
    prev = None; prevs = None
    for t, f in enumerate(frames(name)):
        f = P(t, f)
        g = cv2.GaussianBlur(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), (5, 5), 0)
        t0 = time.perf_counter()
        if prev is None: S['FD'].append(0.0)
        else:
            m = (cv2.absdiff(g, prev) > 25).astype(np.uint8)
            m = cv2.morphologyEx(m, cv2.MORPH_OPEN, K); S['FD'].append(m.mean())
        T['FD'] += time.perf_counter() - t0
        t0 = time.perf_counter()
        small = cv2.resize(g, (g.shape[1]//2, g.shape[0]//2))
        if prevs is None: S['FLOW'].append(0.0)
        else:
            fl = cv2.calcOpticalFlowFarneback(prevs, small, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            S['FLOW'].append(float((np.linalg.norm(fl, axis=2) > 1.0).mean()))
        T['FLOW'] += time.perf_counter() - t0
        prev, prevs = g, small
        for k, s in subs.items():
            t0 = time.perf_counter()
            m = s.apply(f)
            m = (m == 255).astype(np.uint8)  # shadows (127) treated as background
            m = cv2.morphologyEx(m, cv2.MORPH_OPEN, K)
            S[k].append(m.mean()); T[k] += time.perf_counter() - t0
    n = len(S['FD'])
    np.savez(out, **{k: np.array(v) for k, v in S.items()}, **{'ms_'+k: np.array(1000*T[k]/n) for k in T}, fps=fps)
    return out
if __name__ == '__main__':
    from multiprocessing import Pool
    os.makedirs(ROOT + '/results/motion_scores', exist_ok=True)
    jobs = [(v, k) for k in ['clean', 'illum', 'jitter', 'noise'] for v in VIDEOS]
    cv2.setNumThreads(1)
    with Pool(2) as p:
        for r in p.imap_unordered(run, jobs): print('done', r, flush=True)
    print('ALL DONE', cv2.__version__)
