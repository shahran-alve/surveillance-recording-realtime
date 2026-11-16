"""Section 9 analysis: per run (condition x run) mean, p50, p99, max (frames 11+), system-time share and minor page faults per second
(timed part and warm-up), plus per-clip medians; writes e9_summary.json. Usage: python e9_analyze.py OUTDIR"""
import sys, os, json, glob, numpy as np
ROOT = os.environ.get('SS_ROOT', '/root'); sys.path.insert(0, ROOT + '/exp')
from common import VIDEOS
OUT = sys.argv[1]; VIDS = list(VIDEOS); WARM = 10; out = {}
for cond in ['default', 'malloc', 'thp']:
    R = {}
    for d in sorted(glob.glob(OUT + f'/e9/{cond}/run*')):
        if not os.path.exists(d + '/meta_det.json'): continue
        z = np.load(d + '/lat_det.npz'); mt = json.load(open(d + '/meta_det.json')); k = os.path.basename(d)
        x = np.concatenate([z[f'lat|640|1|{v}'][WARM:] for v in VIDS]) * 1e3; cfg = mt['per_cfg']
        user = sum(c['cpustat_delta'][0] for c in cfg); sysj = sum(c['cpustat_delta'][2] for c in cfg); wall = sum(c['wall'] for c in cfg); mf = sum(c['minflt'] for c in cfg)
        R[k] = dict(order=mt['order'], mean=x.mean(), p50=np.percentile(x, 50), p95=np.percentile(x, 95), p99=np.percentile(x, 99), p999=np.percentile(x, 99.9), max=x.max(), max_all_frames=1e3 * max(z[f'lat|640|1|{v}'].max() for v in VIDS),
                    sys_share=sysj / max(1, user + sysj), minflt_per_s=mf / wall, minflt_total=mf, per_clip_median={v: 1e3 * float(np.median(z[f'lat|640|1|{v}'][WARM:])) for v in VIDS}, per_clip_sys={c['clip']: c['sys_share'] for c in cfg},
                    per_clip_minflt_per_s={c['clip']: c['minflt_per_s'] for c in cfg}, warmup=dict(jobs=mt['warmup']['jobs'], mean_ms=mt['warmup']['mean_ms'], sys_share=mt['warmup']['cpustat_delta'][2] / max(1, mt['warmup']['cpustat_delta'][0] + mt['warmup']['cpustat_delta'][2]), minflt_per_s=mt['warmup']['minflt_per_s']),
                    thp_status=mt.get('thp_status'), thp_prctl_rc=mt.get('thp_prctl_rc'), malloc_env=mt.get('malloc_env'), steal=mt['steal_end'] - mt['steal_start'], load=[mt['loadavg_start'], mt['loadavg_end']], torch_threads=sorted({c['torch_threads'] for c in cfg}), start=mt['start'])
    if R:
        allx = np.concatenate([np.concatenate([np.load(OUT + f'/e9/{cond}/{k}/lat_det.npz')[f'lat|640|1|{v}'][WARM:] for v in VIDS]) for k in R]) * 1e3
        out[cond] = dict(runs=R, pooled=dict(n=len(allx), mean=allx.mean(), p50=np.percentile(allx, 50), p99=np.percentile(allx, 99), max=allx.max(), means=[r['mean'] for r in R.values()], sys=[r['sys_share'] for r in R.values()], mf=[r['minflt_per_s'] for r in R.values()],
                                                 n_high=sum(1 for r in R.values() if r['mean'] > 52.0), n_clip_high=sum(1 for r in R.values() for v in VIDS if r['per_clip_median'][v] > 52.0), n_clips=7 * len(R)))
json.dump(out, open(OUT + '/e9_summary.json', 'w'), indent=1, default=float); print('written', OUT + '/e9_summary.json')
for c, d in out.items(): print(c, 'means', [round(m, 1) for m in d['pooled']['means']], 'sys%', [round(100 * s, 1) for s in d['pooled']['sys']], 'minflt/s', [round(m) for m in d['pooled']['mf']], 'high runs', d['pooled']['n_high'], 'high clips', d['pooled']['n_clip_high'], '/', d['pooled']['n_clips'])
