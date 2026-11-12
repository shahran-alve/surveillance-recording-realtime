import json, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family': 'serif', 'font.size': 7.5, 'axes.spines.top': False, 'axes.spines.right': False, 'axes.linewidth': 0.6, 'xtick.major.width': 0.6, 'ytick.major.width': 0.6, 'pdf.fonttype': 42})
BLUE, GREY, ORANGE = '#2a78d6', '#9a9890', '#eb6834'
M = json.load(open('/root/results/det/det_metrics.json')); L = json.load(open('/root/results/latency_det.json'))
L2 = json.load(open('/root/results/latency_det_more.json'))
for k, v in L2.items():
    _, m, s, *r = k.split(':'); L['visdrone|' + f'{m}_{s}' + ('_tta' if 'tta' in r else '')] = v
lab = lambda k: {'yolox_nano_416': 'YOLOX-nano', 'yolox_tiny_416': 'YOLOX-tiny', 'yolox_s_640': 'YOLOX-s', 'yolov8n_640': 'YOLOv8n', 'yolov8s_640': 'YOLOv8s',
                 'yolo11n_640_tiles': 'YOLO11n tiles', 'yolo11n_640_tta': 'YOLO11n TTA'}.get(k, '')
fig, a = plt.subplots(figsize=(3.25, 2.4))
for series, col, ls, name in [(['yolo11n_640', 'yolo11n_960', 'yolo11n_1280'], BLUE, '-', 'YOLO11n'), (['yolo11s_640', 'yolo11s_960', 'yolo11s_1280'], BLUE, '--', 'YOLO11s'),
                              (['yolo26n_640', 'yolo26n_960', 'yolo26n_1280'], ORANGE, '-', 'YOLO26n'), (['yolo26s_640', 'yolo26s_960', 'yolo26s_1280'], ORANGE, '--', 'YOLO26s')]:
    xs = [L['visdrone|' + k] for k in series]; ys = [100 * M[k]['all']['AP'] for k in series]
    a.plot(xs, ys, ls, marker='o', ms=3.2, color=col, lw=1, label=name + ' (640/960/1280)')
for k in ['yolox_nano_416', 'yolox_tiny_416', 'yolox_s_640', 'yolov8n_640', 'yolov8s_640', 'yolo11n_640_tiles', 'yolo11n_640_tta']:
    x, y = L['visdrone|' + k], 100 * M[k]['all']['AP']; a.plot(x, y, 's', ms=3, color=GREY)
    a.annotate(lab(k), (x, y), xytext=(3, -7 if k in ('yolov8n_640', 'yolo11n_640_tta', 'yolov8s_640') else 2), textcoords='offset points', fontsize=5.5, color='#555')
a.set_xscale('log'); a.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter()); a.set_xticks([20, 50, 100, 200, 500]); a.set_xticklabels(['20', '50', '100', '200', '500'])
a.set_xlabel('CPU latency per image (ms, 2 threads, log scale)'); a.set_ylabel('AP (IoU 0.5:0.95)'); a.set_ylim(0, 37); a.set_xlim(15, 1000)
a.grid(lw=0.4, color='#e5e5e5'); a.set_axisbelow(True); a.legend(fontsize=5.5, frameon=False, loc='upper left')
plt.savefig('/root/arxiv/src/fig/speed_acc.pdf', bbox_inches='tight', pad_inches=0.02); print('ok')
