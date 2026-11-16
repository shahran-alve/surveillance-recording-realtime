import cv2, numpy as np, os, json
VID_DIR = '/root/data/sample-videos'
# name: (file, frame step to reach ~10-12 fps)
VIDEOS = {
 'one-by-one':        ('one-by-one-person-detection.mp4', 1),
 'people':            ('people-detection.mp4', 1),
 'person-bike-car':   ('person-bicycle-car-detection.mp4', 1),
 'walk-and-pause':    ('face-demographics-walking-and-pause.mp4', 1),
 'worker-zone':       ('worker-zone-detection.mp4', 5),
 'car-lot':           ('car-detection.mp4', 1),
 'store-aisle':       ('store-aisle-detection.mp4', 5),
}
WIDTH = 768
def video_info(name):
    f, step = VIDEOS[name]
    c = cv2.VideoCapture(os.path.join(VID_DIR, f))
    fps = c.get(cv2.CAP_PROP_FPS); n = int(c.get(cv2.CAP_PROP_FRAME_COUNT))
    return fps/step, len(range(0, n, step))
def frames(name):
    """Yield standardized frames (BGR, width 768) at the benchmark frame rate."""
    f, step = VIDEOS[name]
    c = cv2.VideoCapture(os.path.join(VID_DIR, f)); i = 0
    while True:
        ok, fr = c.read()
        if not ok: break
        if i % step == 0:
            h = int(round(fr.shape[0]*WIDTH/fr.shape[1]))
            if fr.shape[1] != WIDTH: fr = cv2.resize(fr, (WIDTH, h), interpolation=cv2.INTER_AREA)
            yield fr
        i += 1
