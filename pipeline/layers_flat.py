"""Format « animation 2D » : illustrations vectorielles plates dessinées par nos soins.

Tout est dessiné ici (PIL, suréchantillonnage ×3 puis réduction → bords nets et lisses) : aucun élément graphique
d'un autre créateur. Les scènes utilisent Composite(clean=True) : pas de tonemapping ni d'étalonnage, les
couleurs plates restent exactes ; la texture (grain léger, vignette douce) est ajoutée par FlatBG.
"""
import math, functools
import numpy as np
import cv2
from PIL import Image, ImageDraw
from common import W, H, ASSETS, blit_rgba, scale_sprite, text_sprite, ease_out, ease_out_back, ease_in_out, clamp01
from layers_base import Layer
from layers_cine import kf

SS = 3  # suréchantillonnage

def rgb(c, a=255):
    return tuple(int(round(v * 255)) for v in c) + (a,)

PAL = dict(
    navy=(0.10, 0.11, 0.29), navy2=(0.04, 0.05, 0.16), ink=(0.09, 0.09, 0.20), white=(0.97, 0.97, 0.99),
    yellow=(1.0, 0.83, 0.24), orange=(1.0, 0.56, 0.16), red=(0.93, 0.24, 0.26), cyan=(0.38, 0.85, 1.0),
    green=(0.42, 0.80, 0.38), grass=(0.33, 0.70, 0.32), grass2=(0.28, 0.62, 0.28), blue=(0.24, 0.55, 0.96),
    ocean=(0.22, 0.56, 0.95), land=(0.40, 0.78, 0.40), sand=(0.93, 0.78, 0.48), pink=(1.0, 0.45, 0.70),
    brown=(0.52, 0.33, 0.20), grey=(0.62, 0.65, 0.74), purple=(0.55, 0.40, 0.95), cream=(1.0, 0.93, 0.80),
)
INK = rgb(PAL['ink'])


def canvas(w, h):
    img = Image.new('RGBA', (int(w * SS), int(h * SS)), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def finish(img):
    w, h = img.width // SS, img.height // SS
    a = np.asarray(img, np.float32) / 255.0
    # réduction en alpha prémultiplié (pas de franges sombres), puis retour en alpha droit
    pm = a.copy(); pm[..., :3] *= pm[..., 3:4]
    pm = cv2.resize(pm, (w, h), interpolation=cv2.INTER_AREA)
    out = pm.copy()
    al = np.maximum(pm[..., 3:4], 1e-6)
    out[..., :3] = np.where(pm[..., 3:4] > 1e-6, pm[..., :3] / al, 0)
    return np.clip(out, 0, 1).astype(np.float32)


def S(v):
    return v * SS


def circle(d, cx, cy, r, fill, outline=None, width=0):
    d.ellipse([S(cx - r), S(cy - r), S(cx + r), S(cy + r)], fill=fill, outline=outline, width=int(S(width)))


def poly(d, pts, fill, outline=None, width=0):
    d.polygon([(S(x), S(y)) for x, y in pts], fill=fill, outline=outline, width=int(S(width)) if outline else 0)


def rrect(d, x0, y0, x1, y1, r, fill, outline=None, width=0):
    d.rounded_rectangle([S(x0), S(y0), S(x1), S(y1)], radius=S(r), fill=fill, outline=outline, width=int(S(width)))


def shade_mask(size, cx, cy, r, dx, dy):
    """Croissant d'ombre (disque moins disque décalé) en masque PIL."""
    m = Image.new('L', size, 0); md = ImageDraw.Draw(m)
    md.ellipse([S(cx - r), S(cy - r), S(cx + r), S(cy + r)], fill=255)
    md.ellipse([S(cx - r + dx), S(cy - r + dy), S(cx + r + dx), S(cy + r + dy)], fill=0)
    return m


def add_shade(img, cx, cy, r, color=(0, 0, 0), alpha=60, off=0.28):
    m = shade_mask(img.size, cx, cy, r, -r * off, -r * off)
    sh = Image.new('RGBA', img.size, tuple(int(c * 255) for c in color) + (alpha,))
    img.alpha_composite(Image.composite(sh, Image.new('RGBA', img.size, (0, 0, 0, 0)), m))


def highlight(d, cx, cy, r, a=110):
    img = d._image
    hl = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(hl).ellipse([S(cx - r * 0.62), S(cy - r * 0.70), S(cx - r * 0.22), S(cy - r * 0.42)], fill=(255, 255, 255, a))
    img.alpha_composite(hl)


# ----------------------------------------------------------------------------- sprites (mis en cache)
@functools.lru_cache(maxsize=64)
def spr_sun(r):
    pad = r * 0.55; size = int(2 * (r + pad))
    img, d = canvas(size, size); c = size / 2
    for k in range(12):
        a = k * math.pi / 6
        p = [(c + math.cos(a) * (r * 1.12), c + math.sin(a) * (r * 1.12)),
             (c + math.cos(a + 0.13) * (r * 1.02), c + math.sin(a + 0.13) * (r * 1.02)),
             (c + math.cos(a) * (r + pad * 0.85), c + math.sin(a) * (r + pad * 0.85)),
             (c + math.cos(a - 0.13) * (r * 1.02), c + math.sin(a - 0.13) * (r * 1.02))]
        poly(d, p, rgb(PAL['yellow']))
    circle(d, c, c, r, rgb(PAL['orange']))
    circle(d, c - r * 0.06, c - r * 0.06, r * 0.86, rgb((1.0, 0.70, 0.20)))
    circle(d, c - r * 0.14, c - r * 0.14, r * 0.62, rgb((1.0, 0.80, 0.30)))
    highlight(d, c, c, r, 90)
    return finish(img)


@functools.lru_cache(maxsize=32)
def spr_football(r):
    size = int(2 * r + 14); img, d = canvas(size, size); c = size / 2
    circle(d, c, c, r, rgb(PAL['white']))
    m = Image.new('L', img.size, 0); ImageDraw.Draw(m).ellipse([S(c - r * 0.97), S(c - r * 0.97), S(c + r * 0.97), S(c + r * 0.97)], fill=255)
    pent = Image.new('RGBA', img.size, (0, 0, 0, 0)); pd = ImageDraw.Draw(pent)
    def pentagon(px, py, pr, rot):
        poly(pd, [(px + pr * math.cos(rot + k * 2 * math.pi / 5), py + pr * math.sin(rot + k * 2 * math.pi / 5)) for k in range(5)], INK)
    pentagon(c, c, r * 0.30, -math.pi / 2)
    for k in range(5):
        a = -math.pi / 2 + math.pi / 5 + k * 2 * math.pi / 5
        pentagon(c + math.cos(a) * r * 0.80, c + math.sin(a) * r * 0.80, r * 0.24, a + math.pi / 5)
        b = a + math.pi / 5
        pd.line([S(c + math.cos(b) * r * 0.30), S(c + math.sin(b) * r * 0.30), S(c + math.cos(b) * r * 0.70), S(c + math.sin(b) * r * 0.70)],
                fill=INK, width=int(S(max(2, r * 0.035))))
    img.alpha_composite(Image.composite(pent, Image.new('RGBA', img.size, (0, 0, 0, 0)), m))
    add_shade(img, c, c, r, PAL['navy'], 50)
    circle(d, c, c, r, None, rgb((0.72, 0.76, 0.90)), max(2.5, r * 0.05))
    highlight(d, c, c, r, 120)
    return finish(img)


@functools.lru_cache(maxsize=32)
def spr_ball(r, color, stripes=None, gloss=True, outline=True):
    """Bille / pois / balle : disque coloré, bandes optionnelles (bille façon Jupiter), ombre et reflet."""
    size = int(2 * r + 10); img, d = canvas(size, size); c = size / 2
    circle(d, c, c, r, rgb(color))
    if stripes:
        m = Image.new('L', img.size, 0); ImageDraw.Draw(m).ellipse([S(c - r), S(c - r), S(c + r), S(c + r)], fill=255)
        st = Image.new('RGBA', img.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        for (y, h, col) in stripes:
            sd.rectangle([0, S(c - r + y * 2 * r), img.width, S(c - r + (y + h) * 2 * r)], fill=rgb(col))
        img.alpha_composite(Image.composite(st, Image.new('RGBA', img.size, (0, 0, 0, 0)), m))
    add_shade(img, c, c, r, (0, 0, 0.1), 60)
    if outline:
        circle(d, c, c, r, None, INK, max(2, r * 0.05))
    if gloss:
        highlight(d, c, c, r, 150)
    return finish(img)


@functools.lru_cache(maxsize=8)
def spr_pepper(r):
    size = int(2 * r + 8); img, d = canvas(size, size); c = size / 2
    circle(d, c, c, r, rgb((0.25, 0.17, 0.12)))
    for k in range(6):
        a = k * 1.1
        d.arc([S(c - r * 0.7 + math.cos(a) * r * 0.2), S(c - r * 0.7 + math.sin(a) * r * 0.2), S(c + r * 0.5), S(c + r * 0.5)], 200 + k * 40, 260 + k * 40,
              fill=rgb((0.12, 0.08, 0.06)), width=int(S(max(1, r * 0.12))))
    highlight(d, c, c, r, 80)
    return finish(img)


@functools.lru_cache(maxsize=8)
def spr_lens(r):
    """Loupe : anneau + manche (le contenu est dessiné dessous)."""
    size = int(r * 3.4); img, d = canvas(size, size); c = r * 1.15
    circle(d, c, c, r, (190, 230, 255, 40))
    ang = math.radians(45)
    x0, y0 = c + math.cos(ang) * r * 1.02, c + math.sin(ang) * r * 1.02
    x1, y1 = c + math.cos(ang) * r * 2.05, c + math.sin(ang) * r * 2.05
    d.line([S(x0), S(y0), S(x1), S(y1)], fill=rgb(PAL['brown']), width=int(S(r * 0.22)))
    d.line([S(x0), S(y0), S(x1), S(y1)], fill=rgb((0.66, 0.44, 0.28)), width=int(S(r * 0.12)))
    circle(d, c, c, r, None, rgb(PAL['grey']), r * 0.13)
    circle(d, c, c, r * 1.065, None, INK, 3)
    d.arc([S(c - r * 0.8), S(c - r * 0.8), S(c + r * 0.8), S(c + r * 0.8)], 200, 250, fill=(255, 255, 255, 170), width=int(S(r * 0.07)))
    return finish(img), (c - size / 2, c - size / 2)  # décalage du centre de la lentille / centre du sprite


@functools.lru_cache(maxsize=4)
def spr_field(w, h):
    """Terrain de foot vu de dessus (bandes de tonte, lignes blanches)."""
    img, d = canvas(w, h)
    n = 10
    for k in range(n):
        d.rectangle([0, S(k * h / n), S(w), S((k + 1) * h / n)], fill=rgb(PAL['grass'] if k % 2 else PAL['grass2']))
    lw = 6; m = 40; col = (255, 255, 255, 230)
    d.rectangle([S(m), S(m), S(w - m), S(h - m)], outline=col, width=int(S(lw)))
    d.line([S(m), S(h / 2), S(w - m), S(h / 2)], fill=col, width=int(S(lw)))
    circle(d, w / 2, h / 2, w * 0.17, None, col, lw)
    circle(d, w / 2, h / 2, 8, col)
    for yy, sgn in ((m, 1), (h - m, -1)):
        bw, bh = w * 0.56, h * 0.13
        d.rectangle([S(w / 2 - bw / 2), S(min(yy, yy + sgn * bh)), S(w / 2 + bw / 2), S(max(yy, yy + sgn * bh))], outline=col, width=int(S(lw)))
    return finish(img)


@functools.lru_cache(maxsize=16)
def spr_house(s, roof=(0.88, 0.30, 0.25), wall=(0.98, 0.90, 0.75)):
    img, d = canvas(s * 1.3, s * 1.3); o = s * 0.15
    rrect(d, o + s * 0.12, o + s * 0.45, o + s * 0.88, o + s, 6, rgb(wall), INK, 3)
    poly(d, [(o, o + s * 0.5), (o + s * 0.5, o + s * 0.05), (o + s, o + s * 0.5)], rgb(roof), INK, 3)
    rrect(d, o + s * 0.42, o + s * 0.68, o + s * 0.58, o + s, 4, rgb(PAL['brown']))
    rrect(d, o + s * 0.20, o + s * 0.55, o + s * 0.34, o + s * 0.68, 3, rgb(PAL['cyan']), INK, 2)
    rrect(d, o + s * 0.66, o + s * 0.55, o + s * 0.80, o + s * 0.68, 3, rgb(PAL['cyan']), INK, 2)
    return finish(img)


@functools.lru_cache(maxsize=16)
def spr_tree(s):
    img, d = canvas(s, s * 1.2)
    rrect(d, s * 0.44, s * 0.6, s * 0.56, s * 1.18, 4, rgb(PAL['brown']))
    for (x, y, r) in ((0.5, 0.36, 0.30), (0.32, 0.5, 0.22), (0.68, 0.5, 0.22)):
        circle(d, s * x, s * y, s * r, rgb(PAL['green']), INK, 2.5)
    return finish(img)


@functools.lru_cache(maxsize=16)
def spr_person(h, color, arms_up=False):
    """Petit personnage arrondi (corps en gélule, tête ronde)."""
    w = h * 0.62; img, d = canvas(w, h * 1.05); cx = w / 2
    body = rgb(color); dark = rgb(tuple(c * 0.75 for c in color))
    rrect(d, cx - w * 0.12, h * 0.62, cx - w * 0.02, h * 1.0, w * 0.05, dark)
    rrect(d, cx + w * 0.02, h * 0.62, cx + w * 0.12, h * 1.0, w * 0.05, dark)
    if arms_up:
        for sgn in (-1, 1):
            d.line([S(cx + sgn * w * 0.16), S(h * 0.40), S(cx + sgn * w * 0.40), S(h * 0.14)], fill=dark, width=int(S(w * 0.09)))
    else:
        for sgn in (-1, 1):
            d.line([S(cx + sgn * w * 0.17), S(h * 0.36), S(cx + sgn * w * 0.26), S(h * 0.62)], fill=dark, width=int(S(w * 0.09)))
    rrect(d, cx - w * 0.19, h * 0.28, cx + w * 0.19, h * 0.70, w * 0.16, body)
    circle(d, cx, h * 0.15, h * 0.13, body)
    highlight(d, cx, h * 0.15, h * 0.13, 70)
    return finish(img)


@functools.lru_cache(maxsize=4)
def spr_eiffel(h):
    w = h * 0.62; img, d = canvas(w, h); cx = w / 2; col = rgb((0.80, 0.84, 0.98)); dk = rgb((0.55, 0.60, 0.85))
    P = lambda x, y: (cx + x * w, y * h)
    arch = [P(0.25 * math.cos(a), 1.0 - 0.20 * math.sin(a)) for a in np.linspace(0, math.pi, 16)]   # de droite à gauche
    outline = [P(-0.47, 1.0), P(-0.25, 1.0)] + arch[::-1] + [P(0.25, 1.0), P(0.47, 1.0), P(0.21, 0.62), P(0.11, 0.38), P(0.045, 0.13),
               P(0.012, 0.03), P(0.0, 0.0), P(-0.012, 0.03), P(-0.045, 0.13), P(-0.11, 0.38), P(-0.21, 0.62)]
    poly(d, outline, col)
    for y, ww in ((0.62, 0.50), (0.38, 0.27), (0.13, 0.11)):
        rrect(d, cx - w * ww / 2, h * y - 7, cx + w * ww / 2, h * y + 7, 3, dk)
    return finish(img)


@functools.lru_cache(maxsize=4)
def spr_skyline(w, h, seed=3):
    img, d = canvas(w, h); rng = np.random.default_rng(seed)
    col = rgb((0.80, 0.84, 0.98)); win = rgb(PAL['yellow'], 220)
    x = 0
    while x < w:
        bw = rng.uniform(0.07, 0.14) * w; bh = rng.uniform(0.35, 0.75) * h
        d.rectangle([S(x), S(h - bh), S(x + bw - 4), S(h)], fill=col)
        for yy in np.arange(h - bh + 14, h - 10, 22):
            for xx in np.arange(x + 8, x + bw - 14, 18):
                if rng.random() < 0.45:
                    d.rectangle([S(xx), S(yy), S(xx + 7), S(yy + 9)], fill=win)
        x += bw
    # gratte-ciel à flèche, au centre
    ex = w * 0.5
    for (y0, ww) in ((0.25, 0.16), (0.12, 0.09), (0.05, 0.05)):
        d.rectangle([S(ex - w * ww / 2), S(h * y0), S(ex + w * ww / 2), S(h)], fill=col)
    d.line([S(ex), 0, S(ex), S(h * 0.06)], fill=col, width=int(S(5)))
    return finish(img)


@functools.lru_cache(maxsize=8)
def spr_clock(r):
    size = int(2 * r + 12); img, d = canvas(size, size); c = size / 2
    circle(d, c, c, r, rgb(PAL['white']), INK, r * 0.07)
    for k in range(12):
        a = k * math.pi / 6; r0 = r * (0.74 if k % 3 == 0 else 0.82)
        d.line([S(c + math.cos(a) * r0), S(c + math.sin(a) * r0), S(c + math.cos(a) * r * 0.88), S(c + math.sin(a) * r * 0.88)], fill=INK, width=int(S(r * 0.04)))
    return finish(img)


@functools.lru_cache(maxsize=8)
def spr_wave(w, h):
    img, d = canvas(w, h)
    pts = [(0, h)]
    for k in range(61):
        x = w * k / 60
        y = h * (0.55 - 0.35 * math.exp(-((x / w - 0.78) / 0.16) ** 2) + 0.05 * math.sin(k * 0.7))
        pts.append((x, y))
    pts.append((w, h))
    poly(d, pts, rgb(PAL['ocean']))
    pts2 = [(x, y + h * 0.12) for (x, y) in pts[1:-1]]
    poly(d, [(0, h)] + pts2 + [(w, h)], rgb((0.16, 0.44, 0.85)))
    for (x, y) in pts[1:-1:3]:
        circle(d, x, y, h * 0.035, rgb(PAL['white']))
    # crête qui s'enroule
    cx, cy = w * 0.80, h * 0.24
    d.arc([S(cx - h * 0.16), S(cy - h * 0.02), S(cx + h * 0.16), S(cy + h * 0.30)], 180, 330, fill=rgb(PAL['white']), width=int(S(h * 0.045)))
    return finish(img)


@functools.lru_cache(maxsize=8)
def spr_moon(r):
    size = int(2 * r + 8); img, d = canvas(size, size); c = size / 2
    circle(d, c, c, r, rgb((0.93, 0.92, 0.85)))
    for (x, y, rr) in ((-0.3, -0.2, 0.18), (0.25, 0.1, 0.12), (-0.05, 0.4, 0.1), (0.35, -0.35, 0.08)):
        circle(d, c + x * r, c + y * r, rr * r, rgb((0.80, 0.79, 0.72)))
    add_shade(img, c, c, r, (0, 0, 0.1), 50)
    return finish(img)


@functools.lru_cache(maxsize=16)
def spr_text(text, size, color=(1, 1, 1), stroke=10, font='poppins_black'):
    return text_sprite(text, font, size, tuple(int(c * 255) for c in color), stroke, (22, 23, 52), None, 0, 1000)


# ----------------------------------------------------------------------------- couches
class FlatBG(Layer):
    """Fond « dessin animé » : dégradé, étoiles-points qui scintillent, grain léger, vignette douce."""
    def __init__(self, top=(0.13, 0.14, 0.36), bottom=(0.05, 0.06, 0.18), stars=160, seed=1, grain=0.022):
        self.__dict__.update(locals()); del self.__dict__['self']

    def setup(self, dur):
        y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        self.base = (np.array(self.top, np.float32) * (1 - y) + np.array(self.bottom, np.float32) * y) * np.ones((1, W, 1), np.float32)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2)
        self.base *= (1 - 0.35 * np.clip(r / 0.7, 0, 1) ** 2.2)[..., None]
        rng = np.random.default_rng(self.seed)
        self.sx = rng.uniform(0, W, self.stars); self.sy = rng.uniform(0, H, self.stars)
        self.sr = rng.choice([1.5, 2.2, 3.0, 4.2], self.stars, p=[0.45, 0.3, 0.17, 0.08]); self.sp = rng.uniform(0, 6.28, self.stars)
        self.noise = [rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(4)]

    def draw(self, f, t, dur):
        f[:] = self.base
        for x, y, r, p in zip(self.sx, self.sy, self.sr, self.sp):
            a = 0.55 + 0.45 * math.sin(t * 2.0 + p)
            cv2.circle(f, (int(x), int(y)), int(r), (0.85 * a + 0.1, 0.88 * a + 0.1, 0.98 * a + 0.1), -1, cv2.LINE_AA)
        if self.grain:
            n = cv2.resize(self.noise[int(t * 12) % 4], (W, H), interpolation=cv2.INTER_LINEAR)
            f += n[..., None] * self.grain
        return f


class Ground(Layer):
    """Colline / sol herbeux en bas de l'image."""
    def __init__(self, y=1500, color=PAL['grass'], dark=PAL['grass2'], curve=60):
        self.__dict__.update(locals()); del self.__dict__['self']

    def setup(self, dur):
        img, d = canvas(W, H - self.y + self.curve + 20)
        hh = H - self.y + self.curve + 20
        d.ellipse([S(-W * 0.4), 0, S(W * 1.4), S(hh * 3)], fill=rgb(self.color))
        d.ellipse([S(-W * 0.4), S(hh * 0.45), S(W * 1.4), S(hh * 3.4)], fill=rgb(self.dark))
        self.spr = finish(img); self.cy = self.y - self.curve + hh / 2

    def draw(self, f, t, dur):
        blit_rgba(f, self.spr, W / 2, self.cy)
        return f


class Sprite(Layer):
    """Sprite animé : position / échelle / rotation / opacité en images clés, apparition « pop »."""
    def __init__(self, spr, pos=(W / 2, H / 2), scale=1.0, rot=0.0, alpha=1.0, t0=0.0, t1=None, pop=0.35, bob=0.0, spin=0.0, out=0.0):
        self.__dict__.update(locals()); del self.__dict__['self']

    def _v(self, v, t):
        return kf(v, t) if isinstance(v, list) else v

    def draw(self, f, t, dur):
        if t < self.t0 or (self.t1 is not None and t > self.t1):
            return f
        lt = t - self.t0
        spr = self.spr() if callable(self.spr) else self.spr
        sc = self._v(self.scale, t)
        if self.pop:
            sc *= max(0.01, ease_out_back(min(1.0, lt / self.pop)))
        a = self._v(self.alpha, t)
        if self.out and self.t1 is not None:
            a *= clamp01((self.t1 - t) / self.out)
        x, y = self._v(self.pos, t)
        y += self.bob * math.sin(t * 2.4)
        ang = self._v(self.rot, t) + self.spin * t
        img = scale_sprite(spr, sc)
        if abs(ang) > 0.05:
            h, w = img.shape[:2]
            M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, 1.0)
            cs, sn = abs(M[0, 0]), abs(M[0, 1])
            nw, nh = int(h * sn + w * cs) + 2, int(h * cs + w * sn) + 2
            M[0, 2] += nw / 2 - w / 2; M[1, 2] += nh / 2 - h / 2
            img = cv2.warpAffine(img, M, (nw, nh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        blit_rgba(f, img, x, y, a)
        return f


def Big(text, y=430, t0=0.15, color=PAL['yellow'], size=150, x=W / 2, t1=None):
    """Grand nombre / mot qui « pop » (contour sombre épais)."""
    return Sprite(lambda: spr_text(text, size, color, 12), (x, y), t0=t0, t1=t1, pop=0.4)


class Dashed(Layer):
    """Trait pointillé qui se dessine de p0 à p1 (ou le long d'un arc si bend ≠ 0)."""
    def __init__(self, p0, p1, t0=0.2, t1=1.2, color=PAL['yellow'], width=7, dash=26, bend=0.0, gap=0.5):
        self.__dict__.update(locals()); del self.__dict__['self']

    def pts(self, n=200):
        (x0, y0), (x1, y1) = self.p0, self.p1
        s = np.linspace(0, 1, n)
        x = x0 + (x1 - x0) * s; y = y0 + (y1 - y0) * s
        if self.bend:
            nx, ny = -(y1 - y0), (x1 - x0); L = math.hypot(nx, ny) or 1
            b = self.bend * 4 * s * (1 - s)
            x += nx / L * b; y += ny / L * b
        return np.stack([x, y], 1)

    def draw(self, f, t, dur):
        if t < self.t0:
            return f
        k = ease_in_out(clamp01((t - self.t0) / max(self.t1 - self.t0, 1e-3)))
        p = self.pts()
        seg = np.cumsum(np.r_[0, np.hypot(*np.diff(p, axis=0).T)])
        Ltot = seg[-1] * k
        d = 0.0
        while d < Ltot:
            e = min(d + self.dash * (1 - self.gap), Ltot)
            i0, i1 = np.searchsorted(seg, d), np.searchsorted(seg, e)
            if i1 > i0:
                cv2.polylines(f, [np.round(p[i0:i1 + 1] * 4).astype(np.int32)], False, self.color, self.width, cv2.LINE_AA, shift=2)
            d += self.dash
        return f


class Mover(Layer):
    """Petit objet qui suit un chemin (orbite circulaire ou trait) ; sprite optionnel."""
    def __init__(self, spr, center=(W / 2, H / 2), radius=200, period=6.0, phase=0.0, t0=0.0, ry=None):
        self.__dict__.update(locals()); del self.__dict__['self']

    def draw(self, f, t, dur):
        if t < self.t0:
            return f
        a = self.phase + 2 * math.pi * (t - self.t0) / self.period
        x = self.center[0] + math.cos(a) * self.radius
        y = self.center[1] + math.sin(a) * (self.ry or self.radius)
        spr = self.spr() if callable(self.spr) else self.spr
        blit_rgba(f, spr, x, y, min(1, (t - self.t0) / 0.3))
        return f


class Ring(Layer):
    """Cercle (orbite) en pointillés ou plein, qui apparaît en se dessinant."""
    def __init__(self, center, r, t0=0.0, t1=0.8, color=(1, 1, 1), width=4, dashed=True, ry=None, alpha=0.7):
        self.__dict__.update(locals()); del self.__dict__['self']

    def draw(self, f, t, dur):
        if t < self.t0:
            return f
        k = ease_in_out(clamp01((t - self.t0) / max(self.t1 - self.t0, 1e-3)))
        ry = self.ry or self.r
        n = 90 if self.dashed else 1
        ov = f.copy()
        if self.dashed:
            for i in range(int(n * k)):
                if i % 2 == 0:
                    cv2.ellipse(ov, (int(self.center[0] * 4), int(self.center[1] * 4)), (int(self.r * 4), int(ry * 4)), -90, i * 360 / n, (i + 1) * 360 / n, self.color, self.width, cv2.LINE_AA, shift=2)
        else:
            cv2.ellipse(ov, (int(self.center[0] * 4), int(self.center[1] * 4)), (int(self.r * 4), int(ry * 4)), -90, 0, 360 * k, self.color, self.width, cv2.LINE_AA, shift=2)
        return f * (1 - self.alpha) + ov * self.alpha


class Ruler(Layer):
    """Règle graduée jaune qui s'étend (mesure d'un diamètre / d'une distance)."""
    def __init__(self, x0, x1, y, t0=0.2, t1=1.0, color=PAL['yellow']):
        self.__dict__.update(locals()); del self.__dict__['self']

    def draw(self, f, t, dur):
        if t < self.t0:
            return f
        k = ease_out(clamp01((t - self.t0) / max(self.t1 - self.t0, 1e-3)))
        xm = (self.x0 + self.x1) / 2; hw = (self.x1 - self.x0) / 2 * k
        a, b = int(xm - hw), int(xm + hw); y = int(self.y)
        cv2.line(f, (a, y), (b, y), PAL['ink'], 14, cv2.LINE_AA)
        cv2.line(f, (a, y), (b, y), self.color, 8, cv2.LINE_AA)
        for x in np.arange(a, b + 1, 30):
            hh = 16 if int((x - a) / 30) % 5 == 0 else 9
            cv2.line(f, (int(x), y - hh), (int(x), y + hh), self.color, 4, cv2.LINE_AA)
        return f


class Wind(Layer):
    """Traînées de vent horizontales (de gauche à droite)."""
    def __init__(self, t0=0.0, n=46, speed=2600, y0=200, y1=1500, seed=4, ramp=0.6, color=(1, 1, 1)):
        self.__dict__.update(locals()); del self.__dict__['self']

    def setup(self, dur):
        rng = np.random.default_rng(self.seed)
        self.y = rng.uniform(self.y0, self.y1, self.n); self.x = rng.uniform(-W, W, self.n)
        self.l = rng.uniform(120, 420, self.n); self.v = rng.uniform(0.7, 1.3, self.n); self.w = rng.choice([3, 4, 6], self.n)

    def draw(self, f, t, dur):
        if t < self.t0:
            return f
        k = clamp01((t - self.t0) / self.ramp)
        ov = f.copy()
        for y, x, l, v, w in zip(self.y, self.x, self.l, self.v, self.w):
            xx = (x + self.speed * v * (t - self.t0)) % (W + 800) - 400
            cv2.line(ov, (int(xx - l), int(y)), (int(xx), int(y)), self.color, int(w), cv2.LINE_AA)
        return f * (1 - 0.75 * k) + ov * 0.75 * k


class Flying(Layer):
    """Objets emportés par le vent : traversent l'écran en tournoyant."""
    def __init__(self, items, t0=0.3, seed=5, speed=1500):
        self.__dict__.update(locals()); del self.__dict__['self']

    def setup(self, dur):
        rng = np.random.default_rng(self.seed)
        self.p = [(spr, rng.uniform(250, 1400), rng.uniform(0, 1.6), rng.uniform(-360, 360), rng.uniform(0.8, 1.25)) for spr in self.items]

    def draw(self, f, t, dur):
        for spr, y, delay, rot, v in self.p:
            lt = t - self.t0 - delay
            if lt < 0:
                continue
            x = -200 + self.speed * v * lt
            if x > W + 250:
                continue
            Sprite(spr, (x, y - 140 * math.sin(lt * 2.0)), rot=rot * lt, pop=0).draw(f, 0, dur)
        return f


class Hands(Layer):
    """Aiguilles d'horloge (vitesse en tours par seconde)."""
    def __init__(self, c, r, fast=1.2, slow=0.1):
        self.__dict__.update(locals()); del self.__dict__['self']

    def draw(self, f, t, dur):
        cx, cy = self.c
        for (L, w, sp, col) in ((0.5, 12, self.slow, PAL['ink']), (0.74, 7, self.fast, PAL['red'])):
            a = 2 * math.pi * sp * t - math.pi / 2
            cv2.line(f, (int(cx), int(cy)), (int(cx + math.cos(a) * self.r * L), int(cy + math.sin(a) * self.r * L)), col, w, cv2.LINE_AA)
        cv2.circle(f, (int(cx), int(cy)), 12, PAL['ink'], -1, cv2.LINE_AA)
        return f


# ----------------------------------------------------------------------------- planète en dessin plat
TEX = f'{ASSETS}/textures'


@functools.lru_cache(maxsize=2)
def flat_maps():
    """Carte de la Terre simplifiée en aplats (océan / terres vertes / déserts / glaces) + carte « océans aux pôles »."""
    night = cv2.imread(f'{TEX}/earth_night_4k.jpg')[:, :, ::-1].astype(np.float32) / 255
    night = cv2.resize(night, (2048, 1024), interpolation=cv2.INTER_AREA)
    day = cv2.imread(f'{TEX}/earth_viirs_4k.jpg')[:, :, ::-1].astype(np.float32) / 255
    day = cv2.resize(day, (2048, 1024), interpolation=cv2.INTER_AREA)
    base = cv2.medianBlur((night[..., 1] * 255).astype(np.uint8), 5).astype(np.float32) / 255
    land = cv2.GaussianBlur((base > 0.018).astype(np.float32), (0, 0), 2.5) > 0.5
    latg = np.linspace(90, -90, 1024)[:, None] * np.ones((1, 2048))
    long_ = np.linspace(-180, 180, 2048)[None, :] * np.ones((1024, 1))
    r, g, b = day[..., 0], day[..., 1], day[..., 2]
    dry = cv2.GaussianBlur(((r > g * 1.12) & (r > b * 1.25)).astype(np.float32), (0, 0), 9) > 0.35
    ice = (latg < -62) | ((latg > 60) & (long_ > -75) & (long_ < -10)) | (latg > 78)
    out = np.empty_like(day)
    out[:] = PAL['ocean']
    out[land] = PAL['land']
    out[land & dry] = PAL['sand']
    out[land & ice] = PAL['white']
    # carte hypothétique : l'eau migre vers les pôles, un continent unique autour de l'équateur
    lat = latg
    lon = long_
    edge = 38 + 6 * np.sin(np.radians(lon) * 3) + 4 * np.sin(np.radians(lon) * 7 + 1)
    poles = np.empty_like(day)
    poles[:] = PAL['land']
    poles[(np.abs(lat) < edge - 14) & (np.sin(np.radians(lon) * 2 + lat / 20) > 0.3)] = PAL['sand']
    poles[np.abs(lat) > edge] = PAL['ocean']
    poles[np.abs(lat) > 82] = PAL['white']
    return out.astype(np.float32), poles.astype(np.float32)


class FlatGlobe(Layer):
    """Planète Terre en aplats, projection orthographique. lon : degrés (nombre, ou images clés) ; spin : °/s.
    poles : 0 → carte réelle, 1 → carte « océans aux pôles ». light : None (pas d'ombre) ou angle (°) de la lumière."""
    def __init__(self, c=(W / 2, H / 2), r=330, lon=0.0, spin=20.0, tilt=18.0, poles=0.0, light=None, night=0.45, t0=0.0, pop=0.4):
        self.__dict__.update(locals()); del self.__dict__['self']

    def setup(self, dur):
        self.m0, self.m1 = flat_maps()

    def draw(self, f, t, dur):
        if t < self.t0:
            return f
        lt = t - self.t0
        r = kf(self.r, t) if isinstance(self.r, list) else self.r
        if self.pop:
            r *= max(0.02, ease_out_back(min(1.0, lt / self.pop)))
        r = int(r)
        if r < 3:
            return f
        cx, cy = (kf(self.c, t) if isinstance(self.c, list) else self.c)
        lon0 = (kf(self.lon, t) if isinstance(self.lon, list) else self.lon + self.spin * t)
        pk = kf(self.poles, t) if isinstance(self.poles, list) else self.poles
        n = 2 * r + 1
        yy, xx = np.mgrid[-r:r + 1, -r:r + 1].astype(np.float32) / r
        rr = xx ** 2 + yy ** 2
        inside = rr <= 1.0
        z = np.sqrt(np.clip(1 - rr, 0, 1))
        ti = math.radians(self.tilt)
        y2 = yy * math.cos(ti) - z * math.sin(ti); z2 = yy * math.sin(ti) + z * math.cos(ti)
        lat = np.degrees(np.arcsin(np.clip(-y2, -1, 1)))
        lon = np.degrees(np.arctan2(xx, z2)) + lon0
        mx = ((lon + 180) % 360) / 360 * 2048; my = (90 - lat) / 180 * 1024
        mx = mx.astype(np.float32); my = np.clip(my, 0, 1023).astype(np.float32)
        col = cv2.remap(self.m0, mx, my, cv2.INTER_NEAREST, borderMode=cv2.BORDER_WRAP)
        if pk > 0:
            col2 = cv2.remap(self.m1, mx, my, cv2.INTER_NEAREST, borderMode=cv2.BORDER_WRAP)
            col = col * (1 - pk) + col2 * pk
        # ombrage en aplats : croissant sombre + jour/nuit éventuel
        sh = np.ones_like(z)
        sh -= 0.16 * (((xx + 0.30) ** 2 + (yy + 0.30) ** 2) > 1.0)
        if self.light is not None:
            la = math.radians(kf(self.light, t) if isinstance(self.light, list) else self.light)
            d = xx * math.cos(la) - yy * math.sin(la)
            sh = np.where(d < -0.02, sh * self.night, sh)
        col = col * sh[..., None]
        # contour
        a = np.clip((1.0 - np.sqrt(rr)) * r * 0.9, 0, 1)[..., None]
        x0, y0 = int(cx - r), int(cy - r)
        X0, Y0 = max(0, x0), max(0, y0); X1, Y1 = min(W, x0 + n), min(H, y0 + n)
        if X1 <= X0 or Y1 <= Y0:
            return f
        sub = (slice(Y0 - y0, Y1 - y0), slice(X0 - x0, X1 - x0))
        reg = f[Y0:Y1, X0:X1]
        aa = a[sub]
        reg[:] = reg * (1 - aa) + col[sub] * aa
        cv2.circle(f, (int(cx * 4), int(cy * 4)), int(r * 4 + 10), (0.62, 0.84, 1.0), max(3, r // 40), cv2.LINE_AA, shift=2)
        return f


class Lensed(Layer):
    """Loupe posée sur un point : agrandit le contenu de la couche `inner` (dessinée dans un tampon)."""
    def __init__(self, inner, c, r=170, t0=0.6, pop=0.4):
        self.__dict__.update(locals()); del self.__dict__['self']

    def setup(self, dur):
        self.inner.setup(dur)

    def draw(self, f, t, dur):
        if t < self.t0:
            return f
        lt = t - self.t0
        k = max(0.01, ease_out_back(min(1.0, lt / self.pop)))
        buf = np.zeros_like(f); buf[:] = (0.75, 0.88, 1.0)
        buf = self.inner.draw(buf, t, dur)
        rr = int(self.r * k)
        mask = np.zeros(f.shape[:2], np.float32)
        cv2.circle(mask, (int(self.c[0]), int(self.c[1])), rr, 1.0, -1, cv2.LINE_AA)
        f[:] = f * (1 - mask[..., None]) + buf * mask[..., None]
        spr, (ox, oy) = spr_lens(self.r)
        blit_rgba(f, scale_sprite(spr, k), self.c[0] - ox * k, self.c[1] - oy * k)
        return f


@functools.lru_cache(maxsize=4)
def spr_city(w, h, seed=2):
    """Quartier vu du ciel : îlots gris, parcs verts, rues claires."""
    img, d = canvas(w, h); rng = np.random.default_rng(seed)
    d.rectangle([0, 0, S(w), S(h)], fill=rgb((0.80, 0.82, 0.88)))
    bs = 92; st = 22
    for y in np.arange(0, h, bs):
        for x in np.arange(0, w, bs):
            col = PAL['green'] if rng.random() < 0.16 else (0.58, 0.60, 0.70) if rng.random() < 0.5 else (0.66, 0.67, 0.76)
            rrect(d, x + st / 2, y + st / 2, x + bs - st / 2, y + bs - st / 2, 8, rgb(col))
    m = Image.new('L', img.size, 0); ImageDraw.Draw(m).ellipse([0, 0, S(w), S(h)], fill=255)
    out = Image.new('RGBA', img.size, (0, 0, 0, 0)); out.paste(img, (0, 0), m)
    return finish(out)


class Split(Layer):
    """Écran partagé : moitié gauche « jour » (ciel clair), moitié droite « nuit »."""
    def __init__(self, day=(0.45, 0.75, 1.0), night=(0.05, 0.06, 0.18), t0=0.0):
        self.__dict__.update(locals()); del self.__dict__['self']

    def draw(self, f, t, dur):
        k = ease_out(clamp01((t - self.t0) / 0.5))
        x = int(W / 2 * k)
        f[:, :x] = self.day
        f[:, W - x:] = self.night
        return f
