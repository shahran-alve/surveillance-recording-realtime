import sys, numpy as np, pandas as pd
sys.path.insert(0, '/root/exp')
from common import VIDEOS, video_info
from gt_events import frame_labels
W = {}
for v in VIDEOS:
    fps, n = video_info(v); lab, valid = frame_labels(v, fps, n); valid &= np.arange(n) >= 2*fps
    W[v] = dict(n=n, idle=int((~lab & valid).sum()), act=int((lab & valid).sum()))
d = pd.read_csv('/root/results/event_lovo_per_video.csv')
rng = np.random.default_rng(0); out = []
for (m, k), g in d.groupby(['method', 'kind']):
    g = g.set_index('video'); vids = list(g.index)
    def stat(vs):
        n = sum(W[v]['n'] for v in vs); idle = sum(W[v]['idle'] for v in vs); act = sum(W[v]['act'] for v in vs)
        return (sum(g.loc[v, 'stored']*W[v]['n'] for v in vs)/n,
                sum(g.loc[v, 'idle_kept']*W[v]['idle'] for v in vs if W[v]['idle'])/idle,
                sum(g.loc[v, 'frame_recall']*W[v]['act'] for v in vs)/act)
    B = np.array([stat(list(rng.choice(vids, len(vids)))) for _ in range(2000)])
    lo, hi = np.percentile(B, [2.5, 97.5], axis=0)
    out.append(dict(method=m, kind=k, stored_lo=lo[0], stored_hi=hi[0], idle_lo=lo[1], idle_hi=hi[1], rec_lo=lo[2], rec_hi=hi[2]))
pd.DataFrame(out).to_csv('/root/results/event_bootstrap.csv', index=False)
print(pd.DataFrame(out)[lambda x: x.kind == 'clean'].round(3).to_string())
