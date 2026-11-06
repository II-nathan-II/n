"""Couches « images réelles » : extraits vidéo (NASA, Commons…) et photos, recadrés en 9:16 pour le montage."""
import os, json, hashlib, subprocess
import numpy as np
import cv2
from common import *
from layers_base import Layer
import footage

CLIPS = os.path.join(WORK, 'clips')

def _probe(path):
    return footage.probe(path)

class Clip(Layer):
    """Extrait vidéo réel.
    ref   : 'svs:<page>/<fichier>' | 'nasa:<id>' | 'commons:File:...'
    at    : point d'entrée (s) dans la source ; speed : vitesse (2 = accéléré)
    mode  : 'cover' (plein écran recadré, cx/cy = centre du recadrage 0..1) | 'fit' (cadre centré sur fond flou)
    zoom  : recadrage supplémentaire (1 = aucun) ; flip : miroir horizontal
    """
    def __init__(self, ref, at=0.0, speed=1.0, mode='cover', cx=0.5, cy=0.5, zoom=1.0, flip=False, grade=None, fit_scale=1.0):
        self.__dict__.update(locals()); del self.__dict__['self']
        self.cap = None
    def setup(self, dur):
        meta = footage.resolve(self.ref)
        self.meta = meta
        src = meta['path']
        info = _probe(src)
        sw, sh = info['w'], info['h']
        need = (dur + 1.2) * self.speed
        key = hashlib.md5(json.dumps([src, self.at, round(need, 2), self.speed, self.mode, self.cx, self.cy, self.zoom, self.flip, self.fit_scale]).encode()).hexdigest()[:16]
        os.makedirs(CLIPS, exist_ok=True)
        self.path = os.path.join(CLIPS, key + '.mp4')
        if not os.path.exists(self.path):
            if self.mode == 'cover':
                cw = min(sw, sh * 9 / 16) / self.zoom
                ch = cw * 16 / 9
                x = max(0, min(sw - cw, self.cx * sw - cw / 2)); y = max(0, min(sh - ch, self.cy * sh - ch / 2))
                vf = f'crop={int(cw)}:{int(ch)}:{int(x)}:{int(y)},scale={W}:{H}:flags=lanczos'
                if cw < W * 0.8:
                    vf += ',unsharp=5:5:0.7:5:5:0.0'
            else:
                fw = int(W * self.fit_scale) // 2 * 2
                vf = (f'split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=40:4,eq=brightness=-0.12:saturation=1.1[bg];'
                      f'[b]scale={fw}:-2:flags=lanczos,unsharp=5:5:0.5[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2-40')
            if self.flip:
                vf += ',hflip'
            if self.speed != 1.0:
                vf += f',setpts=PTS/{self.speed}'
            vf += f',fps={FPS},format=yuv420p'
            cmd = ['ffmpeg', '-v', 'error', '-y', '-ss', f'{self.at:.3f}', '-t', f'{need:.3f}', '-i', src, '-an', '-filter_complex' if self.mode == 'fit' else '-vf', vf,
                   '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '15', self.path + '.part.mp4']
            subprocess.run(cmd, check=True)
            os.replace(self.path + '.part.mp4', self.path)
        self.nframes = int(cv2.VideoCapture(self.path).get(cv2.CAP_PROP_FRAME_COUNT))
        self.cap = None; self.idx = -1; self.last = None
    def _frame(self, i):
        i = max(0, min(i, self.nframes - 1)) if self.nframes > 0 else 0
        if self.cap is None or i < self.idx:
            self.cap = cv2.VideoCapture(self.path); self.idx = -1
        while self.idx < i:
            ok, fr = self.cap.read()
            if not ok:
                break
            self.idx += 1
            self.last = fr
        return self.last
    def draw(self, f, t, dur):
        fr = self._frame(int(t * FPS))
        if fr is not None:
            f[:] = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255
        return f


class Photo(Layer):
    """Photo réelle (Hubble, Webb, ISS…). Le mouvement (Ken Burns) est fait par la caméra du plan."""
    def __init__(self, ref, mode='cover', cx=0.5, cy=0.5, zoom=1.0):
        self.__dict__.update(locals()); del self.__dict__['self']
    def setup(self, dur):
        meta = footage.resolve(self.ref)
        self.meta = meta
        img = cv2.imread(meta['path'], cv2.IMREAD_COLOR)
        if img is None:
            raise RuntimeError('image illisible ' + meta['path'])
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255
        sh, sw = img.shape[:2]
        if self.mode == 'cover':
            cw = min(sw, sh * 9 / 16) / self.zoom; ch = cw * 16 / 9
            x = int(max(0, min(sw - cw, self.cx * sw - cw / 2))); y = int(max(0, min(sh - ch, self.cy * sh - ch / 2)))
            crop = img[y:y + int(ch), x:x + int(cw)]
            self.img = cv2.resize(crop, (W, H), interpolation=cv2.INTER_AREA if cw > W else cv2.INTER_CUBIC)
        else:
            bg = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA)
            s = max(W / sw, H / sh)
            bg = cv2.resize(img, (int(sw * s) + 2, int(sh * s) + 2), interpolation=cv2.INTER_AREA)
            y0 = (bg.shape[0] - H) // 2; x0 = (bg.shape[1] - W) // 2
            bg = cv2.GaussianBlur(bg[y0:y0 + H, x0:x0 + W], (0, 0), 30) * 0.75
            fh = int(sh * W / sw)
            fg = cv2.resize(img, (W, fh), interpolation=cv2.INTER_AREA)
            out = bg.copy(); y = (H - fh) // 2 - 40
            out[max(0, y):y + fh] = fg[max(0, -y):fh - max(0, y + fh - H)]
            self.img = out
    def draw(self, f, t, dur):
        f[:] = self.img
        return f
