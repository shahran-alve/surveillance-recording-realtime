"""E3 verification from the recorder logs (recorder_*.json in --e3dir):
 a. frame-exact agreement of the written frame indices with event_eval.record() applied to the recorder's own decision sequence
 b. detectable onsets (onsets() of analyze.py, copied verbatim, on the offline clean 640-px scores with theta): onset frame written?
    measured alert delay (decision finish time - due time of the onset frame) vs. bound (k_idle - 1)*T + R_max
 c. frames needed but already evicted from the ring buffer (recorder 'lost'), and detector samples whose frame had been evicted
 d. decode / write time distributions, capture lateness vs. the frame period, detector service time vs. Phase 1
Usage: python e3_verify.py E3DIR E1_SUMMARY_JSON"""
import sys, os, json, glob, numpy as np
ROOT = os.environ.get('SS_ROOT', '/root'); sys.path.insert(0, ROOT + '/exp')
import event_eval as EV
from event_eval import record
from common import VIDEOS, video_info
E3, E1S = sys.argv[1], sys.argv[2]; VIDS = list(VIDEOS); FPS = {v: video_info(v)[0] for v in VIDS}
A = json.load(open(ROOT + '/results/rt/analysis.json')); TH = A['theta']; S = {v: np.load(f'{ROOT}/results/det_scores/yolo11n_{v}_clean.npy') for v in VIDS}
P_PERSIST = 16
def onsets(s, thr, fps):                                   # verbatim from analyze.py
    on = s > thr; W = int(round(fps)); out = []
    for j in range(max(W, int(2 * fps)), len(s) - P_PERSIST):
        if on[j] and not on[j - W:j].any() and on[j:j + P_PERSIST].all(): out.append(j)
    return out
E1 = json.load(open(E1S)); ph1 = E1['pooled']['all']['Detector 640 px']; per_run = E1['pooled']['all']['Detector 640 px']['per_run_max']
import math; RMAX_ALT = ph1['max'] / 1e3; RING_ALT = {v: int(round(1.0 * FPS[v])) + math.ceil(RMAX_ALT * FPS[v]) for v in VIDS}   # sizing with the frames-11+ C_max
def st(x):
    x = np.asarray(x, float); return dict(n=len(x), mean=float(x.mean()), p50=float(np.percentile(x, 50)), p99=float(np.percentile(x, 99)), max=float(x.max())) if len(x) else dict(n=0)
out = {}
for fn in sorted(glob.glob(E3 + '/recorder_*.json')):
    o = json.load(open(fn)); mt = o['meta']; key = f"{mt['policy']}|cores{'-'.join(map(str, mt['cores']))}"; R = dict(meta={k: mt[k] for k in ('policy', 'cores', 'rmax', 'affinity', 'loadavg_start', 'loadavg_end', 'steal_start', 'steal_end', 'torch_threads', 'torch_threads_end')}, clips={})
    Rmax = mt['rmax']; agg = dict(diff_frames=0, n_written=0, n_expected=0, lost=0, det_lost=0, onsets=0, onset_written=0, within_bound=0, delays=[], bounds=[], dec=[], wr=[], late=[], srv=[], det_agree=0, det_jobs=0, late_gt_T=0, n_frames=0)
    for v, r in o['clips'].items():
        fps = r['fps']; T = 1 / fps; n = r['n']; D = r['detector']; alt_written = set()
        tr = np.zeros(n, bool)
        for d in D: tr[d['frame']:d['frame'] + d['k']] = d['pos']
        rec = record(tr, fps); expected = set(np.where(rec)[0].tolist()); written = [w[0] for w in r['written']]; ws = set(written)
        extra = sorted(ws - expected); missing = sorted(expected - ws); dup = len(written) - len(ws)
        # b. onsets
        ons = []
        for j in onsets(S[v], TH[v], fps):
            c = [d for d in D if d['frame'] >= j and d['pos']]
            if not c: ons.append(dict(onset=j, detected=False)); continue
            d0 = c[0]; due_j = r['capture'][j][1]; delay = d0['finish'] - due_j; B = (r['k_idle'] - 1) * T + Rmax
            ons.append(dict(onset=j, first_pos_sample=d0['frame'], delay=delay, bound=B, within=bool(delay <= B + 1e-9), onset_written=bool(j in ws), service=d0['service']))
        # c'. alternative ring sizing (R_max = frames-11+ maximum of Phase 1): for each positive decision, newest captured frame at decision time
        alt_lost = []
        for d in D:
            if not d['pos']: continue
            newest = sum(1 for c in r['capture'] if c[3] <= d['finish']) - 1; lo = max(0, d['frame'] - r['p']); oldest_kept = newest - RING_ALT[v] + 1
            alt_lost += [j for j in range(lo, d['frame']) if j < oldest_kept and j not in alt_written]
            alt_written.update(range(lo, min(n, d['frame'] + d['k'] + r['post'])))
        # agreement of live decisions with offline scores
        ag = [bool(d['pos']) == bool(S[v][d['frame']] > TH[v]) for d in D]
        cap = np.array([c[2] for c in r['capture']]); late = np.array([c[4] for c in r['capture']]); wr = np.array([w[1] for w in r['written']]); srv = np.array([d['service'] for d in D])
        R['clips'][v] = dict(n=n, fps=fps, ring_capacity=r['ring_capacity'], det_jobs=len(D), n_written=len(written), n_expected=len(expected), extra_frames=extra, missing_frames=missing, duplicates=dup,
                             lost=r['lost'], det_lost=r['det_lost'], alt_ring_capacity=RING_ALT[v], alt_lost=alt_lost, onsets=ons, det_agree=100 * float(np.mean(ag)) if ag else None, decode_ms=st(cap), write_ms=st(wr), lateness_ms=st(1e3 * late),
                             lateness_gt_T=int((late > T).sum()), service_ms=st(1e3 * srv), segments=len(r['segments']))
        agg['diff_frames'] += len(extra) + len(missing); agg['n_written'] += len(written); agg['n_expected'] += len(expected); agg['lost'] += len(r['lost']); agg['det_lost'] += len(r['det_lost']); agg['alt_lost'] = agg.get('alt_lost', 0) + len(alt_lost)
        agg['onsets'] += len(ons); agg['onset_written'] += sum(1 for x in ons if x.get('onset_written')); agg['within_bound'] += sum(1 for x in ons if x.get('within')); agg['delays'] += [x['delay'] for x in ons if 'delay' in x]; agg['bounds'] += [x['bound'] for x in ons if 'bound' in x]
        agg['dec'] += cap.tolist(); agg['wr'] += wr.tolist(); agg['late'] += (1e3 * late).tolist(); agg['srv'] += (1e3 * srv).tolist(); agg['det_agree'] += sum(ag); agg['det_jobs'] += len(ag); agg['late_gt_T'] += int((late > T).sum()); agg['n_frames'] += n
    R['summary'] = dict(a_diff_frames=agg['diff_frames'], n_written=agg['n_written'], n_expected=agg['n_expected'], b_onsets=agg['onsets'], b_onset_written=agg['onset_written'], b_within_bound=agg['within_bound'],
                        b_delay_median=float(np.median(agg['delays'])) if agg['delays'] else None, b_delay_max=float(np.max(agg['delays'])) if agg['delays'] else None, b_bound_min=float(np.min(agg['bounds'])) if agg['bounds'] else None, b_bound_max=float(np.max(agg['bounds'])) if agg['bounds'] else None,
                        c_lost=agg['lost'], c_det_lost=agg['det_lost'], c_lost_if_ring_sized_with_frames11plus_cmax=agg.get('alt_lost', 0), rmax_used=Rmax, rmax_alt=RMAX_ALT, d_decode_ms=st(agg['dec']), d_write_ms=st(agg['wr']), d_lateness_ms=st(agg['late']), d_lateness_gt_T=agg['late_gt_T'], d_frames=agg['n_frames'], d_service_ms=st(agg['srv']),
                        d_phase1_640_1=dict(mean=ph1['mean'], p99=ph1['p99'], max=ph1['max'], per_run_max=per_run), det_agree=100 * agg['det_agree'] / agg['det_jobs'], det_jobs=agg['det_jobs'])
    out[key] = R; print(key, {k: (round(x, 3) if isinstance(x, float) else x) for k, x in R['summary'].items() if not isinstance(x, dict)}, flush=True)
json.dump(out, open(E3 + '/e3_verify.json', 'w'), indent=1, default=float); print('written', E3 + '/e3_verify.json')
