# Manual event annotations (seconds, inclusive) made from 1-frame-per-second contact sheets.
# An "event" = at least one person or vehicle (any visible part) is in view.
EVENTS = {
 'one-by-one':      [(6,19),(23,44),(51,69),(75,86),(93,119),(124,135)],
 'people':          [(2,6),(15,21),(28,34),(44,46)],
 'person-bike-car': [(2,7),(15,20),(25,29),(41,49)],
 'walk-and-pause':  [(4,19),(28,43),(55,68),(75,86)],
 'worker-zone':     [(3,9),(12,30),(34,44),(48,56),(58,74)],
 'car-lot':         [(5,8),(15,19),(26,27)],
 'store-aisle':     [(7,65)],
}
import numpy as np
def frame_labels(name, fps, n, dc=1.0):
    """Returns (label[n] in {0,1}, valid[n]) ; frames within dc seconds of an annotated boundary are 'don't care'."""
    t = np.arange(n)/fps
    lab = np.zeros(n, bool); valid = np.ones(n, bool)
    for a, b in EVENTS[name]:
        lo, hi = a-0.5, b+0.5
        lab |= (t >= lo) & (t <= hi)
        valid &= ~((np.abs(t-lo) < dc) | (np.abs(t-hi) < dc))
    return lab, valid
