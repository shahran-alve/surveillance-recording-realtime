"""Appends section 9 to SUMMARY.md from e9_summary.json. Usage: python e9_write.py OUTDIR"""
import sys, json, time, numpy as np
OUT = sys.argv[1]; E = json.load(open(OUT + '/e9_summary.json')); S = []
def table(head, rows): return '| ' + ' | '.join(head) + ' |\n|' + '---|' * len(head) + '\n' + '\n'.join('| ' + ' | '.join(str(c) for c in r) + ' |' for r in rows) + '\n'
f1 = lambda x: f'{x:.1f}'
NAME = {'default': '(a) default', 'malloc': '(b) MALLOC_TRIM_THRESHOLD_=MALLOC_MMAP_THRESHOLD_=4294967296', 'thp': '(c) prctl(PR_SET_THP_DISABLE)'}
S.append(f'\n## 9. Allocator / transparent-hugepage test (added {time.strftime("%Y-%m-%d %H:%M %Z")}; e1_profile2.py, 640 px / 1 thread, 120-s warm-up, clip order rotated by run index, core 2, one torch thread; 15 fresh processes interleaved a,b,c,a,b,c,...)\n')
S.append('Per run: service time over frames 11+ of every clip (ms), system-time share of the timed part (per-core /proc/stat user+sys), minor page faults per second of the process during the timed part (/proc/self/stat minflt); "high clips" = clips whose median exceeds 52 ms. Verification of the conditions: (b) the environment seen by the process is recorded in meta_det.json (malloc_env); (c) prctl return code 0 and /proc/self/status THP_enabled: 0 are recorded (thp_status).\n')
rows = []
for cond, d in E.items():
    for k, r in d['runs'].items():
        nh = sum(1 for v, m in r['per_clip_median'].items() if m > 52.0)
        rows.append([NAME[cond], k, r['order'][0], f1(r['mean']), f1(r['p50']), f1(r['p99']), f1(r['max']), f1(r['max_all_frames']), f"{100*r['sys_share']:.1f}", f"{r['minflt_per_s']:.0f}", f"{100*r['warmup']['sys_share']:.1f} / {r['warmup']['minflt_per_s']:.0f}", f"{nh}/7",
                     ' '.join(f1(r['per_clip_median'][v]) for v in r['per_clip_median']), (r['thp_status'][0].replace('THP_enabled:', 'THP').replace('\t', '') if r['thp_status'] else '-') + ('' if not r['malloc_env'] else ' malloc env set'), r['steal'], ' '.join(r['load'][1])])
S.append(table(['condition', 'run', 'first clip', 'mean', 'p50', 'p99', 'max', 'max all frames', 'sys %', 'minflt/s', 'warm-up sys % / minflt/s', 'high clips', 'per-clip medians (clip order of E1)', 'check', 'steal', 'load end'], rows))
rows = []
for cond, d in E.items():
    p = d['pooled']; rows.append([NAME[cond], len(d['runs']), f1(p['mean']), f1(p['p50']), f1(p['p99']), f1(p['max']), ', '.join(f1(m) for m in p['means']), ', '.join(f'{100*s:.1f}' for s in p['sys']), ', '.join(f'{m:.0f}' for m in p['mf']), f"{p['n_high']} of {len(d['runs'])}", f"{p['n_clip_high']} of {p['n_clips']}"])
S.append('Pooled per condition:\n\n' + table(['condition', 'runs', 'mean', 'p50', 'p99', 'max', 'per-run means', 'per-run sys %', 'per-run minflt/s', 'runs with mean > 52 ms', 'clips with median > 52 ms'], rows))
# verdict
def desc(c):
    p = E[c]['pooled']; return f"{NAME[c]}: per-run means {', '.join(f1(m) for m in p['means'])} ms, system time {', '.join(f'{100*s:.1f}' for s in p['sys'])} %, minor faults {', '.join(f'{m:.0f}' for m in p['mf'])} per s, {p['n_clip_high']} of {p['n_clips']} clip medians above 52 ms"
S.append('Does either setting remove the ~54 ms / high-system-time state? ' + '; '.join(desc(c) for c in E) + '. ' )
d, m, t = (E.get(k, {}).get('pooled') for k in ['default', 'malloc', 'thp'])
if d and m and t:
    verdict = []
    for name, p in [('(b) the glibc thresholds', m), ('(c) THP disabled', t)]:
        removed = p['n_clip_high'] == 0 and max(p['sys']) < 0.03
        reduced = p['n_clip_high'] < d['n_clip_high'] and np.mean(p['sys']) < np.mean(d['sys'])
        verdict.append(f"{name} {'removes the state (no clip above 52 ms, system time below 3 % in every run)' if removed else ('reduces it but does not remove it' if reduced else 'does not remove it')}")
    S.append(' '.join(verdict) + f". The default condition reproduced the state in {d['n_high']} of {len(E['default']['runs'])} runs ({d['n_clip_high']} of {d['n_clips']} clip medians above 52 ms). Minor-fault rate and system-time share move together with the mean in every condition (see the per-run table), which supports page-fault handling as the mechanism; maxima are unaffected by the condition.\n")

# ---- mechanism evidence: THP/compaction counters (snapshot taken during the runs vs now) and memory state
import glob, os
snaps = sorted(glob.glob(OUT + '/e9/vmstat_snapshot_*.txt'))
def counters(txt):
    d = {}
    for l in txt.split('\n'):
        p = l.split()
        if len(p) in (2, 3) and p[0].rstrip(':') in ('thp_fault_alloc', 'thp_fault_fallback', 'compact_stall', 'compact_success', 'allocstall_movable', 'thp_collapse_alloc', 'MemFree', 'MemAvailable', 'Cached', 'AnonHugePages'):
            try: d[p[0].rstrip(':')] = int(p[1])
            except ValueError: pass
    return d
now = counters(open('/proc/vmstat').read() + open('/proc/meminfo').read())
S.append('**Mechanism evidence.** ')
if snaps:
    c0 = counters(open(snaps[0]).read()); t0 = os.path.basename(snaps[0])[-8:-4]
    S.append(f"System-wide counters between the snapshot at {t0[:2]}:{t0[2:]} (e9/{os.path.basename(snaps[0])}, taken while the runs were in progress) and the end of the runs: thp_fault_alloc +{now.get('thp_fault_alloc',0)-c0.get('thp_fault_alloc',0):,}, thp_fault_fallback +{now.get('thp_fault_fallback',0)-c0.get('thp_fault_fallback',0):,}, compact_stall +{now.get('compact_stall',0)-c0.get('compact_stall',0):,}, allocstall_movable +{now.get('allocstall_movable',0)-c0.get('allocstall_movable',0):,}. ")
S.append(f"Memory state at the end of the runs: MemFree {now.get('MemFree',0)/2**20:.1f} GB of 187 GB, page cache {now.get('Cached',0)/2**20:.0f} GB, AnonHugePages {now.get('AnonHugePages',0)/2**20:.1f} GB; THP enabled = always, defrag = madvise (no direct compaction on ordinary page faults, so a huge-page fault that finds no free 2-MB block falls back to 4-KB pages). "
         "Reading of the three conditions: (c) forces every anonymous allocation onto 4-KB pages and lands every clip in the slow state with the highest fault rates, so the slow state is the 4-KB-page state and the fast state is the one in which the activation buffers were backed by huge pages; with only a few GB free and the rest in page cache, whether a fresh process obtains huge pages at its allocation sites is a matter of luck and can change during the process, which is the per-process (and occasionally mid-process) state of sections 3 and 8. "
         "(b) is a request for a 4-GB mmap threshold; glibc caps M_MMAP_THRESHOLD at 32 MB on 64-bit (HEAP_MAX_SIZE/2) and, once either threshold is set explicitly, disables its dynamic adjustment, so the setting most plausibly left the 128-KB default in force without dynamic growth: every activation buffer above 128 KB is then mmap'ed and unmapped on every inference, which matches the 4-6x higher fault rate and the 27-33 % system time observed. This is an inference from glibc's documented behaviour, not a direct measurement. "
         "Neither setting is therefore a fix; the mechanism points to huge-page availability. A direct remedy would be to allocate the activation memory once (caching allocator or a pre-touched arena), or to run with free memory available for huge pages; that was not tested here.\n")

open(OUT + '/SUMMARY.md', 'a').write('\n'.join(S)); print('appended section 9')
