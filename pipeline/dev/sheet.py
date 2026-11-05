"""Planche de contrôle : rend une image de chaque scène à un instant donné."""
import sys, time, numpy as np, cv2
sys.path.insert(0, '/home/user/n/pipeline')
from common import *
def sheet(scenes, out, cols=4, t_frac=0.5, dur=4.0, scale=0.25):
    tiles = []
    for name, sc in scenes:
        t0 = time.time(); sc.setup(dur); t1 = time.time()
        img = sc.render(dur * t_frac, dur); t2 = time.time()
        img = to_u8(np.clip(img, 0, 1))
        small = cv2.resize(img, (int(W * scale), int(H * scale)), interpolation=cv2.INTER_AREA)
        cv2.putText(small, name, (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        print(f'{name}: setup {t1-t0:.2f}s render {t2-t1:.3f}s')
        tiles.append(small)
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
    cv2.imwrite(out, cv2.cvtColor(np.vstack(rows), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])
