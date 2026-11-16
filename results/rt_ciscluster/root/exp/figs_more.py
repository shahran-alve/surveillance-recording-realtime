import json, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
E = json.load(open('/root/results/more_events.json')); T = json.load(open('/root/results/mot/more_mot.json'))
plt.rcParams.update({'font.family': 'serif', 'font.size': 7.5, 'axes.spines.top': False, 'axes.spines.right': False, 'axes.linewidth': 0.6, 'xtick.major.width': 0.6, 'ytick.major.width': 0.6, 'pdf.fonttype': 42})
fig, ax = plt.subplots(1, 3, figsize=(7, 2.15))
# (a) detector calls vs idle kept (clean), uniform stride vs adaptive
ks = sorted(E['stride'], key=int)
x = [100 * E['stride'][k]['clean']['det_calls'] for k in ks]; y = [100 * E['stride'][k]['clean']['idle_kept'] for k in ks]
ax[0].plot(x, y, 'o-', c='#2a78d6', ms=3, label='fixed stride')
for k, xx, yy in zip(ks, x, y):
    if k in ('1', '8', '16', '32'): ax[0].annotate(f'k={k}', (xx, yy), textcoords='offset points', xytext=(3, 3), fontsize=5.5)
for key, c, lab in [('adaptive_rev', '#1baf7a', 'adaptive A'), ('adaptive', '#eb6834', 'adaptive B')]:
    pts = [(100 * v['clean']['det_calls'], 100 * v['clean']['idle_kept'], n) for n, v in E[key].items()]
    ax[0].scatter([p[0] for p in pts], [p[1] for p in pts], s=10, c=c, marker='^' if key == 'adaptive_rev' else 'v', label=lab, zorder=3)
ax[0].set_xscale('log'); ax[0].set_xticks([3, 6, 12.5, 25, 50, 100]); ax[0].set_xticklabels(['3', '6', '12.5', '25', '50', '100'])
ax[0].set_xlabel('frames with a detector run (%)'); ax[0].set_ylabel('idle frames stored (%)'); ax[0].set_title('(a) detector calls vs. idle storage', fontsize=7)
ax[0].legend(fontsize=5.5, frameon=False, loc='upper right')
# (b) buffer ablation
B = E['buffer']; cfg = ['0/0', '0/2', '0.5/1', '1/1', '1/2', '2/3']; lab = ['0/0', '0/2', '0.5/1', '1/1', '1/2*', '2/3']
xx = np.arange(len(cfg)); w = 0.38
ax[1].bar(xx - w / 2, [100 * B[f'stride8 {c}']['idle_kept'] for c in cfg], w, color='#2a78d6', label='detector, every 8th')
ax[1].bar(xx + w / 2, [100 * B[f'MOG2 {c}']['idle_kept'] for c in cfg], w, color='#9a9890', label='MOG2')
ax2 = ax[1].twinx(); ax2.spines['right'].set_visible(True); ax2.plot(xx, [100 * B[f'stride8 {c}']['frame_recall'] for c in cfg], 'k.-', ms=4, lw=0.8, label='recall (detector)')
ax2.set_ylim(90, 100.5); ax2.set_ylabel('frame recall (%)', fontsize=6); ax2.tick_params(labelsize=6)
ax[1].set_xticks(xx); ax[1].set_xticklabels(lab, fontsize=6); ax[1].set_xlabel('pre-roll / post-roll (s)'); ax[1].set_ylabel('idle frames stored (%)')
ax[1].set_ylim(0, 100); ax[1].set_title('(b) recording buffer', fontsize=7); ax[1].legend(fontsize=5, frameon=False, loc='center left', bbox_to_anchor=(0, 0.62))
# (c) tracking under detection dropout
ps = ['0.0', '0.1', '0.2', '0.3', '0.5']; P = [float(p) * 100 for p in ps]
for key, ls, nm in [('dropout_coast', '-', 'coast 3 frames'), ('dropout', '--', 'no coasting')]:
    for mot, c in [('kalman', '#eb6834'), ('none', '#2a78d6')]:
        ax[2].plot(P, [100 * T[key][f'{p}|{mot}']['mota'][0] for p in ps], ls, marker='o', ms=2.5, c=c, lw=1, label=f'{"Kalman" if mot == "kalman" else "no motion"}, {nm}')
ax[2].set_xlabel('detections dropped (%)'); ax[2].set_ylabel('MOTA (%)'); ax[2].set_title('(c) tracking with missed detections', fontsize=7); ax[2].legend(fontsize=5, frameon=False)
for a in ax: a.tick_params(labelsize=6)
fig.tight_layout(w_pad=0.6); fig.savefig('/root/arxiv/src/fig/extended.pdf', bbox_inches='tight'); print('ok')
