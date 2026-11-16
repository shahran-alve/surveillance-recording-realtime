"""Builds the markdown tables for results/rt_<host>/SUMMARY.md from e1_summary.json, e2_summary.json, e3_verify.json and the original
results/rt/analysis*.json. Prints markdown to stdout. Usage: python e_summary_tables.py OUTDIR ORIG_RT_DIR"""
import sys, os, json, numpy as np
OUT, ORIG = sys.argv[1], sys.argv[2]
E1 = json.load(open(OUT + '/e1/e1_summary.json')); A0 = json.load(open(ORIG + '/analysis.json')); B0 = json.load(open(ORIG + '/analysis2.json'))
E2 = json.load(open(OUT + '/e2_640/e2_summary.json')) if os.path.exists(OUT + '/e2_640/e2_summary.json') else None
E2b = json.load(open(OUT + '/e2_320/e2_summary.json')) if os.path.exists(OUT + '/e2_320/e2_summary.json') else None
E3 = json.load(open(OUT + '/e3/e3_verify.json')) if os.path.exists(OUT + '/e3/e3_verify.json') else None
B1 = json.load(open(OUT + '/root/results/rt/analysis2.json')) if os.path.exists(OUT + '/root/results/rt/analysis2.json') else None
CF = ['Detector 640 px', 'Detector 640 px, 2 threads', 'Detector 480 px', 'Detector 320 px']; SH = {'Detector 640 px': '640/1', 'Detector 640 px, 2 threads': '640/2', 'Detector 480 px': '480/1', 'Detector 320 px': '320/1'}
POLS = ['Fixed stride 8', 'Adaptive 16/8', 'Adaptive, deadline-aware']
f1 = lambda x: f'{x:.1f}'; f2 = lambda x: f'{x:.2f}'
def table(head, rows): return '| ' + ' | '.join(head) + ' |\n|' + '---|' * len(head) + '\n' + '\n'.join('| ' + ' | '.join(str(c) for c in r) + ' |' for r in rows) + '\n'
md = []
runs = [k for k in E1['runs'] if 'det' in E1['runs'][k]]
# ---- E1 table 1: distribution per run and config
md.append('### E1.1 Detector service time per run (ms; frames 11+ of every clip, 5,730 samples per run and configuration)\n')
rows = []
for k in runs:
    for c in CF:
        d = E1['runs'][k]['det'][c]; rows.append([k, SH[c], f1(d['mean']), f1(d['p50']), f1(d['p95']), f1(d['p99']), f1(d['p999']), f1(d['max']), f"{d['max_all_frames']:.1f} ({d['max_all_frames_at']})", d['n_gt150'], d['n_gt120']])
for c in CF:
    d = E1['pooled']['all'][c]; rows.append(['pooled 1-5', SH[c], f1(d['mean']), f1(d['p50']), f1(d['p95']), f1(d['p99']), f1(d['p999']), f1(d['max']), f"{d['max_all_frames']:.1f} ({d['max_all_frames_at']})", d['n_gt150'], d['n_gt120']])
md.append(table(['run', 'cfg', 'mean', 'p50', 'p95', 'p99', 'p99.9', 'max (frames 11+)', 'max (all frames, clip:frame)', 'n > 150 ms', 'n > 120 ms'], rows))
f0 = E1['pooled']['all']['Detector 640 px']['frame0_per_clip_per_run']
md.append('Service time of frame 0 of each clip at 640/1, runs 1-5 (ms): ' + '; '.join(f"{v}: {', '.join(f1(x) for x in xs)}" for v, xs in f0.items()) + '. These start-of-clip values are excluded from the distribution columns by the WARM=10 cut of analyze.py (as in the paper) but included in its timing bound (Rmax = lat[idx].max()) and camera simulation.\n')
# ---- E1 table 2: five largest values
md.append('### E1.2 Five largest service times per run (ms, clip:frame)\n')
rows = []
for k in runs:
    for c in CF: rows.append([k, SH[c], ', '.join(f'{t[0]:.1f} ({t[1]}:{t[2]})' for t in E1['runs'][k]['det'][c]['top5'])])
for c in CF: rows.append(['pooled 1-5', SH[c], ', '.join(f'{t[0]:.1f} ({t[1]}:{t[2]}, {t[3]})' for t in E1['pooled']['all'][c]['top5'])])
md.append(table(['run', 'cfg', 'largest five'], rows))
shared = {c: E1['pooled']['all'][c]['top5_frames_shared_by_runs'] for c in CF}
md.append('Frames that appear among the five largest in more than one run: ' + ('; '.join(f'{SH[c]}: ' + (', '.join(f'{f} ({"/".join(r)})' for f, r in s.items()) if s else 'none') for c, s in shared.items())) + '.\n')
if 'spearman_between_runs' in E1['pooled']['all']['Detector 640 px']:
    S = np.array(E1['pooled']['all']['Detector 640 px']['spearman_between_runs']); md.append(f'Spearman rank correlation of per-frame 640/1 service time between runs: min {S[~np.eye(len(S), dtype=bool)].min():.2f}, max {S[~np.eye(len(S), dtype=bool)].max():.2f}.\n')
# ---- E1 table 3: analyze.py quantities per run
md.append('### E1.3 analyze.py per run and pooled: deadline misses (%), k_min, guaranteed cameras floor(k_act*T/C_max) at 12 fps, simulated cameras per core (640/1)\n')
rows = []
def arow(name, A, cmax_ms):
    L = A['latency']['Detector 640 px']; s = A['sched']; cams = A['cameras']
    g = lambda cfg: int(np.floor(8 / 12 / (A['latency'][cfg]['max'] / 1e3)))
    return [name, f1(cmax_ms), f2(L['miss12']), f2(L['miss15']), f2(L['miss30']), f"{s['Detector 640 px']['kmin12']}/{s['Detector 640 px']['kmin15']}/{s['Detector 640 px']['kmin30']}",
            f"{s['Detector 320 px']['kmin12']}/{s['Detector 320 px']['kmin15']}/{s['Detector 320 px']['kmin30']}", f"{g('Detector 640 px')} / {g('Detector 640 px, 2 threads')} / {g('Detector 480 px')} / {g('Detector 320 px')}",
            ' / '.join(str(cams[f'{p}|640 px, 1 thread']) for p in POLS), ' / '.join(str(cams[f'{p}|320 px, 1 thread']) for p in POLS)]
for k in runs:
    if 'analysis' in E1['runs'][k]: rows.append(arow(k, E1['runs'][k]['analysis'], E1['runs'][k]['det']['Detector 640 px']['max']))
if 'analysis' in E1['pooled']: rows.append(arow('pooled (max trace)', E1['pooled']['analysis'], E1['pooled']['analysis']['latency']['Detector 640 px']['max']))
rows.append(arow('paper (VM)', dict(latency=A0['latency'], sched=A0['sched'], cameras={k: v['nmax'] for k, v in A0['cameras'].items()}), A0['latency']['Detector 640 px']['max']))
md.append(table(['run', 'C_max 640/1 (ms, frames 11+)', 'miss 12', 'miss 15', 'miss 30', 'k_min 640/1 12/15/30', 'k_min 320/1 12/15/30', 'guaranteed cams 640/1, 640/2, 480/1, 320/1', 'sim cams 640/1 F8 / A16-8 / DA', 'sim cams 320/1'], rows))
pm = E1['pooled']['all']['Detector 640 px']
md.append(f"Pooled over all samples of runs 1-5 (concatenation): max {pm['max']:.1f} ms, per-run maxima {', '.join(f1(x) for x in pm['per_run_max'])} ms, per-run p99 {', '.join(f1(x) for x in pm['per_run_p99'])} ms; miss rates (mean over runs) 12/15/30 fps: {pm['miss12']:.2f} / {pm['miss15']:.2f} / {pm['miss30']:.2f} %; k_min 12/15/30: {pm['kmin12']}/{pm['kmin15']}/{pm['kmin30']}.\n")
# ---- E1 run conditions
md.append('### E1.4 Run conditions (steal jiffies, core-2 frequency readings between configurations, load average)\n')
rows = []
for k in runs:
    m = E1['runs'][k].get('meta')
    if m: rows.append([k, m['steal_total'], f"{m['freq_min']:.0f}-{m['freq_max']:.0f}", ' '.join(m['load_start']), ' '.join(m['load_end']), f"{m['wall']:.0f}", '; '.join(m['affinities'])])
md.append(table(['run', 'steal (jiffies, whole run)', 'freq range (MHz)', 'load start', 'load end', 'wall (s)', 'affinity sets seen'], rows))
# ---- motion
md.append('### E1.5 Motion triggers per run (ms)\n')
rows = []
for k in runs:
    if 'motion' not in E1['runs'][k]: continue
    for mk, d in E1['runs'][k]['motion'].items(): rows.append([k, mk, f2(d['mean']), f2(d['p50']), f2(d['p99']), f2(d['max']), f2(d['miss30'])])
md.append(table(['run', 'trigger', 'mean', 'p50', 'p99', 'max', 'miss 30 fps (%)'], rows))
# ---- soak
md.append('### E1.6 Soak tests (640/1 and 320/1, 20 min each, pinned to core 2; ms)\n')
rows = []
for k, d in E1['soak'].items(): rows.append([k, d['n'], f1(d['mean']), f1(d['p50']), f1(d['p95']), f1(d['p99']), f1(d['p999']), f1(d['max']), d['n_gt150'], d['n_gt120'], ', '.join(f'{t[0]:.1f} ({t[1]}:{t[2]} #{t[3]})' for t in d['top5']), d['steal']])
md.append(table(['soak', 'jobs', 'mean', 'p50', 'p95', 'p99', 'p99.9', 'max', 'n > 150', 'n > 120', 'largest five (clip:frame #job)', 'steal'], rows))
rows = [[k, ' | '.join(f'{c}: {v:.1f}' for c, v in d['max_vs_count'].items()), f1(d['first_half_max']), f1(d['second_half_max'])] for k, d in E1['soak'].items()]
md.append('Running maximum as a function of sample count (ms):\n\n' + table(['soak', 'max after n samples', 'max first half', 'max second half'], rows))
# ---- E2
def e2tab(E, title):
    md.append(f'### {title}\n'); rows = []
    for r in sorted(E['multi'], key=lambda r: (POLS.index(r['policy']), r['N'], r['rep'])):
        rows.append([r['policy'], r['N'], r['rep'], r['jobs'], f'{r["util"]:.3f}', f'{r["miss"]:.2f} ({r["n_miss"]})', f1(r['resp_p99_ms']), f1(r['resp_max_ms']), f1(r['service_mean_ms']), f1(r['service_max_ms']),
                     f'{r["sim_util"]:.3f}' if r['sim_util'] is not None else '-', f'{r["sim_miss"]:.2f}' if r['sim_miss'] is not None else '-', f1(r['sim_resp_p99_ms']) if r['sim_resp_p99_ms'] else '-', f1(r['sim_resp_max_ms']) if r['sim_resp_max_ms'] else '-', f'{r["agree"]:.1f}', ' '.join(r['load'][1])])
    md.append(table(['policy', 'N', 'rep', 'jobs', 'util', 'miss % (n)', 'resp p99', 'resp max', 'service mean', 'service max', 'sim util', 'sim miss %', 'sim p99', 'sim max', 'decision agree %', 'load end'], rows))
    rows = [[p, v['sim_nstar'], v['live_max_zero_miss_all_repeats'], ', '.join(map(str, v['live_N_tested'])), ', '.join(map(str, v['live_zero_miss_N'])), ', '.join(map(str, v['sim_zero_miss_N_in_range']))] for p, v in E['nstar'].items()]
    md.append('Largest N with zero misses:\n\n' + table(['policy', 'simulated N*', 'live: largest N with 0 misses in both repeats', 'N tested live', 'live N with 0 misses (both repeats)', 'simulated N with 0 misses (tested range)'], rows))
    if E.get('single'):
        rows = [[p, s['jobs'], f'{s["miss"]:.2f} ({s["n_miss"]})', f1(s['service_mean_ms']), f1(s['service_max_ms']), f1(s['resp_p99_ms']), f1(s['resp_max_ms']), f'{s["agree"]:.2f} ({s["n_disagree"]} differ)', f'{s["max_abs_score_diff"]:.2e}'] for p, s in E['single'].items()]
        md.append('Single camera, all seven clips once:\n\n' + table(['policy', 'jobs', 'miss % (n)', 'service mean', 'service max', 'resp p99', 'resp max', 'agreement with offline decisions', 'max |score diff|'], rows))
if E2: e2tab(E2, 'E2.1 Live multi-camera runs, 640 px / 1 thread, 600 s each (ms; "sim" = trace-driven FIFO simulation of analyze.py on the pooled traces for the same N)')
if E2b: e2tab(E2b, 'E2.2 Live multi-camera runs, 320 px / 1 thread, 600 s each')
# ---- E3
if E3:
    md.append('### E3 Recorder checks (all seven clips, three policies, one core vs two cores)\n'); rows = []
    for k, R in E3.items():
        s = R['summary']; rows.append([k, s['n_written'], s['n_expected'], s['a_diff_frames'], f"{s['b_onset_written']}/{s['b_onsets']}", f"{s['b_within_bound']}/{s['b_onsets']}", f"{s['b_delay_median']:.3f}/{s['b_delay_max']:.3f}", f"{s['b_bound_min']:.3f}-{s['b_bound_max']:.3f}", s['c_lost'], s['c_det_lost'],
                                        f"{s['d_decode_ms']['mean']:.2f}/{s['d_decode_ms']['p99']:.2f}/{s['d_decode_ms']['max']:.2f}", f"{s['d_write_ms']['mean']:.2f}/{s['d_write_ms']['p99']:.2f}/{s['d_write_ms']['max']:.2f}", f"{s['d_lateness_ms']['mean']:.2f}/{s['d_lateness_ms']['p99']:.2f}/{s['d_lateness_ms']['max']:.2f}", f"{s['d_lateness_gt_T']}/{s['d_frames']}",
                                        f"{s['d_service_ms']['mean']:.1f}/{s['d_service_ms']['p99']:.1f}/{s['d_service_ms']['max']:.1f}", f"{s['det_agree']:.1f}"])
    md.append(table(['policy | cores', 'frames written', 'record() frames', 'a. differing frames', 'b. onset frame written', 'b. delay within bound', 'b. delay median/max (s)', 'b. bound min-max (s)', 'c. frames lost from ring', 'c. detector frames evicted', 'd. decode ms mean/p99/max', 'd. write ms mean/p99/max', 'd. lateness ms mean/p99/max', 'd. frames later than T', 'd. detector service ms mean/p99/max', 'decision agree %'], rows))
    md.append(f"Phase-1 reference for the detector service time (640/1, pooled runs 1-5): mean {pm['mean']:.1f}, p99 {pm['p99']:.1f}, max {pm['max']:.1f} ms.\n")
    rows = []
    for k, R in E3.items():
        for v, c in R['clips'].items():
            for o in c['onsets']: rows.append([k, v, o['onset'], o.get('first_pos_sample', '-'), f"{o['delay']:.3f}" if 'delay' in o else 'not detected', f"{o['bound']:.3f}" if 'bound' in o else '-', o.get('within', '-'), o.get('onset_written', '-')])
    md.append('Per-onset detail:\n\n' + table(['policy | cores', 'clip', 'onset frame', 'first positive sample', 'alert delay (s)', 'bound (s)', 'within bound', 'onset frame written'], rows))
    rows = [[k, v, c['n_written'], c['n_expected'], len(c['extra_frames']), len(c['missing_frames']), c['duplicates'], len(c['lost']), len(c['det_lost']), c['ring_capacity'], c['segments'], f"{c['lateness_ms']['max']:.2f}", c['lateness_gt_T']] for k, R in E3.items() for v, c in R['clips'].items()]
    md.append('Per-clip detail:\n\n' + table(['policy | cores', 'clip', 'written', 'record()', 'extra', 'missing', 'duplicates', 'lost from ring', 'detector evicted', 'ring capacity', 'segments', 'lateness max (ms)', 'frames later than T'], rows))
# ---- paper vs machine
md.append('### Paper value (VM) vs this machine\n')
PA = E1['pooled']['analysis'] if 'analysis' in E1['pooled'] else None
L0 = A0['latency']['Detector 640 px']; rows = []
def add(name, paper, here, kind): rows.append([name, paper, here, kind])
add('detector 640/1 mean (ms)', f1(L0['mean']), f"{pm['mean']:.1f} (pooled 1-5; per run " + ', '.join(f1(E1['runs'][k]['det']['Detector 640 px']['mean']) for k in runs) + ')', 'timing-dependent')
add('detector 640/1 p95 (ms)', f1(L0['p95']), f1(pm['p95']), 'timing-dependent'); add('detector 640/1 p99 (ms)', f1(L0['p99']), f1(pm['p99']), 'timing-dependent')
add('detector 640/1 max (ms)', f1(L0['max']), f"{pm['max']:.1f} (per run " + ', '.join(f1(x) for x in pm['per_run_max']) + ')', 'timing-dependent')
add('deadline misses 12/15/30 fps (%)', '3.6 / 46.6 / 100', f"{pm['miss12']:.2f} / {pm['miss15']:.2f} / {pm['miss30']:.2f} (mean over runs 1-5)", 'timing-dependent')
for c, pv in [('Detector 320 px', '56.8'), ('Detector 480 px', '67.7'), ('Detector 640 px, 2 threads', '96.1')]: add(f'max {SH[c]} (ms)', pv, f"{E1['pooled']['all'][c]['max']:.1f} (per run " + ', '.join(f1(x) for x in E1['pooled']['all'][c]['per_run_max']) + ')', 'timing-dependent')
add('k_min 640/1 at 12/30 fps', '5 / 11', f"{pm['kmin12']} / {pm['kmin30']}" + (' (per run ' + ', '.join(f"{E1['runs'][k]['det']['Detector 640 px']['kmin12']}/{E1['runs'][k]['det']['Detector 640 px']['kmin30']}" for k in runs) + ')'), 'timing-dependent')
g = lambda c: int(np.floor(8 / 12 / (E1['pooled']['all'][c]['max'] / 1e3)))
add('guaranteed cameras 640/1, 640/2, 480/1, 320/1 (12 fps)', '1 / 6 / 9 / 11', ' / '.join(str(g(c)) for c in CF), 'timing-dependent')
if PA:
    add('simulated cameras 640/1 (F8 / A16-8 / DA)', '10 / 12 / 10', ' / '.join(str(PA['cameras'][f'{p}|640 px, 1 thread']) for p in POLS) + ' (pooled max trace; per run ' + '; '.join('/'.join(str(E1['runs'][k]['analysis']['cameras'][f'{p}|640 px, 1 thread']) for p in POLS) for k in runs if 'analysis' in E1['runs'][k]) + ')', 'timing-dependent')
    add('simulated cameras 320/1 (F8 / A16-8 / DA)', '31 / 38 / 35', ' / '.join(str(PA['cameras'][f'{p}|320 px, 1 thread']) for p in POLS), 'timing-dependent')
    T = PA['timing']; add('detectable onsets', '15', ' / '.join(str(T[f'{p}|1.0']['n']) for p in POLS), 'expected-identical (depends only on scores and theta)')
    add('onset stored (%) F8 / A16-8 / DA', '100 / 73 / 100', ' / '.join(f"{T[f'{p}|1.0']['onset_stored']:.0f}" for p in POLS), 'expected-identical (sampling plan depends only on scores)')
    add('delay median/max (s) F8, A16-8, DA', '0.47/0.76, 1.05/1.36, 0.74/0.95', ', '.join(f"{T[f'{p}|1.0']['median']:.2f}/{T[f'{p}|1.0']['max']:.2f}" for p in POLS), 'timing-dependent (adds measured service time to a fixed frame offset)')
    add('detector runs (%) F8 / A16-8 / DA', '12.5 / 10.1 / 11.1', ' / '.join(f"{PA['policy'][f'{p}|1.0']['clean']['calls']:.1f}" for p in POLS), 'expected-identical')
if E2 and E2.get('single'): add('single-camera live jobs F8 / A16-8 / DA', '729 / 589 / 644', ' / '.join(str(E2['single'][p]['jobs']) for p in POLS), 'expected-identical')
if B1: add('hybrid gate misses (%) MOG2 / CNT / FD (clean)', '5.9 / 1.9 / 1.3', ' / '.join(f"{B1['hybrid'][f'{g}|clean']['miss']:.1f}" for g in ['MOG2', 'CNT', 'FD']), 'timing-dependent')
md.append(table(['quantity', 'paper (VM)', 'this machine', 'kind'], rows))
print('\n'.join(md))
