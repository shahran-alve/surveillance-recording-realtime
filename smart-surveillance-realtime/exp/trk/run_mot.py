import sys, os, numpy as np
np.asfarray = lambda a, dtype=float: np.asarray(a, dtype=dtype)
import pandas as pd, motmetrics as mm, json
sys.path.insert(0, '/root/exp/trk')
import sortcore
from sortcore import Sort, KalmanBoxTracker, iou_batch
SEQS = ['TUD-Campus', 'TUD-Stadtmitte']
DET = '/root/data/sort/data/train/{}/det/det.txt'
GT = '/root/data/py-motmetrics/motmetrics/data/{}/gt.txt'
OUT = '/root/results/mot'; os.makedirs(OUT, exist_ok=True)

def load_dets(seq, min_conf=0.0):
    d = np.loadtxt(DET.format(seq), delimiter=',')
    d = d[d[:, 6] >= min_conf]
    d[:, 4:6] += d[:, 2:4]  # to x1,y1,x2,y2
    return {int(f): d[d[:, 0] == f][:, [2, 3, 4, 5, 6]] for f in np.unique(d[:, 0])}, int(d[:, 0].max())

class NoMotionTracker(KalmanBoxTracker):
    """Same as SORT's track but the 'prediction' is just the last matched box (no motion model)."""
    def __init__(self, bbox):
        super().__init__(bbox); self.last = np.array(bbox[:4], float)
    def update(self, bbox):
        super().update(bbox); self.last = np.array(bbox[:4], float)
    def predict(self):
        super().predict(); return self.last.reshape(1, 4)
    def get_state(self): return self.last.reshape(1, 4)

def run_sort(seq, max_age, min_hits, iou_thr, motion=True):
    dets, nF = load_dets(seq)
    KalmanBoxTracker.count = 0
    sortcore.KalmanBoxTracker = KalmanBoxTracker if motion else NoMotionTracker
    trk = Sort(max_age=max_age, min_hits=min_hits, iou_threshold=iou_thr)
    rows = []
    for f in range(1, nF + 1):
        out = trk.update(dets.get(f, np.empty((0, 5))))
        for x1, y1, x2, y2, tid in out: rows.append([f, int(tid), x1, y1, x2 - x1, y2 - y1])
    sortcore.KalmanBoxTracker = KalmanBoxTracker
    return rows

def run_iou(seq, sigma_l=0.0, sigma_h=0.9, sigma_iou=0.3, t_min=3):
    """IOU tracker (Bochinski et al., 2017): greedy frame-to-frame IoU association, no motion model."""
    dets, nF = load_dets(seq, sigma_l)
    active, finished = [], []
    for f in range(1, nF + 1):
        D = list(dets.get(f, np.empty((0, 5))))
        upd = []
        for tr in active:
            if D:
                ious = iou_batch(np.array([tr['boxes'][-1]]), np.array(D)[:, :4])[0]
                j = int(np.argmax(ious))
                if ious[j] >= sigma_iou:
                    tr['boxes'].append(D[j][:4]); tr['frames'].append(f); tr['max'] = max(tr['max'], D[j][4]); upd.append(tr); D.pop(j); continue
            if tr['max'] >= sigma_h and len(tr['boxes']) >= t_min: finished.append(tr)
        active = upd + [{'boxes': [d[:4]], 'frames': [f], 'max': d[4]} for d in D]
    finished += [tr for tr in active if tr['max'] >= sigma_h and len(tr['boxes']) >= t_min]
    rows = []
    for i, tr in enumerate(finished):
        for f, b in zip(tr['frames'], tr['boxes']): rows.append([f, i + 1, b[0], b[1], b[2] - b[0], b[3] - b[1]])
    return rows

def gt_df(seq):
    g = np.loadtxt(GT.format(seq), delimiter=',')
    return g

def occluded_mask(g, thr=0.3):
    """GT box is 'occluded' if another GT box in the same frame covers >= thr of its area."""
    occ = np.zeros(len(g), bool)
    for f in np.unique(g[:, 0]):
        idx = np.where(g[:, 0] == f)[0]; B = g[idx, 2:6]
        for a, i in enumerate(idx):
            x1, y1, w, h = B[a]
            for b in range(len(idx)):
                if b == a: continue
                X1, Y1, W, H = B[b]
                iw = max(0, min(x1 + w, X1 + W) - max(x1, X1)); ih = max(0, min(y1 + h, Y1 + H) - max(y1, Y1))
                if iw * ih >= thr * w * h: occ[i] = True
    return occ

def evaluate(seq, rows):
    g = gt_df(seq); occ = occluded_mask(g)
    occ_set = {(int(r[0]), int(r[1])) for r, o in zip(g, occ) if o}
    acc = mm.MOTAccumulator(auto_id=True)
    R = np.array(rows) if rows else np.zeros((0, 6))
    nF = int(max(g[:, 0].max(), R[:, 0].max() if len(R) else 0))
    for f in range(1, nF + 1):
        G = g[g[:, 0] == f]; H = R[R[:, 0] == f] if len(R) else np.zeros((0, 6))
        dist = mm.distances.iou_matrix(G[:, 2:6], H[:, 2:6], max_iou=0.5)
        acc.update(G[:, 1].astype(int).tolist(), H[:, 1].astype(int).tolist(), dist)
    ev = acc.mot_events.reset_index()
    # occlusion-aware recall and ID switches
    def isocc(fr, oid): return (int(fr) + 1, int(oid)) in occ_set  # auto_id frames start at 0
    m = ev[ev.Type.isin(['MATCH', 'SWITCH', 'MISS'])]
    o = np.array([isocc(fr, oid) for fr, oid in zip(m.FrameId, m.OId)]) if len(m) else np.array([], bool)
    hit = m.Type.isin(['MATCH', 'SWITCH']).values
    sw = ev[ev.Type == 'SWITCH']
    sw_occ = sum(isocc(fr, oid) or isocc(fr - 1, oid) or isocc(fr - 2, oid) for fr, oid in zip(sw.FrameId, sw.OId))
    extra = dict(recall_occ=float(hit[o].mean()) if o.any() else np.nan, recall_vis=float(hit[~o].mean()),
                 n_occ=int(o.sum()), n_vis=int((~o).sum()), idsw_near_occ=int(sw_occ))
    return acc, extra

if __name__ == '__main__':
    configs = {
        'IOU tracker (no motion)': ('iou', {}),
        'Hungarian, no motion model (max_age=1)': ('sort', dict(max_age=1, min_hits=3, iou_thr=0.3, motion=False)),
        'SORT, Kalman (max_age=1)': ('sort', dict(max_age=1, min_hits=3, iou_thr=0.3)),
        'SORT, Kalman (max_age=5)': ('sort', dict(max_age=5, min_hits=3, iou_thr=0.3)),
        'SORT, Kalman (max_age=15)': ('sort', dict(max_age=15, min_hits=3, iou_thr=0.3)),
    }
    mh = mm.metrics.create(); res = []; extras = []
    for cname, (kind, kw) in configs.items():
        accs = []; ex_all = []
        for seq in SEQS:
            rows = run_iou(seq, **kw) if kind == 'iou' else run_sort(seq, **kw)
            pd.DataFrame(rows).to_csv(f'{OUT}/{cname.split(",")[0].split(" ")[0]}_{kw.get("max_age","")}_{kw.get("motion",True)}_{seq}.txt', header=False, index=False)
            acc, ex = evaluate(seq, rows); accs.append(acc); ex_all.append(ex)
        s = mh.compute_many(accs, names=SEQS, metrics=['mota', 'idf1', 'num_switches', 'num_false_positives', 'num_misses', 'mostly_tracked', 'mostly_lost', 'num_fragmentations', 'motp', 'num_unique_objects'], generate_overall=True)
        s['config'] = cname; res.append(s)
        tot = lambda k: sum(e[k] for e in ex_all)
        extras.append(dict(config=cname,
            recall_occ=sum(e['recall_occ'] * e['n_occ'] for e in ex_all) / tot('n_occ'),
            recall_vis=sum(e['recall_vis'] * e['n_vis'] for e in ex_all) / tot('n_vis'),
            n_occ=tot('n_occ'), n_vis=tot('n_vis'), idsw_near_occ=tot('idsw_near_occ')))
    df = pd.concat(res); df.to_csv(f'{OUT}/mot_metrics.csv')
    pd.DataFrame(extras).to_csv(f'{OUT}/mot_occlusion.csv', index=False)
    pd.set_option('display.width', 250); print(df); print(pd.DataFrame(extras))
