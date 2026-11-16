"""Section 8 analysis: (A) E2 320-px deadline-aware extension N = 38-40 (same columns as E2.2), (B) E1 extension runs (e1b), and the
per-process mean service time of all E2 640-px runs. Writes e8_summary.json and appends/overwrites nothing else. Usage: python e8_analyze.py OUTDIR"""
import sys, os, json, glob, numpy as np
ROOT = os.environ.get('SS_ROOT', '/root'); sys.path.insert(0, ROOT + '/exp')
from common import VIDEOS, video_info
OUT = sys.argv[1]; VIDS = list(VIDEOS); FPS = {v: video_info(v)[0] for v in VIDS}; WARM = 10; A = json.load(open(ROOT + '/results/rt/analysis.json')); out = {}
def fifo(release, service):
    fin = np.empty(len(release)); t = 0.0
    for i in range(len(release)):
        t = max(t, release[i]) + service[i]; fin[i] = t
    return fin - release
# ---- A
P = 'Adaptive, deadline-aware'; curve = A['cameras'][f'{P}|320 px, 1 thread']['curve']; rows = []
for fn in sorted(glob.glob(OUT + '/e2_320/live_Adaptivedeadline-aware_N*_rep*.json')):
    o = json.load(open(fn)); m = o['multi']; s = m['summary']; N = m['N']; rep = int(fn.split('_rep')[1].split('.')[0]); sim = curve.get(str(N)); r = m['rec']; miss = [x for x in r if x['miss']]
    rows.append(dict(N=N, rep=rep, jobs=s['jobs'], util=s['util'], miss=s['miss'], n_miss=s['n_miss'], resp_p99_ms=s['resp_p99'], resp_max_ms=s['resp_max'], service_mean_ms=s['service_mean'], service_max_ms=s['service_max'], agree=s['agree'],
                     sim_util=sim['util'] if sim else None, sim_miss=sim['miss'] if sim else None, sim_resp_p99_ms=1e3 * sim['resp_p99'] if sim else None, sim_resp_max_ms=1e3 * sim['resp_max'] if sim else None, load_end=o['meta']['loadavg_end'],
                     miss_per_60s=np.histogram([x['release'] for x in miss], bins=np.arange(0, 601, 60))[0].tolist(), new=N in (38, 39, 40)))
rows.sort(key=lambda r: (r['N'], r['rep'])); Ns = sorted({r['N'] for r in rows}); ok = [N for N in Ns if len([r for r in rows if r['N'] == N]) >= 2 and all(r['miss'] == 0 for r in rows if r['N'] == N)]
out['A'] = dict(rows=rows, live_max_zero_miss_all_repeats=max(ok) if ok else 0, zero_miss_N=ok, N_tested=Ns, sim_nstar=A['cameras'][f'{P}|320 px, 1 thread']['nmax'], sim_zero_miss=[int(n) for n, v in curve.items() if v['miss'] == 0 and int(n) in Ns])
# ---- B: e1b runs
runs = sorted(d for d in glob.glob(OUT + '/e1b/run*') if os.path.exists(d + '/meta_det.json')); B = {}; allx = []; per_run = []
for d in runs:
    z = np.load(d + '/lat_det.npz'); mt = json.load(open(d + '/meta_det.json')); k = os.path.basename(d)
    x = np.concatenate([z[f'lat|640|1|{v}'][WARM:] for v in VIDS]) * 1e3; allx.append(x)
    mi = {}
    for fps in (12, 15, 30):
        T = 1 / fps; mm = []
        for v in VIDS:
            s = z[f'lat|640|1|{v}'][WARM:]; mm.append(fifo(np.arange(len(s)) * T, s) > T)
        mi[fps] = 100 * float(np.concatenate(mm).mean())
    cfg = {c['clip']: c for c in mt['per_cfg']}; first = mt['order'][0]
    B[k] = dict(order=mt['order'], warmup=mt['warmup'], n=len(x), mean=x.mean(), p50=np.percentile(x, 50), p95=np.percentile(x, 95), p99=np.percentile(x, 99), p999=np.percentile(x, 99.9), max=x.max(), max_all_frames=1e3 * max(z[f'lat|640|1|{v}'].max() for v in VIDS),
                per_clip_median={v: 1e3 * float(np.median(z[f'lat|640|1|{v}'][WARM:])) for v in VIDS}, per_clip_frame0={v: 1e3 * float(z[f'lat|640|1|{v}'][0]) for v in VIDS}, sys_share={v: cfg[v]['sys_share'] for v in VIDS},
                sys_share_total=sum(cfg[v]['cpustat_delta'][2] for v in VIDS) / sum(cfg[v]['cpustat_delta'][0] + cfg[v]['cpustat_delta'][2] for v in VIDS), miss12=mi[12], miss15=mi[15], miss30=mi[30], first_clip=first,
                first_clip_median=1e3 * float(np.median(z[f'lat|640|1|{first}'][WARM:])), first_clip_sys_share=cfg[first]['sys_share'], steal=mt['steal_end'] - mt['steal_start'], load=[mt['loadavg_start'], mt['loadavg_end']], torch_threads=sorted({c['torch_threads'] for c in mt['per_cfg']}))
if allx:
    x = np.concatenate(allx); out['B'] = dict(runs=B, pooled=dict(n=len(x), mean=x.mean(), p50=np.percentile(x, 50), p95=np.percentile(x, 95), p99=np.percentile(x, 99), p999=np.percentile(x, 99.9), max=x.max(), miss12=float(np.mean([B[k]['miss12'] for k in B])), miss15=float(np.mean([B[k]['miss15'] for k in B])), miss30=float(np.mean([B[k]['miss30'] for k in B]))))
    # reference: original runs 1-5 one-by-one median and the other clips
    E1 = json.load(open(OUT + '/e1/e1_summary.json')); ref = {}
    for k in ['run1', 'run2', 'run3', 'run4', 'run5']:
        z = np.load(OUT + f'/e1/{k}/lat_det.npz'); ref[k] = {v: 1e3 * float(np.median(z[f'lat|640|1|{v}'][WARM:])) for v in VIDS}
    out['B']['reference_e1_per_clip_median'] = ref
# ---- C: per-process mean service time of the E2 640-px runs
rows = []
for fn in sorted(glob.glob(OUT + '/e2_640/live_*_N*_rep*.json')):
    o = json.load(open(fn)); m = o['multi']; r = m['rec']; s = np.array([x['service'] for x in r]) * 1e3
    rows.append(dict(file=os.path.basename(fn), policy=m['policy'], N=m['N'], rep=int(fn.split('_rep')[1].split('.')[0]), jobs=len(r), service_mean=s.mean(), service_p50=float(np.percentile(s, 50)), service_p99=float(np.percentile(s, 99)), service_max=s.max(),
                     first120_mean=float(np.mean([x['service'] for x in r if x['release'] < 120])) * 1e3, rest_mean=float(np.mean([x['service'] for x in r if x['release'] >= 120])) * 1e3, util=m['summary']['util'], miss=m['summary']['miss'], start=o['meta']['t_start'], torch_threads=o['meta']['torch_threads_end']))
o = json.load(open(OUT + '/e2_640/live_single.json'))
for p, rec in o['single'].items():
    s = np.array([x['service'] for x in rec]) * 1e3; rows.append(dict(file='live_single.json', policy=p, N=1, rep=0, jobs=len(rec), service_mean=s.mean(), service_p50=float(np.percentile(s, 50)), service_p99=float(np.percentile(s, 99)), service_max=s.max(), first120_mean=None, rest_mean=None, util=None, miss=0.0, start=o['meta']['t_start'], torch_threads=o['meta']['torch_threads_end']))
rows.sort(key=lambda r: r['service_mean']); means = np.array([r['service_mean'] for r in rows if r['N'] > 1]); gaps = np.diff(means); g = int(np.argmax(gaps))
out['C'] = dict(rows=rows, sorted_means=means.tolist(), largest_gap_ms=float(gaps[g]), gap_between=[float(means[g]), float(means[g + 1])], group_low=means[:g + 1].tolist(), group_high=means[g + 1:].tolist(),
                mean_of_gaps_excluding_largest=float(np.mean(np.delete(gaps, g))), max_other_gap=float(np.max(np.delete(gaps, g))))
json.dump(out, open(OUT + '/e8_summary.json', 'w'), indent=1, default=float); print('written', OUT + '/e8_summary.json')
