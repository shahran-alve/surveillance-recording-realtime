import cv2, numpy as np, time, json, os, sys
D = '/root/data/opencv_extra/testdata/cv/tracking'; M = '/root/data/models'
SEQS = ['faceocc2', 'david', 'dudek']
def make(name):
    if name == 'MIL': return cv2.TrackerMIL_create()
    if name == 'KCF': return cv2.TrackerKCF_create()
    if name == 'CSRT': return cv2.TrackerCSRT_create()
    if name == 'MOSSE': return cv2.legacy.TrackerMOSSE_create()
    if name == 'NanoTrack (Siamese)':
        p = cv2.TrackerNano_Params(); p.backbone = f'{M}/nanotrack_backbone_sim.onnx'; p.neckhead = f'{M}/nanotrack_head_sim.onnx'
        return cv2.TrackerNano_create(p)
    if name == 'VitTrack':
        p = cv2.TrackerVit_Params(); p.net = f'{M}/vitTracker.onnx'; return cv2.TrackerVit_create(p)
def iou(a, b):
    ax2, ay2, bx2, by2 = a[0]+a[2], a[1]+a[3], b[0]+b[2], b[1]+b[3]
    iw = max(0, min(ax2, bx2)-max(a[0], b[0])); ih = max(0, min(ay2, by2)-max(a[1], b[1]))
    u = a[2]*a[3]+b[2]*b[3]-iw*ih; return iw*ih/u if u > 0 else 0
def load(seq):
    gt = np.loadtxt(f'{D}/{seq}/gt.txt', delimiter=',')
    cap = cv2.VideoCapture(f'{D}/{seq}/data/{seq}.webm'); F = []
    while True:
        ok, f = cap.read()
        if not ok: break
        F.append(f)
    hard = np.zeros(len(gt), bool)
    p = f'{D}/{seq}/initOmit/{seq}.txt'
    if os.path.exists(p):
        for line in open(p):
            if line.strip(): a, b = map(int, line.split()); hard[a-1:b] = True
    import re
    st = int(re.search(r'start:\s*(\d+)', open(f'{D}/{seq}/{seq}.yml').read()).group(1))
    return F[st-1:st-1+len(gt)], gt, hard
cv2.setNumThreads(1)
res = {}
for seq in SEQS:
    F, gt, hard = load(seq)
    for name in ['MOSSE', 'KCF', 'MIL', 'CSRT', 'NanoTrack (Siamese)', 'VitTrack']:
        tr = make(name); tr.init(F[0], tuple(int(v) for v in gt[0]))
        ious, errs, t = [1.0], [0.0], 0.0
        for i in range(1, len(gt)):
            t0 = time.perf_counter(); ok, b = tr.update(F[i]); t += time.perf_counter()-t0
            b = b if ok else (0, 0, 0, 0)
            ious.append(iou(b, gt[i]) if ok else 0.0)
            c1 = np.array([b[0]+b[2]/2, b[1]+b[3]/2]); c2 = gt[i, :2]+gt[i, 2:]/2
            errs.append(np.linalg.norm(c1-c2) if ok else 1e9)
        ious, errs = np.array(ious), np.array(errs)
        th = np.linspace(0, 1, 21)
        succ = lambda m: float(np.mean([(ious[m] > x).mean() for x in th]))
        res[f'{seq}|{name}'] = dict(seq=seq, tracker=name, auc=succ(slice(None)), prec20=float((errs <= 20).mean()),
            auc_hard=succ(hard) if hard.any() else None, auc_easy=succ(~hard) if hard.any() else None,
            fps=(len(gt)-1)/t, n=len(gt), n_hard=int(hard.sum()))
        print(res[f'{seq}|{name}'], flush=True)
os.makedirs('/root/results/sot', exist_ok=True)
json.dump(res, open('/root/results/sot/sot.json', 'w'), indent=1)
