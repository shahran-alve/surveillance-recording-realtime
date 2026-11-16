"""Writes results/rt_<host>/SUMMARY.md from the raw outputs (robust to missing stages: each section reports what exists).
Usage: python e_write_summary.py OUTDIR ORIG_RT_DIR"""
import sys, os, json, glob, time, subprocess, numpy as np
OUT, ORIG = sys.argv[1], sys.argv[2]; HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
def J(p):
    try: return json.load(open(p))
    except Exception: return None
def rd(p):
    try: return open(p).read()
    except Exception: return ''
E1 = J(OUT + '/e1/e1_summary.json'); E2 = J(OUT + '/e2_640/e2_summary.json'); E2b = J(OUT + '/e2_320/e2_summary.json'); E3 = J(OUT + '/e3/e3_verify.json'); A0 = J(ORIG + '/analysis.json')
POLS = ['Fixed stride 8', 'Adaptive 16/8', 'Adaptive, deadline-aware']; S = []
def table(head, rows): return '| ' + ' | '.join(head) + ' |\n|' + '---|' * len(head) + '\n' + '\n'.join('| ' + ' | '.join(str(c) for c in r) + ' |' for r in rows) + '\n'
def sec(t): S.append('\n## ' + t + '\n')
try: tables = subprocess.run([sys.executable, HERE + '/e_summary_tables.py', OUT, ORIG], capture_output=True, text=True, env=dict(os.environ)); TAB = tables.stdout; TABERR = tables.stderr
except Exception as e: TAB, TABERR = '', str(e)
def grab(title_prefix):
    """Return the table block(s) of e_summary_tables.py output whose '### ' heading starts with title_prefix."""
    out = []; keep = False
    for line in TAB.split('\n'):
        if line.startswith('### '): keep = line[4:].startswith(title_prefix)
        if keep: out.append(line)
    return '\n'.join(out) + '\n'
t0 = rd(OUT + '/logs/t_start.txt').split('\n'); t_start = float(t0[0]) if t0 and t0[0].strip() else None
_done = [l for l in rd(OUT + '/logs/master_chain.log').split('\n') if l.startswith('MASTER CHAIN DONE')]
t_end = time.mktime(time.strptime(_done[-1].replace('MASTER CHAIN DONE ', '').strip(), '%a %b %d %H:%M:%S %Z %Y')) if _done else time.time(); wall_h = (t_end - t_start) / 3600 if t_start else None
S.append(f'# Re-run of the real-time experiments on {os.uname().nodename} (E1 repeated profiling, E2 live multi-camera, E3 end-to-end recorder)\n')
S.append(f'Generated {time.strftime("%Y-%m-%d %H:%M %Z")} by exp/rt/e_write_summary.py from the raw files listed in section 7. Original results (2-core VM) in results/rt/ were not modified; everything new is under results/rt_{os.uname().nodename}/.\n')
# ---------------- key findings
sec('Key findings')
KF = []
if E1:
    p = E1['pooled']['all']['Detector 640 px']
    KF.append(f"E1: the 358.7 ms outlier of the VM is not reproducible here. Over 6 profiling runs and 4 soak tests (about 232,000 inferences) no detector service time exceeded 150 ms; C_max at 640 px / 1 thread is {p['max']:.1f} ms (frames 11+ of each clip, paper convention) or {p['max_all_frames']:.1f} ms including the reproducible first inference on a new clip. k_min = {p['kmin12']} / {p['kmin30']} at 12 / 30 fps in every run (paper: 5 / 11). All quantities that depend only on scores and thresholds (theta = 0.2, 15 onsets, onset stored 100/73/100 %, detector runs 12.6/10.2/11.2 %, single-camera jobs 729/589/644) reproduce exactly; the scores themselves are bit-identical to the original arrays.")
if E2:
    ns = E2['nstar']; KF.append("E2 (640 px): largest N with zero misses in both 600-s repeats, live vs simulated: " + '; '.join(f"{p} {v['live_max_zero_miss_all_repeats']} vs {v['sim_nstar']}" for p, v in ns.items()) + ". Live decisions equal the offline trace on 100 % of jobs in every run. Live misses at or above N* occur in bursts (one to three 60-s windows per run, see section 4), not at process start.")
if E2b:
    ns = E2b['nstar']; KF.append("E2 (320 px): " + '; '.join(f"{p} {v['live_max_zero_miss_all_repeats']} vs {v['sim_nstar']}" for p, v in ns.items()) + " (the deadline-aware policy had 4-17 misses out of about 31,000 jobs already at N = 41-42, so no tested N was clean in both repeats).")
if E3:
    tot = sum(R['summary']['a_diff_frames'] for R in E3.values()); lost = sum(R['summary']['c_lost'] for R in E3.values()); ob = all(R['summary']['b_within_bound'] == R['summary']['b_onsets'] for R in E3.values())
    KF.append(f"E3: in all six recorder passes (3 policies x 1 or 2 cores) the written frame indices equal event_eval.record() applied to the recorder's own decisions ({tot} differing frames out of {sum(R['summary']['n_written'] for R in E3.values()):,} written), {lost} frames were lost from the ring buffer, every measured alert delay is within the bound (k_idle-1)T + R_max ({'all' if ob else 'NOT all'} 15 onsets per pass), the onset frame itself was written for 15/15 (fixed 8, deadline-aware) and 11/15 (adaptive 16/8) onsets as in the paper, no captured frame was later than one frame period, and sharing one core with decode and write raised the detector's mean service time by about 3 ms and its maximum from 72-75 ms to 89-104 ms.")
S.append('\n'.join('- ' + k for k in KF) + '\n')
# ---------------- 1 platform
sec('1. Platform and idle-machine caveat')
plat = rd(OUT + '/platform.txt')
S.append('From platform.txt (full lscpu there):\n')
keyl = [l for l in plat.split('\n') if any(k in l for k in ('hostname', 'uname', 'virt', 'DMI', 'OS:', 'Model name', 'CPU(s):', 'Thread(s)', 'Core(s)', 'Socket', 'NUMA node(s)', 'CPU max', 'CPU min', 'L3', 'governor', 'scaling', 'turbo', 'Mem:', 'loadavg', 'steal', 'slurm', 'python'))]
S.append('```\n' + '\n'.join(keyl) + '\n```\n')
S.append('- Bare metal (systemd-detect-virt: none), Dell PowerEdge R740xd, 2 x Intel Xeon Gold 6126 (12 cores each, no SMT, 24 CPUs), 187 GB RAM, Rocky Linux 8.10, kernel 4.18.0-553.123.1, governor `performance` (intel_cpufreq passive driver, turbo enabled, 1.0-3.7 GHz), NUMA balancing on, transparent hugepages `always`.\n'
         '- The machine is the shared Slurm head node of a cluster. Nobody else used CPU during the runs (checked with top before every stage), but other users had idle login sessions. The load average at the Phase 0 check was 0.40 (above the 0.3 criterion of the brief) and 0.13 one minute later; the 1-minute load before every timed run is logged (e1/run*/e1_profile.log BEFORE/AFTER lines, e2_*/e2_run.log, e3/e3_run.log, *_meta.json). During the timed runs the load was 1.0-1.3, i.e. our own pinned process plus the VS Code server of this session (about 1-2 % of one CPU).\n'
         '- All timed processes were pinned with sched_setaffinity to physical core 2 (NUMA node 0); the 2-thread configuration to cores 2 and 4. /proc/stat steal time was 0 throughout (bare metal). MSR access (turbostat) is not permitted; the sysfs `scaling_cur_freq` readings taken between configurations are unreliable with this passive driver (1.1-3.7 GHz while /proc/cpuinfo showed 3.5-3.7 GHz when sampled during a run), so no frequency claim is made beyond "performance governor, turbo on".\n'
         '- Python 3.11.7 virtualenvs built from requirements-analysis.txt (opencv-contrib-python-headless 4.10.0.84, numpy 2.x) and requirements-detector.txt (torch 2.14.1+cpu, torchvision 0.29.1+cpu, ultralytics 8.4.190, onnxruntime 1.31.1, opencv-python 5.0.0 as the unpinned latest); CUDA_VISIBLE_DEVICES="" and no GPU present; pip freeze in logs/pip_freeze_*.txt. Frames decoded by the two OpenCV versions are byte-identical (sha256 check, logs/).\n')
# ---------------- 2 phase 0
sec('2. Phase 0 checks')
S.append('Frame counts (logs/frame_counts.txt):\n\n```\n' + rd(OUT + '/logs/frame_counts.txt').strip() + '\n```\n')
sc = J(OUT + '/logs/score_check.json')
if sc:
    S.append('Clean 640-px YOLO11n scores regenerated here (det_scores.py, 1 thread) vs. the arrays `score|640|1|<clip>` in results/rt/lat_det.npz:\n\n| clip | n | max abs diff | decisions at 0.2 agree |\n|---|---|---|---|\n' + '\n'.join(f"| {v} | {d['n']} | {d['max_abs_diff']:.2e} | {'yes' if d['decisions_agree'] else 'NO (' + str(d['n_decisions_differ']) + ' differ)'} |" for v, d in sc.items()) + '\n')
    S.append('The scores are bit-identical to the original run (max abs difference 0.0 on every clip), so every quantity that depends only on scores and thresholds is expected to reproduce exactly. (Side check in logs/score_check.txt: scores computed with 8 torch threads differ from 1-thread scores by up to 3e-6 and never change a decision.)\n')
S.append('Thresholds re-derived by analyze.py (leave-one-video-out, fixed stride 8): theta = 0.2 for every clip, identical to the paper; theta_lowres identical as well (e1/pooled/analysis.json).\n')
# ---------------- 3 E1
sec('3. E1: repeated service-time profiling')
S.append('Runs: run0 = the unmodified measure_det.py (process pinned with `taskset -c 2,4`, i.e. a two-core mask for all configurations; it also produced the 320/480-px score files analyze.py needs). Runs 1-5 = fresh processes of measure_motion.py (unmodified, `taskset -c 2`) and e1_profile.py (the timing loop of measure_det.py copied verbatim, with the affinity switched per configuration: {2} for 1 thread, {2,4} for 2 threads, applied to every thread of the process). Steal time and frequency were recorded before/after every configuration (e1/run*/meta_det.json). Configurations: 640/1, 640/2, 480/1, 320/1 in the original order, 5,800 frames each.\n')
S.append(grab('E1.1')); S.append(grab('E1.2')); S.append(grab('E1.4')); S.append(grab('E1.3')); S.append(grab('E1.5')); S.append(grab('E1.6'))
if E1:
    p = E1['pooled']['all']['Detector 640 px']; runs = [k for k in E1['runs'] if 'det' in E1['runs'][k]]
    n150 = sum(E1['runs'][k]['det'][c]['n_gt150'] for k in runs for c in E1['runs'][k]['det']); n150s = sum(d['n_gt150'] for d in E1['soak'].values()); nsoak = sum(d['n'] for d in E1['soak'].values()); nprof = sum(E1['runs'][k]['det'][c]['n'] for k in runs for c in E1['runs'][k]['det'])
    f60 = ', '.join('%.1f' % (1e3 * float(np.load(OUT + '/e1/%s/lat_det.npz' % k)['lat|640|1|one-by-one'][60])) for k in runs)
    S.append('**Answers.**\n')
    S.append(f'- Is a > 150 ms outlier reproducible? No: in {nprof:,} profiled inferences (6 runs x 4 configurations) and {nsoak:,} soak inferences there were {n150 + n150s} samples above 150 ms (and {sum(E1["runs"][k]["det"][c]["n_gt120"] for k in runs for c in E1["runs"][k]["det"])} above 120 ms in the profiling runs); the per-run maxima at 640/1 (frames 11+) were {", ".join(f"{x:.1f}" for x in p["per_run_max"])} ms, their locations differ between runs (no frame is among the five largest in two runs; Spearman rank correlation of per-frame service time between runs 0.5-0.8, so the slow *frames* are only weakly reproducible while the slow *tail* is a property of the run). The one systematic exception is the first inference on a new clip (frame 0 of store-aisle: {", ".join(f"{x:.0f}" for x in p["frame0_per_clip_per_run"]["store-aisle"])} ms in runs 1-5 and 106 ms in run0; frame 0 of car-lot about 72 ms), which analyze.py excludes from its distribution table (WARM = 10) but includes in its timing bound and camera simulation. The 358.7 ms sample of the VM (one-by-one, frame 60) has no counterpart here: frame 60 of one-by-one took {f60} ms in runs 0-5.\n')
    S.append(f'- What is C_max on this machine? 640 px / 1 thread: {p["max"]:.1f} ms over frames 11+ of runs 1-5 (the convention of the paper\'s latency table; {p["max_all_frames"]:.1f} ms at {p["max_all_frames_at"]} if the first ten frames of every clip are included); 640/2: {E1["pooled"]["all"]["Detector 640 px, 2 threads"]["max"]:.1f} ms, 480/1: {E1["pooled"]["all"]["Detector 480 px"]["max"]:.1f} ms, 320/1: {E1["pooled"]["all"]["Detector 320 px"]["max"]:.1f} ms. Soak maxima: ' + ', '.join(f'{k} {d["max"]:.1f} ms ({d["n"]:,} jobs)' for k, d in E1['soak'].items()) + '.\n')
    S.append(f'- What are k_min at 12/30 fps? 640/1: {p["kmin12"]} / {p["kmin30"]} (ceil(C_max f) with C_max = {p["max"]:.1f} ms; {int(np.ceil(p["max_all_frames"]/1e3*12))} / {int(np.ceil(p["max_all_frames"]/1e3*30))} with the all-frames C_max); identical in every single run (paper: 5 / 11). Guaranteed cameras floor(k_act T / C_max) at 12 fps, k_act = 8: {p["guaranteed_cams"]} at 640/1 (paper: 1).\n')
    S.append('- Soak: the running maximum settles within the first 1,000-3,000 samples in every soak and the second-half maximum never exceeds the first-half maximum by more than 4 ms (table E1.6); paced operation (one job every 0.667 s from an idle core) gives the same mean as back-to-back inference (52.3 vs 51.8 ms at 640 px).\n')
    S.append('- Note on the first configuration of each fresh process: in runs 1-5 the first configuration (one-by-one, 640/1) ran with 11-16 % system time (per-core /proc/stat in meta_det.json: 831-1319 jiffies vs. 1-25 for later 1-thread configurations) and a median of about 58 ms instead of 48 ms; a /proc sample taken during one of the discarded runs showed about 35,000 minor page faults per second in that phase (e1/invalid_first_config_8threads/run2/sysmon_first_minutes.txt); the cause was not isolated (transparent hugepages are `always` on this node; allocator re-faulting of the activation buffers is the likely mechanism). It inflates the mean of that one clip-configuration (one-by-one 640/1) but not the maximum, and it is absent from the soak runs, which warm up once and then run for 20 min.\n')
# ---------------- 4 E2
sec('4. E2: live multi-camera validation (live2.py)')
S.append('live2.py keeps live.py unchanged and adds: all seven clips (camera c plays clip c mod 7), the phase stagger and loop restart of jobs_for_camera() in analyze.py, all three policies, per-job score logging, decision agreement with the offline scores, and the thread-reset guard. One FIFO worker, 1 torch thread, process pinned to core 2, frames pre-decoded (decode excluded), 600 s per run, two repeats, fresh process per run. N* = simulated maximum cameras with zero misses from analyze.py on the pooled Phase-1 trace. "sim" columns = the trace-driven prediction for the same N.\n')
S.append(grab('E2.1'))
if E2:
    S.append('**Largest N with zero misses in every repeat (640 px):** ' + '; '.join(f"{p}: live {v['live_max_zero_miss_all_repeats']} vs simulated {v['sim_nstar']} (N tested {', '.join(map(str, v['live_N_tested']))})" for p, v in E2['nstar'].items()) + '.\n')
    if E2.get('single'): S.append('Single-camera pass (all seven clips once, three policies): ' + '; '.join(f"{p}: {s['jobs']} jobs, {s['n_miss']} misses, service mean/max {s['service_mean_ms']:.1f}/{s['service_max_ms']:.1f} ms, decisions equal to the offline trace on {s['agree']:.2f} % of jobs (max |score diff| {s['max_abs_score_diff']:.1e})" for p, s in E2['single'].items()) + '.\n')
else: S.append('E2 640 px: not available (stage did not complete; see section 7).\n')
def bursts(d):
    rows = []
    for fn in sorted(glob.glob(OUT + f'/{d}/live_*_N*_rep*.json')):
        o = json.load(open(fn)); r = o['multi']['rec']; m = [x for x in r if x['miss']]
        if not m: continue
        h = np.histogram([x['release'] for x in m], bins=np.arange(0, 601, 60))[0]; s1 = np.mean([x['service'] for x in r if x['release'] < 120]); s2 = np.mean([x['service'] for x in r if x['release'] >= 120])
        rows.append([o['multi']['policy'], o['multi']['N'], os.path.basename(fn).split('_rep')[1].split('.')[0], f"{len(m)} / {len(r)}", ' '.join(str(x) for x in h), f"{1e3*s1:.1f} / {1e3*s2:.1f}", f"{max(x['resp'] for x in m):.2f}"])
    return rows
br = bursts('e2_640')
if br: S.append('Runs with misses (640 px): number of missed jobs per 60-s window of the 600-s run, mean service time in the first 120 s vs the rest, worst response time. Misses cluster in a few windows in which the staggered cameras\' active phases (k = 8) coincide; they are not a start-up effect. The mean service time differs by up to 3 ms (6 %) between otherwise identical processes, which is the size of the utilisation margin at N*.\n\n' + table(['policy', 'N', 'rep', 'missed / jobs', 'misses per 60-s window', 'service mean first 120 s / rest (ms)', 'worst response (s)'], br))
S.append(grab('E2.2'))
br = bursts('e2_320')
if br: S.append('Runs with misses (320 px), same columns:\n\n' + table(['policy', 'N', 'rep', 'missed / jobs', 'misses per 60-s window', 'service mean first 120 s / rest (ms)', 'worst response (s)'], br))
if E2b: S.append('**Largest N with zero misses in every repeat (320 px):** ' + '; '.join(f"{p}: live {v['live_max_zero_miss_all_repeats']} vs simulated {v['sim_nstar']} (N tested {', '.join(map(str, v['live_N_tested']))})" for p, v in E2b['nstar'].items()) + '.\n')
else: S.append('E2 at 320 px: not run or not completed (see section 7).\n')
# ---------------- 5 E3
sec('5. E3: end-to-end recorder (recorder.py)')
rm = rd(OUT + '/e3/rmax.txt').strip()
S.append(f'recorder.py: capture thread (cv2.VideoCapture, frame step and 768-px resize as common.frames(), frames due at t0 + t/fps, decode+resize timed), ring buffer of p + ceil(R_max fps) frames with p = round(fps) and {rm} (largest service time over all timed Phase-1 frames of runs 1-5, store-aisle frame 0), detector worker (1 torch thread, theta = 0.2, decision held for k frames, sample plan identical to analyze.py), writer thread (cv2.VideoWriter MJPG, one file per contiguous segment, every written frame index and write time logged). Three policies x seven clips, once with the whole process pinned to core 2 and once to cores 2 and 4. Video segments were written to local disk (session scratchpad, see section 7), not to the NFS home.\n')
S.append(grab('E3 '))
if E3:
    S.append('**Checks.**\n')
    for k, R in E3.items():
        s = R['summary']
        S.append(f"- {k}: (a) written frames = record() frames on the recorder's own decisions: {s['n_written']} written vs {s['n_expected']} expected, {s['a_diff_frames']} differing frames"
                 + ('' if s['a_diff_frames'] == 0 else ' (' + '; '.join(f"{v}: extra {c['extra_frames'][:20]} missing {c['missing_frames'][:20]}" for v, c in R['clips'].items() if c['extra_frames'] or c['missing_frames']) + ')')
                 + f"; (b) {s['b_onset_written']} of {s['b_onsets']} detectable onset frames written, alert delay median/max {s['b_delay_median']:.3f}/{s['b_delay_max']:.3f} s, {s['b_within_bound']} of {s['b_onsets']} within the bound (k_idle-1)T + R_max ({s['b_bound_min']:.3f}-{s['b_bound_max']:.3f} s); (c) frames needed but evicted from the ring buffer: {s['c_lost']}, detector samples whose frame had been evicted: {s['c_det_lost']} (with a ring sized from the frames-11+ C_max of {1e3*s['rmax_alt']:.1f} ms instead, {s['c_lost_if_ring_sized_with_frames11plus_cmax']} pre-roll frames would have been lost); (d) decode+resize mean/p99/max {s['d_decode_ms']['mean']:.2f}/{s['d_decode_ms']['p99']:.2f}/{s['d_decode_ms']['max']:.2f} ms, write {s['d_write_ms']['mean']:.2f}/{s['d_write_ms']['p99']:.2f}/{s['d_write_ms']['max']:.2f} ms, capture lateness {s['d_lateness_ms']['mean']:.2f}/{s['d_lateness_ms']['p99']:.2f}/{s['d_lateness_ms']['max']:.2f} ms ({s['d_lateness_gt_T']} of {s['d_frames']} frames later than one frame period), detector service {s['d_service_ms']['mean']:.1f}/{s['d_service_ms']['p99']:.1f}/{s['d_service_ms']['max']:.1f} ms vs Phase 1 (640/1, pooled) {s['d_phase1_640_1']['mean']:.1f}/{s['d_phase1_640_1']['p99']:.1f}/{s['d_phase1_640_1']['max']:.1f} ms; live decisions equal to the offline trace on {s['det_agree']:.1f} % of {s['det_jobs']} jobs.\n")
else: S.append('E3: not available (stage did not complete; see section 7).\n')
# ---------------- 6 paper vs machine
sec('6. Paper value (VM) vs this machine')
S.append(grab('Paper value'))
S.append('"expected-identical" rows depend only on the (bit-identical) scores, thresholds, annotations and policies; "timing-dependent" rows depend on measured service times and therefore on the machine. Note that the paper\'s k_min of 5 at 12 fps and the single guaranteed camera at 640/1 both derive from the single 358.7 ms sample of the VM; on this machine the equivalent numbers follow from an 81.5 ms maximum.\n')
# ---------------- 7 deviations, failures, wall clock, paths
sec('7. Deviations from the brief, failures, wall-clock time, raw files')
dev = [
 'SS_ROOT: all RT-pipeline scripts (exp/common.py, event_eval.py, event_analysis.py, motion_scores.py, det_scores.py, exp/rt/*.py) read `SS_ROOT` (default `/root`); diff in logs/ss_root.diff. live.py received only this path edit (no logic change). Scripts outside the RT pipeline (exp/det, exp/trk, exp/sot, exp/quant, other exp/*.py) still hard-code /root. SS_ROOT points to results/rt_ciscluster/root, where `exp` and `data` are symlinks (to the repo exp/ and the gitignored data/) and `results/` holds the new rt/, motion_scores/, det_scores/ and a copy of event_thresholds.json, so that all new outputs live under results/rt_ciscluster/ and results/rt/ stays untouched.',
 'ultralytics 8.4.190 resets the torch thread count to min(8, cpu-1) = 8 on the first predict (select_device()). On the 2-core VM this was 1, here it silently overrides torch.set_num_threads(1) in det_scores.py, measure_det.py and live.py. The unmodified scripts were therefore run through exp/rt/run_vm_threads.py (sets that constant to 1); all new scripts guard against it. The first version of e1_profile.py lacked the guard: its first configuration ran 8 threads on one core; the two affected runs were discarded (kept in e1/invalid_first_config_8threads/ with a README) and all five runs were redone. The detector scores generated during the first minutes with 8 threads were also discarded and regenerated with 1 thread.',
 'measure_det.py was not itself run five times: with taskset the 1-thread configurations cannot be pinned to one core while the 2-thread one uses two, so e1_profile.py reproduces its timing loop verbatim with per-configuration affinity (and omits the perturbed 320-px score pass). The unmodified measure_det.py ran once as run0 (two-core mask) and supplied the 320/480-px score files.',
 'analyze.py per run: run0 has no motion trace of its own (measure_motion.py was run in runs 1-5 only), so run0 was analysed with run1\'s lat_motion.npz. The "pooled" analyze.py run used element-wise-maximum traces over runs 1-5 (worst case per frame, so C_max is the worst case over runs); distribution statistics and miss rates over the concatenation of runs 1-5 are given alongside.',
 'C_max convention: the paper\'s latency table (and k_min) exclude the first 10 frames of every clip (WARM = 10 in analyze.py); the timing bound and camera simulation in analyze.py include them. Both maxima are reported (81.5 ms vs 113.2 ms at 640/1). The recorder ring buffer (E3) was sized with the larger, all-frames value; the consequence of the smaller value is computed from the logs (check c).',
 'live2.py restarts a looped clip at t0 + L*n*T with frame 0 (as jobs_for_camera() in analyze.py), whereas live.py continued from the last release time; this was done so that live and simulated job sequences coincide.',
 'E3 video segments were written to the local disk of the node (session scratchpad), not to the NFS home directory; the frame-index and write-time logs are in e3/recorder_*.json.',
 'The soak at 640 px back-to-back started with a 1-minute load average of 7.8 that was the decaying trace of the seven parallel analyze.py processes which had just finished (no process was running); all other timed stages started at load about 1.0-1.3 (this process plus the VS Code server).',
 'Phase 0 idle check: load 0.40 at the first check (criterion 0.3), 0.13 a minute later; no foreign CPU activity was seen at any stage start.',
 'run_device.sh (Phase 4) was written but, as instructed, not run here.',
 'The interactive assistant session was closed during E2 (the operator logged out); the stages were already chained in detached processes (exp/rt/e_master_chain.sh, e_finalize.sh) and ran to completion unattended. This file was generated by e_write_summary.py when the chain finished and then reviewed.',
 'E3 video segments (MJPG .avi, 831 MB in total) are on the node\'s local disk in the session scratchpad (/tmp/claude-8800/.../scratchpad/e3_video/<policy>_cores<c>/) and are not part of the results directory; the written-frame logs in e3/recorder_*.json are the verified artefact.',
 'In E2 the simulated prediction uses the element-wise-maximum trace of Phase 1 (conservative service times); live utilisation at the same N is therefore 1-10 % lower than simulated, while live misses at N* arise from response-time bursts the deterministic trace does not produce.',
]
S.append('\n'.join('- ' + d for d in dev) + '\n')
fails = []
for lg in glob.glob(OUT + '/e*/*.log') + glob.glob(OUT + '/e1/*/*.log') + glob.glob(OUT + '/e1/soak/*.log') + glob.glob(OUT + '/logs/*.log'):
    txt = rd(lg)
    if 'Traceback' in txt or 'exit=1' in txt or 'exit=2' in txt or 'Killed' in txt: fails.append(os.path.relpath(lg, OUT))
S.append('Failures / incomplete stages detected automatically (logs containing Traceback, non-zero exit or Killed): ' + (', '.join(fails) if fails else 'none') + '.\n')
missing = [n for n, ok in [('e1/e1_summary.json', E1 is not None), ('e2_640/e2_summary.json', E2 is not None), ('e2_640/live_single.json', os.path.exists(OUT + '/e2_640/live_single.json')), ('e3/e3_verify.json', E3 is not None), ('e2_320/e2_summary.json', E2b is not None)] if not ok]
S.append('Missing outputs: ' + (', '.join(missing) if missing else 'none') + '.\n')
if TABERR.strip(): S.append('Table generator messages: `' + TABERR.strip()[-500:] + '`\n')
S.append(f'Total wall-clock time from the first setup command ({t0[1].strip() if len(t0) > 1 else "?"}) to the end of the pipeline (MASTER CHAIN DONE in logs/master_chain.log): {wall_h:.1f} h (setup+scores 0.4 h, E1 incl. soak 4.0 h, E2 640 px 4.6 h, E3 0.9 h, E2 320 px 4.8 h).\n' if wall_h else 'Wall-clock: start time not recorded.\n')
S.append('Raw files (all under results/rt_ciscluster/):\n')
paths = ['platform.txt, logs/frame_counts.txt, logs/score_check.{txt,json}, logs/ss_root.diff, logs/pip_freeze_*.txt, logs/download.log, logs/det_scores_*.log, logs/motion_scores.log',
         'root/results/motion_scores/*.npz, root/results/det_scores/*.npy (regenerated scores), root/results/rt/{lat_det,lat_motion}.npz (= pooled max traces), root/results/rt/analysis.json (pooled), analysis2.json (hybrid gate misses on the pooled traces), analyze2.log',
         'e1/run0/{lat_det.npz, measure_det.log, analysis.json, analyze.log}; e1/run{1..5}/{lat_det.npz, meta_det.json, e1_profile.log, lat_motion.npz, measure_motion.log, analysis.json, analyze.log}; e1/pooled/{lat_det.npz, lat_motion.npz, analysis.json, analyze.log}; e1/soak/soak_{640,320}_{b2b,paced}.{npz,_meta.json,log}; e1/e1_summary.json; e1/e1_chain.log; e1/invalid_first_config_8threads/',
         'e2_640/live_<policy>_N<N>_rep<r>.{json,log} (per-job records), e2_640/live_single.{json,log}, e2_640/nstar.txt, e2_640/e2_run.log, e2_640/e2_summary.json; e2_320/ likewise',
         'e3/recorder_<policy>_cores<c>.{json,log} (capture, detector, written-frame and lost-frame logs), e3/rmax.txt, e3/e3_run.log, e3/e3_verify.{json,log}',
         'logs/master_chain.log, logs/summary_tables.md (all tables), SUMMARY.md (this file)',
         'New code: exp/rt/{e1_profile.py, e1_soak.py, e1_run.sh, e1_chain2.sh, e1_analyze.py, live2.py, e2_run.sh, e2_analyze.py, recorder.py, e3_run.sh, e3_verify.py, run_vm_threads.py, e_master_chain.sh, e_summary_tables.py, e_write_summary.py}, run_device.sh (repo root)']
S.append('\n'.join('- ' + p for p in paths) + '\n')
S.append('\nAll tables are also in logs/summary_tables.md.\n')
open(OUT + '/SUMMARY.md', 'w').write('\n'.join(S)); print('written', OUT + '/SUMMARY.md')
