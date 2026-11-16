import sys, glob, os, json
sys.path.insert(0, '/root/exp/det'); from coco_eval import evaluate
GT = '/root/results/det/visdrone_gt.json'; out = {}
for f in sorted(glob.glob('/root/results/det/dets_*.json')):
    tag = os.path.basename(f)[5:-5]
    if tag.startswith('test'): continue
    r = {'all': evaluate(GT, f), 'person': evaluate(GT, f, cat=1), 'vehicle': evaluate(GT, f, cat=2)}
    out[tag] = r; print(tag, {k: round(v, 3) for k, v in r['all'].items()}, 'person AP50', round(r['person']['AP50'], 3), 'veh AP50', round(r['vehicle']['AP50'], 3), flush=True)
json.dump(out, open('/root/results/det/det_metrics.json', 'w'), indent=1)
