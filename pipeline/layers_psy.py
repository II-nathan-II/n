"""Couches « cerveau & illusions » : stimuli interactifs (générés en code) et schémas explicatifs."""
import math, functools
import numpy as np
import cv2
from common import *
from layers_base import Layer

FLAG = [(0, 85, 164), (255, 255, 255), (239, 65, 53)]


class Countdown(Layer):
    """Petit compte à rebours discret (en haut) + barre de progression fine."""
    def __init__(self, t0, t1, y=260, color=(255, 255, 255), size=96, bar_y=None, bar_w=700):
        self.__dict__.update(locals()); del self.__dict__['self']
    def draw(self, f, t, dur):
        if t < self.t0 or t > self.t1:
            return f
        rem = self.t1 - t
        put_text(f, str(int(math.ceil(rem))), W / 2, self.y, fname='anton', size=self.size, color=self.color, shadow=0, alpha=0.9)
        if self.bar_y:
            k = (t - self.t0) / (self.t1 - self.t0)
            x0 = int(W / 2 - self.bar_w / 2)
            f[self.bar_y:self.bar_y + 8, x0:x0 + self.bar_w] = f[self.bar_y:self.bar_y + 8, x0:x0 + self.bar_w] * 0.5 + 0.15
            f[self.bar_y:self.bar_y + 8, x0:x0 + int(self.bar_w * (1 - k))] = np.array(self.color, np.float32) / 255
        return f


class InvertedFlag(Layer):
    """Drapeau français aux couleurs inversées ; à `switch_at`, écran blanc avec le même point de fixation."""
    def __init__(self, switch_at=None, center=(W / 2, 800), size=(900, 600), bg=(38, 38, 42), white=(240, 240, 240), invert=True,
                 colors=None):
        self.__dict__.update(locals()); del self.__dict__['self']
    def setup(self, dur):
        cols = self.colors or FLAG
        cols = [tuple(255 - c for c in col) for col in cols] if self.invert else cols
        img = np.ones((H, W, 3), np.float32) * np.array(self.bg, np.float32) / 255
        w, h = self.size
        x0, y0 = int(self.center[0] - w / 2), int(self.center[1] - h / 2)
        for i, c in enumerate(cols):
            img[y0:y0 + h, x0 + i * w // 3:x0 + (i + 1) * w // 3] = np.array(c, np.float32) / 255
        self.flag = img
        self.blank = np.ones((H, W, 3), np.float32) * np.array(self.white, np.float32) / 255
    def draw(self, f, t, dur):
        if self.switch_at is not None and t >= self.switch_at:
            f[:] = self.blank
            aa_circle(f, self.center, 9, (0.05, 0.05, 0.05))
        else:
            f[:] = self.flag
            aa_circle(f, self.center, 11, (1, 1, 1))
            aa_circle(f, self.center, 4, (0, 0, 0))
        return f


class ConeCells(Layer):
    """Trois cônes (S, M, L) avec jauge de « fatigue »."""
    def __init__(self, drain=(0.2, 0.9, 0.9), labels=('Bleu', 'Vert', 'Rouge'), y=760, t0=0.3):
        self.__dict__.update(locals()); del self.__dict__['self']
    def draw(self, f, t, dur):
        cols = [(70, 120, 255), (60, 220, 110), (255, 70, 60)]
        k = ease_in_out((t - self.t0) / max(dur * 0.75, 1e-3))
        for i, (c, lab, dr) in enumerate(zip(cols, self.labels, self.drain)):
            x = W / 2 + (i - 1) * 300
            u8 = np.zeros((H, W, 3), np.uint8)
            pts = [(x, self.y - 260), (x - 80, self.y + 60), (x + 80, self.y + 60)]
            aa_poly(u8, pts, c[::-1])
            cv2.ellipse(u8, (int(x), self.y + 60), (80, 40), 0, 0, 360, c[::-1], -1, cv2.LINE_AA)
            cv2.line(u8, (int(x), self.y + 100), (int(x), self.y + 190), (200, 200, 200), 8, cv2.LINE_AA)
            level = 1 - dr * k
            m = (u8.sum(2, keepdims=True) > 0)
            f[:] = np.where(m, u8[..., ::-1].astype(np.float32) / 255 * (0.35 + 0.65 * level), f)
            blit_rgba(f, radial_glow(320, c, 2.2), x, self.y - 80, 0.5 * level, additive=True)
            # jauge
            by = self.y + 240
            f[by:by + 28, int(x - 90):int(x + 90)] = 0.15
            f[by:by + 28, int(x - 90):int(x - 90 + 180 * level)] = np.array(c, np.float32) / 255
            put_text(f, lab, x, by + 80, fname='poppins_sb', size=44, color=(235, 235, 240), shadow=3)
        return f


class OpponentPairs(Layer):
    def __init__(self, y0=520, gap=260, t0=0.2):
        self.__dict__.update(locals()); del self.__dict__['self']
    def draw(self, f, t, dur):
        pairs = [((235, 50, 50), (40, 200, 90), 'ROUGE', 'VERT'), ((50, 100, 255), (255, 220, 40), 'BLEU', 'JAUNE'),
                 ((10, 10, 10), (250, 250, 250), 'NOIR', 'BLANC')]
        for i, (a, b, la, lb) in enumerate(pairs):
            lt = t - self.t0 - i * 0.35
            if lt < 0:
                continue
            al = min(1, lt / 0.3)
            y = self.y0 + i * self.gap
            xa, xb = 250, W - 250
            u8 = np.zeros((H, W, 3), np.uint8)
            cv2.line(u8, (xa + 80, y), (xb - 80, y), (120, 120, 140), 6, cv2.LINE_AA)
            f += u8.astype(np.float32) / 255 * al
            for (x, c) in ((xa, a), (xb, b)):
                blit_rgba(f, shaded_sphere(70, c, spec=0.3), x, y, al)
                if c == (10, 10, 10):
                    aa_circle(f, (x, y), 72, (0.6, 0.6, 0.65), 3)
            s = 0.5 + 0.38 * math.sin(lt * 2.2 + i)
            blit_rgba(f, shaded_sphere(22, (240, 240, 245)), lerp(xa + 100, xb - 100, s), y, al)
            put_text(f, la, xa, y + 115, fname='poppins_xb', size=40, color=(235, 235, 240), alpha=al, shadow=3)
            put_text(f, lb, xb, y + 115, fname='poppins_xb', size=40, color=(235, 235, 240), alpha=al, shadow=3)
        return f


class AfterimageDemo(Layer):
    """Illustration : tache rouge → fantôme vert sur fond blanc (blouses de chirurgiens)."""
    def __init__(self, switch=0.5):
        self.switch = switch
    def draw(self, f, t, dur):
        k = t / max(dur, 1e-3)
        f[:] = 0.93
        rng = np.random.default_rng(3)
        if k < self.switch:
            a = 1.0
            col = np.array([0.75, 0.05, 0.08])
        else:
            a = 0.35 * (1 - (k - self.switch) / (1 - self.switch) * 0.5)
            col = np.array([0.55, 1.0, 0.85])
        m = np.zeros((H, W), np.float32)
        for i in range(7):
            cv2.circle(m, (int(W / 2 + rng.normal(0, 120)), int(760 + rng.normal(0, 140))), int(rng.uniform(60, 160)), 1.0, -1, cv2.LINE_AA)
        m = cv2.GaussianBlur(m, (0, 0), 12)[..., None] * a
        f[:] = f * (1 - m) + col * m
        return f


class Spiral(Layer):
    """Spirale d'Archimède en rotation (paraît s'étendre vers l'extérieur)."""
    def __init__(self, center=(W / 2, 800), radius=470, arms=4, k=0.055, speed=3.2, stop_at=None, colors=((12, 12, 14), (245, 245, 245)), bg=(20, 20, 24)):
        self.__dict__.update(locals()); del self.__dict__['self']
    def setup(self, dur):
        R = self.radius
        yy, xx = np.mgrid[-R:R, -R:R].astype(np.float32)
        self.r = np.sqrt(xx * xx + yy * yy); self.phi = np.arctan2(yy, xx)
        self.mask = np.clip(R - self.r, 0, 1)[..., None]
        self.c0 = np.array(self.colors[0], np.float32) / 255; self.c1 = np.array(self.colors[1], np.float32) / 255
    def draw(self, f, t, dur):
        f[:] = np.array(self.bg, np.float32) / 255
        tt = t if self.stop_at is None else min(t, self.stop_at)
        s = np.sin(self.r * self.k + self.arms * self.phi - self.speed * tt * 2)
        v = np.clip(s * 4, -1, 1) * 0.5 + 0.5
        img = self.c0 + (self.c1 - self.c0) * v[..., None]
        cx, cy = int(self.center[0]), int(self.center[1])
        R = self.radius
        reg = f[cy - R:cy + R, cx - R:cx + R]
        reg[:] = reg * (1 - self.mask) + img * self.mask
        aa_circle(f, self.center, 14, (0.95, 0.1, 0.1))
        return f


class Mosaic(Layer):
    """Image fixe très détaillée (mosaïque de Voronoï) pour révéler l'effet consécutif de mouvement."""
    def __init__(self, seed=5, center=(W / 2, 800)):
        self.seed = seed; self.center = center
    def setup(self, dur):
        rng = np.random.default_rng(self.seed)
        pts = rng.uniform(0, 1, (900, 2)) * [W, H]
        small = 4
        yy, xx = np.mgrid[0:H // small, 0:W // small].astype(np.float32) * small
        from scipy.spatial import cKDTree
        tree = cKDTree(pts)
        d, idx = tree.query(np.stack([xx.ravel(), yy.ravel()], 1), k=2)
        idx = idx[:, 0].reshape(xx.shape); edge = (d[:, 1] - d[:, 0]).reshape(xx.shape)
        cols = palette_map(rng.uniform(0, 1, len(pts)), [(0, (20, 60, 140)), (0.3, (40, 170, 190)), (0.55, (250, 210, 80)), (0.8, (240, 90, 60)), (1, (140, 40, 120))])
        img = cols[idx]
        img *= smoothstep(1.5, 6, edge)[..., None]
        self.img = cv2.resize(img.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
    def draw(self, f, t, dur):
        f[:] = self.img
        aa_circle(f, self.center, 14, (0.95, 0.1, 0.1))
        aa_circle(f, self.center, 14, (1, 1, 1), 3)
        return f


class Neurons(Layer):
    """Réseau de neurones stylisé avec impulsions ; deux populations dont l'une se fatigue."""
    def __init__(self, seed=2, fatigue=0.0, colors=((70, 200, 255), (255, 150, 60)), labels=None, balance_bar=False, fatigue_at=0.3):
        self.__dict__.update(locals()); del self.__dict__['self']
    def setup(self, dur):
        rng = np.random.default_rng(self.seed)
        n = 46
        self.p = np.stack([rng.uniform(100, W - 100, n), rng.uniform(330, 1200, n)], 1)
        self.g = rng.integers(0, 2, n)
        d = np.linalg.norm(self.p[:, None] - self.p[None], axis=2)
        self.e = [(i, j) for i in range(n) for j in np.argsort(d[i])[1:4] if i < j]
        self.ph = rng.uniform(0, 1, len(self.e)); self.sp = rng.uniform(0.4, 1.1, len(self.e))
    def draw(self, f, t, dur):
        fat = self.fatigue * ease_in_out((t / max(dur, 1e-3) - self.fatigue_at) / 0.5)
        u8 = np.zeros((H, W, 3), np.uint8)
        for (i, j) in self.e:
            cv2.line(u8, tuple(self.p[i].astype(int)), tuple(self.p[j].astype(int)), (70, 80, 110), 2, cv2.LINE_AA)
        f += u8.astype(np.float32) / 255 * 0.7
        for k, (i, j) in enumerate(self.e):
            g = self.g[i]
            act = 1.0 - (fat if g == 0 else 0)
            x = (self.ph[k] + t * self.sp[k]) % 1.0
            pos = self.p[i] + (self.p[j] - self.p[i]) * x
            blit_rgba(f, radial_glow(46, self.colors[g], 2.0, 0.25), pos[0], pos[1], 0.9 * act, additive=True)
        for i, (x, y) in enumerate(self.p):
            g = self.g[i]
            act = 1.0 - (fat if g == 0 else 0)
            blit_rgba(f, radial_glow(70, self.colors[g], 2.2, 0.3), x, y, 0.4 + 0.6 * act * (0.7 + 0.3 * math.sin(t * 4 + i)), additive=True)
        if self.balance_bar:
            y = 1230
            x0, x1 = 140, W - 140
            mid = lerp((x0 + x1) / 2, x0 + (x1 - x0) * 0.82, fat)
            f[y:y + 26, x0:int(mid)] = np.array(self.colors[0], np.float32) / 255 * (1 - fat * 0.6)
            f[y:y + 26, int(mid):x1] = np.array(self.colors[1], np.float32) / 255
            if self.labels:
                put_text(f, self.labels[0], x0 + 120, y - 50, fname='poppins_sb', size=40, color=self.colors[0], shadow=3)
                put_text(f, self.labels[1], x1 - 140, y - 50, fname='poppins_sb', size=40, color=self.colors[1], shadow=3)
        return f


class Troxler(Layer):
    def __init__(self, center=(W / 2, 800), seed=4, bg=(196, 196, 200), fade=None):
        self.__dict__.update(locals()); del self.__dict__['self']
    def setup(self, dur):
        rng = np.random.default_rng(self.seed)
        img = np.ones((H, W, 3), np.float32) * np.array(self.bg, np.float32) / 255
        cols = [(255, 120, 150), (120, 200, 255), (255, 220, 110), (150, 230, 160), (200, 150, 255), (255, 170, 100), (110, 220, 220), (255, 140, 210)]
        for i, c in enumerate(cols):
            a = i / len(cols) * 2 * np.pi + rng.uniform(-0.2, 0.2)
            r = rng.uniform(240, 360)
            x = self.center[0] + r * math.cos(a); y = self.center[1] + r * math.sin(a) * 1.15
            m = np.zeros((H, W), np.float32)
            cv2.circle(m, (int(x), int(y)), int(rng.uniform(90, 130)), 1.0, -1)
            m = cv2.GaussianBlur(m, (0, 0), 60)[..., None]
            img = img * (1 - m * 0.85) + np.array(c, np.float32) / 255 * m * 0.85
        self.img = img
        self.bgimg = np.ones((H, W, 3), np.float32) * np.array(self.bg, np.float32) / 255
    def draw(self, f, t, dur):
        if self.fade is not None:
            k = ease_in_out((t - self.fade[0]) / max(self.fade[1] - self.fade[0], 1e-3)) * 0.85
            f[:] = self.img * (1 - k) + self.bgimg * k
        else:
            f[:] = self.img
        cx, cy = self.center
        aa_line(f, (cx - 16, cy), (cx + 16, cy), (0, 0, 0), 4)
        aa_line(f, (cx, cy - 16), (cx, cy + 16), (0, 0, 0), 4)
        return f


class LilacChaser(Layer):
    """Illusion du « lilac chaser » (J. Hinton) recréée en code : 12 disques flous, un disparaît à tour de rôle."""
    def __init__(self, center=(W / 2, 800), radius=330, step=0.11, bg=(190, 190, 190), color=(214, 112, 214), simulate=False, fade_pinks=None):
        self.__dict__.update(locals()); del self.__dict__['self']
    def setup(self, dur):
        self.base = np.ones((H, W, 3), np.float32) * np.array(self.bg, np.float32) / 255
        self.discs = []
        for i in range(12):
            a = i / 12 * 2 * np.pi - np.pi / 2
            x = self.center[0] + self.radius * math.cos(a); y = self.center[1] + self.radius * math.sin(a)
            self.discs.append((x, y))
        s = 200
        m = np.zeros((s, s), np.float32)
        cv2.circle(m, (s // 2, s // 2), 44, 1.0, -1, cv2.LINE_AA)
        m = cv2.GaussianBlur(m, (0, 0), 13)
        self.spr = np.dstack([np.broadcast_to(np.array(self.color, np.float32) / 255, (s, s, 3)), m * 0.95]).astype(np.float32)
    def draw(self, f, t, dur):
        f[:] = self.base
        miss = int(t / self.step) % 12
        pa = 1.0
        if self.fade_pinks is not None:
            pa = 1 - 0.92 * ease_in_out((t - self.fade_pinks[0]) / max(self.fade_pinks[1] - self.fade_pinks[0], 1e-3))
        for i, (x, y) in enumerate(self.discs):
            if i != miss:
                blit_rgba(f, self.spr, x, y, pa)
            elif self.simulate:
                g = self.spr.copy(); g[..., :3] = np.array([0.35, 0.85, 0.45])
                blit_rgba(f, g, x, y, 0.9)
        cx, cy = self.center
        aa_line(f, (cx - 18, cy), (cx + 18, cy), (0, 0, 0), 4)
        aa_line(f, (cx, cy - 18), (cx, cy + 18), (0, 0, 0), 4)
        return f


class BlindSpot(Layer):
    """Test de la tache aveugle : croix à gauche, point à droite (variante : ligne interrompue)."""
    def __init__(self, cross=(190, 800), dot=(890, 800), line=False, guide=None):
        self.__dict__.update(locals()); del self.__dict__['self']
    def draw(self, f, t, dur):
        f[:] = 0.97
        cx, cy = self.cross
        aa_line(f, (cx - 34, cy), (cx + 34, cy), (0.05, 0.05, 0.05), 9)
        aa_line(f, (cx, cy - 34), (cx, cy + 34), (0.05, 0.05, 0.05), 9)
        if self.line:
            aa_line(f, (560, self.dot[1]), (self.dot[0] - 50, self.dot[1]), (0.05, 0.05, 0.05), 10)
            aa_line(f, (self.dot[0] + 50, self.dot[1]), (W - 30, self.dot[1]), (0.05, 0.05, 0.05), 10)
            aa_circle(f, self.dot, 34, (0.85, 0.1, 0.1))
        else:
            aa_circle(f, self.dot, 38, (0.05, 0.05, 0.05))
        if self.guide:
            put_text(f, self.guide, W / 2, 470, fname='poppins_xb', size=54, color=(30, 30, 40), shadow=0, max_width=900)
        return f


class EyeDiagram(Layer):
    """Coupe de l'œil : cornée, cristallin, rétine, nerf optique, tache aveugle."""
    def __init__(self, highlight=True, t_hl=1.0):
        self.highlight = highlight; self.t_hl = t_hl
    def draw(self, f, t, dur):
        cx, cy, R = 500, 780, 330
        u8 = np.zeros((H, W, 3), np.uint8)
        # nerf optique
        ang = math.radians(12)
        nx, ny = cx + R * math.cos(ang), cy + R * math.sin(ang)
        cv2.line(u8, (int(nx - 20), int(ny)), (W + 50, int(ny + 80)), (120, 190, 230), 90, cv2.LINE_AA)
        cv2.circle(u8, (cx, cy), R + 14, (230, 230, 235), -1, cv2.LINE_AA)
        cv2.circle(u8, (cx, cy), R, (60, 60, 140), -1, cv2.LINE_AA)
        cv2.ellipse(u8, (cx, cy), (R - 8, R - 8), 0, -110, 110, (120, 140, 255), 22, cv2.LINE_AA)  # rétine
        cv2.ellipse(u8, (cx - R + 10, cy), (60, 170), 0, 90, 270, (250, 230, 200), -1, cv2.LINE_AA)  # cornée
        cv2.ellipse(u8, (cx - R + 95, cy), (45, 110), 0, 0, 360, (240, 200, 120), -1, cv2.LINE_AA)  # cristallin
        cv2.line(u8, (cx - R + 60, cy - 150), (cx - R + 60, cy - 60), (90, 60, 30), 22, cv2.LINE_AA)
        cv2.line(u8, (cx - R + 60, cy + 60), (cx - R + 60, cy + 150), (90, 60, 30), 22, cv2.LINE_AA)
        img = u8[..., ::-1].astype(np.float32) / 255
        m = (u8.sum(2, keepdims=True) > 0)
        f[:] = np.where(m, img, f)
        # rayons lumineux
        k = ease_out(t / 0.9)
        for dy in (-90, 0, 90):
            p0 = (20, cy + dy * 1.6); p1 = (cx - R + 95, cy + dy * 0.6)
            p2 = (lerp(p1[0], cx + R - 20, k), lerp(p1[1], cy + 20, k))
            aa_line(f, p0, p1, (1.0, 0.95, 0.6), 4); aa_line(f, p1, p2, (1.0, 0.95, 0.6), 4)
        if self.highlight and t > self.t_hl:
            p = 0.6 + 0.4 * math.sin(t * 6)
            blit_rgba(f, radial_glow(200, (255, 60, 60), 2.0, 0.3), nx, ny, p, additive=True)
            put_text(f, 'Tache aveugle', nx - 40, ny + 150, fname='poppins_xb', size=48, color=(255, 120, 110), shadow=4)
        put_text(f, 'Rétine', cx + 60, cy - R - 60, fname='poppins_sb', size=42, color=(170, 190, 255), shadow=3)
        put_text(f, 'Nerf optique', 880, ny - 100, fname='poppins_sb', size=40, color=(150, 210, 240), shadow=3)
        return f


# ----------------------------------------------------------------------------- échiquier à l'ombre (version originale)
GRAY_AB = 0.42  # valeur exacte des cases A et B


@functools.lru_cache(maxsize=2)
def checker_scene():
    """Rend un échiquier en perspective avec un cylindre et son ombre portée.
    Les cases A (sombre, au soleil) et B (claire, à l'ombre) ont exactement la même valeur."""
    light_alb, dark_alb = 0.80, GRAY_AB
    s_fac = dark_alb / light_alb  # facteur d'ombre : claire à l'ombre == sombre au soleil
    N = 5
    # homographie : plateau (u,v in [0,N]) -> écran
    src = np.float32([[0, 0], [N, 0], [N, N], [0, N]])
    dst = np.float32([[300, 380], [860, 460], [800, 1150], [120, 1000]])
    Hm = cv2.getPerspectiveTransform(dst, src)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    pts = np.stack([xx.ravel(), yy.ravel(), np.ones(xx.size, np.float32)], 0)
    uvw = Hm @ pts
    u = (uvw[0] / uvw[2]).reshape(H, W); v = (uvw[1] / uvw[2]).reshape(H, W)
    inside = (u >= 0) & (u < N) & (v >= 0) & (v < N)
    ti, tj = np.floor(u).astype(int), np.floor(v).astype(int)
    alb = np.where((ti + tj) % 2 == 0, light_alb, dark_alb)
    # case B : claire à l'ombre (2,3) ; case A : sombre au soleil (1,1)... vérifie la parité
    A, B = (1, 0), (2, 2)
    assert (A[0] + A[1]) % 2 == 1 and (B[0] + B[1]) % 2 == 0
    # ombre douce allongée, projetée depuis le pied du cylindre vers l'avant-gauche
    sc_u, sc_v = 2.5, 2.5
    d_u, d_v = -0.6, 0.8
    du, dv = u - sc_u, v - sc_v
    along = du * d_u + dv * d_v; perp = du * d_v - dv * d_u
    d = np.sqrt((along / 1.9) ** 2 + (perp / 1.15) ** 2)
    shadow = 1 - smoothstep(0.78, 1.18, d)
    inB = (ti == B[0]) & (tj == B[1]) & inside; inA = (ti == A[0]) & (tj == A[1]) & inside
    assert shadow[inB].min() > 0.97 and shadow[inA].max() < 0.03, (shadow[inB].min(), shadow[inA].max())
    shadow = np.where(inB, 1.0, shadow); shadow = np.where(inA, 0.0, shadow)
    light = 1.0 * (1 - shadow) + s_fac * shadow
    val = alb * light
    img = np.zeros((H, W, 3), np.float32)
    bg = gradient_v(H, W, (35, 40, 60), (12, 14, 22))
    img[:] = bg
    col = np.stack([val, val, val], -1)
    img = np.where(inside[..., None], col, img)
    # tranche du plateau
    side = np.float32([[120, 1000], [800, 1150], [800, 1200], [120, 1048]])
    side2 = np.float32([[800, 1150], [860, 460], [860, 505], [800, 1200]])
    for poly, c in ((side, 0.22), (side2, 0.3)):
        m = np.zeros((H, W), np.uint8); aa_poly(m, poly, 255)
        mm = m.astype(np.float32)[..., None] / 255
        img = img * (1 - mm) + c * mm
    # cylindre vert
    base = np.float32([sc_u - d_u * 1.3, sc_v - d_v * 1.3, 1.0]); Hinv = np.linalg.inv(Hm)
    p = Hinv @ base; bx, by = p[0] / p[2], p[1] / p[2]
    cw, chh = 120, 330
    cyl = np.zeros((H, W, 3), np.float32); cm = np.zeros((H, W), np.float32)
    x0, x1 = int(bx - cw), int(bx + cw)
    xs = np.linspace(-1, 1, x1 - x0)
    shade = (0.35 + 0.65 * np.clip(np.cos((xs + 0.35) * 1.3), 0, 1))
    cyl[int(by - chh):int(by), x0:x1] = np.array([0.2, 0.62, 0.25])[None, None, :] * shade[None, :, None]
    cm[int(by - chh):int(by), x0:x1] = 1
    e = np.zeros((H, W), np.uint8)
    cv2.ellipse(e, (int(bx), int(by)), (cw, 42), 0, 0, 180, 255, -1, cv2.LINE_AA)
    cv2.ellipse(e, (int(bx), int(by - chh)), (cw, 42), 0, 0, 360, 255, -1, cv2.LINE_AA)
    em = e.astype(np.float32) / 255
    top = np.zeros((H, W), np.uint8); cv2.ellipse(top, (int(bx), int(by - chh)), (cw, 42), 0, 0, 360, 255, -1, cv2.LINE_AA)
    ex = np.arange(W)[None, :]
    shade_full = np.clip(0.35 + 0.65 * np.cos(((ex - bx) / cw + 0.35) * 1.3), 0.2, 1)
    cyl = np.where(em[..., None] > 0, np.array([0.2, 0.62, 0.25]) * shade_full[..., None], cyl)
    cm = np.maximum(cm, em)
    tm = top.astype(np.float32)[..., None] / 255
    cyl = cyl * (1 - tm) + np.array([0.35, 0.8, 0.4]) * tm
    img = img * (1 - cm[..., None]) + cyl * cm[..., None]
    # contrôle : A et B strictement identiques
    va = img[inA & ~(cm > 0)].mean(); vb = img[inB & ~(cm > 0)].mean()
    assert abs(va - vb) < 1e-4, (va, vb)
    def tile_center(t):
        q = Hinv @ np.float32([t[0] + 0.5, t[1] + 0.5, 1]); return q[0] / q[2], q[1] / q[2]
    return img.astype(np.float32), inA, inB, tile_center(A), tile_center(B), inside


class Checker(Layer):
    """mode : 'normal' | 'bars' (bande de même gris reliant A et B) | 'isolate' (tout le reste masqué)."""
    def __init__(self, mode='normal', t0=0.0, labels=True, back=False):
        self.__dict__.update(locals()); del self.__dict__['self']
    def draw(self, f, t, dur):
        img, inA, inB, cA, cB, inside = checker_scene()
        f[:] = img
        lt = t - self.t0
        if self.mode == 'bars' and lt > 0:
            k = ease_out(lt / 0.8)
            bw = 46
            y = int(cA[1]) - bw // 2
            x0, x1 = int(cA[0]), int(lerp(cA[0], cB[0], k))
            f[y:y + bw, min(x0, x1):max(x0, x1)] = GRAY_AB
            yb0, yb1 = int(cA[1]), int(lerp(cA[1], cB[1], k))
            f[min(yb0, yb1):max(yb0, yb1), int(cB[0]) - bw // 2:int(cB[0]) + bw // 2] = GRAY_AB if k >= 0.999 else f[min(yb0, yb1):max(yb0, yb1), int(cB[0]) - bw // 2:int(cB[0]) + bw // 2]
            if k >= 0.999:
                f[y:y + bw, int(cA[0]):int(cB[0]) + bw // 2] = GRAY_AB
                f[min(yb0, int(cB[1])):max(yb0, int(cB[1])), int(cB[0]) - bw // 2:int(cB[0]) + bw // 2] = GRAY_AB
        if self.mode == 'isolate':
            k = ease_in_out(lt / 0.7) if not self.back else 1 - ease_in_out(lt / 0.7)
            keep = (inA | inB)[..., None]
            bg = np.array([0.08, 0.1, 0.16])
            f[:] = np.where(keep, f, f * (1 - k) + bg * k)
        if self.labels:
            for (c, lab) in ((cA, 'A'), (cB, 'B')):
                put_text(f, lab, c[0], c[1], fname='anton', size=92, color=(250, 250, 250) if lab == 'A' else (20, 20, 20), shadow=0)
        return f


class DressSwatches(Layer):
    def draw(self, f, t, dur):
        f[:] = 0.06
        for i, (cols, lab) in enumerate(((((40, 60, 160), (20, 18, 15)), 'Bleue et noire'), (((235, 235, 240), (190, 150, 70)), 'Blanche et dorée'))):
            x0 = 90 + i * 470
            for k in range(6):
                c = cols[k % 2]
                f[420 + k * 110:420 + (k + 1) * 110, x0:x0 + 430] = np.array(c, np.float32) / 255
            put_text(f, lab, x0 + 215, 1150, fname='poppins_xb', size=48, color=(240, 240, 245), shadow=4)
        put_text(f, '2015', W / 2, 300, fname='anton', size=120, color=(255, 210, 90), shadow=6)
        return f


class PaperShadow(Layer):
    """Feuille blanche à moitié à l'ombre : le cerveau voit la même couleur."""
    def draw(self, f, t, dur):
        f[:] = gradient_v(H, W, (110, 85, 60), (60, 45, 30))
        pts = np.float32([[230, 420], [850, 470], [800, 1180], [180, 1110]])
        m = np.zeros((H, W), np.uint8); aa_poly(m, pts, 255)
        mm = m.astype(np.float32)[..., None] / 255
        xx = np.arange(W)[None, :, None]
        sh = smoothstep(500, 560, xx)
        val = 0.93 * (1 - sh) + 0.5 * sh
        f[:] = f * (1 - mm) + val * mm
        k = t / max(dur, 1e-3)
        if k > 0.3:
            put_text(f, '93 %', 350, 760, fname='anton', size=110, color=(40, 40, 40), shadow=0)
            put_text(f, '50 %', 680, 790, fname='anton', size=110, color=(230, 230, 230), shadow=0)
        if k > 0.6:
            put_text(f, 'Ton cerveau voit : BLANC', W / 2, 300, fname='poppins_xb', size=64, color=(255, 230, 120), shadow=5)
        return f


class FlagCompare(Layer):
    """Drapeau inversé → drapeau réel, avec flèche."""
    def draw(self, f, t, dur):
        w, h = 380, 253
        for k, (cx, inv) in enumerate(((W / 2, True), (W / 2, False))):
            cy = 520 if inv else 1060
            if not inv and t < 0.6:
                continue
            a = 1.0 if inv else min(1, (t - 0.6) / 0.3)
            for i, c in enumerate(FLAG):
                col = tuple(255 - v for v in c) if inv else c
                x0 = int(cx - w / 2 + i * w / 3)
                reg = f[int(cy - h / 2):int(cy + h / 2), x0:x0 + w // 3]
                reg[:] = reg * (1 - a) + np.array(col, np.float32) / 255 * a
        put_text(f, '↓', W / 2, 790, fname='poppins_xb', size=120, color=(255, 225, 80), shadow=4) if False else None
        aa_line(f, (W / 2, 690), (W / 2, 880), (1.0, 0.88, 0.3), 10)
        aa_poly(f, [(W / 2 - 40, 860), (W / 2 + 40, 860), (W / 2, 920)], (1.0, 0.88, 0.3))
        put_text(f, "À l'écran", W / 2 + 330, 520, fname='poppins_sb', size=40, color=(220, 220, 230), shadow=3)
        if t > 0.6:
            put_text(f, 'Dans ton cerveau', W / 2 + 330, 1060, fname='poppins_sb', size=40, color=(255, 225, 80), shadow=3, max_width=260)
        return f
