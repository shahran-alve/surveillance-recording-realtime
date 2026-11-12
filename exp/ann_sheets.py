import sys, cv2, numpy as np, math
sys.path.insert(0,'/root/exp')
from common import VIDEOS, frames, video_info
TW, COLS, ROWS = 320, 6, 6
import sys as _s
for name in (_s.argv[1:] or VIDEOS):
    fps, n = video_info(name)
    tiles = []
    pick = {int(round(k*fps)): k for k in range(int(n/fps)+1)}
    for t, f in enumerate(frames(name)):
        if t in pick:  # one frame per second
            s = pick[t]; h = int(f.shape[0]*TW/f.shape[1]); x = cv2.resize(f, (TW, h))
            cv2.rectangle(x, (0,0), (70,20), (0,0,0), -1); cv2.putText(x, f"{s}s", (4,15), 0, 0.5, (0,255,255), 1)
            tiles.append(x)
    per = COLS*ROWS
    for p in range(math.ceil(len(tiles)/per)):
        ch = tiles[p*per:(p+1)*per]; h = ch[0].shape[0]
        S = np.zeros((math.ceil(len(ch)/COLS)*h, COLS*TW, 3), np.uint8)
        for i, x in enumerate(ch): S[(i//COLS)*h:(i//COLS+1)*h, (i%COLS)*TW:(i%COLS+1)*TW] = x
        cv2.imwrite(f'/root/work/sheets/ann_{name}_{p}.jpg', S, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(name, len(tiles))
