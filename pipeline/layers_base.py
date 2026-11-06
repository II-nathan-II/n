"""Couches génériques : fond spatial, textes in-image, compteurs, barres, cartes d'archive, particules."""
import math, functools
import numpy as np
import cv2
from common import *


class Layer:
    def setup(self, dur):
        pass
    def draw(self, f, t, dur):
        return f


class Composite:
    """Une scène = un empilement de couches. `clean` : pas de grain/vignette (stimuli d'illusions)."""
    def __init__(self, layers, clean=False, grade=True):
        self.layers = layers; self.clean = clean; self.grade = grade
        self._ready = False
    def setup(self, dur):
        if not self._ready:
            for l in self.layers:
                l.setup(dur)
            self._ready = True
    def render(self, t, dur):
        f = np.zeros((H, W, 3), np.float32)
        for l in self.layers:
            r = l.draw(f, t, dur)
            if r is not None:
                f = r
        return f


# ----------------------------------------------------------------------------- fonds
NEB_PALETTES = {
    'blue': [(0, (2, 3, 10)), (0.45, (8, 18, 48)), (0.7, (30, 60, 140)), (0.88, (90, 140, 230)), (1, (200, 220, 255))],
    'purple': [(0, (3, 2, 10)), (0.45, (25, 8, 45)), (0.7, (90, 30, 130)), (0.88, (220, 90, 170)), (1, (255, 200, 230))],
    'teal': [(0, (1, 5, 8)), (0.45, (5, 30, 40)), (0.7, (20, 100, 120)), (0.88, (80, 200, 200)), (1, (220, 255, 250))],
    'orange': [(0, (6, 2, 2)), (0.45, (40, 12, 8)), (0.7, (140, 50, 20)), (0.88, (240, 140, 60)), (1, (255, 230, 180))],
    'deep': [(0, (0, 0, 2)), (0.55, (4, 6, 16)), (0.8, (14, 20, 45)), (1, (50, 60, 110))],
    'red': [(0, (5, 1, 2)), (0.45, (35, 5, 12)), (0.7, (120, 20, 40)), (0.88, (230, 80, 80)), (1, (255, 200, 190))],
}

STAR_COLORS = np.array([(155, 176, 255), (202, 215, 255), (248, 247, 255), (255, 244, 234), (255, 210, 161), (255, 190, 130)], np.float32) / 255


@functools.lru_cache(maxsize=16)
def _space_canvas(seed, palette, nebula, density, cw, ch):
    rng = np.random.default_rng(seed)
    n1 = fbm_noise(ch // 3, cw // 3, beta=2.8, seed=seed)
    n2 = fbm_noise(ch // 3, cw // 3, beta=2.2, seed=seed + 1)
    neb = n1 * 0.75 + n2 * 0.25
    neb = np.clip((neb - 0.35) / 0.65, 0, 1) ** 1.6
    dust = fbm_noise(ch // 3, cw // 3, beta=2.4, seed=seed + 2)
    neb = neb * (0.55 + 0.45 * smoothstep(0.3, 0.7, dust))
    col = palette_map(neb, NEB_PALETTES[palette]) * nebula
    col = cv2.resize(col, (cw, ch), interpolation=cv2.INTER_CUBIC)
    col = cv2.GaussianBlur(col, (0, 0), 2)
    # étoiles faibles
    n = int(5500 * density * (cw * ch) / (W * H))
    xs = rng.uniform(0, cw, n); ys = rng.uniform(0, ch, n)
    b = rng.pareto(2.2, n) * 0.18 + 0.05
    cidx = rng.integers(0, len(STAR_COLORS), n)
    stars = np.zeros((ch, cw, 3), np.float32)
    xi = np.clip(xs.astype(int), 0, cw - 1); yi = np.clip(ys.astype(int), 0, ch - 1)
    for c in range(3):
        np.add.at(stars[..., c], (yi, xi), np.minimum(b, 2.5) * STAR_COLORS[cidx, c])
    stars = cv2.GaussianBlur(stars, (0, 0), 0.7) * 2.2
    big = b > 0.9
    glow = cv2.GaussianBlur(stars * big[..., None].any() if False else stars, (0, 0), 3.0) * 0.6
    canvas = col + stars + glow
    # étoiles brillantes (scintillement dynamique)
    order = np.argsort(-b)[:45]
    bright = [(xs[i], ys[i], min(b[i], 3.0), STAR_COLORS[cidx[i]]) for i in order]
    return canvas.astype(np.float32), bright


class SpaceBG(Layer):
    def __init__(self, seed=1, palette='blue', nebula=0.9, density=1.0, drift=(6, -10), rot=0.0, zoom=(1.0, 1.0),
                 brightness=1.0):
        self.k = (seed, palette, nebula, density)
        self.drift = drift; self.rot = rot; self.zoom = zoom; self.brightness = brightness
    def setup(self, dur):
        self.cw, self.ch = int(W * 1.35), int(H * 1.35)
        self.canvas, self.bright = _space_canvas(*self.k, self.cw, self.ch)
        self.flare = radial_glow(64, (255, 255, 255), falloff=3.5, core=0.12)
    def draw(self, f, t, dur):
        z = lerp(self.zoom[0], self.zoom[1], ease_in_out(t / max(dur, 1e-3)))
        cx = self.cw / 2 + self.drift[0] * t; cy = self.ch / 2 + self.drift[1] * t
        M = cv2.getRotationMatrix2D((cx, cy), self.rot * t, z)
        M[0, 2] += W / 2 - cx; M[1, 2] += H / 2 - cy
        img = cv2.warpAffine(self.canvas, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        for i, (x, y, b, c) in enumerate(self.bright):
            px = M[0, 0] * x + M[0, 1] * y + M[0, 2]; py = M[1, 0] * x + M[1, 1] * y + M[1, 2]
            if -40 < px < W + 40 and -40 < py < H + 40:
                tw = 0.65 + 0.35 * math.sin(t * (2.0 + i * 0.37) + i)
                spr = self.flare.copy(); spr[..., :3] = c
                blit_rgba(img, scale_sprite(spr, 0.4 + 0.35 * b), px, py, alpha=0.5 * b * tw, additive=True)
        f[:] = img * self.brightness
        return f


class GradientBG(Layer):
    def __init__(self, top=(10, 14, 30), bottom=(2, 3, 8), blobs=0, blob_colors=((60, 90, 255), (255, 80, 160)), seed=0):
        self.top, self.bottom, self.blobs, self.bc, self.seed = top, bottom, blobs, blob_colors, seed
    def setup(self, dur):
        self.base = gradient_v(H, W, self.top, self.bottom)
        rng = np.random.default_rng(self.seed)
        self.bl = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(300, 700), self.bc[i % len(self.bc)],
                    rng.uniform(0, 6.28), rng.uniform(0.1, 0.3)) for i in range(self.blobs)]
        self.spr = radial_glow(256, (255, 255, 255), falloff=2.2)
    def draw(self, f, t, dur):
        f[:] = self.base
        for (x, y, s, c, ph, sp) in self.bl:
            spr = self.spr.copy(); spr[..., :3] = np.array(c, np.float32) / 255
            blit_rgba(f, scale_sprite(spr, s / 256 * 2), x + 120 * math.sin(t * sp + ph), y + 90 * math.cos(t * sp * 0.8 + ph),
                      alpha=0.16, additive=True)
        return f


class Solid(Layer):
    def __init__(self, color):
        self.c = np.array(color, np.float32) / 255
    def draw(self, f, t, dur):
        f[:] = self.c
        return f


# ----------------------------------------------------------------------------- textes / graphismes
class Text(Layer):
    """Texte in-image animé (étiquettes de schéma, gros chiffres...)."""
    def __init__(self, text, x=W / 2, y=760, size=90, fname='poppins_xb', color=(255, 255, 255), t0=0.0, t1=None,
                 anim='pop', stroke=0, stroke_color=(0, 0, 0), shadow=6, max_width=None, alpha=1.0, weight=None, box=None):
        self.__dict__.update(locals()); del self.__dict__['self']
    def draw(self, f, t, dur):
        t1 = self.t1 if self.t1 is not None else dur + 10
        if t < self.t0 or t > t1:
            return f
        lt = t - self.t0
        a = min(1, lt / 0.25) * min(1, (t1 - t) / 0.25) * self.alpha
        sc = 1.0; dy = 0
        if self.anim == 'pop':
            sc = 0.6 + 0.4 * ease_out_back(lt / 0.35)
        elif self.anim == 'rise':
            dy = 40 * (1 - ease_out(lt / 0.4))
        spr = text_sprite(self.text, self.fname, self.size, tuple(self.color), self.stroke, tuple(self.stroke_color),
                          self.weight, self.shadow, self.max_width)
        if self.box is not None:
            h, w = spr.shape[:2]
            bx = np.zeros((h + 10, w + 36, 4), np.float32)
            bx[..., :3] = np.array(self.box, np.float32) / 255; bx[..., 3] = 0.92
            blit_rgba(f, scale_sprite(bx, sc), self.x, self.y + dy, a)
        blit_rgba(f, scale_sprite(spr, sc), self.x, self.y + dy, a)
        return f


class Counter(Layer):
    """Nombre qui défile de v0 à v1."""
    def __init__(self, v0, v1, x=W / 2, y=700, size=260, fname='anton', color=(255, 255, 255), suffix='', prefix='',
                 t0=0.1, t1=None, fmt='int', sub=None, sub_size=60, sub_color=(200, 210, 230), ease='out', decimals=1):
        self.__dict__.update(locals()); del self.__dict__['self']
    def value_str(self, v):
        if self.fmt == 'int':
            s = f'{int(round(v)):,}'.replace(',', ' ')
        elif self.fmt == 'time':
            m, s_ = divmod(int(v), 60); s = f'{m:02d}:{s_:02d}'
        else:
            s = f'{v:.{self.decimals}f}'.replace('.', ',')
        return self.prefix + s + self.suffix
    def draw(self, f, t, dur):
        t1 = self.t1 if self.t1 is not None else dur * 0.8
        p = (t - self.t0) / max(t1 - self.t0, 1e-3)
        p = ease_out(p) if self.ease == 'out' else ease_in_out(p) if self.ease == 'inout' else clamp01(p)
        v = lerp(self.v0, self.v1, p)
        a = min(1, max(0, t - self.t0 + 0.2) / 0.2)
        put_text(f, self.value_str(v), self.x, self.y, alpha=a, fname=self.fname, size=self.size, color=tuple(self.color), shadow=8)
        if self.sub:
            put_text(f, self.sub, self.x, self.y + self.size * 0.62, alpha=a, fname='poppins_sb', size=self.sub_size,
                     color=tuple(self.sub_color), shadow=4)
        return f


class Bars(Layer):
    """Barres de progression comparatives : [(label, max_value, color)] remplies à la même vitesse."""
    def __init__(self, items, vmax, y0=520, gap=330, t0=0.2, t1=None, unit='jours', x0=110, width=860):
        self.__dict__.update(locals()); del self.__dict__['self']
    def draw(self, f, t, dur):
        t1 = self.t1 if self.t1 is not None else dur * 0.85
        v = self.vmax * ease_in_out((t - self.t0) / max(t1 - self.t0, 1e-3))
        u8 = np.zeros((H, W, 3), np.uint8)
        for i, (lab, mx, col) in enumerate(self.items):
            y = self.y0 + i * self.gap
            put_text(f, lab, W / 2, y - 80, fname='poppins_xb', size=58, color=(235, 240, 250), shadow=4)
            fillw = self.width * min(v, mx) / self.vmax
            bg = f[y - 34:y + 34, self.x0:self.x0 + self.width]
            bg *= 0.45; bg += 0.06
            if fillw > 1:
                c = np.array(col, np.float32) / 255
                f[y - 34:y + 34, self.x0:self.x0 + int(fillw)] = c * (0.85 + 0.15 * np.linspace(1, 0, 68)[:, None, None])
            done = v >= mx
            put_text(f, f'{int(min(v, mx))} {self.unit}', self.x0 + self.width - 130, y + 90,
                     fname='anton', size=80, color=(255, 230, 120) if done else (255, 255, 255), shadow=3)
        return f


class ArchiveCard(Layer):
    """Fiche « archive » : nom + date + sous-titre, sur papier vieilli."""
    def __init__(self, name, date, subtitle='', y=760, t0=0.0, seed=0, icon=None):
        self.__dict__.update(locals()); del self.__dict__['self']
    def setup(self, dur):
        cw, ch = 820, 520
        n = fbm_noise(ch, cw, beta=1.8, seed=self.seed)
        paper = palette_map(n * 0.5 + 0.35, [(0, (190, 170, 130)), (1, (245, 232, 200))])
        dx, dy = radial_grid(ch, cw)
        v = 1 - 0.35 * np.clip(np.sqrt((dx / cw * 2) ** 2 + (dy / ch * 2) ** 2) - 0.5, 0, 1)
        paper *= v[..., None]
        card = np.dstack([paper, np.ones((ch, cw), np.float32)])
        put_text(card, self.date, cw / 2, 120, fname='anton', size=96, color=(120, 30, 25), shadow=0)
        put_text(card, self.name, cw / 2, 270, fname='poppins_xb', size=64 if len(self.name) < 18 else 52, color=(30, 26, 22), shadow=0)
        if self.subtitle:
            put_text(card, self.subtitle, cw / 2, 400, fname='poppins_sb', size=40, color=(70, 60, 50), shadow=0, max_width=700)
        card[..., 3] = 1
        self.card = card.astype(np.float32)
        self.shadow = np.zeros((ch + 80, cw + 80, 4), np.float32)
        self.shadow[40:-40, 40:-40, 3] = 0.6
        self.shadow[..., 3] = cv2.GaussianBlur(self.shadow[..., 3], (0, 0), 18)
    def draw(self, f, t, dur):
        lt = t - self.t0
        if lt < 0:
            return f
        p = ease_out_back(lt / 0.5, 1.2)
        ang = lerp(-14, -3, ease_out(lt / 0.6)) + 1.0 * math.sin(t * 0.8)
        sc = lerp(1.3, 1.0, p)
        a = min(1, lt / 0.2)
        M = cv2.getRotationMatrix2D((self.card.shape[1] / 2, self.card.shape[0] / 2), ang, sc)
        size = (int(self.card.shape[1] * 1.5), int(self.card.shape[0] * 1.8))
        M[0, 2] += (size[0] - self.card.shape[1]) / 2; M[1, 2] += (size[1] - self.card.shape[0]) / 2
        warped = cv2.warpAffine(self.card, M, size, flags=cv2.INTER_LINEAR)
        sh = cv2.warpAffine(self.shadow, M, size)
        blit_rgba(f, sh, W / 2 + 18, self.y + 26, a)
        blit_rgba(f, warped, W / 2, self.y, a)
        return f


class Particles(Layer):
    """Poussières / neige marine / bokeh flottant."""
    def __init__(self, n=120, color=(200, 220, 255), size=(1, 4), vel=(0, -20), alpha=0.6, seed=0, glow=True, area=None):
        self.__dict__.update(locals()); del self.__dict__['self']
    def setup(self, dur):
        rng = np.random.default_rng(self.seed)
        self.p = rng.uniform(0, 1, (self.n, 2)) * [W, H]
        self.s = rng.uniform(*self.size, self.n)
        self.ph = rng.uniform(0, 6.28, self.n)
        self.v = np.array(self.vel, np.float32) * rng.uniform(0.5, 1.5, (self.n, 1))
    def draw(self, f, t, dur):
        pos = (self.p + self.v * t + np.stack([np.sin(t * 0.7 + self.ph) * 12, np.cos(t * 0.5 + self.ph) * 8], 1)) % [W, H]
        layer = np.zeros((H, W), np.uint8)
        for (x, y), s in zip(pos, self.s):
            cv2.circle(layer, (int(x * 4), int(y * 4)), int(s * 4), 255, -1, cv2.LINE_AA, 2)
        lf = layer.astype(np.float32) / 255
        if self.glow:
            lf = lf + cv2.GaussianBlur(lf, (0, 0), 5) * 1.5
        f += lf[..., None] * (np.array(self.color, np.float32) / 255) * self.alpha
        return f


class Flash(Layer):
    """Flash lumineux à un instant donné."""
    def __init__(self, at=0.0, color=(255, 255, 255), dur_=0.35, strength=1.0):
        self.__dict__.update(locals()); del self.__dict__['self']
    def draw(self, f, t, dur):
        x = (t - self.at) / self.dur_
        if 0 <= x <= 1:
            f += (1 - x) ** 2 * self.strength * np.array(self.color, np.float32) / 255
        return f


class Fn(Layer):
    """Couche définie par une fonction draw(f, t, dur)."""
    def __init__(self, fn, setup=None):
        self.fn = fn; self._s = setup
    def setup(self, dur):
        if self._s:
            self._s(dur)
    def draw(self, f, t, dur):
        r = self.fn(f, t, dur)
        return f if r is None else r


class Shade(Layer):
    """Assombrit / teinte l'image : amount constant, ou progression de a0 à a1 entre t0 et t1."""
    def __init__(self, a0=0.0, a1=None, t0=0.0, t1=1.0, color=(0, 0, 0)):
        self.__dict__.update(locals()); del self.__dict__['self']
    def draw(self, f, t, dur):
        a = self.a0 if self.a1 is None else lerp(self.a0, self.a1, ease_in_out((t - self.t0) / max(self.t1 - self.t0, 1e-3)))
        if a > 0:
            c = np.array(self.color, np.float32) / 255
            f[:] = f * (1 - a) + c * a
        return f


class Backdrop(Layer):
    """Bandeau sombre dégradé derrière un texte/graphique in-image (lisibilité sur vidéo)."""
    def __init__(self, y0=200, y1=700, alpha=0.55):
        self.__dict__.update(locals()); del self.__dict__['self']
    def draw(self, f, t, dur):
        h = self.y1 - self.y0
        x = np.linspace(0, 1, h, dtype=np.float32)
        prof = (np.clip(np.minimum(x, 1 - x) / 0.35, 0, 1) ** 2 * (3 - 2 * np.clip(np.minimum(x, 1 - x) / 0.35, 0, 1))) * self.alpha
        f[self.y0:self.y1] *= (1 - prof)[:, None, None]
        return f
