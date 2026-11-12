import sys, time, json, numpy as np, cv2, torch, os
sys.path.insert(0, '/root/exp'); sys.path.insert(0, '/root/exp/det')
from common import frames
torch.set_num_threads(2); os.environ['THREADS'] = '2'
import run_det as R
from visdrone import image_list
EV = [f for i, f in zip(range(120), frames('one-by-one'))]
VD = [cv2.imread(p) for p in image_list()[:60]]
res = {}
def bench(tag, fn, imgs, warm=10):
    ts = []
    for i, f in enumerate(imgs):
        t0 = time.perf_counter(); fn(f); dt = time.perf_counter()-t0
        if i >= warm: ts.append(dt)
    res[tag] = 1000*float(np.median(ts)); print(tag, round(res[tag], 1), flush=True)
from ultralytics import YOLO
for m in ['yolov8n', 'yolo11n', 'yolo26n', 'yolo11s']:
    y = YOLO(f'/root/data/models/{m}.pt')
    bench(f'event|{m}_640', lambda f: y.predict(f, imgsz=640, conf=0.05, verbose=False), EV)
for c in sys.argv[1:]:
    fam, model, imgsz, *rest = c.split(':'); tiles = 'tiles' in rest
    fn = R.ultra(model, int(imgsz), tiles) if fam == 'ultra' else R.yolox(model, int(imgsz))
    bench(f'visdrone|{model}_{imgsz}' + ('_tiles' if tiles else ''), fn, VD)
json.dump(res, open('/root/results/latency_det.json', 'w'), indent=1)
