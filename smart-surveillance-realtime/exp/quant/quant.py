"""FP32 vs INT8 (static, QDQ) ONNX of YOLO11n on VisDrone: accuracy on held-out images + CPU latency."""
import sys, os, json, time, numpy as np, cv2, glob
sys.path.insert(0, '/root/exp/det')
from visdrone import image_list, COCO2CAT
from coco_eval import evaluate
import onnxruntime as ort
from onnxruntime.quantization import quantize_static, CalibrationDataReader, QuantFormat, QuantType
from onnxruntime.quantization.shape_inference import quant_pre_process
OUT = '/root/results/quant'; os.makedirs(OUT, exist_ok=True)
paths = image_list(); CAL = list(range(0, 548, 11))[:50]; EVAL = [i for i in range(548) if i not in CAL]
SZ = 640
fp32 = '/root/data/models/yolo11n.onnx'
if not os.path.exists(fp32):
    from ultralytics import YOLO
    YOLO('/root/data/models/yolo11n.pt').export(format='onnx', imgsz=SZ, opset=17, simplify=False, dynamic=False)
def prep(img):
    H, W = img.shape[:2]; r = min(SZ/H, SZ/W); nh, nw = int(round(H*r)), int(round(W*r))
    pad = np.full((SZ, SZ, 3), 114, np.uint8); top, left = (SZ-nh)//2, (SZ-nw)//2
    pad[top:top+nh, left:left+nw] = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LINEAR)
    x = pad[:, :, ::-1].transpose(2, 0, 1)[None].astype(np.float32)/255.
    return np.ascontiguousarray(x), r, left, top
class Reader(CalibrationDataReader):
    def __init__(s): s.it = iter([{'images': prep(cv2.imread(paths[i]))[0]} for i in CAL])
    def get_next(s): return next(s.it, None)
int8 = f'{OUT}/yolo11n_int8.onnx'
if not os.path.exists(int8):
    pre = f'{OUT}/yolo11n_pre.onnx'; quant_pre_process(fp32, pre)
    import onnx
    head = [n.name for n in onnx.load(pre).graph.node if '/model.23/' in n.name]  # keep the detection head in FP32
    quantize_static(pre, int8, Reader(), quant_format=QuantFormat.QDQ, per_channel=True, nodes_to_exclude=head,
                    activation_type=QuantType.QUInt8, weight_type=QuantType.QInt8)
import torch, torchvision
def run(model, tag, threads):
    so = ort.SessionOptions(); so.intra_op_num_threads = threads
    s = ort.InferenceSession(model, so, providers=['CPUExecutionProvider']); name = s.get_inputs()[0].name
    dets = []; times = []
    for i in EVAL:
        img = cv2.imread(paths[i]); x, r, left, top = prep(img)
        t0 = time.perf_counter(); o = s.run(None, {name: x})[0][0]; times.append(time.perf_counter()-t0)
        o = o.T; b, sc = o[:, :4], o[:, 4:]; cls = sc.argmax(1); conf = sc.max(1)
        m = np.isin(cls, list(COCO2CAT)) & (conf > 0.001); b, cls, conf = b[m], cls[m], conf[m]
        xy = np.stack([b[:, 0]-b[:, 2]/2, b[:, 1]-b[:, 3]/2, b[:, 0]+b[:, 2]/2, b[:, 1]+b[:, 3]/2], 1)
        xy[:, [0, 2]] = (xy[:, [0, 2]]-left)/r; xy[:, [1, 3]] = (xy[:, [1, 3]]-top)/r
        if len(xy):
            k = torchvision.ops.batched_nms(torch.tensor(xy), torch.tensor(conf), torch.tensor(cls), 0.7).numpy()[:300]
            for j in k: dets.append({'image_id': i, 'category_id': COCO2CAT[int(cls[j])], 'bbox': [float(xy[j, 0]), float(xy[j, 1]), float(xy[j, 2]-xy[j, 0]), float(xy[j, 3]-xy[j, 1])], 'score': float(conf[j])})
    f = f'{OUT}/dets_{tag}.json'; json.dump(dets, open(f, 'w'))
    ev = evaluate('/root/results/det/visdrone_gt.json', f, EVAL)
    ev['ms_median'] = 1000*float(np.median(times[5:])); ev['size_MB'] = os.path.getsize(model)/1e6
    print(tag, ev, flush=True); return ev
res = {t: run(m, t, int(os.environ.get('THREADS', '2'))) for t, m in [('fp32', fp32), ('int8', int8)]}
json.dump(res, open(f'{OUT}/quant.json', 'w'), indent=1)
