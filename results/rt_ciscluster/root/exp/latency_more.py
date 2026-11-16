import sys, time, json, numpy as np, cv2, torch, os
sys.path.insert(0, '/root/exp/det'); torch.set_num_threads(2); os.environ['THREADS'] = '2'
import run_det as R
from visdrone import image_list
VD = [cv2.imread(p) for p in image_list()[:60]]; res = {}
for c in sys.argv[1:]:
    fam, model, imgsz, *rest = c.split(':'); fn = R.ultra(model, int(imgsz), 'tiles' in rest, 'tta' in rest); ts = []
    for i, f in enumerate(VD):
        t0 = time.perf_counter(); fn(f); dt = time.perf_counter() - t0
        if i >= 10: ts.append(dt)
    res[c] = 1000 * float(np.median(ts)); print(c, round(res[c], 1), flush=True)
json.dump(res, open('/root/results/latency_det_more.json', 'w'), indent=1)
