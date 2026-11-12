import os, glob, json, numpy as np, cv2
ROOT = '/root/data/visdrone/VisDrone2019-DET-val'
CATS = [{'id': 1, 'name': 'person'}, {'id': 2, 'name': 'vehicle'}]
VD2CAT = {1: 1, 2: 1, 4: 2, 5: 2, 6: 2, 9: 2}
COCO2CAT = {0: 1, 2: 2, 5: 2, 7: 2}
def image_list():
    return sorted(glob.glob(f'{ROOT}/images/*.jpg'))
def build_gt(paths, out):
    imgs, anns = [], []; aid = 1
    for i, p in enumerate(paths):
        h, w = cv2.imread(p).shape[:2]; imgs.append({'id': i, 'file_name': os.path.basename(p), 'width': w, 'height': h})
        a = np.loadtxt(p.replace('/images/', '/annotations/').replace('.jpg', '.txt'), delimiter=',', ndmin=2, usecols=range(8))
        for x, y, bw, bh, score, c, trunc, occ in a:
            c = int(c)
            if c in (0, 11):  # ignored region / others -> crowd (ignore) for both categories
                for cid in (1, 2):
                    anns.append({'id': aid, 'image_id': i, 'category_id': cid, 'bbox': [x, y, bw, bh], 'area': bw*bh, 'iscrowd': 1, 'occ': -1}); aid += 1
            elif c in VD2CAT:
                anns.append({'id': aid, 'image_id': i, 'category_id': VD2CAT[c], 'bbox': [x, y, bw, bh], 'area': bw*bh, 'iscrowd': 0, 'occ': int(occ)}); aid += 1
    json.dump({'images': imgs, 'annotations': anns, 'categories': CATS}, open(out, 'w'))
    return out
