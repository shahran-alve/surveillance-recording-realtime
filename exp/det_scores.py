import sys, os, numpy as np, torch
sys.path.insert(0, '/root/exp')
from common import VIDEOS, frames, video_info
from perturb import make_perturber
from ultralytics import YOLO
torch.set_num_threads(1)
CLS = [0, 1, 2, 3, 5, 7]  # person, bicycle, car, motorcycle, bus, truck
model_name, kinds = sys.argv[1], sys.argv[2].split(',')
m = YOLO(f'/root/data/models/{model_name}.pt')
os.makedirs('/root/results/det_scores', exist_ok=True)
for kind in kinds:
    for name in VIDEOS:
        out = f'/root/results/det_scores/{model_name}_{name}_{kind}.npy'
        if os.path.exists(out): continue
        fps, n = video_info(name); P = make_perturber(kind, n, seed=sum(map(ord, name)))
        S = []
        for t, f in enumerate(frames(name)):
            r = m.predict(P(t, f), imgsz=640, conf=0.05, classes=CLS, verbose=False)[0]
            S.append(float(r.boxes.conf.max()) if len(r.boxes) else 0.0)
        np.save(out, np.array(S)); print('done', out, flush=True)
