"""E1 analysis: per-run and pooled service-time statistics of the detector (and motion triggers), tail reproducibility, soak-test
statistics, and the analyze.py quantities per run and pooled. Writes e1_summary.json and e1_tables.md in --e1dir.
Pooled traces: 'pooled_max' = element-wise maximum over runs 1-5 per (config, clip, frame) -> C_max is the worst case over runs
(this trace is what analyze.py was run on for the pooled row); 'pooled_all' = concatenation of all samples of runs 1-5 (distribution
statistics, miss rates = mean over runs)."""
import sys, os, json, glob, numpy as np
ROOT = os.environ.get('SS_ROOT', '/root'); sys.path.insert(0, ROOT + '/exp')
from common import VIDEOS, video_info
E1 = sys.argv[1]; VIDS = list(VIDEOS); FPS = {v: video_info(v)[0] for v in VIDS}; WARM = 10
CFGS = [('640|1', 'Detector 640 px'), ('640|2', 'Detector 640 px, 2 threads'), ('480|1', 'Detector 480 px'), ('320|1', 'Detector 320 px')]
MOT = ['FD', 'CNT', 'MOG2', 'KNN', 'FLOW', 'GSOC']
def fifo(release, service):
    fin = np.empty(len(release)); t = 0.0
    for i in range(len(release)):
        t = max(t, release[i]) + service[i]; fin[i] = t
    return fin - release
def stats(x):
    x = np.asarray(x) * 1e3
    return dict(n=len(x), mean=x.mean(), p50=np.percentile(x, 50), p95=np.percentile(x, 95), p99=np.percentile(x, 99), p999=np.percentile(x, 99.9), max=x.max(), n_gt150=int((x > 150).sum()), n_gt120=int((x > 120).sum()))
def top5(key, z):
    rows = []
    for v in VIDS:
        x = z[f'{key}|{v}'][WARM:]
        for i in np.argsort(x)[-5:]: rows.append((1e3 * x[i], v, int(i) + WARM))
    return sorted(rows, reverse=True)[:5]
def misses(key, z):
    r = {}
    for fps in (12, 15, 30):
        T = 1 / fps; mm = []
        for v in VIDS:
            s = z[f'{key}|{v}'][WARM:]; mm.append(fifo(np.arange(len(s)) * T, s) > T)
        r[fps] = 100 * float(np.concatenate(mm).mean())
    return r
runs = sorted(d for d in glob.glob(E1 + '/run*') if os.path.isdir(d)); out = dict(runs={}, pooled={}, soak={}); md = []
Z = {}
for d in runs:
    k = os.path.basename(d); r = {}
    if os.path.exists(d + '/lat_det.npz'):
        z = np.load(d + '/lat_det.npz'); Z[k] = z; r['det'] = {}
        for key, name in CFGS:
            x = np.concatenate([z[f'lat|{key}|{v}'][WARM:] for v in VIDS]); mi = misses('lat|' + key, z)
            am = max(((1e3 * z[f'lat|{key}|{v}'].max(), v, int(z[f'lat|{key}|{v}'].argmax())) for v in VIDS))
            r['det'][name] = stats(x) | dict(max_all_frames=am[0], max_all_frames_at=f'{am[1]}:{am[2]}', first10_max=max(1e3 * z[f'lat|{key}|{v}'][:10].max() for v in VIDS), top5=top5('lat|' + key, z), miss12=mi[12], miss15=mi[15], miss30=mi[30], kmin12=int(np.ceil(x.max() * 12)), kmin15=int(np.ceil(x.max() * 15)), kmin30=int(np.ceil(x.max() * 30)),
                                                guaranteed_cams=int(np.floor(8 / 12 / x.max())))
        if os.path.exists(d + '/meta_det.json'):
            mt = json.load(open(d + '/meta_det.json')); r['meta'] = dict(steal_total=mt['steal_end'] - mt['steal_start'], steal_per_cfg_max=max(c['steal_delta'] for c in mt['per_cfg']), freq_start=mt['freq_start'], freq_end=mt['freq_end'],
                                                                             freq_min=min(c['freq_after'] for c in mt['per_cfg'] if c['freq_after']), freq_max=max(c['freq_after'] for c in mt['per_cfg'] if c['freq_after']),
                                                                             load_start=mt['loadavg_start'], load_end=mt['loadavg_end'], affinities=sorted({str(c['affinity_all']) for c in mt['per_cfg']}), wall=mt['end'] - mt['start'])
    if os.path.exists(d + '/lat_motion.npz'):
        zm = np.load(d + '/lat_motion.npz'); r['motion'] = {}
        for mk in MOT:
            x = np.concatenate([zm[f'{mk}|{v}'][WARM:] for v in VIDS]); mi = misses(mk, zm); r['motion'][mk] = stats(x) | dict(top5=top5(mk, zm), miss12=mi[12], miss15=mi[15], miss30=mi[30])
    if os.path.exists(d + '/analysis.json'):
        A = json.load(open(d + '/analysis.json')); r['analysis'] = dict(latency={n: {k2: A['latency'][n][k2] for k2 in ('mean', 'p50', 'p95', 'p99', 'max', 'miss12', 'miss15', 'miss30')} for _, n in CFGS},
                                                                      sched={n: {k2: A['sched'][n][k2] for k2 in ('kmin12', 'kmin15', 'kmin30')} for _, n in CFGS},
                                                                      cameras={k2: v['nmax'] for k2, v in A['cameras'].items()}, timing={k2: {a: b for a, b in v.items() if a != 'delays'} for k2, v in A['timing'].items() if k2.endswith('|1.0')},
                                                                      theta=A['theta'], cmax_ms=1e3 * max(np.load(d + '/lat_det.npz')[f'lat|640|1|{v}'].max() for v in VIDS))
    out['runs'][k] = r
# ---- pooled over runs 1-5 (profile runs with per-config pinning)
P = [k for k in Z if k != 'run0']
if P:
    pooled_all = {}; pooled_max = {}
    for key, name in CFGS:
        allx = np.concatenate([np.concatenate([Z[k][f'lat|{key}|{v}'][WARM:] for v in VIDS]) for k in P])
        top = sorted(sum([[(t[0], t[1], t[2], k) for t in top5('lat|' + key, Z[k])] for k in P], []), reverse=True)[:5]
        mi = {fps: float(np.mean([misses('lat|' + key, Z[k])[fps] for k in P])) for fps in (12, 15, 30)}
        pooled_all[name] = stats(allx) | dict(top5=top, miss12=mi[12], miss15=mi[15], miss30=mi[30], kmin12=int(np.ceil(allx.max() * 12)), kmin15=int(np.ceil(allx.max() * 15)), kmin30=int(np.ceil(allx.max() * 30)),
                                               guaranteed_cams=int(np.floor(8 / 12 / allx.max())), per_run_max=[1e3 * float(np.concatenate([Z[k][f'lat|{key}|{v}'][WARM:] for v in VIDS]).max()) for k in P],
                                               per_run_p99=[1e3 * float(np.percentile(np.concatenate([Z[k][f'lat|{key}|{v}'][WARM:] for v in VIDS]), 99)) for k in P])
        # are the largest values on the same frames across runs?
        fr = {}
        for k in P:
            for t in top5('lat|' + key, Z[k]): fr.setdefault((t[1], t[2]), []).append(k)
        am = max(((1e3 * Z[k][f'lat|{key}|{v}'].max(), v, int(Z[k][f'lat|{key}|{v}'].argmax()), k) for k in P for v in VIDS))
        pooled_all[name]['max_all_frames'] = am[0]; pooled_all[name]['max_all_frames_at'] = f'{am[1]}:{am[2]} ({am[3]})'
        pooled_all[name]['per_run_max_all_frames'] = [max(1e3 * Z[k][f'lat|{key}|{v}'].max() for v in VIDS) for k in P]
        pooled_all[name]['frame0_per_clip_per_run'] = {v: [1e3 * float(Z[k][f'lat|{key}|{v}'][0]) for k in P] for v in VIDS}
        pooled_all[name]['top5_frames_shared_by_runs'] = {f'{v}:{i}': ks for (v, i), ks in fr.items() if len(ks) > 1}
        # rank correlation of per-frame service time between runs (640/1): do the same frames tend to be slow?
        if key == '640|1':
            from scipy.stats import spearmanr
            mats = [np.concatenate([Z[k][f'lat|{key}|{v}'][WARM:] for v in VIDS]) for k in P]
            pooled_all[name]['spearman_between_runs'] = [[float(spearmanr(mats[i], mats[j])[0]) for j in range(len(P))] for i in range(len(P))]
    out['pooled']['all'] = pooled_all; out['pooled']['runs'] = P
    if os.path.exists(E1 + '/pooled/analysis.json'):
        A = json.load(open(E1 + '/pooled/analysis.json')); out['pooled']['analysis'] = dict(latency={n: {k2: A['latency'][n][k2] for k2 in ('mean', 'p50', 'p95', 'p99', 'max', 'miss12', 'miss15', 'miss30')} for _, n in CFGS},
            sched={n: {k2: A['sched'][n][k2] for k2 in ('kmin12', 'kmin15', 'kmin30')} for _, n in CFGS}, cameras={k2: v['nmax'] for k2, v in A['cameras'].items()},
            cameras_curve={k2: v['curve'] for k2, v in A['cameras'].items()}, timing={k2: {a: b for a, b in v.items() if a != 'delays'} for k2, v in A['timing'].items()}, theta=A['theta'], theta_lowres=A['theta_lowres'],
            policy=A['policy'], onset_events=A['onset_events'], cameras_motion=A['cameras_motion'], motion_latency={n: {k2: A['latency'][n][k2] for k2 in ('mean', 'p50', 'p95', 'p99', 'max', 'miss12', 'miss15', 'miss30')} for n in ('FD', 'CNT', 'MOG2', 'KNN', 'Optical flow', 'GSOC')})
# ---- soak
for f in sorted(glob.glob(E1 + '/soak/*.npz')):
    z = np.load(f); s = z['service']; mt = json.load(open(f.replace('.npz', '_meta.json'))); k = os.path.basename(f)[:-4]
    i5 = np.argsort(s)[-5:][::-1]; cps = [100, 300, 1000, 3000, 10000, 30000, 100000]
    out['soak'][k] = stats(s) | dict(top5=[(1e3 * float(s[i]), str(z['clip'][i]), int(z['frame'][i]), int(i)) for i in i5], max_vs_count={str(c): 1e3 * float(s[:c].max()) for c in cps if c <= len(s)} | {str(len(s)): 1e3 * float(s.max())},
                                   minutes=mt['minutes'], mode=mt['mode'], imgsz=mt['imgsz'], steal=mt['steal_end'] - mt['steal_start'], load_start=mt['loadavg_start'], load_end=mt['loadavg_end'], freq=[mt['freq_start'], mt['freq_end']],
                                   gt150_idx=[int(i) for i in np.where(s > 0.150)[0]], first_half_max=1e3 * float(s[:len(s) // 2].max()), second_half_max=1e3 * float(s[len(s) // 2:].max()))
json.dump(out, open(E1 + '/e1_summary.json', 'w'), indent=1, default=float); print('written', E1 + '/e1_summary.json')
