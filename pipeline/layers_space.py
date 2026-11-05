"""Couches « espace » : planètes, étoiles, trou noir, galaxies, toile cosmique, schémas..."""
import math, functools
import numpy as np
import cv2
from common import *
from layers_base import Layer, SpaceBG
import textures as T


def anim_pos(p0, p1, t, dur, ease=ease_in_out):
    if p1 is None:
        return p0
    k = ease(t / max(dur, 1e-3))
    return (lerp(p0[0], p1[0], k), lerp(p0[1], p1[1], k))


class Planet(Layer):
    def __init__(self, tex='earth', diameter=760, pos=(W / 2, 760), pos1=None, size1=None, spin=0.012, tilt=0.35,
                 light=(-0.65, -0.35, 0.68), atmo=(110, 170, 255), atmo_k=0.8, night=0.035, clouds=False,
                 cloud_spin=0.016, emissive=0.0, tint=None, alpha=1.0, glow_color=None, day_glow=0.0, t_offset=0.0, lights_off=None):
        self.__dict__.update(locals()); del self.__dict__['self']
    def setup(self, dur):
        if callable(self.tex):
            self.texture = self.tex()
        else:
            self.texture = {'earth': lambda: T.earth(), 'earth_frozen': lambda: T.earth(frozen=True),
                            'cobalt': lambda: T.gas_giant(1, 'cobalt'), 'jupiter': lambda: T.gas_giant(2, 'jupiter'),
                            'saturn': lambda: T.gas_giant(3, 'saturn'), 'venus': lambda: T.venus(),
                            'sun': lambda: T.sun(), 'moon': lambda: T.rocky(5, 'grey'), 'mars': lambda: T.rocky(6, 'red')}[self.tex]()
        if self.tint is not None:
            self.texture = self.texture * np.array(self.tint, np.float32)
        self.cl = T.clouds() if self.clouds else None
        self._grid_d = None
    def _grid(self, D):
        D = int(D)
        if self._grid_d == D:
            return
        self._grid_d = D
        M = int(D * 0.16) + 4
        S = D + 2 * M
        c = (np.arange(S, dtype=np.float32) - S / 2 + 0.5) / (D / 2)
        x, y = np.meshgrid(c, c)
        r = np.sqrt(x * x + y * y)
        z = np.sqrt(np.clip(1 - r * r, 0, 1))
        ct, st = math.cos(self.tilt), math.sin(self.tilt)
        xr = x * ct - y * st; yr = x * st + y * ct
        lat = np.arcsin(np.clip(-yr, -1, 1))
        lon = np.arctan2(xr, np.maximum(z, 1e-4))
        self.u0 = (lon / (2 * np.pi)).astype(np.float32)
        self.mv = ((0.5 - lat / np.pi) * (T.TH - 1)).astype(np.float32)
        L = np.array(self.light, np.float32); L /= np.linalg.norm(L)
        ndl = x * L[0] + y * L[1] + z * L[2]
        lit = smoothstep(-0.12, 0.35, ndl)
        self.shade = (self.night + (1 - self.night) * lit) * (0.78 + 0.22 * z)
        if self.emissive > 0:
            self.shade = self.shade * (1 - self.emissive) + self.emissive * (0.55 + 0.45 * z ** 0.5)
        self.alpha_m = np.clip((1 - r) * D / 2 + 0.5, 0, 1)
        side = np.clip((x * L[0] + y * L[1]) / np.maximum(r, 1e-3) * 0.7 + 0.45, 0, 1) if self.emissive == 0 else np.ones_like(r)
        rim_in = (1 - z) ** 2.2 * (0.25 + lit) * self.atmo_k
        out = np.exp(-np.maximum(r - 1, 0) * D / 2 / (M * 0.33)) * (r > 1) * side * self.atmo_k * 0.9
        self.atmo_in = rim_in.astype(np.float32)
        self.atmo_out = out.astype(np.float32)
        self.S = S
    def draw(self, f, t, dur):
        t = t + self.t_offset
        D = self.diameter if self.size1 is None else lerp(self.diameter, self.size1, ease_in_out(t / max(dur, 1e-3)))
        D = max(8, int(D))
        self._grid(D)
        cx, cy = anim_pos(self.pos, self.pos1, t, dur)
        mx = ((self.u0 + self.spin * t) % 1.0) * T.TW
        col = cv2.remap(self.texture, mx, self.mv, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        if self.cl is not None:
            mc = ((self.u0 + self.cloud_spin * t) % 1.0) * T.TW
            c = cv2.remap(self.cl, mc, self.mv, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)[..., None]
            col = col * (1 - c * 0.85) + c * 0.95
        ac = np.array(self.atmo, np.float32) / 255
        shade = self.shade; ain = self.atmo_in; aout_k = 1.0
        if self.lights_off is not None:
            lo = clamp01((t - self.lights_off) / 0.5)
            shade = shade * (1 - lo) + 0.025 * lo; ain = ain * (1 - lo) + ain * 0.08 * lo; aout_k = 1 - 0.9 * lo
        rgb = col * shade[..., None] + ain[..., None] * ac
        spr = np.dstack([rgb, self.alpha_m]).astype(np.float32)
        blit_rgba(f, spr, cx, cy, self.alpha)
        glow = np.dstack([np.broadcast_to(ac, rgb.shape), self.atmo_out * aout_k]).astype(np.float32)
        blit_rgba(f, glow, cx, cy, self.alpha, additive=True)
        if self.day_glow > 0:
            g = radial_glow(int(D * 2.2), self.glow_color or self.atmo, falloff=2.5)
            blit_rgba(f, g, cx, cy, self.day_glow * self.alpha, additive=True)
        return f


class Star(Layer):
    """Étoile / Soleil : disque granuleux + couronne."""
    def __init__(self, diameter=520, pos=(W / 2, 700), pos1=None, color=(255, 170, 60), corona=1.0, spin=0.01,
                 fade=None, size1=None, pulse=0.03, alpha=1.0):
        self.__dict__.update(locals()); del self.__dict__['self']
    def setup(self, dur):
        from layers_space import Planet
        self.disk = Planet(tex='sun', diameter=self.diameter, pos=self.pos, pos1=self.pos1, size1=self.size1,
                           spin=self.spin, tilt=0.1, light=(0, 0, 1), atmo=self.color, atmo_k=0.0, night=1.0, emissive=0.85)
        self.disk.setup(dur)
        s = 1024
        dx, dy = radial_grid(s, s)
        r = np.sqrt(dx * dx + dy * dy) / (s / 2)
        ang = np.arctan2(dy, dx)
        rays = 0.6 + 0.4 * np.abs(np.sin(ang * 7 + np.sin(ang * 3) * 2)) ** 3
        a = np.clip(1 - r, 0, 1) ** 2.4 * rays + np.clip(1 - r, 0, 1) ** 6
        self.corona_spr = np.dstack([np.broadcast_to(np.array(self.color, np.float32) / 255, (s, s, 3)), a]).astype(np.float32)
    def draw(self, f, t, dur):
        a = self.alpha
        if self.fade is not None:
            t0, t1 = self.fade
            a *= 1 - clamp01((t - t0) / max(t1 - t0, 1e-3))
        if a <= 0.001:
            return f
        D = self.diameter if self.size1 is None else lerp(self.diameter, self.size1, ease_in_out(t / max(dur, 1e-3)))
        cx, cy = anim_pos(self.pos, self.pos1, t, dur)
        pul = 1 + self.pulse * math.sin(t * 2.1)
        cs = scale_sprite(self.corona_spr, D * 3.2 * pul / 1024)
        blit_rgba(f, cs, cx, cy, 0.9 * self.corona * a, additive=True)
        self.disk.alpha = a
        self.disk.draw(f, t, dur)
        g = radial_glow(int(D * 1.6), (255, 230, 180), falloff=4)
        blit_rgba(f, g, cx, cy, 0.5 * a, additive=True)
        return f


class Glow(Layer):
    def __init__(self, pos=(W / 2, 760), size=400, color=(255, 255, 255), alpha=0.8, pulse=0.0, t0=0.0, t1=None, falloff=2.5, pos1=None):
        self.__dict__.update(locals()); del self.__dict__['self']
    def draw(self, f, t, dur):
        t1 = self.t1 if self.t1 is not None else 1e9
        if t < self.t0 or t > t1:
            return f
        a = self.alpha * min(1, (t - self.t0) / 0.3) * (1 + self.pulse * math.sin(t * 3))
        cx, cy = anim_pos(self.pos, self.pos1, t, dur)
        blit_rgba(f, radial_glow(int(self.size), self.color, self.falloff), cx, cy, a, additive=True)
        return f


# ----------------------------------------------------------------------------- trou noir
@functools.lru_cache(maxsize=2)
def _disk_tex(seed=0):
    th, tw = 256, 2048
    n = fbm_noise(th, tw, beta=2.0, seed=seed)
    streak = cv2.resize(cv2.resize(fbm_noise(th, tw, beta=1.6, seed=seed + 1), (tw, 32)), (tw, th), interpolation=cv2.INTER_CUBIC)
    r = np.linspace(0, 1, th, dtype=np.float32)[:, None]
    v = (0.55 * streak + 0.45 * n) * (1 - r) ** 0.6
    v *= smoothstep(0.0, 0.05, r) * (1 - smoothstep(0.75, 1.0, r))
    return v.astype(np.float32)


class BlackHole(Layer):
    def __init__(self, pos=(W / 2, 760), rs=118, incl=0.17, speed=0.12, palette='fire', lens_bg=True, size1=None, intensity=1.0):
        self.__dict__.update(locals()); del self.__dict__['self']
    def setup(self, dur):
        self.tex = _disk_tex()
        self._rs = None
    def _grid(self, rs):
        rs = int(rs)
        if self._rs == rs:
            return
        self._rs = rs
        hw = int(rs * 4.6); hh = int(rs * 3.0)
        xs = np.arange(-hw, hw, dtype=np.float32); ys = np.arange(-hh, hh, dtype=np.float32)
        x, y = np.meshgrid(xs, ys)
        self.box = (hw, hh)
        rin, rout = 1.6 * rs, 4.3 * rs
        si = max(self.incl, 0.05)
        xd, yd = x, y / si
        r = np.sqrt(xd * xd + yd * yd)
        th = np.arctan2(yd, xd)
        self.d_r = np.clip((r - rin) / (rout - rin), 0, 1) * 255
        self.d_th = (th / (2 * np.pi)) % 1.0
        self.d_valid = ((r >= rin) & (r <= rout)).astype(np.float32)
        self.d_rel = (rin / np.maximum(r, rin)) ** 1.5
        rho = np.sqrt(x * x + y * y)
        phi = np.arctan2(y, x)
        self.front = (y > 0).astype(np.float32)
        self.shadow = smoothstep(rs * 0.98, rs * 1.03, rho)
        # anneau lentillé (image de la face arrière du disque)
        k = 0.42 + 0.22 * np.abs(np.sin(phi))
        lr = (rho - rs * 1.04) / (k * (rout - rin) * 0.45)
        self.l_valid = ((lr >= 0) & (lr <= 1)).astype(np.float32) * (0.55 + 0.45 * np.abs(np.sin(phi)))
        self.l_r = np.clip(lr, 0, 1) * 255
        self.l_th = (phi / (2 * np.pi)) % 1.0
        self.ring = np.exp(-((rho - rs * 1.04) / (rs * 0.025)) ** 2)
        self.dopp = 1 + 0.75 * np.cos(th - np.pi)
        self.dopp_l = 1 + 0.5 * np.cos(phi - np.pi)
        if self.lens_bg:
            e2 = (rs * 1.5) ** 2
            rr = np.maximum(rho, 1)
            src = rr - e2 / rr
            self.lx = (x / rr * src).astype(np.float32); self.ly = (y / rr * src).astype(np.float32)
            edge = np.minimum(hw - np.abs(x), hh - np.abs(y))
            self.lens_m = smoothstep(rs * 0.9, rs * 1.3, rho) * smoothstep(0, rs * 0.9, edge) * (1 - smoothstep(rs * 2.0, rs * 2.9, rho))
    def draw(self, f, t, dur):
        rs = self.rs if self.size1 is None else lerp(self.rs, self.size1, ease_in_out(t / max(dur, 1e-3)))
        self._grid(rs)
        hw, hh = self.box
        cx, cy = int(self.pos[0]), int(self.pos[1])
        x0, y0 = cx - hw, cy - hh
        # découpe dans la frame
        fx0, fy0, fx1, fy1 = max(0, x0), max(0, y0), min(W, cx + hw), min(H, cy + hh)
        if fx1 <= fx0 or fy1 <= fy0:
            return f
        sl = (slice(fy0 - y0, fy1 - y0), slice(fx0 - x0, fx1 - x0))
        region = f[fy0:fy1, fx0:fx1]
        if self.lens_bg:
            mx = (self.lx[sl] + cx).astype(np.float32); my = (self.ly[sl] + cy).astype(np.float32)
            lensed = cv2.remap(f, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            m = self.lens_m[sl][..., None]
            region[:] = region * (1 - m) + lensed * m
        pal = np.array([[1.0, 0.55, 0.18], [1.0, 0.85, 0.6], [1.0, 1.0, 0.95]], np.float32) if self.palette == 'fire' else \
            np.array([[0.4, 0.6, 1.0], [0.7, 0.85, 1.0], [1.0, 1.0, 1.0]], np.float32)
        def colorize(v):
            v = np.clip(v, 0, None)
            return (pal[0] * np.clip(v * 2, 0, 1)[..., None] + pal[1] * np.clip(v * 2 - 0.6, 0, 1)[..., None] * 0.8 +
                    pal[2] * np.clip(v * 2 - 1.3, 0, 1)[..., None] * 1.5)
        TWd = self.tex.shape[1]
        mxd = ((self.d_th[sl] + self.speed * t * self.d_rel[sl]) % 1.0) * TWd
        disk = cv2.remap(self.tex, mxd.astype(np.float32), self.d_r[sl].astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        disk = disk * self.d_valid[sl] * self.dopp[sl] * 0.95 * self.intensity
        mxl = ((self.l_th[sl] - self.speed * t * 0.6) % 1.0) * TWd
        lens = cv2.remap(self.tex, mxl.astype(np.float32), self.l_r[sl].astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        lens = lens * self.l_valid[sl] * self.dopp_l[sl] * 1.25 * self.intensity
        sh = self.shadow[sl][..., None]
        fr = self.front[sl]
        back = colorize(disk * (1 - fr)) * sh
        region[:] = region * sh + back
        region += colorize(lens) * sh
        region += self.ring[sl][..., None] * np.array([1.0, 0.85, 0.6]) * 1.4 * self.intensity
        front = colorize(disk * fr)
        fa = np.clip(disk * fr * 3, 0, 1)[..., None]
        region[:] = region * (1 - fa * 0.85) + front
        glow = cv2.GaussianBlur(cv2.resize(region, (region.shape[1] // 4, region.shape[0] // 4)), (0, 0), 6)
        region += cv2.resize(glow, (region.shape[1], region.shape[0])) * 0.25
        return f


# ----------------------------------------------------------------------------- galaxies
@functools.lru_cache(maxsize=4)
def _galaxy_points(seed=0, n=60000, arms=2):
    rng = np.random.default_rng(seed)
    r = rng.exponential(0.42, n)
    r = r[r < 1.25][:n]
    n = len(r)
    arm = rng.integers(0, arms, n)
    pitch = 0.32
    th = np.log(r + 0.05) / math.tan(pitch) + arm * 2 * np.pi / arms + rng.normal(0, 0.16 + 0.4 * (r < 0.12), n)
    z = rng.normal(0, 0.03, n)
    col = np.where((r < 0.22)[:, None], [1.0, 0.85, 0.6], [0.6, 0.75, 1.0])
    pink = rng.random(n) < 0.04
    col[pink] = [1.0, 0.45, 0.7]
    w = rng.uniform(0.4, 1.0, n) * (1.0 + 0.6 * np.minimum(r, 1.0)) * np.where(r < 0.15, 0.35, 1.0)
    bulge = rng.normal(0, 0.09, (3000, 3))
    return r, th, z, col, w, bulge


class Galaxy(Layer):
    def __init__(self, pos=(W / 2, 760), size=900, incl=1.0, rot=0.06, seed=0, alpha=1.0, angle=-0.4, size1=None, pos1=None):
        self.__dict__.update(locals()); del self.__dict__['self']
    def render_sprite(self, t, size):
        r, th, z, col, w, bulge = _galaxy_points(self.seed)
        ang = th + self.rot * t / np.sqrt(r + 0.1)
        x = r * np.cos(ang); y = r * np.sin(ang)
        ca, sa = math.cos(self.angle), math.sin(self.angle)
        px = x * ca - y * sa; py = (x * sa + y * ca) * math.cos(self.incl) + z * math.sin(self.incl)
        bx, by = bulge[:, 0], bulge[:, 1] * math.cos(self.incl) * 0.8
        S = int(size / 2)
        img = np.zeros((S * S, 3), np.float32)
        def splat(xx, yy, ww, cc):
            ix = ((xx / 1.3) * S / 2 + S / 2).astype(int); iy = ((yy / 1.3) * S / 2 + S / 2).astype(int)
            ok = (ix >= 0) & (ix < S) & (iy >= 0) & (iy < S)
            idx = iy[ok] * S + ix[ok]
            for c in range(3):
                img[:, c] += np.bincount(idx, weights=(ww * cc[:, c])[ok], minlength=S * S)
        splat(px, py, w * 0.5, col)
        splat(bx, by, np.full(len(bx), 0.6), np.tile([[1.0, 0.85, 0.65]], (len(bx), 1)))
        img = img.reshape(S, S, 3)
        g = cv2.GaussianBlur(img, (0, 0), 0.8) * 0.5 + cv2.GaussianBlur(img, (0, 0), 4) * 1.2 + cv2.GaussianBlur(img, (0, 0), 14) * 2.0
        g = cv2.resize(g, (size, size), interpolation=cv2.INTER_LINEAR) * 0.35
        return g
    def draw(self, f, t, dur):
        size = int(self.size if self.size1 is None else lerp(self.size, self.size1, ease_in_out(t / max(dur, 1e-3))))
        g = self.render_sprite(t, size)
        a = np.clip(g.max(2, keepdims=True), 0, 1)
        spr = np.dstack([g, np.ones(g.shape[:2], np.float32)])
        cx, cy = anim_pos(self.pos, self.pos1, t, dur)
        blit_rgba(f, spr, cx, cy, self.alpha, additive=True)
        return f


class GalaxyRow(Layer):
    """Rangée de galaxies alignées qui s'enfonce en perspective (comparaison d'échelle)."""
    def __init__(self, n=14, t0=0.0, count_label=None):
        self.__dict__.update(locals()); del self.__dict__['self']
    def setup(self, dur):
        g = Galaxy(size=260, incl=1.15, seed=3).render_sprite(0, 260)
        self.spr = np.dstack([g, np.ones(g.shape[:2], np.float32)]).astype(np.float32)
    def draw(self, f, t, dur):
        k = ease_out((t - self.t0) / max(dur * 0.7, 1e-3))
        shown = int(self.n * k) + 1
        for i in range(min(shown, self.n) - 1, -1, -1):
            d = i / self.n
            s = 1.6 * (1 - d) ** 1.6 + 0.08
            x = W * 0.5 + (i * 0.0) ; y = 1150 - (1 - (1 - d) ** 1.4) * 700
            xx = lerp(W * 0.15, W * 0.5, 1 - (1 - d) ** 1.4)
            blit_rgba(f, scale_sprite(self.spr, s), xx + (i % 2) * 20, y, 0.9, additive=True)
        return f


# ----------------------------------------------------------------------------- toile cosmique
@functools.lru_cache(maxsize=2)
def _web_points(seed=4, void_r=0.5):
    rng = np.random.default_rng(seed)
    nodes = []
    while len(nodes) < 90:
        p = rng.uniform(-1.4, 1.4, 3)
        if np.linalg.norm(p) > void_r + 0.15:
            nodes.append(p)
    nodes = np.array(nodes)
    pts, wts = [], []
    from itertools import combinations
    d = np.linalg.norm(nodes[:, None] - nodes[None], axis=2)
    for i in range(len(nodes)):
        for j in np.argsort(d[i])[1:4]:
            a, b = nodes[i], nodes[j]
            # évite de traverser le vide
            ts = np.linspace(0, 1, 20)
            seg = a[None] + (b - a)[None] * ts[:, None]
            if np.min(np.linalg.norm(seg, axis=1)) < void_r:
                continue
            L = np.linalg.norm(b - a)
            m = int(L * 900)
            tt = rng.uniform(0, 1, m)
            p = a[None] + (b - a)[None] * tt[:, None] + rng.normal(0, 0.03, (m, 3))
            pts.append(p); wts.append(np.full(m, 0.5))
    for nd in nodes:
        m = 500
        pts.append(nd[None] + rng.normal(0, 0.06, (m, 3))); wts.append(np.full(m, 0.9))
    # les ~60 galaxies isolées dans le vide
    v = rng.normal(0, 1, (60, 3)); v = v / np.linalg.norm(v, axis=1, keepdims=True) * (rng.uniform(0, 1, (60, 1)) ** (1 / 3)) * void_r * 0.85
    P = np.concatenate(pts); Wt = np.concatenate(wts)
    return P.astype(np.float32), Wt.astype(np.float32), v.astype(np.float32)


class CosmicWeb(Layer):
    def __init__(self, rot=0.08, dist0=2.9, dist1=2.5, highlight_void=0.0, void_galaxies=True, color=(0.55, 0.65, 1.0), tilt=0.35):
        self.__dict__.update(locals()); del self.__dict__['self']
    def draw(self, f, t, dur):
        P, Wt, V = _web_points()
        ang = self.rot * t
        dist = lerp(self.dist0, self.dist1, ease_in_out(t / max(dur, 1e-3)))
        ca, sa = math.cos(ang), math.sin(ang)
        ct, st = math.cos(self.tilt), math.sin(self.tilt)
        def proj(Q):
            x = Q[:, 0] * ca + Q[:, 2] * sa; z = -Q[:, 0] * sa + Q[:, 2] * ca; y = Q[:, 1]
            y, z = y * ct - z * st, y * st + z * ct
            zz = z + dist
            ok = zz > 0.1
            sx = W / 2 + x / zz * 900; sy = 760 + y / zz * 900
            return sx, sy, zz, ok
        S = 2
        hw, hh = W // S, H // S
        img = np.zeros(hw * hh, np.float32)
        sx, sy, zz, ok = proj(P)
        ix = (sx / S).astype(int); iy = (sy / S).astype(int)
        ok &= (ix >= 0) & (ix < hw) & (iy >= 0) & (iy < hh)
        img += np.bincount(iy[ok] * hw + ix[ok], weights=(Wt / zz ** 1.5)[ok], minlength=hw * hh)
        img = img.reshape(hh, hw)
        g = cv2.GaussianBlur(img, (0, 0), 1.0) * 0.6 + cv2.GaussianBlur(img, (0, 0), 6) * 2.5
        g = cv2.resize(g, (W, H)) * 0.55
        col = np.array(self.color, np.float32)
        f += np.clip(g, 0, 3)[..., None] * col + np.clip(g - 1, 0, 3)[..., None] * np.array([0.6, 0.4, 0.2])
        if self.void_galaxies:
            vx, vy, vz, vok = proj(V)
            for x, y, z_, o in zip(vx, vy, vz, vok):
                if o:
                    blit_rgba(f, radial_glow(int(40 / z_ * 2), (255, 220, 170), 3, 0.1), x, y, 0.9, additive=True)
        if self.highlight_void > 0:
            c = (W / 2, 760)
            rr = 0.5 / dist * 900
            layer = np.zeros((H, W), np.float32)
            cv2.circle(layer, (int(c[0] * 4), int(c[1] * 4)), int(rr * 4), 1.0, 3, cv2.LINE_AA, 2)
            f += layer[..., None] * np.array([1.0, 0.8, 0.3]) * self.highlight_void * (0.6 + 0.4 * math.sin(t * 4))
        return f


# ----------------------------------------------------------------------------- particules spécifiques
class GlassRain(Layer):
    """Pluie de verre horizontale : traits lumineux rapides avec reflets."""
    def __init__(self, n=260, angle=-12, speed=2600, alpha=1.0, color=(190, 225, 255), seed=0, length=(60, 220)):
        self.__dict__.update(locals()); del self.__dict__['self']
    def setup(self, dur):
        rng = np.random.default_rng(self.seed)
        self.p = rng.uniform(0, 1, (self.n, 2)) * [W * 1.5, H]
        self.L = rng.uniform(*self.length, self.n)
        self.z = rng.uniform(0.3, 1.0, self.n)
        self.glint = rng.random(self.n) < 0.12
    def draw(self, f, t, dur):
        a = math.radians(self.angle)
        d = np.array([math.cos(a), math.sin(a)])
        layer = np.zeros((H, W), np.uint8)
        heads = []
        for (x, y), L, z, g in zip(self.p, self.L, self.z, self.glint):
            px = (x - self.speed * z * t) % (W * 1.5) - W * 0.25
            py = (y + self.speed * z * t * math.tan(-a) * 0.15) % H
            ex, ey = px + d[0] * L * z, py + d[1] * L * z
            cv2.line(layer, (int(px * 16), int(py * 16)), (int(ex * 16), int(ey * 16)), int(90 + 165 * z), max(1, int(3 * z)), cv2.LINE_AA, 4)
            if g:
                heads.append((px, py, z))
        lf = layer.astype(np.float32) / 255
        lf = lf + cv2.GaussianBlur(lf, (0, 0), 3) * 0.8
        f += lf[..., None] * (np.array(self.color, np.float32) / 255) * self.alpha
        for (x, y, z) in heads:
            blit_rgba(f, radial_glow(int(50 * z) + 6, (255, 255, 255), 3, 0.15), x, y, 0.8 * self.alpha, additive=True)
        return f


class CloudLayers(Layer):
    """Nuages défilant horizontalement (intérieur d'atmosphère)."""
    def __init__(self, palette='cobalt', speed=(260, 520, 900), seed=2, haze_color=(60, 120, 255)):
        self.__dict__.update(locals()); del self.__dict__['self']
    def setup(self, dur):
        pals = {'cobalt': [(0, (1, 3, 12)), (0.5, (6, 20, 70)), (0.8, (25, 70, 160)), (1, (110, 170, 245))],
                'venus': [(0, (60, 35, 10)), (0.5, (170, 120, 50)), (0.8, (230, 190, 110)), (1, (255, 240, 200))]}
        self.tex = []
        for i in range(3):
            n = fbm_noise(512, 1024, beta=2.4, seed=self.seed + i)
            n = cv2.resize(n, (W * 2, H), interpolation=cv2.INTER_CUBIC)
            self.tex.append(palette_map(n, pals[self.palette]))
    def draw(self, f, t, dur):
        acc = None
        for i, (tx, sp) in enumerate(zip(self.tex, self.speed)):
            off = int(sp * t) % (W * 2)
            if off + W <= W * 2:
                img = tx[:, off:off + W]
            else:
                img = np.concatenate([tx[:, off:], tx[:, :off + W - W * 2]], 1)
            acc = img if acc is None else acc * 0.5 + img * 0.65
        f[:] = acc
        return f


# ----------------------------------------------------------------------------- schémas
class Orbits(Layer):
    """Étoile centrale + orbites + planètes en mouvement."""
    def __init__(self, center=(W / 2, 760), orbits=(), star_size=120, star_color=(255, 200, 120), t0=0.0, tilt=0.35):
        # orbits : liste de dict(r=, period=, color=, label=, size=, dashed=False, phase=0)
        self.__dict__.update(locals()); del self.__dict__['self']
    def draw(self, f, t, dur):
        cx, cy = self.center
        u8 = np.zeros((H, W, 3), np.uint8)
        for o in self.orbits:
            r = o['r']
            col = tuple(int(c) for c in o.get('color', (120, 160, 255)))
            ry = r * self.tilt
            if o.get('dashed'):
                for a0 in range(0, 360, 10):
                    aa_ellipse(u8, (cx, cy), (r, ry), 0, a0, a0 + 5, col, 3)
            else:
                aa_ellipse(u8, (cx, cy), (r, ry), 0, 0, 360, col, 3)
        f += u8.astype(np.float32) / 255 * 0.8
        blit_rgba(f, radial_glow(int(self.star_size * 3), self.star_color, 2.5), cx, cy, 0.9, additive=True)
        blit_rgba(f, radial_glow(int(self.star_size), (255, 250, 230), 1.2, 0.45), cx, cy, 1.0, additive=True)
        for o in self.orbits:
            r = o['r']; ang = o.get('phase', 0) + 2 * np.pi * (t - self.t0) / o['period']
            x = cx + r * math.cos(ang); y = cy + r * self.tilt * math.sin(ang)
            sz = o.get('size', 26)
            spr = shaded_sphere(int(sz), tuple(o.get('pcolor', (90, 150, 255))), light=(-(x - cx) / (r + 1) * 0.8, -(y - cy) / (r * self.tilt + 1) * 0.8, 0.5))
            blit_rgba(f, spr, x, y)
            if o.get('label'):
                put_text(f, o['label'], x, y - sz - 40, fname='poppins_sb', size=40, color=(230, 235, 255), shadow=3)
        return f


class LightPath(Layer):
    """Schéma vertical Soleil → Terre avec impulsion lumineuse et chronomètre."""
    def __init__(self, sun_y=330, earth_y=1130, period=None, label=True):
        self.__dict__.update(locals()); del self.__dict__['self']
    def draw(self, f, t, dur):
        x = W / 2
        u8 = np.zeros((H, W, 3), np.uint8)
        for y in range(self.sun_y + 140, self.earth_y - 80, 28):
            cv2.line(u8, (int(x), y), (int(x), y + 12), (120, 140, 190), 3, cv2.LINE_AA)
        f += u8.astype(np.float32) / 255 * 0.7
        per = self.period or dur * 0.85
        k = clamp01(t / per)
        py = lerp(self.sun_y + 150, self.earth_y - 90, ease_in_out(k))
        blit_rgba(f, radial_glow(140, (255, 230, 150), 2.2, 0.15), x, py, 1.0, additive=True)
        tsec = 500 * ease_in_out(k)
        m, s = divmod(int(tsec), 60)
        put_text(f, f'{m:02d}:{s:02d}', x + 250, (self.sun_y + self.earth_y) / 2, fname='anton', size=170, color=(255, 225, 120), shadow=8)
        put_text(f, '150 millions de km', x - 250, (self.sun_y + self.earth_y) / 2, fname='poppins_xb', size=50, color=(220, 228, 245), shadow=5, max_width=330)
        return f


class GWMerger(Layer):
    """Deux étoiles à neutrons spiralant + ondes gravitationnelles en spirale, puis fusion (kilonova)."""
    def __init__(self, center=(W / 2, 760), merge_at=0.8):
        self.__dict__.update(locals()); del self.__dict__['self']
    def setup(self, dur):
        s = 2
        hw, hh = W // s, H // s
        yy, xx = np.mgrid[0:hh, 0:hw].astype(np.float32)
        dx = xx * s - self.center[0]; dy = yy * s - self.center[1]
        self.rho = np.sqrt(dx * dx + dy * dy); self.phi = np.arctan2(dy, dx)
    def draw(self, f, t, dur):
        tm = self.merge_at * dur
        cx, cy = self.center
        if t < tm:
            k = t / tm
            sep = 230 * (1 - k) ** 0.25 + 10
            ang = 2 * np.pi * (2.5 * (-(1 - k) ** 0.6 * 3 + 3))
            w = 0.04 + 0.12 * k ** 2
            wave = 0.5 + 0.5 * np.cos(2 * self.phi - self.rho * w + ang * 2)
            env = np.exp(-self.rho / 600) * smoothstep(sep * 0.6, sep * 1.5, self.rho)
            g = cv2.resize((wave * env).astype(np.float32), (W, H))
            f += g[..., None] * np.array([0.25, 0.4, 0.9]) * (0.4 + 0.6 * k)
            for sgn in (1, -1):
                x = cx + sgn * sep / 2 * math.cos(ang); y = cy + sgn * sep / 2 * math.sin(ang) * 0.9
                blit_rgba(f, radial_glow(150, (180, 210, 255), 2.4, 0.18), x, y, 1.0, additive=True)
                blit_rgba(f, radial_glow(50, (255, 255, 255), 1.0, 0.5), x, y, 1.0, additive=True)
        else:
            k = (t - tm) / max(dur - tm, 1e-3)
            blit_rgba(f, radial_glow(int(300 + 1400 * ease_out(k)), (255, 210, 160), 2.2, 0.1), cx, cy, 1.6 * (1 - k * 0.5), additive=True)
            ring = np.exp(-((self.rho - k * 900) / 25) ** 2)
            f += cv2.resize(ring.astype(np.float32), (W, H))[..., None] * np.array([0.6, 0.7, 1.0]) * (1 - k)
        return f


class NightSky(Layer):
    """Ciel nocturne vu du sol, avec des planètes qui s'éteignent l'une après l'autre."""
    def __init__(self, planets=(), seed=6, dark_k=1.0, clock=None):
        # planets : [(label, x, y, fade_t0, fade_t1, color)]
        self.__dict__.update(locals()); del self.__dict__['self']
    def setup(self, dur):
        rng = np.random.default_rng(self.seed)
        xs = np.linspace(0, 1, W)
        h = np.zeros(W)
        for o in range(1, 7):
            h += np.sin(xs * (2 + o * 3.1) * np.pi + rng.uniform(0, 6)) * (0.5 ** o)
        self.horizon = (1260 + h * 90).astype(int)
        mask = np.zeros((H, W), np.float32)
        for x in range(W):
            mask[self.horizon[x]:, x] = 1
        self.ground = cv2.GaussianBlur(mask, (0, 0), 1.2)[..., None]
    def draw(self, f, t, dur):
        f *= (1 - self.ground) * self.dark_k
        f += self.ground * np.array([0.01, 0.012, 0.02])
        for (lab, x, y, t0, t1, col) in self.planets:
            a = 1 - clamp01((t - t0) / max(t1 - t0, 1e-3))
            if a > 0:
                blit_rgba(f, radial_glow(150, col, 2.2, 0.25), x, y, a * (0.85 + 0.15 * math.sin(t * 5 + x)), additive=True)
                put_text(f, lab, x, y + 85, fname='poppins_xb', size=52, color=(220, 225, 240), alpha=a, shadow=3)
        return f


class Vent(Layer):
    """Source hydrothermale abyssale : cheminée, panache noir, lueur, vers tubicoles."""
    def __init__(self, seed=8):
        self.seed = seed
    def setup(self, dur):
        rng = np.random.default_rng(self.seed)
        self.bg = gradient_v(H, W, (2, 12, 26), (0, 2, 5))
        # cheminée
        m = np.zeros((H, W), np.uint8)
        pts = []
        for y in np.linspace(700, 1500, 30):
            k = (y - 700) / 800
            wdt = 60 + 160 * k ** 1.5 + rng.uniform(-14, 14)
            pts.append((W / 2 - wdt + rng.uniform(-8, 8), y))
        right = [(W - x + rng.uniform(-10, 10), y) for x, y in pts[::-1]]
        poly = np.array(pts + right + [(0, 1500), (0, H), (W, H), (W, 1500)], np.float32)
        poly = np.array(pts + right, np.float32)
        aa_poly(m, poly, 255)
        cv2.rectangle(m, (0, 1480), (W, H), 255, -1)
        n = fbm_noise(H, W, beta=2.0, seed=self.seed)
        rock = palette_map(n, [(0, (8, 6, 6)), (0.6, (30, 22, 18)), (1, (60, 45, 35))])
        self.mask = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 1.5)[..., None]
        self.rock = rock
        self.smoke = fbm_noise(1024, 512, beta=2.2, seed=self.seed + 1)
        self.worms = [(W / 2 + rng.uniform(-260, 260), rng.uniform(1380, 1480), rng.uniform(40, 90)) for _ in range(24)]
        yy, xx = np.mgrid[0:H // 2, 0:W // 2].astype(np.float32) * 2
        self.vy, self.vx = yy, xx
        n2 = fbm_noise(H, W, beta=1.6, seed=self.seed + 3)
        self.rock = self.rock * (0.7 + 0.6 * n2[..., None])
        dxg = (xx - W / 2); dyg = (yy - 720)
        rim = np.exp(-np.sqrt(dxg ** 2 + dyg ** 2) / 380)
        self.rim = cv2.resize(rim, (W, H))[..., None] * 0.45
        bx, by = (xx - 200), (yy + 100)
        ang = np.arctan2(bx, by)
        beam = np.exp(-((ang - 0.42) / 0.16) ** 2) * np.exp(-np.sqrt(bx ** 2 + by ** 2) / 1800)
        self.beam = cv2.resize(beam.astype(np.float32), (W, H))[..., None] * np.array([0.10, 0.22, 0.30])
    def draw(self, f, t, dur):
        f[:] = self.bg + self.beam
        # panache
        off = int(t * 120) % 1024
        sm = np.roll(self.smoke, off, axis=0)
        sm = cv2.resize(sm, (W // 2, H // 2))
        yy, xx = self.vy, self.vx
        width = 50 + (700 - np.minimum(yy, 700)) * 0.55
        cone = np.exp(-((xx - W / 2 - np.sin(yy * 0.01 + t) * 30) / width) ** 2) * (yy < 720)
        dens = cv2.resize((np.clip(sm * 1.4 - 0.2, 0, 1) * cone).astype(np.float32), (W, H))
        f[:] = f * (1 - dens[..., None] * 0.9) + dens[..., None] * np.array([0.02, 0.025, 0.03])
        f[:] = f * (1 - self.mask) + self.rock * self.mask * (1 + self.rim * np.array([2.2, 1.0, 0.3]))
        glow = radial_glow(500, (255, 120, 30), 2.4)
        blit_rgba(f, glow, W / 2, 720, 0.45 + 0.1 * math.sin(t * 3), additive=True)
        u8 = np.zeros((H, W, 3), np.uint8)
        for (x, y, L) in self.worms:
            sway = math.sin(t * 1.5 + x) * 8
            cv2.line(u8, (int(x), int(y)), (int(x + sway), int(y - L)), (200, 200, 190), 6, cv2.LINE_AA)
            cv2.circle(u8, (int(x + sway), int(y - L)), 9, (40, 40, 220), -1, cv2.LINE_AA)
        um = u8.astype(np.float32) / 255
        f[:] = np.where(um.sum(2, keepdims=True) > 0, um[..., ::-1] * 0.6, f)
        return f


class VenusSurface(Layer):
    """Paysage vénusien : ciel orange, dalles rocheuses, brume de chaleur. Option : lueur du Soleil qui se lève."""
    def __init__(self, seed=11, sun=None, labels=False, shimmer=True):
        self.__dict__.update(locals()); del self.__dict__['self']
    def setup(self, dur):
        rng = np.random.default_rng(self.seed)
        hz = 1000
        sky = gradient_v(hz, W, (120, 60, 15), (250, 175, 80))
        img = np.zeros((H, W, 3), np.float32)
        img[:hz] = sky
        xs = np.linspace(0, 1, W)
        for li, (base, amp, col) in enumerate([(930, 70, (200, 120, 55)), (965, 50, (160, 90, 40)), (1000, 35, (120, 65, 30))]):
            h = np.zeros(W)
            for o in range(1, 6):
                h += np.sin(xs * (1.5 + o * 2.7) * np.pi + rng.uniform(0, 6)) * amp * 0.55 ** o
            top = (base - h).astype(int)
            for x in range(W):
                img[top[x]:hz + 40, x] = np.array(col) / 255
        # sol en perspective
        tex = fbm_noise(512, 512, beta=1.8, seed=self.seed)
        r = ridged(fbm_noise(512, 512, beta=1.6, seed=self.seed + 1))
        g = tex * 0.6 + r * 0.4
        gy = np.arange(hz, H)
        depth = 300.0 / (gy - hz + 20)
        my = (depth * 2400) % 512
        mx = ((np.arange(W)[None, :] - W / 2) * depth[:, None] * 2.2) % 512
        samp = cv2.remap(g, mx.astype(np.float32), np.repeat(my[:, None], W, 1).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        ground = palette_map(samp, [(0, (40, 20, 8)), (0.5, (120, 70, 30)), (1, (210, 140, 70))])
        fog = np.clip(depth[:, None, None] * 1.1, 0, 1)
        ground = ground * (1 - fog * 0.6) + np.array([0.85, 0.55, 0.25]) * fog * 0.6
        img[hz:] = ground
        self.img = img.astype(np.float32)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        self.yy, self.xx = yy, xx
    def draw(self, f, t, dur):
        if self.shimmer:
            dy = (np.sin(self.yy * 0.05 + t * 6) * 1.8 * (self.yy > 900)).astype(np.float32)
            dx = (np.sin(self.yy * 0.031 + t * 4.3) * 1.5 * (self.yy > 900)).astype(np.float32)
            f[:] = cv2.remap(self.img, self.xx + dx, self.yy + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        else:
            f[:] = self.img
        if self.sun is not None:
            x0, x1 = self.sun
            k = ease_in_out(t / max(dur, 1e-3))
            sx = lerp(x0[0], x1[0], k); sy = lerp(x0[1], x1[1], k)
            blit_rgba(f, radial_glow(900, (255, 235, 180), 2.0), sx, sy, 0.7, additive=True)
        if self.labels:
            put_text(f, 'OUEST', 170, 1110, fname='anton', size=70, color=(255, 255, 255), shadow=6)
            put_text(f, 'EST', W - 150, 1110, fname='anton', size=70, color=(255, 255, 255), shadow=6)
        return f


class CloudSea(Layer):
    """Mer de nuages vénusiens vue à 50 km d'altitude."""
    def __init__(self, seed=13, speed=0.06):
        self.seed = seed; self.speed = speed
    def setup(self, dur):
        self.tex = fbm_noise(1024, 1024, beta=2.3, seed=self.seed)
        self.hz = 720
        gy = np.arange(self.hz, H, dtype=np.float32)
        self.depth = 220.0 / (gy - self.hz + 12)
        self.mx0 = ((np.arange(W, dtype=np.float32)[None, :] - W / 2) * self.depth[:, None] * 1.6)
        self.my0 = np.repeat((self.depth * 900)[:, None], W, 1).astype(np.float32)
        self.sky = gradient_v(self.hz, W, (190, 140, 60), (255, 235, 180))
    def draw(self, f, t, dur):
        f[:self.hz] = self.sky
        mx = ((self.mx0 + t * 60) % 1024).astype(np.float32)
        my = ((self.my0 - t * self.speed * 2000) % 1024).astype(np.float32)
        s = cv2.remap(self.tex, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        c = palette_map(s, [(0, (150, 100, 40)), (0.5, (225, 180, 105)), (1, (255, 245, 215))])
        fog = np.clip(self.depth[:, None, None] * 1.4, 0, 1)
        c = c * (1 - fog) + np.array([1.0, 0.92, 0.72]) * fog
        f[self.hz:] = c
        return f


class Airship(Layer):
    def __init__(self, pos=(W / 2, 640), size=520, t0=0.0):
        self.__dict__.update(locals()); del self.__dict__['self']
    def setup(self, dur):
        w, h = self.size, int(self.size * 0.42)
        spr = np.zeros((h + 120, w + 40, 4), np.float32)
        cx, cy = (w + 40) / 2, h / 2 + 10
        yy, xx = np.mgrid[0:spr.shape[0], 0:spr.shape[1]].astype(np.float32)
        e = ((xx - cx) / (w / 2)) ** 2 + ((yy - cy) / (h / 2)) ** 2
        body = e <= 1
        shade = np.clip(1 - ((yy - cy + h * 0.25) / h) ** 2 * 1.2, 0.2, 1)
        spr[body, :3] = (np.array([0.92, 0.9, 0.86]) * shade[body, None])
        spr[body, 3] = 1
        for i in range(-3, 4):
            band = np.abs(xx - cx - i * w / 8) < 2
            spr[body & band, :3] *= 0.85
        g = np.zeros_like(spr[..., 0])
        cv2.rectangle(g, (int(cx - w * 0.14), int(cy + h / 2 + 8)), (int(cx + w * 0.14), int(cy + h / 2 + 50)), 1.0, -1)
        spr[g > 0, :3] = [0.35, 0.36, 0.4]; spr[g > 0, 3] = 1
        for k in range(5):
            x = int(cx - w * 0.11 + k * w * 0.055)
            spr[int(cy + h / 2 + 22):int(cy + h / 2 + 34), x:x + 10, :3] = [1.0, 0.85, 0.5]
        pts = np.array([(cx + w / 2 - 30, cy), (cx + w / 2 + 15, cy - h * 0.45), (cx + w / 2 - 70, cy)], np.float32)
        ff = np.zeros_like(g); aa_poly(ff, pts, 1.0)
        spr[ff > 0, :3] = [0.75, 0.72, 0.7]; spr[ff > 0, 3] = 1
        self.spr = spr
    def draw(self, f, t, dur):
        lt = t - self.t0
        if lt < 0:
            return f
        x = self.pos[0] - 60 + lt * 25; y = self.pos[1] + 12 * math.sin(lt * 1.2)
        blit_rgba(f, self.spr, x, y, min(1, lt / 0.6))
        return f


class Thermometer(Layer):
    def __init__(self, vmax=465, marks=((0, '0 °C'), (100, '100 °C'), (327, 'Le plomb fond'), (465, '465 °C')), x=190, y0=1120, y1=470):
        self.__dict__.update(locals()); del self.__dict__['self']
    def draw(self, f, t, dur):
        k = ease_out(t / max(dur * 0.7, 1e-3))
        v = self.vmax * k
        u8 = np.zeros((H, W, 3), np.uint8)
        cv2.rectangle(u8, (self.x - 38, self.y1 - 30), (self.x + 38, self.y0), (70, 70, 80), -1, cv2.LINE_AA)
        cv2.circle(u8, (self.x, self.y0 + 55), 86, (70, 70, 80), -1, cv2.LINE_AA)
        m = (u8.sum(2, keepdims=True) > 0)
        f[:] = np.where(m, u8.astype(np.float32) / 255, f)
        yv = int(lerp(self.y0, self.y1, v / self.vmax))
        col = np.array([1.0, 0.25 + 0.45 * (1 - k), 0.08])
        f[yv:self.y0 + 10, self.x - 24:self.x + 24] = col
        aa_circle(f, (self.x, self.y0 + 55), 66, tuple(col))
        for val, lab in self.marks:
            yy = int(lerp(self.y0, self.y1, val / self.vmax))
            f[yy - 3:yy + 3, self.x + 46:self.x + 100] = 1.0
            hit = v >= val
            spr = text_sprite(lab, 'poppins_xb', 54, (255, 220, 120) if hit else (235, 235, 235), 0, (0, 0, 0), None, 5)
            blit_rgba(f, spr, self.x + 120 + spr.shape[1] / 2, yy)
        put_text(f, f'{int(v)} °C', W / 2 + 40, 300, fname='anton', size=170, color=(255, 120, 60), shadow=10)
        return f


class DepthGauge(Layer):
    def __init__(self, depth=900):
        self.depth = depth
    def draw(self, f, t, dur):
        k = ease_in_out(t / max(dur * 0.8, 1e-3))
        f[:] = gradient_v(H, W, (20, 120, 190), (0, 5, 20))
        cur = self.depth * k
        for d in range(0, self.depth + 1, 150):
            y = int(250 + d / self.depth * 950)
            f[y - 1:y + 2, 120:220] = 0.8
            put_text(f, f'{d} m', 300, y, fname='poppins_sb', size=40, color=(220, 235, 255), shadow=3)
        y = 250 + cur / self.depth * 950
        blit_rgba(f, shaded_sphere(36, (255, 200, 60)), 170, y)
        put_text(f, f'-{int(cur)} m', 760, 640, fname='anton', size=170, color=(255, 255, 255), shadow=10)
        put_text(f, '= 92 bars', 760, 800, fname='poppins_xb', size=70, color=(255, 210, 110), shadow=6)
        return f


class JWST(Layer):
    """Miroir hexagonal doré stylisé (18 segments) avec reflet balayant."""
    def __init__(self, pos=(W / 2, 760), size=110):
        self.__dict__.update(locals()); del self.__dict__['self']
    def draw(self, f, t, dur):
        cx, cy = self.pos
        s = self.size
        cells = []
        for q in range(-2, 3):
            for r in range(-2, 3):
                if abs(q + r) <= 2 and not (q == 0 and r == 0):
                    x = cx + s * 1.5 * q; y = cy + s * math.sqrt(3) * (r + q / 2)
                    cells.append((x, y))
        u8 = np.zeros((H, W, 3), np.uint8)
        sweep = (t * 0.6) % 2.0 - 0.5
        for (x, y) in cells:
            pts = [(x + s * 0.95 * math.cos(a), y + s * 0.95 * math.sin(a)) for a in np.linspace(0, 2 * np.pi, 7)[:-1]]
            k = (x - (W / 2 - 400)) / 800
            b = 0.55 + 0.45 * math.exp(-((k - sweep) * 4) ** 2) + 0.1 * math.sin(x * 0.01 + y * 0.02)
            col = (int(40 * b), int(170 * b), int(240 * min(b, 1.06)))
            aa_poly(u8, pts, col)
        f[:] = f * (1 - (u8.sum(2, keepdims=True) > 0)) + u8[..., ::-1].astype(np.float32) / 255 * 1.1
        for a in (90, 210, 330):
            ar = math.radians(a)
            aa = np.zeros((H, W, 3), np.uint8)
            cv2.line(aa, (int(cx), int(cy)), (int(cx + 520 * math.cos(ar)), int(cy - 520 * math.sin(ar) * 0.4 - 300)), (150, 150, 160), 4, cv2.LINE_AA)
            f += aa.astype(np.float32) / 255 * 0.5
        blit_rgba(f, shaded_sphere(30, (200, 200, 210)), cx, cy - 300)
        return f


class Prism(Layer):
    """Lumière d'étoile décomposée en spectre, avec mise en évidence du bleu."""
    def __init__(self, highlight_blue=True, t_hl=1.2):
        self.__dict__.update(locals()); del self.__dict__['self']
    def draw(self, f, t, dur):
        pc = (W / 2 - 80, 760)
        u8 = np.zeros((H, W, 3), np.uint8)
        k = ease_out(t / 0.8)
        cv2.line(u8, (40, 900), (int(lerp(40, pc[0], k)), int(lerp(900, pc[1], k))), (255, 255, 255), 10, cv2.LINE_AA)
        f += cv2.GaussianBlur(u8.astype(np.float32) / 255, (0, 0), 3) * 1.2 + u8.astype(np.float32) / 255
        tri = [(pc[0], pc[1] - 200), (pc[0] - 170, pc[1] + 120), (pc[0] + 170, pc[1] + 120)]
        m = np.zeros((H, W), np.uint8); aa_poly(m, tri, 255)
        mf = m.astype(np.float32)[..., None] / 255
        f[:] = f * (1 - mf * 0.5) + mf * np.array([0.5, 0.6, 0.7]) * 0.35
        if t > 0.7:
            kk = ease_out((t - 0.7) / 0.6)
            cols = [(255, 40, 40), (255, 140, 0), (255, 240, 0), (40, 220, 60), (40, 120, 255), (130, 40, 255)]
            for i, c in enumerate(cols):
                ang = math.radians(-14 + i * 6)
                L = 560 * kk
                p0 = (pc[0] + 90, pc[1])
                p1 = (p0[0] + L * math.cos(ang), p0[1] + L * math.sin(ang))
                lay = np.zeros((H, W, 3), np.uint8)
                cv2.line(lay, (int(p0[0]), int(p0[1])), (int(p1[0]), int(p1[1])), c[::-1], 26, cv2.LINE_AA)
                inten = 1.0
                if self.highlight_blue and t > self.t_hl:
                    inten = 1.6 if i == 4 else 0.35
                f += lay[..., ::-1].astype(np.float32) / 255 * inten * 0.8
        return f


class GlassShards(Layer):
    def __init__(self, n=26, seed=1):
        self.n = n; self.seed = seed
    def setup(self, dur):
        rng = np.random.default_rng(self.seed)
        self.sh = []
        for _ in range(self.n):
            k = rng.integers(4, 7)
            ang = np.sort(rng.uniform(0, 2 * np.pi, k))
            rad = rng.uniform(0.5, 1.0, k)
            pts = np.stack([np.cos(ang) * rad, np.sin(ang) * rad], 1)
            self.sh.append(dict(pts=pts, x=rng.uniform(-200, W + 200), y=rng.uniform(250, 1300), s=rng.uniform(20, 120),
                                rot=rng.uniform(-2, 2), flip=rng.uniform(0.5, 2.5), ph=rng.uniform(0, 6), v=rng.uniform(150, 600)))
    def draw(self, f, t, dur):
        lay = np.zeros((H, W, 3), np.float32)
        for s in self.sh:
            x = (s['x'] - s['v'] * t) % (W + 400) - 200
            a = s['rot'] * t + s['ph']; fl = math.cos(s['flip'] * t + s['ph'])
            R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
            p = (s['pts'] * [abs(fl) + 0.1, 1]) @ R.T * s['s'] + [x, s['y']]
            m = np.zeros((H, W), np.uint8)
            aa_poly(m, p, 255)
            b = 0.35 + 0.65 * abs(fl)
            mm = m.astype(np.float32)[..., None] / 255
            lay += mm * np.array([0.55, 0.8, 1.0]) * 0.35 * b
            e = np.zeros((H, W), np.uint8)
            aa_poly(e, p, 255, thickness=2)
            lay += e.astype(np.float32)[..., None] / 255 * np.array([0.8, 0.95, 1.0]) * b
        f += lay + cv2.GaussianBlur(lay, (0, 0), 6) * 0.6
        return f


class Molecule(Layer):
    """Molécule 3D tournante (sphères ombrées). atoms : [(element, (x,y,z))]."""
    COLORS = {'S': (240, 210, 40), 'H': (235, 235, 240), 'C': (70, 70, 75), 'O': (230, 50, 40)}
    RADII = {'S': 120, 'H': 62, 'C': 95, 'O': 105}
    def __init__(self, atoms, pos=(W / 2, 760), scale=210, spin=0.6, label=None, wobble=False):
        self.__dict__.update(locals()); del self.__dict__['self']
    def draw(self, f, t, dur):
        a = self.spin * t if not self.wobble else 0.55 * math.sin(t * 0.9)
        ca, sa = math.cos(a), math.sin(a)
        pts = []
        for el, (x, y, z) in self.atoms:
            X = x * ca + z * sa; Z = -x * sa + z * ca
            pts.append((Z, el, self.pos[0] + X * self.scale, self.pos[1] + y * self.scale, 1 + Z * 0.15))
        cen = pts[0]
        u8 = np.zeros((H, W, 3), np.uint8)
        for p in pts[1:]:
            cv2.line(u8, (int(cen[2]), int(cen[3])), (int(p[2]), int(p[3])), (200, 200, 200), 26, cv2.LINE_AA)
        f[:] = f * (1 - (u8.sum(2, keepdims=True) > 0) * 0.9) + u8.astype(np.float32) / 255 * 0.55
        for Z, el, x, y, s in sorted(pts, key=lambda p: p[0]):
            blit_rgba(f, shaded_sphere(int(self.RADII[el] * s), self.COLORS[el]), x, y)
        if self.label:
            put_text(f, self.label, self.pos[0], self.pos[1] + 330, fname='anton', size=110, color=(255, 255, 255), shadow=8)
        return f


@functools.lru_cache(maxsize=2)
def astronaut_sprite(h=360):
    w = int(h * 0.55)
    spr = np.zeros((h, w, 4), np.float32)
    m = np.zeros((h, w), np.uint8)
    cx = w // 2
    cv2.circle(m, (cx, int(h * 0.13)), int(h * 0.11), 255, -1, cv2.LINE_AA)
    cv2.rectangle(m, (cx - int(w * 0.28), int(h * 0.24)), (cx + int(w * 0.28), int(h * 0.58)), 255, -1, cv2.LINE_AA)
    cv2.line(m, (cx - int(w * 0.28), int(h * 0.3)), (cx - int(w * 0.45), int(h * 0.52)), 255, int(w * 0.16), cv2.LINE_AA)
    cv2.line(m, (cx + int(w * 0.28), int(h * 0.3)), (cx + int(w * 0.45), int(h * 0.52)), 255, int(w * 0.16), cv2.LINE_AA)
    cv2.line(m, (cx - int(w * 0.13), int(h * 0.58)), (cx - int(w * 0.16), int(h * 0.92)), 255, int(w * 0.2), cv2.LINE_AA)
    cv2.line(m, (cx + int(w * 0.13), int(h * 0.58)), (cx + int(w * 0.16), int(h * 0.92)), 255, int(w * 0.2), cv2.LINE_AA)
    a = m.astype(np.float32) / 255
    xx = np.linspace(-1, 1, w)[None, :]
    shade = 0.75 + 0.25 * np.cos(xx * 1.4)
    spr[..., :3] = np.array([0.93, 0.93, 0.95]) * shade[..., None]
    v = np.zeros((h, w), np.uint8)
    cv2.ellipse(v, (cx, int(h * 0.135)), (int(h * 0.075), int(h * 0.05)), 0, 0, 360, 255, -1, cv2.LINE_AA)
    vm = v > 0
    spr[vm, :3] = [0.95, 0.65, 0.2]
    spr[..., 3] = a
    return spr


class Astronaut(Layer):
    def __init__(self, pos=(W / 2, 760), pos1=None, stretch=(1.0, 1.0), angle=0.0, redshift=(0.0, 0.0), fade=(1.0, 1.0), size=360, spin=0.0):
        self.__dict__.update(locals()); del self.__dict__['self']
    def draw(self, f, t, dur):
        k = ease_in(t / max(dur, 1e-3))
        st = lerp(self.stretch[0], self.stretch[1], k)
        spr = astronaut_sprite(self.size).copy()
        rs = lerp(self.redshift[0], self.redshift[1], k)
        if rs > 0:
            spr[..., :3] = spr[..., :3] * (1 - rs) + spr[..., :3].mean(2, keepdims=True) * np.array([1.0, 0.25, 0.15]) * rs
        h, w = spr.shape[:2]
        spr = cv2.resize(spr, (max(2, int(w / st ** 0.5)), max(2, int(h * st))), interpolation=cv2.INTER_LINEAR)
        ang = self.angle + self.spin * t
        if ang:
            S = int(max(spr.shape[:2]) * 1.2)
            M = cv2.getRotationMatrix2D((spr.shape[1] / 2, spr.shape[0] / 2), ang, 1)
            M[0, 2] += (S - spr.shape[1]) / 2; M[1, 2] += (S - spr.shape[0]) / 2
            spr = cv2.warpAffine(spr, M, (S, S))
        cx, cy = anim_pos(self.pos, self.pos1, t, dur, ease=ease_in)
        blit_rgba(f, spr, cx, cy, lerp(self.fade[0], self.fade[1], k))
        return f


class Clocks(Layer):
    """Deux horloges : la tienne (normale) et celle vue par l'observateur (ralentit)."""
    def __init__(self, labels=('Toi', 'Ton ami te voit'), y=700):
        self.labels = labels; self.y = y
    def draw(self, f, t, dur):
        for i, (lab, x) in enumerate(zip(self.labels, (W * 0.28, W * 0.72))):
            if i == 0:
                ang = t * 2.0
            else:
                k = t / max(dur, 1e-3)
                ang = 2.0 * dur * (1 - (1 - k) ** 0.25) * 0.5 if k < 1 else 2.0 * dur * 0.5
            u8 = np.zeros((H, W, 3), np.uint8)
            cv2.circle(u8, (int(x), self.y), 170, (40, 40, 50), -1, cv2.LINE_AA)
            cv2.circle(u8, (int(x), self.y), 170, (220, 220, 230), 6, cv2.LINE_AA)
            for k_ in range(12):
                a = k_ * np.pi / 6
                cv2.line(u8, (int(x + 140 * math.sin(a)), int(self.y - 140 * math.cos(a))), (int(x + 158 * math.sin(a)), int(self.y - 158 * math.cos(a))), (220, 220, 230), 5, cv2.LINE_AA)
            col = (90, 120, 255) if i == 1 else (230, 230, 240)
            cv2.line(u8, (int(x), self.y), (int(x + 130 * math.sin(ang)), int(self.y - 130 * math.cos(ang))), col, 8, cv2.LINE_AA)
            cv2.line(u8, (int(x), self.y), (int(x + 85 * math.sin(ang / 12)), int(self.y - 85 * math.cos(ang / 12))), (230, 230, 240), 10, cv2.LINE_AA)
            m = (u8.sum(2, keepdims=True) > 0).astype(np.float32)
            f[:] = f * (1 - m * 0.9) + u8[..., ::-1].astype(np.float32) / 255
            put_text(f, lab, x, self.y + 240, fname='poppins_sb', size=44, color=(230, 235, 245), shadow=4)
        return f


class SpacetimeGrid(Layer):
    """Grille d'espace-temps en perspective, creusée par une masse ; ondes qui se propagent."""
    def __init__(self, depth=3.2, waves=0.0, mass_glow=(255, 210, 140), cy=820, color=(255, 160, 90)):
        self.__dict__.update(locals()); del self.__dict__['self']
        if self.depth > 20:
            self.depth = self.depth / 80.0
    def draw(self, f, t, dur):
        cam = np.array([0.0, 7.5, -15.0])
        pitch = math.atan2(7.5, 15.0) + 0.05
        cp, sp_ = math.cos(pitch), math.sin(pitch)
        def proj(X, Z):
            r = np.sqrt(X * X + Z * Z)
            Y = -self.depth * np.exp(-(r / 2.4) ** 2)
            if self.waves:
                Y = Y + self.waves * 0.35 * np.sin(r * 1.6 - t * 4.0) * np.exp(-r / 9) * smoothstep(1.0, 3.0, r)
            x, y, z = X - cam[0], Y - cam[1], Z - cam[2]
            y2 = y * cp + z * sp_; z2 = -y * sp_ + z * cp
            z2 = np.maximum(z2, 0.5)
            return W / 2 + x / z2 * 1100, self.cy - y2 / z2 * 1100
        u8 = np.zeros((H, W, 3), np.uint8)
        g = np.linspace(-12, 12, 25); fine = np.linspace(-12, 12, 120)
        col = tuple(int(c) for c in self.color[::-1])
        for k in g:
            for X, Z in ((np.full_like(fine, k), fine), (fine, np.full_like(fine, k))):
                sx, sy = proj(X, Z)
                pts = (np.stack([sx, sy], 1) * 16).astype(np.int32).reshape(-1, 1, 2)
                cv2.polylines(u8, [pts], False, col, 2, cv2.LINE_AA, 4)
        gg = u8[..., ::-1].astype(np.float32) / 255
        f += gg * 0.75 + cv2.GaussianBlur(gg, (0, 0), 4) * 0.5
        mx, my = proj(np.array([0.0]), np.array([0.0]))
        blit_rgba(f, radial_glow(300, self.mass_glow, 2.0, 0.22), mx[0], my[0] - 60, 1.0, additive=True)
        blit_rgba(f, shaded_sphere(46, self.mass_glow, light=(0, 0, 1), spec=0.0), mx[0], my[0] - 60, 1.0)
        return f


class Constellation(Layer):
    def __init__(self, stars, lines, name='', y_off=0, t0=0.2):
        self.__dict__.update(locals()); del self.__dict__['self']
    def draw(self, f, t, dur):
        k = ease_out((t - self.t0) / 1.2)
        u8 = np.zeros((H, W, 3), np.uint8)
        for (a, b) in self.lines:
            p, q = self.stars[a], self.stars[b]
            e = (p[0] + (q[0] - p[0]) * k, p[1] + (q[1] - p[1]) * k)
            aa_line(u8, p, e, (150, 190, 255), 3)
        f += u8.astype(np.float32) / 255 * 0.8
        for (x, y) in self.stars:
            blit_rgba(f, radial_glow(70, (220, 230, 255), 2.4, 0.2), x, y, 1.0, additive=True)
        if self.name:
            put_text(f, self.name, W / 2, 1180, fname='anton', size=90, color=(220, 230, 255), alpha=k, shadow=6)
        return f


class Tunnel(Layer):
    """Toutes les trajectoires convergent vers le centre (intérieur du trou noir)."""
    def __init__(self, n=160, seed=3, color=(255, 170, 90)):
        self.__dict__.update(locals()); del self.__dict__['self']
    def setup(self, dur):
        rng = np.random.default_rng(self.seed)
        self.a = rng.uniform(0, 2 * np.pi, self.n); self.ph = rng.uniform(0, 1, self.n); self.sp = rng.uniform(0.4, 1.0, self.n)
    def draw(self, f, t, dur):
        u8 = np.zeros((H, W), np.uint8)
        cx, cy = W / 2, 760
        for a, ph, sp in zip(self.a, self.ph, self.sp):
            k = 1 - ((ph + t * sp * 0.6) % 1.0)
            r1 = 60 + k ** 2 * 1300; r0 = r1 * 0.75
            p0 = (cx + r0 * math.cos(a), cy + r0 * math.sin(a)); p1 = (cx + r1 * math.cos(a), cy + r1 * math.sin(a))
            aa_line(u8, p0, p1, int(255 * min(1, k * 1.5)), 3)
        g = u8.astype(np.float32) / 255
        f += (g + cv2.GaussianBlur(g, (0, 0), 5))[..., None] * np.array(self.color, np.float32) / 255
        blit_rgba(f, radial_glow(300, (0, 0, 0), 1.0, 0.6), cx, cy, 1.0)
        return f


class Lander(Layer):
    """Sonde type Venera stylisée posée au sol."""
    def __init__(self, pos=(W / 2, 1180), size=300):
        self.pos = pos; self.size = size
    def draw(self, f, t, dur):
        cx, cy = self.pos; s = self.size
        u8 = np.zeros((H, W, 3), np.uint8)
        cv2.ellipse(u8, (int(cx), int(cy)), (int(s * 0.55), int(s * 0.14)), 0, 0, 360, (90, 90, 95), -1, cv2.LINE_AA)
        cv2.rectangle(u8, (int(cx - s * 0.18), int(cy - s * 0.45)), (int(cx + s * 0.18), int(cy - s * 0.05)), (170, 170, 175), -1, cv2.LINE_AA)
        cv2.circle(u8, (int(cx), int(cy - s * 0.55)), int(s * 0.2), (200, 200, 205), -1, cv2.LINE_AA)
        cv2.ellipse(u8, (int(cx), int(cy - s * 0.78)), (int(s * 0.32), int(s * 0.06)), 0, 0, 360, (140, 140, 150), -1, cv2.LINE_AA)
        cv2.line(u8, (int(cx), int(cy - s * 0.84)), (int(cx), int(cy - s * 1.05)), (200, 200, 205), 6, cv2.LINE_AA)
        m = (u8.sum(2, keepdims=True) > 0).astype(np.float32)
        lit = np.array([1.0, 0.8, 0.55])
        f[:] = f * (1 - m) + u8.astype(np.float32) / 255 * lit * m
        return f
