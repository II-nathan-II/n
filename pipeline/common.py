"""Utilitaires partagés : constantes, bruit procédural, dessin, texte, compositing."""
import os, math, functools
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
SR = 48000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.environ.get('TT_ASSETS', '/opt/assets')
FONTS = os.path.join(ASSETS, 'fonts')
WORK = os.environ.get('TT_WORK', os.path.join(ROOT, '.work'))
PROJECT = os.path.join(ROOT, 'TikTok_Viral_Project')

FONT_FILES = {
    'anton': 'Anton-Regular.ttf',
    'bebas': 'BebasNeue-Regular.ttf',
    'poppins_black': 'Poppins-Black.ttf',
    'poppins_xb': 'Poppins-ExtraBold.ttf',
    'poppins_sb': 'Poppins-SemiBold.ttf',
    'montserrat': 'Montserrat[wght].ttf',
    'orbitron': 'Orbitron[wght].ttf',
    'archivo': 'ArchivoBlack-Regular.ttf',
    'serif': 'DMSerifDisplay-Regular.ttf',
}


# ----------------------------------------------------------------------------- easing
def clamp01(x):
    return max(0.0, min(1.0, x))

def ease_in_out(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)

def ease_out(x):
    x = clamp01(x)
    return 1 - (1 - x) ** 3

def ease_in(x):
    x = clamp01(x)
    return x ** 3

def ease_out_back(x, s=1.70158):
    x = clamp01(x) - 1
    return x * x * ((s + 1) * x + s) + 1

def lerp(a, b, t):
    return a + (b - a) * t

def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-9), 0, 1)
    return t * t * (3 - 2 * t)


# ----------------------------------------------------------------------------- noise
def fbm_noise(h, w, beta=2.0, seed=0, periodic=True):
    """Bruit fractal 2D par synthèse spectrale (1/f^beta), normalisé 0..1, périodique."""
    rng = np.random.default_rng(seed)
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.rfftfreq(w)[None, :]
    f = np.sqrt(fx * fx + fy * fy)
    f[0, 0] = 1.0
    amp = 1.0 / (f ** (beta / 2.0))
    amp[0, 0] = 0
    phase = rng.uniform(0, 2 * np.pi, amp.shape)
    spec = amp * (np.cos(phase) + 1j * np.sin(phase))
    n = np.fft.irfft2(spec, s=(h, w))
    n -= n.min(); n /= (n.max() + 1e-9)
    return n.astype(np.float32)

def ridged(n):
    return 1.0 - np.abs(n * 2 - 1)

def palette_map(x, stops):
    """x float array 0..1 ; stops = [(pos, (r,g,b)), ...] → float32 HxWx3 0..1."""
    x = np.clip(x, 0, 1)
    pos = np.array([s[0] for s in stops], np.float32)
    cols = np.array([s[1] for s in stops], np.float32) / 255.0
    out = np.empty(x.shape + (3,), np.float32)
    for c in range(3):
        out[..., c] = np.interp(x, pos, cols[:, c])
    return out


# ----------------------------------------------------------------------------- compositing
def to_u8(img):
    return np.clip(img * 255.0 + 0.5, 0, 255).astype(np.uint8) if img.dtype != np.uint8 else img

def to_f(img):
    return img.astype(np.float32) / 255.0 if img.dtype == np.uint8 else img

def add_glow(img, sigma=25, strength=0.6, thresh=0.0):
    """img float 0..1 ; bloom additif."""
    src = np.maximum(img - thresh, 0) if thresh > 0 else img
    small = cv2.resize(src, (img.shape[1] // 4, img.shape[0] // 4), interpolation=cv2.INTER_AREA)
    b = cv2.GaussianBlur(small, (0, 0), sigma / 4)
    b = cv2.resize(b, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_LINEAR)
    return img + b * strength

def blit_rgba(dst, sprite, cx, cy, alpha=1.0, additive=False):
    """dst float HxWx3 ; sprite float hxwx4 (premultiplié non requis). Centre (cx, cy)."""
    sh, sw = sprite.shape[:2]
    x0 = int(round(cx - sw / 2)); y0 = int(round(cy - sh / 2))
    x1, y1 = x0 + sw, y0 + sh
    dx0, dy0 = max(0, x0), max(0, y0)
    dx1, dy1 = min(dst.shape[1], x1), min(dst.shape[0], y1)
    if dx1 <= dx0 or dy1 <= dy0:
        return dst
    s = sprite[dy0 - y0:dy1 - y0, dx0 - x0:dx1 - x0]
    a = s[..., 3:4] * alpha
    region = dst[dy0:dy1, dx0:dx1]
    if dst.shape[2] == 4:
        rgb = region[..., :3]
        rgb *= (1 - a); rgb += s[..., :3] * a
        region[..., 3:4] = np.maximum(region[..., 3:4], a)
        return dst
    if additive:
        region += s[..., :3] * a
    else:
        region *= (1 - a)
        region += s[..., :3] * a
    return dst

def scale_sprite(sprite, s):
    if abs(s - 1) < 1e-3:
        return sprite
    h, w = sprite.shape[:2]
    nw, nh = max(1, int(w * s)), max(1, int(h * s))
    return cv2.resize(sprite, (nw, nh), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR)

def radial_grid(h, w, cx=None, cy=None):
    cx = w / 2 if cx is None else cx
    cy = h / 2 if cy is None else cy
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    return xx - cx, yy - cy

def radial_glow(size, color, falloff=2.0, core=0.0):
    """Sprite RGBA float : halo lumineux circulaire."""
    dx, dy = radial_grid(size, size)
    r = np.sqrt(dx * dx + dy * dy) / (size / 2)
    a = np.clip(1 - r, 0, 1) ** falloff
    if core > 0:
        a = np.maximum(a, np.clip(1 - r / core, 0, 1))
    spr = np.zeros((size, size, 4), np.float32)
    spr[..., :3] = np.array(color, np.float32) / 255.0
    spr[..., 3] = a
    return spr

@functools.lru_cache(maxsize=64)
def shaded_sphere(radius, color, light=(-0.5, -0.6, 0.62), spec=0.5, rim=0.25):
    d = radius * 2 + 4
    dx, dy = radial_grid(d, d)
    x, y = dx / radius, dy / radius
    r2 = x * x + y * y
    inside = r2 <= 1
    z = np.sqrt(np.clip(1 - r2, 0, 1))
    L = np.array(light, np.float32); L /= np.linalg.norm(L)
    diff = np.clip(x * L[0] + y * L[1] + z * L[2], 0, 1)
    hv = np.array([L[0], L[1], L[2] + 1]); hv /= np.linalg.norm(hv)
    sp = np.clip(x * hv[0] + y * hv[1] + z * hv[2], 0, 1) ** 40 * spec
    col = np.array(color, np.float32) / 255.0
    rgb = col[None, None, :] * (0.18 + 0.85 * diff[..., None]) + sp[..., None] + rim * (1 - z[..., None]) ** 3 * col
    a = np.clip((1 - np.sqrt(r2)) * radius, 0, 1)
    spr = np.dstack([np.clip(rgb, 0, 1.5), a]).astype(np.float32)
    spr[~inside, 3] = 0
    return spr

_vig = {}
def vignette(strength=0.55, power=2.2):
    k = (strength, power)
    if k not in _vig:
        dx, dy = radial_grid(H, W)
        r = np.sqrt((dx / (W * 0.75)) ** 2 + (dy / (H * 0.72)) ** 2)
        _vig[k] = (1 - strength * np.clip(r, 0, 1.4) ** power).astype(np.float32)[..., None]
    return _vig[k]

_grain = None
def grain_frame(i, amount=0.035):
    global _grain
    if _grain is None:
        rng = np.random.default_rng(7)
        g = rng.normal(0, 1, (6, H // 2, W // 2)).astype(np.float32)
        _grain = [cv2.resize(x, (W, H), interpolation=cv2.INTER_LINEAR)[..., None] for x in g]
    return _grain[i % len(_grain)] * amount


# ----------------------------------------------------------------------------- text
@functools.lru_cache(maxsize=128)
def font(name, size, weight=None):
    f = ImageFont.truetype(os.path.join(FONTS, FONT_FILES.get(name, name)), size)
    if weight is not None:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f

@functools.lru_cache(maxsize=512)
def text_sprite(text, fname='poppins_xb', size=80, color=(255, 255, 255), stroke=0, stroke_color=(0, 0, 0),
                weight=None, shadow=0, max_width=None, spacing=0, align='center'):
    """Rend un texte en sprite RGBA float (0..1)."""
    f = font(fname, size, weight)
    lines = [text]
    if max_width:
        words, lines, cur = text.split(), [], ''
        for wd in words:
            test = (cur + ' ' + wd).strip()
            if f.getlength(test) > max_width and cur:
                lines.append(cur); cur = wd
            else:
                cur = test
        lines.append(cur)
    txt = '\n'.join(lines)
    tmp = Image.new('L', (1, 1))
    bbox = ImageDraw.Draw(tmp).multiline_textbbox((0, 0), txt, font=f, stroke_width=stroke, spacing=spacing, align=align)
    pad = 8 + stroke + shadow * 2
    bbox = [int(math.floor(bbox[0])), int(math.floor(bbox[1])), int(math.ceil(bbox[2])), int(math.ceil(bbox[3]))]
    w = bbox[2] - bbox[0] + pad * 2; h = bbox[3] - bbox[1] + pad * 2
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    org = (pad - bbox[0], pad - bbox[1])
    if shadow:
        sh = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(sh).multiline_text((org[0] + shadow, org[1] + shadow), txt, font=f, fill=(0, 0, 0, 170),
                                          stroke_width=stroke, stroke_fill=(0, 0, 0, 170), spacing=spacing, align=align)
        arr = np.array(sh).astype(np.float32)
        arr[..., 3] = cv2.GaussianBlur(arr[..., 3], (0, 0), shadow * 0.8)
        img = Image.alpha_composite(img, Image.fromarray(arr.astype(np.uint8)))
        d = ImageDraw.Draw(img)
    d.multiline_text(org, txt, font=f, fill=tuple(color) + (255,), stroke_width=stroke,
                     stroke_fill=tuple(stroke_color) + (255,), spacing=spacing, align=align)
    return np.array(img).astype(np.float32) / 255.0

def put_text(dst, text, cx, cy, alpha=1.0, scale=1.0, **kw):
    spr = text_sprite(text, **kw)
    if scale != 1.0:
        spr = scale_sprite(spr, scale)
    return blit_rgba(dst, spr, cx, cy, alpha)


# ----------------------------------------------------------------------------- shapes (anti-aliased via cv2 with shift)
def aa_circle(img, c, r, color, thickness=-1):
    sh = 4
    cv2.circle(img, (int(c[0] * 16), int(c[1] * 16)), int(r * 16), color, thickness, cv2.LINE_AA, sh)

def aa_line(img, p0, p1, color, thickness=2):
    cv2.line(img, (int(p0[0] * 16), int(p0[1] * 16)), (int(p1[0] * 16), int(p1[1] * 16)), color, thickness, cv2.LINE_AA, 4)

def aa_poly(img, pts, color, closed=True, thickness=-1):
    p = (np.asarray(pts) * 16).astype(np.int32).reshape(-1, 1, 2)
    if thickness < 0:
        cv2.fillPoly(img, [p], color, cv2.LINE_AA, 4)
    else:
        cv2.polylines(img, [p], closed, color, thickness, cv2.LINE_AA, 4)

def aa_ellipse(img, c, axes, angle, a0, a1, color, thickness=2):
    cv2.ellipse(img, (int(c[0] * 16), int(c[1] * 16)), (int(axes[0] * 16), int(axes[1] * 16)), angle, a0, a1, color,
                thickness, cv2.LINE_AA, 4)

def gradient_v(h, w, top, bottom):
    t = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    a = np.array(top, np.float32) / 255; b = np.array(bottom, np.float32) / 255
    return np.repeat((a * (1 - t) + b * t), w, axis=1)
