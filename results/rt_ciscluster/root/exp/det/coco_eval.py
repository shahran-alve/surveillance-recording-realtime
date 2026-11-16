import json, numpy as np, io, contextlib
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval
def evaluate(gt_json, det_json, img_ids=None, cat=None):
    with contextlib.redirect_stdout(io.StringIO()):
        G = COCO(gt_json); D = G.loadRes(det_json) if len(json.load(open(det_json))) else None
        E = COCOeval(G, D, 'bbox')
        if img_ids is not None: E.params.imgIds = img_ids
        if cat is not None: E.params.catIds = [cat]
        E.params.maxDets = [1, 100, 500]
        E.evaluate(); E.accumulate(); E.summarize()
    s = E.stats
    return dict(AP=s[0], AP50=s[1], AP75=s[2], APs=s[3], APm=s[4], APl=s[5], AR500=s[8])
