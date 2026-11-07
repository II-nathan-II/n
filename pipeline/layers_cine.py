"""Animations 3D « cinéma » calculées image par image (style « réflexion » de Vertige Cosmique).

Tout est rendu en numpy/OpenCV, sans GPU :
  Globe      planète texturée (cartes NASA du domaine public), lumière du Soleil, nuit, atmosphère
  StarField  champ d'étoiles en 3D (dérive ou plongée vers l'avant)
  Filaments  arborescence lumineuse façon neurones / racines, qui pousse et tourne
  Atom       noyau + nuage électronique
  Galaxy     galaxie spirale de ~150 000 étoiles
  Web        toile cosmique (filaments de galaxies)
  Rays       lignes de lumière qui convergent vers le centre
  Shell      onde de choc d'une supernova
  Halo       point lumineux (étoile, « point bleu pâle ») avec cercle optionnel
Les couches s'additionnent (lumière) sur fond noir, puis la caméra du plan s'applique.
"""
import os, math, functools
import numpy as np
import cv2
from common import W, H, ASSETS, ease_in_out, lerp, smoothstep
from layers_base import Layer

TEX = os.path.join(ASSETS, 'textures')


@functools.lru_cache(maxsize=8)
def texture(name):
    img = cv2.imread(os.path.join(TEX, name), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(name)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255


def kf(keys, t):
    """Interpolation douce entre images clés [(t, valeur), …] (valeurs scalaires ou tuples)."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            k = ease_in_out((t - t0) / max(t1 - t0, 1e-6))
            if isinstance(v0, (tuple, list)):
                return tuple(lerp(a, b, k) for a, b in zip(v0, v1))
            return lerp(v0, v1, k)
    return keys[-1][1]


def bloom(img, amount=1.0, sigmas=(3, 9, 24), weights=(0.9, 0.6, 0.35)):
    """Halo lumineux : flou à plusieurs échelles ajouté à l'image (calculé à demi-résolution)."""
    h, w = img.shape[:2]
    small = cv2.resize(img, (w // 2, h // 2), interpolation=cv2.INTER_AREA)
    acc = np.zeros_like(small)
    for s, wt in zip(sigmas, weights):
        acc += cv2.GaussianBlur(small, (0, 0), s / 2) * wt
    return img + cv2.resize(acc, (w, h), interpolation=cv2.INTER_LINEAR) * amount


def splat(buf, xs, ys, vals):
    """Ajoute des points (valeurs RGB) dans un tampon, avec répartition bilinéaire (pas de scintillement)."""
    h, w = buf.shape[:2]
    x0 = np.floor(xs).astype(np.int32); y0 = np.floor(ys).astype(np.int32)
    fx = (xs - x0)[:, None]; fy = (ys - y0)[:, None]
    for dx, dy, wt in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        xx = x0 + dx; yy = y0 + dy
        ok = (xx >= 0) & (xx < w) & (yy >= 0) & (yy < h)
        np.add.at(buf, (yy[ok], xx[ok]), vals[ok] * wt[ok])
    return buf


def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], np.float32)


def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], np.float32)


def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], np.float32)


# ============================================================================= planète
class Globe(Layer):
    """Planète texturée en projection orthographique.

    r, c     : images clés [(t, rayon px)], [(t, (x, y))] ; un nombre/tuple seul = fixe
    lon0     : longitude au centre du disque (degrés) ; spin : degrés par seconde
    tilt     : inclinaison de l'axe dans l'image (degrés) ; lat : latitude vue de face
    sun      : direction du Soleil dans l'espace de la vue (x droite, y haut, z vers nous)
    """
    def __init__(self, day='earth_viirs_4k.jpg', night=None, r=380, c=(W / 2, H / 2), lon0=15.0, spin=4.0, tilt=-18.0, lat=12.0,
                 sun=(-0.75, 0.35, 0.56), atmos=(0.35, 0.62, 1.0), atmos_w=0.05, ambient=0.03, night_gain=1.6, spec=0.35, exposure=1.0, fade=None):
        self.__dict__.update(locals()); del self.__dict__['self']

    def setup(self, dur):
        self.tday = texture(self.day)
        self.tnight = texture(self.night) if self.night else None
        if self.spec > 0:
            d = self.tday
            # océans : pixels sombres et bleutés de la carte (pour le reflet du Soleil)
            self.ocean = np.clip((d[..., 2] - d[..., 0]) * 4 - (d.mean(-1) - 0.35) * 3, 0, 1).astype(np.float32)
        s = np.array(self.sun, np.float32); self.L = s / np.linalg.norm(s)

    def _val(self, v, t):
        return kf(v, t) if isinstance(v, list) else v

    def draw(self, f, t, dur):
        R = float(self._val(self.r, t)); cx, cy = self._val(self.c, t)
        a_fade = 1.0 if self.fade is None else float(kf(self.fade, t))
        if R < 0.6 or a_fade <= 0:
            return f
        ext = R * (1 + self.atmos_w * 4) + 2
        x0, x1 = int(max(0, cx - ext)), int(min(W, cx + ext + 1)); y0, y1 = int(max(0, cy - ext)), int(min(H, cy + ext + 1))
        if x1 <= x0 or y1 <= y0:
            return f
        ys, xs = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        X = (xs - cx) / R; Y = (cy - ys) / R
        rr = X * X + Y * Y
        inside = rr <= 1.0
        Z = np.sqrt(np.clip(1 - rr, 0, 1))
        # normale (vue) → repère de la planète
        M = rot_y(-math.radians(self.lon0 + self.spin * t)) @ rot_x(math.radians(self.lat)) @ rot_z(math.radians(-self.tilt))
        n = np.stack([X, Y, Z], -1)
        b = n @ M.T
        lon = np.arctan2(b[..., 0], b[..., 2]); latp = np.arcsin(np.clip(b[..., 1], -1, 1))
        th, tw = self.tday.shape[:2]
        u = ((lon / (2 * math.pi) + 0.5) * tw).astype(np.float32); v = ((0.5 - latp / math.pi) * th).astype(np.float32)
        day = cv2.remap(self.tday, u, v, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        ndl = (n @ self.L)
        lit = smoothstep(-0.12, 0.35, ndl)[..., None]
        col = day * (self.ambient + lit * np.clip(ndl, 0, 1)[..., None] ** 0.8 * 1.15)
        if self.tnight is not None:
            nl = cv2.remap(self.tnight, u, v, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
            col += nl * (1 - smoothstep(-0.18, 0.08, ndl))[..., None] * self.night_gain * np.array([1.0, 0.85, 0.6], np.float32)
        if self.spec > 0:
            oc = cv2.remap(self.ocean, u, v, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
            hvec = self.L + np.array([0, 0, 1], np.float32); hvec /= np.linalg.norm(hvec)
            sp = np.clip(n @ hvec, 0, 1) ** 60 * oc * self.spec * (ndl > 0)
            col += sp[..., None] * np.array([1.0, 0.95, 0.85], np.float32)
        # atmosphère : liseré bleu sur le bord éclairé, puis halo à l'extérieur
        ac = np.array(self.atmos, np.float32)
        rim = (1 - Z) ** 2.5 * np.clip(ndl + 0.35, 0, 1)
        col += rim[..., None] * ac * 0.9
        col = col * self.exposure
        rad = np.sqrt(rr)
        L2 = self.L[:2] / (np.linalg.norm(self.L[:2]) + 1e-6)
        side = np.clip((X * L2[0] + Y * L2[1]) / (rad + 1e-6) * 0.6 + 0.45 + self.L[2] * 0.3, 0, 1)
        halo = np.exp(-np.clip(rad - 1, 0, None) / self.atmos_w) * (~inside) * side
        region = f[y0:y1, x0:x1]
        aa = np.clip((1 - rad) * R + 0.5, 0, 1)[..., None]  # bord net mais lissé
        out = region * (1 - aa * a_fade) + col * aa * a_fade
        out += halo[..., None] * ac * 0.85 * a_fade
        f[y0:y1, x0:x1] = out
        return f


# ============================================================================= étoiles
class StarField(Layer):
    """Étoiles en 3D. speed > 0 : plongée vers l'avant ; drift : dérive latérale (px/s) ; fade : [(t, alpha)]."""
    def __init__(self, n=2600, seed=1, speed=0.0, drift=(0.0, 0.0), bright=1.0, fov=900, fade=None, tint=None):
        self.__dict__.update(locals()); del self.__dict__['self']

    def setup(self, dur):
        rng = np.random.default_rng(self.seed)
        self.p = np.stack([rng.uniform(-1.6, 1.6, self.n), rng.uniform(-2.6, 2.6, self.n), rng.uniform(0.15, 1.0, self.n)], 1).astype(np.float32)
        cols = np.array([(0.62, 0.72, 1.0), (0.8, 0.86, 1.0), (1.0, 1.0, 1.0), (1.0, 0.95, 0.88), (1.0, 0.82, 0.62)], np.float32)
        self.col = cols[rng.integers(0, len(cols), self.n)]
        self.mag = (rng.pareto(2.2, self.n) + 1).clip(1, 12).astype(np.float32)
        self.ph = rng.uniform(0, 6.28, self.n).astype(np.float32)

    def draw(self, f, t, dur):
        a = 1.0 if self.fade is None else float(kf(self.fade, t))
        if a <= 0:
            return f
        if self.speed > 0.2:
            return self._warp(f, t, a)
        z = (self.p[:, 2] - self.speed * t) % 1.0 + 0.02
        xs = W / 2 + self.p[:, 0] / z * self.fov * 0.5 + self.drift[0] * t
        ys = H / 2 + self.p[:, 1] / z * self.fov * 0.5 + self.drift[1] * t
        xs = (xs + W) % (W * 1.0) if self.speed == 0 else xs
        ys = (ys + H) % (H * 1.0) if self.speed == 0 else ys
        tw = 0.8 + 0.2 * np.sin(t * 2.3 + self.ph)
        br = (self.mag * 0.13 * tw * (0.35 + 0.65 * (1 - z) if self.speed else 1.0) * self.bright * a)[:, None] * self.col
        if self.tint is not None:
            br = br * np.array(self.tint, np.float32)
        buf = np.zeros((H, W, 3), np.float32)
        splat(buf, xs, ys, br.astype(np.float32))
        buf = cv2.GaussianBlur(buf, (0, 0), 0.75) * 6.0
        f += bloom(buf, 1.2, (2, 6, 16), (0.8, 0.45, 0.2))
        return f


    def _warp(self, f, t, a):
        """Plongée rapide : traînées d'étoiles qui jaillissent du centre (effet « hyperespace »)."""
        dt = 1 / 30
        z1 = (self.p[:, 2] - self.speed * t) % 1.0 + 0.04
        z0 = np.minimum(z1 + self.speed * dt * 2.5, 1.04)
        sc = self.fov * 0.18
        x1 = W / 2 + self.p[:, 0] / z1 * sc; y1 = H / 2 + self.p[:, 1] / z1 * sc
        x0 = W / 2 + self.p[:, 0] / z0 * sc; y0 = H / 2 + self.p[:, 1] / z0 * sc
        br = np.clip((1.05 - z1) ** 1.5, 0, 1) * self.bright * a
        buf = np.zeros((H // 2, W // 2, 3), np.float32)
        ok = (np.abs(x1 - W / 2) < W) & (np.abs(y1 - H / 2) < H)
        for i in np.nonzero(ok)[0]:
            c = tuple(float(v) for v in self.col[i] * br[i] * 1.6)
            cv2.line(buf, (int(x0[i] * 8), int(y0[i] * 8)), (int(x1[i] * 8), int(y1[i] * 8)), c, 1, cv2.LINE_AA, 4)
        buf = bloom(buf, 1.0, (2, 6, 16), (0.7, 0.4, 0.2))
        f += cv2.resize(buf, (W, H), interpolation=cv2.INTER_LINEAR)
        return f


# ============================================================================= filaments (neurones / racines)
class Filaments(Layer):
    """Arborescence lumineuse en 3D qui pousse (grow : [(t, 0..1)]) et tourne lentement."""
    def __init__(self, seed=3, roots=9, steps=110, branch=0.05, jitter=0.13, palette=((0.25, 0.95, 1.0), (0.3, 1.0, 0.65), (1.0, 0.65, 0.35)),
                 grow=((0, 0.0), (6, 1.0)), spin=0.12, scale=1.0, center=(W / 2, H * 0.47), sparks=900, bright=1.0, fade=None):
        self.__dict__.update(locals()); del self.__dict__['self']

    def setup(self, dur):
        rng = np.random.default_rng(self.seed)
        segs = []  # (p0, p1, birth, depth)
        def walk(p, d, birth, depth, n):
            for i in range(n):
                d = d + rng.normal(0, self.jitter, 3); d /= np.linalg.norm(d)
                q = p + d * (0.028 * (0.92 ** depth))
                segs.append((p.copy(), q.copy(), birth + i / self.steps, depth))
                p = q
                if depth < 5 and rng.random() < self.branch * (1.2 - depth * 0.15):
                    nd = d + rng.normal(0, 0.9, 3); nd /= np.linalg.norm(nd)
                    walk(p.copy(), nd, birth + i / self.steps, depth + 1, int(n * rng.uniform(0.35, 0.7)))
        for k in range(self.roots):
            ang = k / self.roots * 6.283 + rng.normal(0, 0.3)
            d0 = np.array([math.cos(ang), rng.normal(0, 0.45), math.sin(ang)]); d0 /= np.linalg.norm(d0)
            walk(np.array([0.0, 0.0, 0.0]) + rng.normal(0, 0.02, 3), -d0, 0.0, 0, self.steps)
        a = np.array([s[0] for s in segs], np.float32); b = np.array([s[1] for s in segs], np.float32)
        allp = np.concatenate([a, b]); mid = (allp.max(0) + allp.min(0)) / 2; ext = (allp.max(0) - allp.min(0)).max() / 2
        a = (a - mid) / ext * 0.95; b = (b - mid) / ext * 0.95
        self.a, self.b = a, b
        self.birth = np.array([s[2] for s in segs], np.float32); self.birth /= max(self.birth.max(), 1e-6)
        self.depth = np.array([s[3] for s in segs], np.int32)
        pal = np.array(self.palette, np.float32)
        pw = np.array([0.55, 0.3, 0.15][:len(pal)]); pick = rng.choice(len(pal), len(segs), p=pw / pw.sum())
        self.col = pal[pick] * (0.55 + 0.45 * rng.random(len(segs)))[:, None]
        self.sp_seg = rng.integers(0, len(segs), self.sparks); self.sp_ph = rng.random(self.sparks).astype(np.float32)

    def _proj(self, P, t):
        M = rot_y(self.spin * t) @ rot_x(0.25)
        Q = P @ M.T
        z = Q[:, 2] + 2.4
        s = 1150 * self.scale / z
        return np.stack([self.center[0] + Q[:, 0] * s, self.center[1] - Q[:, 1] * s], 1), z

    def draw(self, f, t, dur):
        g = float(kf(list(self.grow), t)); a = 1.0 if self.fade is None else float(kf(self.fade, t))
        if g <= 0 or a <= 0:
            return f
        show = self.birth <= g
        pa, za = self._proj(self.a[show], t); pb, _ = self._proj(self.b[show], t)
        hw, hh = W // 2, H // 2
        canvas = np.zeros((hh, hw, 3), np.float32)
        cols = self.col[show]; dep = self.depth[show]
        fresh = np.clip((g - self.birth[show]) * 8, 0, 1)  # pointes qui poussent plus brillantes
        for th in (2, 1):
            sel = (dep <= 1) if th == 2 else (dep > 1)
            P = np.concatenate([pa[sel], pb[sel]], 1) / 2
            for (x0, y0, x1, y1), c, fr in zip(P, cols[sel], fresh[sel]):
                cv2.line(canvas, (int(x0 * 16), int(y0 * 16)), (int(x1 * 16), int(y1 * 16)),
                         tuple(float(v * (0.5 + 0.9 * (1 - fr))) for v in c), th, cv2.LINE_AA, 4)
        # étincelles qui circulent le long des branches
        sid = self.sp_seg[np.isin(self.sp_seg, np.nonzero(show)[0])]
        if len(sid):
            k = (self.sp_ph[:len(sid)] + t * 0.6) % 1.0
            A, _ = self._proj(self.a[sid], t); B, _ = self._proj(self.b[sid], t)
            P = (A + (B - A) * k[:, None]) / 2
            splat(canvas, P[:, 0], P[:, 1], np.tile(np.array([[0.9, 1.0, 0.95]], np.float32), (len(sid), 1)) * 0.9)
        canvas = bloom(canvas, 1.3, (2, 6, 18), (1.0, 0.7, 0.45))
        f += cv2.resize(canvas, (W, H), interpolation=cv2.INTER_LINEAR) * self.bright * a
        return f


# ============================================================================= atome
class Atom(Layer):
    """Noyau de nucléons éclairés + nuage électronique (densité de probabilité) qui respire."""
    def __init__(self, center=(W / 2, H * 0.45), r=(0, 220), cloud=520, n_e=60000, seed=5, fade=None, nucleus_scale=1.0):
        self.__dict__.update(locals()); del self.__dict__['self']

    def setup(self, dur):
        rng = np.random.default_rng(self.seed)
        k = 14
        self.nuc = rng.normal(0, 0.55, (k, 3)).astype(np.float32)
        self.ntype = rng.integers(0, 2, k)
        # orbitales 1s + 2p (lobes) : échantillonnage simple
        r1 = rng.gamma(3, 0.18, self.n_e // 2); d1 = rng.normal(0, 1, (self.n_e // 2, 3)); d1 /= np.linalg.norm(d1, axis=1, keepdims=True)
        s1 = d1 * r1[:, None]
        m = self.n_e - len(s1)
        r2 = rng.gamma(5, 0.2, m); d2 = rng.normal(0, 1, (m, 3)); d2[:, 0] = np.abs(d2[:, 0]) * np.sign(rng.random(m) - 0.5) * 2.2
        d2 /= np.linalg.norm(d2, axis=1, keepdims=True)
        self.e = np.concatenate([s1, d2 * r2[:, None]]).astype(np.float32)
        self.ec = np.where((np.arange(self.n_e) < len(s1))[:, None], np.array([0.35, 0.7, 1.0], np.float32), np.array([0.65, 0.45, 1.0], np.float32))

    def draw(self, f, t, dur):
        a = 1.0 if self.fade is None else float(kf(self.fade, t))
        if a <= 0:
            return f
        cx, cy = self.center
        M = rot_y(t * 0.35) @ rot_x(0.4 + 0.1 * math.sin(t * 0.3))
        E = self.e @ M.T
        sc = self.cloud * (0.92 + 0.08 * math.sin(t * 1.7))
        buf = np.zeros((H // 2, W // 2, 3), np.float32)
        jit = np.random.default_rng(int(t * 30)).normal(0, 0.012, E.shape).astype(np.float32)
        Ej = E + jit
        splat(buf, (cx + Ej[:, 0] * sc) / 2, (cy - Ej[:, 1] * sc) / 2, self.ec * 0.5 * (560 / sc) ** 0.15)
        buf = cv2.GaussianBlur(buf, (0, 0), 1.4)
        buf = buf / (1 + buf * 0.6)  # compression douce des zones denses
        buf = bloom(buf, 0.9, (3, 10, 26), (0.7, 0.45, 0.3))
        f += cv2.resize(buf, (W, H), interpolation=cv2.INTER_LINEAR) * a
        # noyau : petites sphères éclairées, triées en profondeur
        Nn = self.nuc @ M.T
        order = np.argsort(Nn[:, 2])
        rn = 26 * self.nucleus_scale
        for i in order:
            x, y = int(cx + Nn[i, 0] * rn * 1.6), int(cy - Nn[i, 1] * rn * 1.6)
            base = np.array([1.0, 0.35, 0.25] if self.ntype[i] else [0.75, 0.8, 0.9], np.float32)
            rr = int(rn)
            y0, y1, x0, x1 = max(0, y - rr), min(H, y + rr + 1), max(0, x - rr), min(W, x + rr + 1)
            if y1 <= y0 or x1 <= x0:
                continue
            yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
            dx, dy = (xx - x) / rr, (yy - y) / rr
            d2 = dx * dx + dy * dy
            m = d2 <= 1
            z = np.sqrt(np.clip(1 - d2, 0, 1))
            sh = np.clip(-dx * 0.5 - dy * 0.6 + z * 0.6, 0, 1)[..., None]
            col = base * (0.15 + sh * 0.95) + (sh ** 18) * 0.6
            aa = np.clip((1 - np.sqrt(d2)) * rr, 0, 1)[..., None] * a
            reg = f[y0:y1, x0:x1]
            f[y0:y1, x0:x1] = reg * (1 - aa) + col * aa
        return f


# ============================================================================= galaxie
class Galaxy(Layer):
    """Galaxie spirale vue en perspective (tilt), qui tourne ; r : rayon à l'écran (px) ou images clés."""
    def __init__(self, n=160000, seed=7, r=520, center=(W / 2, H * 0.46), tilt=62, spin=0.05, arms=2, fade=None, roll=-20):
        self.__dict__.update(locals()); del self.__dict__['self']

    def setup(self, dur):
        rng = np.random.default_rng(self.seed)
        n = self.n
        nb = n // 9
        rad = rng.exponential(0.32, n - nb).clip(0, 1.4)
        arm = rng.integers(0, self.arms, n - nb)
        th = np.log(rad + 0.05) * 2.6 + arm * (2 * math.pi / self.arms) + rng.normal(0, 0.32 + 0.15 * (1 - rad), n - nb)
        disk = np.stack([rad * np.cos(th), rng.normal(0, 0.02, n - nb), rad * np.sin(th)], 1)
        bul = rng.normal(0, 0.13, (nb, 3)) * np.array([1, 0.6, 1])
        self.p = np.concatenate([disk, bul]).astype(np.float32)
        warm = np.array([1.0, 0.82, 0.6], np.float32); cool = np.array([0.6, 0.75, 1.0], np.float32); pink = np.array([1.0, 0.45, 0.6], np.float32)
        rr = np.linalg.norm(self.p[:, [0, 2]], axis=1)
        k = np.clip(rr / 0.6, 0, 1)[:, None]
        col = warm * (1 - k) + cool * k
        hii = rng.random(n) < 0.015
        col[hii] = pink
        self.col = col * rng.uniform(0.4, 1.0, n)[:, None]
        self.col[n - nb:] *= 0.45
        self.col[:n - nb] *= 1.5

    def draw(self, f, t, dur):
        a = 1.0 if self.fade is None else float(kf(self.fade, t))
        if a <= 0:
            return f
        R = float(kf(self.r, t)) if isinstance(self.r, list) else self.r
        M = rot_z(math.radians(self.roll)) @ rot_x(math.radians(self.tilt)) @ rot_y(self.spin * t)
        P = self.p @ M.T
        buf = np.zeros((H // 2, W // 2, 3), np.float32)
        splat(buf, (self.center[0] + P[:, 0] * R) / 2, (self.center[1] - P[:, 1] * R) / 2, self.col * 0.12 * (520 / max(R, 60)) ** 0.5)
        buf = cv2.GaussianBlur(buf, (0, 0), 0.8)
        buf = buf / (1 + buf * 0.5)
        buf = bloom(buf, 1.0, (3, 10, 30), (0.8, 0.5, 0.35))
        f += cv2.resize(buf, (W, H), interpolation=cv2.INTER_LINEAR) * a
        return f


# ============================================================================= toile cosmique
class Web(Layer):
    """Toile cosmique : nœuds reliés par des filaments de galaxies (points), en lente rotation."""
    def __init__(self, seed=11, nodes=110, n=220000, scale=620, fade=None, spin=0.04, color=(0.75, 0.55, 1.0)):
        self.__dict__.update(locals()); del self.__dict__['self']

    def setup(self, dur):
        rng = np.random.default_rng(self.seed)
        nodes = rng.uniform(-1, 1, (self.nodes, 3))
        pairs = []
        for i in range(self.nodes):
            d = np.linalg.norm(nodes - nodes[i], axis=1)
            for j in np.argsort(d)[1:4]:
                if i < j:
                    pairs.append((i, j))
        pairs = np.array(pairs)
        k = rng.integers(0, len(pairs), self.n)
        u = rng.random(self.n)[:, None]
        pts = nodes[pairs[k, 0]] * (1 - u) + nodes[pairs[k, 1]] * u + rng.normal(0, 0.009, (self.n, 3))
        clus = nodes[rng.integers(0, self.nodes, self.n // 3)] + rng.normal(0, 0.025, (self.n // 3, 3))
        self.p = np.concatenate([pts, clus]).astype(np.float32)
        c = np.array(self.color, np.float32)
        self.col = (c * rng.uniform(0.3, 1.0, len(self.p))[:, None]).astype(np.float32)

    def draw(self, f, t, dur):
        a = 1.0 if self.fade is None else float(kf(self.fade, t))
        if a <= 0:
            return f
        P = self.p @ (rot_y(self.spin * t) @ rot_x(0.3)).T
        z = P[:, 2] + 2.6
        s = self.scale * 2.6 / z
        buf = np.zeros((H // 2, W // 2, 3), np.float32)
        splat(buf, (W / 2 + P[:, 0] * s) / 2, (H / 2 - P[:, 1] * s) / 2, self.col * 0.09 * (2.6 / z)[:, None] ** 2)
        buf = cv2.GaussianBlur(buf, (0, 0), 0.6)
        buf = buf / (1 + buf * 0.5)
        buf = bloom(buf, 1.1, (3, 10, 28), (0.8, 0.5, 0.3))
        f += cv2.resize(buf, (W, H), interpolation=cv2.INTER_LINEAR) * a
        return f


# ============================================================================= lignes de lumière
class Rays(Layer):
    """Lignes de lumière horizontales qui convergent vers un point, avec impulsions qui y courent."""
    def __init__(self, center=(W / 2, H * 0.47), n=7, spread=170, color=(0.85, 0.92, 1.0), fade=None, seed=2):
        self.__dict__.update(locals()); del self.__dict__['self']

    def setup(self, dur):
        rng = np.random.default_rng(self.seed)
        self.off = np.sort(rng.uniform(-1, 1, (2, self.n)), axis=1) * self.spread
        self.ph = rng.random((2, self.n))

    def draw(self, f, t, dur):
        a = 1.0 if self.fade is None else float(kf(self.fade, t))
        if a <= 0:
            return f
        cx, cy = self.center
        buf = np.zeros((H // 2, W // 2, 3), np.float32)
        col = tuple(float(c) * 0.55 for c in self.color)
        for side, x_edge in ((0, -40), (1, W + 40)):
            for i in range(self.n):
                ye = cy + self.off[side, i]
                cv2.line(buf, (int(x_edge / 2 * 16), int(ye / 2 * 16)), (int(cx / 2 * 16), int((cy + self.off[side, i] * 0.12) / 2 * 16)), col, 1, cv2.LINE_AA, 4)
                k = (self.ph[side, i] + t * 0.35) % 1.0
                px = x_edge + (cx - x_edge) * k; py = ye + (cy + self.off[side, i] * 0.12 - ye) * k
                cv2.circle(buf, (int(px / 2), int(py / 2)), 2, tuple(float(c) * 1.4 for c in self.color), -1, cv2.LINE_AA)
        buf = bloom(buf, 1.2, (2, 6, 16), (0.9, 0.5, 0.3))
        f += cv2.resize(buf, (W, H), interpolation=cv2.INTER_LINEAR) * a
        return f


# ============================================================================= supernova
class Shell(Layer):
    """Explosion : éclair puis coquille de gaz filamenteuse qui s'étend (t0 : début, r1 : rayon final)."""
    def __init__(self, center=(W / 2, H * 0.46), t0=0.4, r1=620, n=90000, seed=13, fade=None):
        self.__dict__.update(locals()); del self.__dict__['self']

    def setup(self, dur):
        rng = np.random.default_rng(self.seed)
        cl = rng.normal(0, 1, (260, 3)); cl /= np.linalg.norm(cl, axis=1, keepdims=True)
        k = rng.integers(0, 260, self.n)
        d = cl[k] + rng.normal(0, 0.09, (self.n, 3)) * rng.uniform(0.3, 1.6, self.n)[:, None]
        m = rng.random(self.n) < 0.25
        d[m] = rng.normal(0, 1, (m.sum(), 3))
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        self.d = d.astype(np.float32)
        self.v = rng.normal(1.0, 0.07, self.n).astype(np.float32) * np.where(m, 0.8, 1.0).astype(np.float32)
        hot = np.array([1.0, 0.85, 0.6], np.float32); oxy = np.array([0.4, 0.9, 1.0], np.float32); hyd = np.array([1.0, 0.35, 0.45], np.float32)
        pick = rng.random(self.n)
        self.col = np.where((pick < 0.4)[:, None], hyd, np.where((pick < 0.75)[:, None], oxy, hot)).astype(np.float32)

    def draw(self, f, t, dur):
        a = 1.0 if self.fade is None else float(kf(self.fade, t))
        tt = t - self.t0
        if a <= 0 or tt < -0.3:
            return f
        cx, cy = self.center
        if tt < 0.6:  # éclair
            fl = math.exp(-((tt - 0.05) / 0.18) ** 2)
            yy, xx = np.ogrid[0:H, 0:W]
            d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
            f += (np.exp(-d / 140) * fl * 1.6)[..., None] * np.array([1.0, 0.95, 0.85], np.float32) * a
        if tt > 0:
            k = 1 - math.exp(-tt / 2.2)
            P = self.d @ rot_y(t * 0.08).T * (self.v * k * self.r1)[:, None]
            buf = np.zeros((H // 2, W // 2, 3), np.float32)
            splat(buf, (cx + P[:, 0]) / 2, (cy - P[:, 1]) / 2, self.col * 0.12 * (1 - 0.5 * k))
            buf = cv2.GaussianBlur(buf, (0, 0), 0.9)
            buf = buf / (1 + buf * 0.5)
            buf = bloom(buf, 1.0, (3, 9, 24), (0.8, 0.5, 0.3))
            f += cv2.resize(buf, (W, H), interpolation=cv2.INTER_LINEAR) * a
        return f


# ============================================================================= point lumineux
class Halo(Layer):
    """Point lumineux (étoile, Terre vue de très loin) avec cercle optionnel."""
    def __init__(self, center=(W / 2, H * 0.47), color=(0.55, 0.75, 1.0), size=3.0, ring=0, fade=None, t_ring=0.4):
        self.__dict__.update(locals()); del self.__dict__['self']

    def draw(self, f, t, dur):
        a = 1.0 if self.fade is None else float(kf(self.fade, t))
        if a <= 0:
            return f
        cx, cy = self.center
        x0, x1, y0, y1 = int(max(0, cx - 200)), int(min(W, cx + 200)), int(max(0, cy - 200)), int(min(H, cy + 200))
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        glow = np.exp(-(d / self.size) ** 2) * 1.6 + np.exp(-d / (self.size * 6)) * 0.35
        f[y0:y1, x0:x1] += glow[..., None] * np.array(self.color, np.float32) * a
        if self.ring:
            k = smoothstep(self.t_ring, self.t_ring + 0.5, t)
            if k > 0:
                cv2.circle(f, (int(cx), int(cy)), int(self.ring + 30 * (1 - k)), (1.0 * k * a, 0.85 * k * a, 0.4 * k * a), 3, cv2.LINE_AA)
        return f


# ============================================================================= fond de nébuleuse
@functools.lru_cache(maxsize=8)
def _nebula_tex(seed, c1, c2):
    from common import fbm_noise
    h, w = H // 4, W // 4
    n1 = fbm_noise(h, w * 2, beta=2.6, seed=seed); n2 = fbm_noise(h, w * 2, beta=2.2, seed=seed + 1)
    m = np.clip((n1 - 0.45) * 2.2, 0, 1) ** 1.6
    col = (np.array(c1, np.float32) * (1 - n2[..., None]) + np.array(c2, np.float32) * n2[..., None]) * m[..., None]
    return col.astype(np.float32)


class Nebula(Layer):
    """Voile de nébuleuse très discret qui dérive (évite le noir total)."""
    def __init__(self, seed=1, c1=(0.16, 0.28, 0.75), c2=(0.6, 0.2, 0.65), amount=0.3, drift=6.0, fade=None):
        self.__dict__.update(locals()); del self.__dict__['self']

    def draw(self, f, t, dur):
        a = 1.0 if self.fade is None else float(kf(self.fade, t))
        if a <= 0:
            return f
        tex = _nebula_tex(self.seed, tuple(self.c1), tuple(self.c2))
        h, w2 = tex.shape[:2]; w = w2 // 2
        off = int(t * self.drift / 4) % w
        crop = tex[:, off:off + w]
        f += cv2.resize(crop, (W, H), interpolation=cv2.INTER_CUBIC) * self.amount * a
        return f


# ============================================================================= champ profond (galaxies lointaines)
class DeepField(Layer):
    """Des centaines de galaxies lointaines (ellipses lumineuses aux couleurs variées), en lent zoom avant."""
    def __init__(self, n=420, seed=17, zoom=(1.0, 1.25), fade=None):
        self.__dict__.update(locals()); del self.__dict__['self']

    def setup(self, dur):
        rng = np.random.default_rng(self.seed)
        n = self.n
        self.x = rng.uniform(-0.1, 1.1, n) * W; self.y = rng.uniform(-0.1, 1.1, n) * H
        self.size = (rng.pareto(1.6, n) + 1).clip(1, 14) * 3.2
        self.ax = rng.uniform(0.25, 1.0, n); self.ang = rng.uniform(0, 180, n)
        pal = np.array([(1.0, 0.85, 0.65), (0.95, 0.9, 1.0), (0.65, 0.75, 1.0), (1.0, 0.6, 0.45), (0.9, 0.7, 1.0)], np.float32)
        self.col = pal[rng.integers(0, len(pal), n)] * rng.uniform(0.5, 1.0, n)[:, None]
        self.dur = dur

    def draw(self, f, t, dur):
        a = 1.0 if self.fade is None else float(kf(self.fade, t))
        if a <= 0:
            return f
        z = lerp(self.zoom[0], self.zoom[1], min(1.0, t / max(dur, 1e-3)))
        buf = np.zeros((H // 2, W // 2, 3), np.float32)
        for x, y, sz, ax, ang, c in zip(self.x, self.y, self.size, self.ax, self.ang, self.col):
            X = (W / 2 + (x - W / 2) * z) / 2; Y = (H / 2 + (y - H / 2) * z) / 2
            r = sz * z / 2
            if X < -r or X > W / 2 + r or Y < -r or Y > H / 2 + r:
                continue
            cv2.ellipse(buf, (int(X * 16), int(Y * 16)), (max(1, int(r * 16)), max(1, int(r * ax * 16))), float(ang), 0, 360,
                        tuple(float(v) * 0.35 for v in c), -1, cv2.LINE_AA, 4)
            cv2.circle(buf, (int(X), int(Y)), max(1, int(r * 0.25)), tuple(float(v) * 1.2 for v in c), -1, cv2.LINE_AA)
        buf = cv2.GaussianBlur(buf, (0, 0), 1.2)
        buf = bloom(buf, 0.9, (2, 6, 16), (0.7, 0.4, 0.2))
        f += cv2.resize(buf, (W, H), interpolation=cv2.INTER_LINEAR) * a
        return f
