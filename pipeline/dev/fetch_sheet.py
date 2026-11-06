"""Télécharge une liste de sources et produit une planche (une ligne de 8 vignettes par source)."""
import sys, os, subprocess, json
sys.path.insert(0, '/home/user/n/pipeline')
import numpy as np, cv2
from concurrent.futures import ThreadPoolExecutor
import footage
out = sys.argv[1]; refs = sys.argv[2:]
def get(r):
    try:
        m = footage.resolve(r); return r, m, footage.probe(m['path']), None
    except Exception as e:
        return r, None, None, str(e)
with ThreadPoolExecutor(4) as ex:
    res = list(ex.map(get, refs))
rows = []
for i, (r, m, info, err) in enumerate(res):
    if err:
        print('ERR', r, err); continue
    dur = info['dur']; print(f"[{i}] {r} | {info['w']}x{info['h']} | {dur:.1f}s | {(os.path.getsize(m['path'])/1e6 if os.path.exists(m['path']) else 0):.0f}MB")
    tiles = []
    n = int(os.environ.get('NFR', 8))
    for k in range(n):
        t = (k + 0.5) * dur / n if dur > 0.5 else 0
        if dur > 0.5:
            rr = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.2f}', '-i', m['path'], '-frames:v', '1', '-vf', 'scale=240:135:force_original_aspect_ratio=decrease,pad=240:135:(ow-iw)/2:(oh-ih)/2', '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True)
            img = cv2.imdecode(np.frombuffer(rr.stdout, np.uint8), cv2.IMREAD_COLOR)
        else:
            im = cv2.imread(m['path']); img = cv2.resize(im, (240, 135)) if k == 0 else None
        if img is None:
            img = np.zeros((135, 240, 3), np.uint8)
        cv2.putText(img, f'{i}:{t:.0f}s', (4, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        tiles.append(img)
    rows.append(np.hstack(tiles))
cv2.imwrite(out, np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 80])
