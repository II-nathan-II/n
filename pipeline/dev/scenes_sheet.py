"""Planche de toutes les scènes d'une vidéo (timeline factice de 3,5 s par segment)."""
import sys, inspect; sys.path.insert(0, '/home/user/n/pipeline'); sys.path.insert(0, '/home/user/n/pipeline/dev')
import numpy as np, cv2
from common import *
import build, render
vid = sys.argv[1]; out = sys.argv[2]; frac = float(sys.argv[3]) if len(sys.argv) > 3 else 0.6
v = build.all_videos()[vid]
segs = []
t = 0.0
for s in v['segments']:
    d = s.get('hold', 3.5) if not s.get('text') else 3.5
    segs.append(dict(start=t, end=t + d, speech_end=t + d - 0.3, words=[])); t += d
tl = dict(duration=t, segments=segs)
shots = render.build_shots(v, tl)
tiles = []
for sh in shots:
    img = render.render_shot(sh, sh.start + sh.dur * frac, [], [])
    if not getattr(sh.scene, 'clean', False):
        img = render.tonemap(np.maximum(img, 0))
    small = cv2.resize(to_u8(np.clip(img, 0, 1)), (216, 384), interpolation=cv2.INTER_AREA)
    cv2.putText(small, str(sh.idx), (6, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
    tiles.append(small)
cols = 8
while len(tiles) % cols: tiles.append(np.zeros_like(tiles[0]))
rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
cv2.imwrite(out, cv2.cvtColor(np.vstack(rows), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 85])
print(vid, len(shots), 'shots')
