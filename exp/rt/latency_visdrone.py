"""Median CPU latency (2 threads) of every detector configuration on 50 VisDrone validation images (after 10 warm-up images)."""
import sys, time, json, numpy as np, cv2, torch, os
sys.path.insert(0, '/root/exp/det'); torch.set_num_threads(2); os.environ['THREADS'] = '2'
import run_det as R
from visdrone import image_list
VD = [cv2.imread(p) for p in image_list()[:60]]; res = {}
CFG = ['yolox:yolox_nano:416', 'yolox:yolox_tiny:416', 'yolox:yolox_s:640', 'ultra:yolov8n:640', 'ultra:yolo11n:640', 'ultra:yolo26n:640', 'ultra:yolov8s:640', 'ultra:yolo11s:640', 'ultra:yolo26s:640',
       'ultra:yolo11n:960', 'ultra:yolo11n:1280', 'ultra:yolo11n:640:tiles', 'ultra:yolo11n:640:tta', 'ultra:yolo11s:960', 'ultra:yolo11s:1280', 'ultra:yolo26n:960', 'ultra:yolo26n:1280', 'ultra:yolo26s:960', 'ultra:yolo26s:1280']
for c in CFG:
    fam, model, imgsz, *rest = c.split(':'); fn = R.ultra(model, int(imgsz), 'tiles' in rest, 'tta' in rest) if fam == 'ultra' else R.yolox(model, int(imgsz)); ts = []
    for i, f in enumerate(VD):
        t0 = time.perf_counter(); fn(f); dt = time.perf_counter() - t0
        if i >= 10: ts.append(dt)
    key = f'{model}_{imgsz}' + ''.join('_' + r for r in rest); res[key] = 1000 * float(np.median(ts)); res[key + '|p99'] = 1000 * float(np.percentile(ts, 99)); print(key, round(res[key], 1), round(res[key + '|p99'], 1), flush=True)
    json.dump(res, open('/root/results/rt/latency_visdrone.json', 'w'), indent=1)
print('DONE')
