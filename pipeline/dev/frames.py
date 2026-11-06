"""Planche de 16 images d'un MP4 final."""
import sys, subprocess, numpy as np, cv2
V, out = sys.argv[1], sys.argv[2]
d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', V], capture_output=True, text=True).stdout)
tiles = []
for k in range(16):
    t = 1.0 + k * (d - 2.0) / 15
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.2f}', '-i', V, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True)
    img = np.frombuffer(r.stdout, np.uint8).reshape(1920, 1080, 3)
    s = cv2.resize(img, (216, 384), interpolation=cv2.INTER_AREA).copy()
    cv2.putText(s, f'{t:.0f}', (5, 20), 0, 0.6, (255, 0, 0), 2); tiles.append(s)
cv2.imwrite(out, cv2.cvtColor(np.vstack([np.hstack(tiles[i:i + 8]) for i in range(0, 16, 8)]), cv2.COLOR_RGB2BGR))
print(f'{d:.1f}s')
