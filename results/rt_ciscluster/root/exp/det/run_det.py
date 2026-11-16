"""Detector accuracy on VisDrone2019-DET-val (person & vehicle, COCO-pretrained, zero-shot)."""
import sys, os, json, time, numpy as np, cv2, torch
sys.path.insert(0, '/root/exp/det')
from visdrone import image_list, build_gt, COCO2CAT
torch.set_num_threads(int(os.environ.get('THREADS', '1')))
OUT = '/root/results/det'; os.makedirs(OUT, exist_ok=True)
paths = image_list()
GT = f'{OUT}/visdrone_gt.json'
if not os.path.exists(GT): build_gt(paths, GT)

def nms_merge(boxes, scores, cls, iou=0.6):
    import torchvision
    keep = torchvision.ops.batched_nms(torch.tensor(boxes, dtype=torch.float32), torch.tensor(scores, dtype=torch.float32), torch.tensor(cls), iou)
    return keep.numpy()

def ultra(model, imgsz, tiles=False, tta=False):
    from ultralytics import YOLO
    m = YOLO(f'/root/data/models/{model}.pt')
    def run(img):
        B, S, C = [], [], []
        views = [(0, 0, img)]
        if tiles:
            H, W = img.shape[:2]; th, tw = int(np.ceil(H/2*1.2)), int(np.ceil(W/2*1.2))
            for y0 in (0, H-th):
                for x0 in (0, W-tw): views.append((x0, y0, img[y0:y0+th, x0:x0+tw]))
        for x0, y0, v in views:
            r = m.predict(v, imgsz=imgsz, conf=0.001, iou=0.7, classes=list(COCO2CAT), max_det=300, verbose=False, augment=tta)[0].boxes
            b = r.xyxy.numpy().copy(); b[:, [0, 2]] += x0; b[:, [1, 3]] += y0
            B.append(b); S.append(r.conf.numpy()); C.append(r.cls.numpy().astype(int))
        B, S, C = np.concatenate(B), np.concatenate(S), np.concatenate(C)
        if tiles and len(B):
            k = nms_merge(B, S, C); k = k[np.argsort(-S[k])][:300]; B, S, C = B[k], S[k], C[k]
        return B, S, C
    return run

def yolox(model, imgsz):
    import onnxruntime as ort
    so = ort.SessionOptions(); so.intra_op_num_threads = int(os.environ.get('THREADS', '1'))
    sess = ort.InferenceSession(f'/root/data/models/{model}.onnx', so, providers=['CPUExecutionProvider'])
    inp = sess.get_inputs()[0].name
    grids, strides = [], []
    for s in (8, 16, 32):
        hs, ws = imgsz//s, imgsz//s; xv, yv = np.meshgrid(np.arange(ws), np.arange(hs))
        g = np.stack((xv, yv), 2).reshape(-1, 2); grids.append(g); strides.append(np.full((len(g), 1), s))
    grids, strides = np.concatenate(grids), np.concatenate(strides)
    def run(img):
        H, W = img.shape[:2]; r = min(imgsz/H, imgsz/W)
        pad = np.full((imgsz, imgsz, 3), 114, np.uint8); rs = cv2.resize(img, (int(W*r), int(H*r)), interpolation=cv2.INTER_LINEAR)
        pad[:rs.shape[0], :rs.shape[1]] = rs
        x = pad.transpose(2, 0, 1)[None].astype(np.float32)
        o = sess.run(None, {inp: x})[0][0]
        o[:, :2] = (o[:, :2]+grids)*strides; o[:, 2:4] = np.exp(o[:, 2:4])*strides
        sc = o[:, 4:5]*o[:, 5:]; cls = sc.argmax(1); conf = sc.max(1)
        sel = np.isin(cls, list(COCO2CAT)) & (conf > 0.001); o, cls, conf = o[sel], cls[sel], conf[sel]
        b = np.stack([o[:, 0]-o[:, 2]/2, o[:, 1]-o[:, 3]/2, o[:, 0]+o[:, 2]/2, o[:, 1]+o[:, 3]/2], 1)/r
        if len(b):
            k = nms_merge(b, conf, cls, 0.65)[:300]; b, conf, cls = b[k], conf[k], cls[k]
        return b, conf, cls
    return run

def run_cfg(tag, fn, subset=None):
    out = f'{OUT}/dets_{tag}.json'
    if os.path.exists(out): return out
    dets = []; t = 0
    for i, p in enumerate(paths):
        if subset is not None and i not in subset: continue
        img = cv2.imread(p); t0 = time.perf_counter(); B, S, C = fn(img); t += time.perf_counter()-t0
        for b, s, c in zip(B, S, C):
            dets.append({'image_id': i, 'category_id': COCO2CAT[int(c)], 'bbox': [float(b[0]), float(b[1]), float(b[2]-b[0]), float(b[3]-b[1])], 'score': float(s)})
    json.dump(dets, open(out, 'w')); print(tag, 'done', round(t, 1), 's', flush=True)
    return out

if __name__ == '__main__':
    cfgs = sys.argv[1:]
    for c in cfgs:
        fam, model, imgsz, *rest = c.split(':'); imgsz = int(imgsz); tiles = 'tiles' in rest; tta = 'tta' in rest
        tag = f'{model}_{imgsz}' + ('_tiles' if tiles else '') + ('_tta' if tta else '')
        fn = ultra(model, imgsz, tiles, tta) if fam == 'ultra' else yolox(model, imgsz)
        run_cfg(tag, fn)
