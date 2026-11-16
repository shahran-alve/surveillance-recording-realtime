"""Figures for the real-time analysis (Springer style: sans-serif, >= 8 pt at final size, vector, embedded TrueType fonts)."""
import json, csv, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['DejaVu Sans'], 'font.size': 8, 'axes.spines.top': False, 'axes.spines.right': False, 'axes.linewidth': 0.6,
                     'xtick.major.width': 0.6, 'ytick.major.width': 0.6, 'pdf.fonttype': 42, 'legend.fontsize': 7.5})
BLUE, ORANGE, GREEN, PURPLE, GREY, INK = '#2a78d6', '#eb6834', '#1baf7a', '#4a3aa7', '#8a8880', '#333333'
R = '/root/results/rt/'; A = json.load(open(R + 'analysis.json')); OUT = '/root/jrtip/paper/fig/'
LM = np.load(R + 'lat_motion.npz'); LD = np.load(R + 'lat_det.npz')
def pool(z, pre): return 1e3 * np.concatenate([z[k][10:] for k in z.files if k.startswith(pre)])

# ---------- Fig3: service-time ranges against frame deadlines
rows = [('FD', pool(LM, 'FD|'), GREY), ('CNT', pool(LM, 'CNT|'), GREY), ('MOG2', pool(LM, 'MOG2|'), GREY), ('KNN', pool(LM, 'KNN|'), GREY), ('Optical flow', pool(LM, 'FLOW|'), GREY), ('GSOC', pool(LM, 'GSOC|'), GREY),
        ('Detector 320 px', pool(LD, 'lat|320|1|'), BLUE), ('Detector 480 px', pool(LD, 'lat|480|1|'), BLUE), ('Detector 640 px, 2 thr.', pool(LD, 'lat|640|2|'), BLUE), ('Detector 640 px', pool(LD, 'lat|640|1|'), BLUE)]
fig, a = plt.subplots(figsize=(3.3, 2.75))
for d, lab, ha, dx in [(1000 / 30, '30 fps', 'right', 0.93), (1000 / 15, '15', 'right', 0.96), (1000 / 12, '12 fps', 'left', 1.05)]:
    a.axvline(d, color=ORANGE, lw=0.8, ls='--', zorder=0); a.text(d * dx, len(rows) - 0.35, lab, color=ORANGE, ha=ha, va='bottom', fontsize=7)
for i, (name, x, c) in enumerate(rows):
    y = len(rows) - 1 - i; p50, p95, p99, mx = np.percentile(x, 50), np.percentile(x, 95), np.percentile(x, 99), x.max()
    a.plot([p50, mx], [y, y], color=c, lw=1.2, solid_capstyle='butt'); a.plot([p50], [y], 'o', color=c, ms=4.2); a.plot([p95], [y], '|', color=c, ms=7, mew=1.2); a.plot([p99], [y], 'D', color=c, ms=3.2); a.plot([mx], [y], 'x', color=INK, ms=4, mew=0.9)
a.set_yticks(range(len(rows))); a.set_yticklabels([r[0] for r in rows][::-1]); a.set_xscale('log'); a.set_xlim(0.5, 600); a.set_ylim(-0.6, len(rows) + 0.35)
a.set_xticks([1, 10, 100]); a.set_xticklabels(['1', '10', '100']); a.set_xlabel('Service time per frame (ms, log scale)')
h = [plt.Line2D([], [], marker='o', ls='', color=INK, ms=4.2, label='median'), plt.Line2D([], [], marker='|', ls='', color=INK, ms=7, mew=1.2, label='p95'),
     plt.Line2D([], [], marker='D', ls='', color=INK, ms=3.2, label='p99'), plt.Line2D([], [], marker='x', ls='', color=INK, ms=4, label='max')]
a.legend(handles=h, loc='lower center', bbox_to_anchor=(0.36, 1.0), frameon=False, ncol=4, columnspacing=1.0, handletextpad=0.2, borderaxespad=0.1)
a.grid(axis='x', lw=0.4, color='#e5e5e5'); a.set_axisbelow(True)
fig.savefig(OUT + 'Fig3.pdf', bbox_inches='tight', pad_inches=0.02); plt.close(fig)

# ---------- Fig4: idle frames stored under perturbation (thresholds fixed from clean video)
Rr = list(csv.DictReader(open('/root/results/event_lovo.csv'))); get = lambda m, k: 100 * float([r for r in Rr if r['method'] == m and r['kind'] == k][0]['idle_kept'])
meth = [('FD', 'FD'), ('FLOW', 'Flow'), ('MOG2', 'MOG2'), ('KNN', 'KNN'), ('CNT', 'CNT'), ('GSOC', 'GSOC'), ('Detector (every frame)', 'Det\nk=1'), ('Detector (every 8th frame)', 'Det\nk=8'), ('Hybrid: MOG2 gate + detector', 'MOG2\n+det')]
kinds = [('clean', 'Clean', GREY, ''), ('illum', 'Illumination steps', ORANGE, '///'), ('jitter', 'Camera jitter', BLUE, '')]
fig, a = plt.subplots(figsize=(3.3, 2.2)); w = 0.27
for j, (k, lab, c, hatch) in enumerate(kinds):
    a.bar(np.arange(len(meth)) + (j - 1) * w, [get(m, k) for m, _ in meth], w * 0.9, color=c, label=lab, hatch=hatch, edgecolor='white', linewidth=0.3)
a.set_xticks(range(len(meth))); a.set_xticklabels([m[1] for m in meth], fontsize=6.5); a.set_ylabel('Idle frames stored (%)'); a.set_ylim(0, 108)
a.legend(frameon=False, ncol=3, loc='upper center', bbox_to_anchor=(0.5, 1.16), columnspacing=0.9, handlelength=1.2, handletextpad=0.3)
a.grid(axis='y', lw=0.4, color='#e5e5e5'); a.set_axisbelow(True)
fig.savefig(OUT + 'Fig4.pdf', bbox_inches='tight', pad_inches=0.02); plt.close(fig)

# ---------- Fig5: (a) alert delay on detectable onsets vs bound, (b) deadline misses vs cameras per core
fig, (a, b) = plt.subplots(1, 2, figsize=(6.9, 2.3), gridspec_kw={'width_ratios': [1.05, 1]})
pol = [('Every frame', 'Every\nframe'), ('Fixed stride 8', 'Fixed\nstride 8'), ('Adaptive, deadline-aware', 'Deadline-\naware'), ('Adaptive 16/8', 'Adaptive\n16/8'), ('Fixed stride 16', 'Fixed\nstride 16')]
rng = np.random.default_rng(1)
for i, (p, lab) in enumerate(pol):
    t = A['timing'][p + '|1.0']; d = np.array(t['delays']); late = d > 1.0 + 1e-9
    a.plot(i + rng.uniform(-0.16, 0.16, len(d)), d, 'o', ms=3.4, color=BLUE, mec='white', mew=0.3, zorder=3)
    a.plot([i - 0.3, i + 0.3], [t['bound_max']] * 2, color=INK, lw=1.3, zorder=2)
a.axhline(1.0, color=ORANGE, ls='--', lw=0.9); a.text(-0.5, 1.03, 'pre-roll 1 s', color=ORANGE, fontsize=7, va='bottom')
a.plot([], [], 'o', ms=3.4, color=BLUE, label='detectable onset'); a.plot([], [], color=INK, lw=1.3, label=r'bound $(k_{\mathrm{idle}}-1)T+C_{\max}$')
a.set_xticks(range(len(pol))); a.set_xticklabels([p[1] for p in pol], fontsize=7); a.set_ylabel('Alert delay (s)'); a.set_ylim(0, 1.75); a.set_xlim(-0.55, len(pol) - 0.45)
a.legend(frameon=False, loc='lower center', bbox_to_anchor=(0.55, 1.0), ncol=2, handletextpad=0.4, columnspacing=1.0); a.grid(axis='y', lw=0.4, color='#e5e5e5'); a.set_axisbelow(True); a.set_title('(a)', loc='left', fontsize=8, fontweight='bold')
sty = {'Fixed stride 8': (BLUE, '-', 'o'), 'Adaptive 16/8': (ORANGE, '--', 's'), 'Adaptive, deadline-aware': (PURPLE, '-.', '^')}
for p, (c, ls, mk) in sty.items():
    cv = A['cameras'][p + '|640 px, 1 thread']['curve']; N = sorted(int(n) for n in cv); b.plot(N, [cv[str(n)]['miss'] for n in N], ls, marker=mk, ms=3, color=c, lw=1, label={'Adaptive, deadline-aware': 'Deadline-aware'}.get(p, p))
b.set_xlabel('Cameras on one core (640 px, 1 thread)'); b.set_ylabel('Jobs missing deadline (%)'); b.set_yscale('symlog', linthresh=1); b.set_ylim(-0.08, 120); b.set_yticks([0, 1, 10, 100]); b.set_yticklabels(['0', '1', '10', '100'])
b.legend(frameon=False, loc='upper left'); b.grid(lw=0.4, color='#e5e5e5'); b.set_axisbelow(True); b.set_title('(b)', loc='left', fontsize=8, fontweight='bold')
fig.tight_layout(w_pad=1.2); fig.savefig(OUT + 'Fig5.pdf', bbox_inches='tight', pad_inches=0.02); plt.close(fig)

# ---------- Fig6: accuracy vs latency on VisDrone
M = json.load(open('/root/results/det/det_metrics.json')); L = json.load(open('/root/results/rt/latency_visdrone.json'))
fig, a = plt.subplots(figsize=(3.3, 2.5))
for series, col, ls, mk, name in [(['yolo11n_640', 'yolo11n_960', 'yolo11n_1280'], BLUE, '-', 'o', 'YOLO11n'), (['yolo11s_640', 'yolo11s_960', 'yolo11s_1280'], BLUE, '--', 's', 'YOLO11s'),
                                  (['yolo26n_640', 'yolo26n_960', 'yolo26n_1280'], ORANGE, '-', 'o', 'YOLO26n'), (['yolo26s_640', 'yolo26s_960', 'yolo26s_1280'], ORANGE, '--', 's', 'YOLO26s')]:
    a.plot([L[k] for k in series], [100 * M[k]['all']['AP'] for k in series], ls, marker=mk, ms=3.4, color=col, lw=1, label=name + ' (640/960/1280 px)')
lab = {'yolox_s_640': 'YOLOX-s', 'yolov8n_640': 'YOLOv8n', 'yolov8s_640': 'YOLOv8s', 'yolo11n_640_tiles': 'tiles', 'yolo11n_640_tta': 'TTA'}
for k, t in lab.items():
    x, y = L[k], 100 * M[k]['all']['AP']; a.plot(x, y, 'D', ms=3, color=GREY); a.annotate(t, (x, y), xytext={'yolox_s_640': (-30, -9), 'yolov8s_640': (4, -7), 'yolov8n_640': (3, -8), 'yolo11n_640_tta': (4, -3), 'yolo11n_640_tiles': (4, 2)}[k], textcoords='offset points', fontsize=7, color='#444')
a.set_xscale('log'); a.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter()); a.set_xticks([50, 100, 200, 500]); a.set_xticklabels(['50', '100', '200', '500'])
a.set_xlabel('CPU latency per image (ms, 2 threads, log scale)'); a.set_ylabel('AP (IoU 0.5:0.95)'); a.set_ylim(0, 38); a.set_xlim(50, 700)
a.grid(lw=0.4, color='#e5e5e5'); a.set_axisbelow(True); a.legend(frameon=False, loc='lower right', fontsize=7, borderaxespad=0.2)
fig.savefig(OUT + 'Fig6.pdf', bbox_inches='tight', pad_inches=0.02); print('ok')
