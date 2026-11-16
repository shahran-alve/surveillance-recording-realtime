"""E2 analysis: per (policy, N, repeat) live results vs. the trace-driven simulation prediction (analysis.json 'cameras' curve, pooled
Phase-1 traces, same clip order / stagger / horizon), largest N with zero misses in every repeat (live) vs. simulated N*, and the
single-camera pass (jobs, misses, service mean/max, agreement with the offline scores). Usage: python e2_analyze.py E2DIR IMGSZ"""
import sys, os, json, glob, numpy as np
ROOT = os.environ.get('SS_ROOT', '/root'); E2, IMGSZ = sys.argv[1], sys.argv[2]
A = json.load(open(ROOT + '/results/rt/analysis.json')); LN = f'{IMGSZ} px, 1 thread'; out = dict(multi=[], nstar={}, single={})
for fn in sorted(glob.glob(E2 + '/live_*_N*_rep*.json')):
    o = json.load(open(fn)); m = o['multi']; s = m['summary']; P = m['policy']; N = m['N']; rep = int(fn.split('_rep')[1].split('.')[0]); curve = A['cameras'][f'{P}|{LN}']['curve']; sim = curve.get(str(N))
    out['multi'].append(dict(policy=P, N=N, rep=rep, jobs=s['jobs'], util=s['util'], miss=s['miss'], n_miss=s['n_miss'], resp_p99_ms=s['resp_p99'], resp_max_ms=s['resp_max'], service_mean_ms=s['service_mean'], service_max_ms=s['service_max'],
                             min_slack_ms=1e3 * s['min_slack'], agree=s['agree'], sim_util=sim['util'] if sim else None, sim_miss=sim['miss'] if sim else None, sim_resp_p99_ms=1e3 * sim['resp_p99'] if sim else None, sim_resp_max_ms=1e3 * sim['resp_max'] if sim else None,
                             load=[o['meta']['loadavg_start'], o['meta']['loadavg_end']], steal=o['meta']['steal_end'] - o['meta']['steal_start'], freq=[o['meta']['freq_start'], o['meta']['freq_end']], torch_threads=[o['meta']['torch_threads'], o['meta']['torch_threads_end']], file=os.path.basename(fn)))
for P in ['Fixed stride 8', 'Adaptive 16/8', 'Adaptive, deadline-aware']:
    rows = [r for r in out['multi'] if r['policy'] == P]; Ns = sorted({r['N'] for r in rows}); ok = [N for N in Ns if all(r['miss'] == 0 for r in rows if r['N'] == N) and len([r for r in rows if r['N'] == N]) >= 2]
    curve = A['cameras'][f'{P}|{LN}']['curve']; simok = [int(n) for n, v in curve.items() if v['miss'] == 0]
    out['nstar'][P] = dict(sim_nstar=A['cameras'][f'{P}|{LN}']['nmax'], live_max_zero_miss_all_repeats=max(ok) if ok else 0, live_N_tested=Ns, live_zero_miss_N=ok, sim_zero_miss_N_in_range=[n for n in simok if n in Ns])
if os.path.exists(E2 + '/live_single.json'):
    o = json.load(open(E2 + '/live_single.json'))
    for P, s in o['single_summary'].items(): out['single'][P] = dict(jobs=s['jobs'], miss=s['miss'], n_miss=s['n_miss'], service_mean_ms=s['service_mean'], service_max_ms=s['service_max'], resp_p99_ms=s['resp_p99'], resp_max_ms=s['resp_max'], agree=s['agree'], n_disagree=s['n_disagree'], max_abs_score_diff=s['max_abs_score_diff'])
    out['single_meta'] = {k: o['meta'][k] for k in ('loadavg_start', 'loadavg_end', 'steal_start', 'steal_end', 'torch_threads', 'torch_threads_end')}
json.dump(out, open(E2 + '/e2_summary.json', 'w'), indent=1, default=float)
for r in out['multi']: print(r['policy'], r['N'], r['rep'], 'jobs', r['jobs'], 'util', round(r['util'], 3), 'miss', round(r['miss'], 3), 'p99', round(r['resp_p99_ms']), 'max', round(r['resp_max_ms']), '| sim util', round(r['sim_util'], 3) if r['sim_util'] is not None else None, 'miss', round(r['sim_miss'], 3) if r['sim_miss'] is not None else None, 'p99', round(r['sim_resp_p99_ms']) if r['sim_resp_p99_ms'] else None, 'max', round(r['sim_resp_max_ms']) if r['sim_resp_max_ms'] else None)
print(json.dumps(out['nstar'], indent=1)); print(json.dumps(out['single'], indent=1))
