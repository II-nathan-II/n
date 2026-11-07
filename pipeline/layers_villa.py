"""« Villa Vitamine » en dessin animé 2D : personnages-fruits, décors de la villa, habillage télé-réalité.

Tout est dessiné ici (PIL, suréchantillonnage ×3) : personnages et décors originaux, aucun élément repris
d'une émission ou d'un autre créateur. Les personnages parlent (bouche synchronisée sur les mots de la
narration via Ctx), clignent des yeux, marchent et tombent (Pépin).
"""
import math, functools
import numpy as np
import cv2
from PIL import Image, ImageDraw
from common import W, H, blit_rgba, scale_sprite, text_sprite, ease_out, ease_out_back, ease_in_out, clamp01
from layers_base import Layer
from layers_cine import kf
from layers_flat import canvas, finish, S, circle, poly, rrect, rgb, add_shade, PAL, INK, spr_text, spr_ball

C = dict(kiwi=(0.56, 0.39, 0.21), kiwi_d=(0.42, 0.28, 0.14), banana=(1.0, 0.86, 0.22), banana_d=(0.86, 0.66, 0.12),
         lemon=(0.98, 0.92, 0.26), lemon_d=(0.86, 0.78, 0.12), apple=(0.62, 0.88, 0.33), apple_d=(0.45, 0.72, 0.22),
         straw=(0.95, 0.24, 0.33), straw_d=(0.76, 0.12, 0.22), pine=(1.0, 0.76, 0.22), pine_d=(0.80, 0.52, 0.12),
         leaf=(0.30, 0.72, 0.30), leaf_d=(0.20, 0.55, 0.22), white=(0.98, 0.98, 1.0), gold=(1.0, 0.80, 0.20),
         pink=(1.0, 0.50, 0.70), shadow=(0.05, 0.05, 0.12))

CHAR_KIND = dict(kiki='kiwi', berenice='banana', cyril='lemon', pepin='apple', fanny='straw', ananas='pine', margaux='mango')
SHOE = dict(kiki=(0.92, 0.25, 0.25), berenice=(1.0, 0.45, 0.70), cyril=(0.35, 0.40, 0.55), pepin=(0.35, 0.65, 0.95),
            fanny=(1.0, 0.85, 0.30), ananas=(0.15, 0.15, 0.20), margaux=(0.08, 0.07, 0.14))


def _strip_pts(xs, ys, ws):
    left = [(x - w, y) for x, y, w in zip(xs, ys, ws)]
    right = [(x + w, y) for x, y, w in zip(xs, ys, ws)][::-1]
    return left + right


def _body(kind, h, cx):
    """Géométrie du corps : (polygone ou ellipse, couleur, couleur sombre, centre visage, demi-largeur(y), haut, bas)."""
    if kind == 'banana':
        s = np.linspace(0, 1, 60)
        xs = cx + 0.11 * h * np.sin(np.pi * s) - 0.05 * h
        ys = 0.07 * h + s * 0.80 * h
        ws = 0.185 * h * np.sin(np.pi * np.clip(s, 0, 1)) ** 0.55 + 0.012 * h
        pts = _strip_pts(xs, ys, ws)
        k = 22
        return dict(poly=pts, col=C['banana'], dark=C['banana_d'], face=(xs[k] + 0.01 * h, ys[k] + 0.02 * h), top=ys[0], bot=ys[-1],
                    hw=lambda y: float(np.interp(y, ys, ws)), xc=lambda y: float(np.interp(y, ys, xs)))
    if kind == 'straw':
        y0, y1 = 0.17 * h, 0.87 * h
        s = np.linspace(0, 1, 60)
        ys = y0 + s * (y1 - y0)
        ws = 0.32 * h * (1 - s ** 2.3) ** 0.9 * np.minimum(1, (s + 0.05) / 0.24) ** 0.45
        pts = _strip_pts(np.full_like(s, cx), ys, ws)
        return dict(poly=pts, col=C['straw'], dark=C['straw_d'], face=(cx, 0.43 * h), top=y0, bot=y1,
                    hw=lambda y: float(np.interp(y, ys, ws)), xc=lambda y: cx)
    E = dict(kiwi=(0.47, 0.30, 0.38, 'kiwi'), lemon=(0.48, 0.31, 0.35, 'lemon'), apple=(0.55, 0.33, 0.30, 'apple'),
             pine=(0.53, 0.29, 0.33, 'pine'), mango=(0.50, 0.29, 0.37, 'mango'))[kind]
    cy, rx, ry, key = E[0] * h, E[1] * h, E[2] * h, E[3]
    col = dict(kiwi=C['kiwi'], lemon=C['lemon'], apple=C['apple'], pine=C['pine'], mango=(0.07, 0.06, 0.13))[kind]
    dark = dict(kiwi=C['kiwi_d'], lemon=C['lemon_d'], apple=C['apple_d'], pine=C['pine_d'], mango=(0.07, 0.06, 0.13))[kind]
    face = (cx, cy - 0.05 * h)
    return dict(ell=(cx, cy, rx, ry), col=col, dark=dark, face=face, top=cy - ry, bot=cy + ry,
                hw=lambda y: rx * math.sqrt(max(0.0, 1 - ((y - cy) / ry) ** 2)), xc=lambda y: cx)


def _mask_of(img_size, geo, grow=0):
    m = Image.new('L', img_size, 0); md = ImageDraw.Draw(m)
    if 'poly' in geo:
        md.polygon([(S(x), S(y)) for x, y in geo['poly']], fill=255)
    else:
        cx, cy, rx, ry = geo['ell']
        md.ellipse([S(cx - rx - grow), S(cy - ry - grow), S(cx + rx + grow), S(cy + ry + grow)], fill=255)
    return m


def _paint_body(img, d, kind, geo, h):
    cx = geo['face'][0]
    col = rgb(geo['col']); ink = INK; lw = max(2.0, 0.016 * h)
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    if 'poly' in geo:
        ld.polygon([(S(x), S(y)) for x, y in geo['poly']], fill=col)
    else:
        bx, by, rx, ry = geo['ell']
        ld.ellipse([S(bx - rx), S(by - ry), S(bx + rx), S(by + ry)], fill=col)
    mask = _mask_of(img.size, geo)
    tex = Image.new('RGBA', img.size, (0, 0, 0, 0)); td = ImageDraw.Draw(tex)
    rng = np.random.default_rng(len(kind) * 7)
    top, bot = geo['top'], geo['bot']
    if kind == 'kiwi':
        for _ in range(int(140 * (h / 400))):
            y = rng.uniform(top, bot); x = geo['xc'](y) + rng.uniform(-1, 1) * geo['hw'](y)
            td.line([S(x), S(y), S(x + rng.uniform(-3, 3)), S(y + rng.uniform(2, 6))], fill=rgb(C['kiwi_d'], 160), width=int(S(1.4)))
    elif kind == 'lemon':
        for _ in range(int(90 * (h / 400))):
            y = rng.uniform(top, bot); x = geo['xc'](y) + rng.uniform(-0.9, 0.9) * geo['hw'](y)
            td.ellipse([S(x - 1.4), S(y - 1.4), S(x + 1.4), S(y + 1.4)], fill=rgb(C['lemon_d'], 150))
    elif kind == 'straw':
        for yy in np.arange(top + 0.07 * h, bot - 0.03 * h, 0.075 * h):
            hw = geo['hw'](yy)
            off = 0.035 * h if int((yy - top) / (0.075 * h)) % 2 else 0
            for xx in np.arange(cx - hw + 0.03 * h + off, cx + hw - 0.02 * h, 0.07 * h):
                td.ellipse([S(xx - 0.009 * h), S(yy - 0.016 * h), S(xx + 0.009 * h), S(yy + 0.016 * h)], fill=rgb((1.0, 0.88, 0.35)))
    elif kind == 'pine':
        step = 0.075 * h
        for k in range(-12, 13):
            x0 = cx + k * step
            td.line([S(x0 - 0.6 * h), S(top - 0.1 * h), S(x0 + 0.6 * h), S(top + 1.1 * h)], fill=rgb(C['pine_d'], 200), width=int(S(lw * 0.8)))
            td.line([S(x0 + 0.6 * h), S(top - 0.1 * h), S(x0 - 0.6 * h), S(top + 1.1 * h)], fill=rgb(C['pine_d'], 200), width=int(S(lw * 0.8)))
    elif kind == 'banana':
        s = np.linspace(0.08, 0.92, 30)
        pts = [(geo['xc'](geo['top'] + v * (geo['bot'] - geo['top'])) - 0.6 * geo['hw'](geo['top'] + v * (geo['bot'] - geo['top'])),
                geo['top'] + v * (geo['bot'] - geo['top'])) for v in s]
        td.line([(S(x), S(y)) for x, y in pts], fill=rgb((1.0, 0.95, 0.55), 200), width=int(S(0.03 * h)))
    layer.alpha_composite(Image.composite(tex, Image.new('RGBA', img.size, (0, 0, 0, 0)), mask))
    # ombre propre (croissant bas-droite)
    sh = Image.new('RGBA', img.size, rgb(geo['dark'], 120))
    off = Image.new('L', img.size, 0); od = ImageDraw.Draw(off)
    if 'poly' in geo:
        od.polygon([(S(x - 0.05 * h), S(y - 0.05 * h)) for x, y in geo['poly']], fill=255)
    else:
        bx, by, rx, ry = geo['ell']
        od.ellipse([S(bx - rx - 0.07 * h), S(by - ry - 0.07 * h), S(bx + rx - 0.07 * h), S(by + ry - 0.07 * h)], fill=255)
    cres = Image.fromarray(np.minimum(np.asarray(mask), 255 - np.asarray(off)).astype(np.uint8))
    if kind != 'mango':
        layer.alpha_composite(Image.composite(sh, Image.new('RGBA', img.size, (0, 0, 0, 0)), cres))
    img.alpha_composite(layer)
    # contour
    if 'poly' in geo:
        d.line([(S(x), S(y)) for x, y in geo['poly'] + geo['poly'][:1]], fill=ink, width=int(S(lw)), joint='curve')
    else:
        bx, by, rx, ry = geo['ell']
        d.ellipse([S(bx - rx), S(by - ry), S(bx + rx), S(by + ry)], outline=ink, width=int(S(lw)))
    # reflet
    if kind != 'mango':
        hx, hy = geo['xc'](top + 0.22 * (bot - top)) - geo['hw'](top + 0.22 * (bot - top)) * 0.45, top + 0.22 * (bot - top)
        hl = Image.new('RGBA', img.size, (0, 0, 0, 0))
        ImageDraw.Draw(hl).ellipse([S(hx - 0.05 * h), S(hy - 0.028 * h), S(hx + 0.05 * h), S(hy + 0.028 * h)], fill=(255, 255, 255, 110))
        img.alpha_composite(hl)


def _limb(d, p0, p1, h, mid=None):
    w = int(S(0.03 * h))
    pts = [p0] + ([mid] if mid else []) + [p1]
    d.line([(S(x), S(y)) for x, y in pts], fill=INK, width=w, joint='curve')


def _hand(d, x, y, h, col=(1, 1, 1)):
    circle(d, x, y, 0.045 * h, rgb(col), INK, 0.012 * h)


def _eye(d, x, y, h, blink, gaze, expr, lid_col, lashes=False, wink=False):
    rx, ry = 0.052 * h, 0.066 * h
    if expr == 'shock':
        rx, ry = rx * 1.15, ry * 1.2
    if blink or wink:
        d.arc([S(x - rx), S(y - ry * 0.5), S(x + rx), S(y + ry * 0.7)], 200, 340, fill=INK, width=int(S(0.016 * h)))
        return
    d.ellipse([S(x - rx), S(y - ry), S(x + rx), S(y + ry)], fill=rgb(C['white']), outline=INK, width=int(S(0.012 * h)))
    pr = 0.03 * h * (0.7 if expr == 'shock' else 1.0)
    px, py = x + gaze * 0.017 * h, y + 0.008 * h
    circle(d, px, py, pr, rgb((0.08, 0.07, 0.14)))
    circle(d, px - pr * 0.35, py - pr * 0.4, pr * 0.32, rgb(C['white']))
    if expr in ('diva', 'grumpy', 'sly'):
        # paupière mi-close (regard blasé / sûr de soi)
        d.chord([S(x - rx - 1), S(y - ry - 1), S(x + rx + 1), S(y + ry + 1)], 180, 360, fill=rgb(lid_col))
        d.line([S(x - rx), S(y), S(x + rx), S(y)], fill=INK, width=int(S(0.013 * h)))
    if lashes:
        for k in range(3):
            d.line([S(x + (k - 1) * rx * 0.6), S(y - ry * 0.95), S(x + (k - 1) * rx * 0.9), S(y - ry * 1.35)], fill=INK, width=int(S(0.011 * h)))


def _brows(d, ex, ey, h, expr, side, thick=False):
    w = int(S((0.026 if thick else 0.014) * h))
    y = ey - 0.105 * h
    dx = 0.05 * h
    sgn = -1 if side < 0 else 1
    if expr == 'grumpy':   # extrémité intérieure basse
        d.line([S(ex - dx * sgn), S(y + 0.024 * h), S(ex + dx * sgn), S(y - 0.02 * h)], fill=INK, width=w)
    elif expr == 'shy':    # extrémité intérieure haute (air inquiet)
        d.line([S(ex - dx * sgn), S(y - 0.02 * h), S(ex + dx * sgn), S(y + 0.012 * h)], fill=INK, width=w)
    elif expr == 'shock':
        d.arc([S(ex - dx), S(y - 0.05 * h), S(ex + dx), S(y + 0.02 * h)], 200, 340, fill=INK, width=w)
    elif expr in ('smirk', 'sly') and side > 0:
        d.arc([S(ex - dx), S(y - 0.05 * h), S(ex + dx), S(y + 0.015 * h)], 200, 340, fill=INK, width=w)
    else:
        d.arc([S(ex - dx), S(y - 0.02 * h), S(ex + dx), S(y + 0.03 * h)], 210, 330, fill=INK, width=w)


def _mouth(d, x, y, h, mouth, expr, lip=None):
    lw = int(S(0.015 * h))
    if mouth == 0 and expr != 'shock':
        if expr == 'grumpy':
            d.arc([S(x - 0.05 * h), S(y + 0.0), S(x + 0.05 * h), S(y + 0.05 * h)], 200, 340, fill=INK, width=lw)
        elif expr in ('smirk', 'sly'):
            d.arc([S(x - 0.06 * h), S(y - 0.05 * h), S(x + 0.07 * h), S(y + 0.02 * h)], 25, 120, fill=INK, width=lw)
        elif expr == 'shy':
            d.arc([S(x - 0.035 * h), S(y - 0.03 * h), S(x + 0.035 * h), S(y + 0.015 * h)], 20, 160, fill=INK, width=lw)
        else:
            if lip:
                d.chord([S(x - 0.06 * h), S(y - 0.04 * h), S(x + 0.06 * h), S(y + 0.035 * h)], 0, 180, fill=rgb(lip), outline=INK, width=lw)
            else:
                d.arc([S(x - 0.07 * h), S(y - 0.06 * h), S(x + 0.07 * h), S(y + 0.03 * h)], 20, 160, fill=INK, width=lw)
        return
    if expr == 'shock' and mouth == 0:
        mouth = 3
    rw, rh = {1: (0.045, 0.025), 2: (0.06, 0.05), 3: (0.035, 0.055)}[mouth]
    rw, rh = rw * h, rh * h
    d.ellipse([S(x - rw), S(y - rh * 0.6), S(x + rw), S(y + rh)], fill=rgb((0.35, 0.06, 0.10)), outline=INK, width=lw)
    if mouth == 2:
        d.chord([S(x - rw * 0.6), S(y + rh * 0.1), S(x + rw * 0.6), S(y + rh * 0.95)], 0, 180, fill=rgb((1.0, 0.45, 0.50)))
        d.chord([S(x - rw * 0.8), S(y - rh * 0.6), S(x + rw * 0.8), S(y - rh * 0.1)], 180, 360, fill=rgb(C['white']))
    if lip:
        d.ellipse([S(x - rw), S(y - rh * 0.6), S(x + rw), S(y + rh)], outline=rgb(lip), width=int(S(0.012 * h)))


@functools.lru_cache(maxsize=1024)
def spr_fruit(who, h, mouth=0, blink=False, expr='smile', arms='down', gaze=0.0, shades=False, wink=False, legs=True):
    kind = CHAR_KIND[who]
    Wc, Hc = h * 1.15, h * 1.18
    img, d = canvas(Wc, Hc)
    cx = Wc / 2
    geo = _body(kind, h, cx)
    fx, fy = geo['face']
    sil = kind == 'mango'
    # couronne / chapeau / tige derrière le corps
    if kind == 'pine':
        for k, a in enumerate(np.linspace(-62, 62, 7)):
            L = (0.30 - 0.0011 * abs(a)) * h
            ar = math.radians(a - 90)
            bx, by = cx, geo['top'] + 0.04 * h
            tip = (bx + math.cos(ar) * L, by + math.sin(ar) * L)
            n = (-math.sin(ar) * 0.05 * h, math.cos(ar) * 0.05 * h)
            poly(d, [(bx + n[0], by + n[1]), tip, (bx - n[0], by - n[1])], rgb(C['leaf'] if k % 2 else C['leaf_d']), INK, 0.01 * h)
    if kind == 'mango':
        poly(d, [(cx + 0.02 * h, geo['top'] + 0.02 * h), (cx + 0.16 * h, geo['top'] - 0.10 * h), (cx + 0.26 * h, geo['top'] - 0.02 * h), (cx + 0.10 * h, geo['top'] + 0.06 * h)], rgb((0.07, 0.06, 0.13)))
    # bras (derrière le corps sauf bras croisés)
    sy = geo['top'] + 0.58 * (geo['bot'] - geo['top'])
    hwL = geo['hw'](sy) * 0.94
    shL = (geo['xc'](sy) - hwL, sy); shR = (geo['xc'](sy) + hwL, sy)
    handcol = C['pink'] if who == 'berenice' else C['white']
    if sil:
        handcol = (0.07, 0.06, 0.13)
    hands = []
    if arms in ('down', 'phone', 'cards', 'key', 'hip', 'wave', 'open', 'glass'):
        for side, sh in ((-1, shL), (1, shR)):
            if arms == 'open' or (arms == 'wave' and side > 0):
                hp = (sh[0] + side * 0.22 * h, sh[1] - (0.20 if arms == 'open' else 0.26) * h)
                _limb(d, sh, hp, h, (sh[0] + side * 0.14 * h, sh[1] - 0.02 * h))
            elif arms == 'hip':
                hp = (sh[0] + side * 0.01 * h, sh[1] + 0.13 * h)
                _limb(d, sh, hp, h, (sh[0] + side * 0.15 * h, sh[1] + 0.06 * h))
            elif (arms in ('phone', 'cards', 'key', 'glass') and side > 0):
                hp = (sh[0] + 0.12 * h, sh[1] - 0.10 * h)
                _limb(d, sh, hp, h, (sh[0] + 0.15 * h, sh[1] + 0.06 * h))
            else:
                hp = (sh[0] + side * 0.10 * h, sh[1] + 0.20 * h)
                _limb(d, sh, hp, h, (sh[0] + side * 0.07 * h, sh[1] + 0.11 * h))
            hands.append((side, hp))
    # jambes
    if legs:
        for side in (-1, 1):
            lx = geo['xc'](geo['bot']) + side * 0.075 * h
            _limb(d, (lx, geo['bot'] - 0.03 * h), (lx, 1.08 * h), h)
            sc = SHOE[who]
            rrect(d, lx - 0.06 * h + side * 0.02 * h, 1.055 * h, lx + 0.06 * h + side * 0.02 * h, 1.115 * h, 0.03 * h, rgb(sc), INK, 0.011 * h)
    _paint_body(img, d, kind, geo, h)
    d = ImageDraw.Draw(img)
    # pomme : tige + feuille ; fraise : chapeau de feuilles ; banane : queue
    if kind == 'apple':
        d.line([S(cx), S(geo['top'] + 0.04 * h), S(cx + 0.02 * h), S(geo['top'] - 0.08 * h)], fill=rgb((0.45, 0.28, 0.15)), width=int(S(0.025 * h)))
        lf = Image.new('RGBA', img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lf)
        ld.ellipse([S(cx + 0.02 * h), S(geo['top'] - 0.12 * h), S(cx + 0.17 * h), S(geo['top'] - 0.05 * h)], fill=rgb(C['leaf']), outline=INK, width=int(S(0.01 * h)))
        img.alpha_composite(lf.rotate(-20, center=(S(cx + 0.03 * h), S(geo['top'] - 0.08 * h))))
    if kind == 'straw':
        for k in range(7):
            a = math.radians(-180 + k * 30)
            tip = (cx + math.cos(a) * 0.20 * h, geo['top'] + 0.04 * h + math.sin(a) * 0.08 * h + 0.03 * h)
            n = (-math.sin(a) * 0.045 * h, math.cos(a) * 0.03 * h)
            poly(d, [(cx + n[0], geo['top'] + 0.02 * h + n[1]), tip, (cx - n[0], geo['top'] + 0.02 * h - n[1])], rgb(C['leaf'] if k % 2 else C['leaf_d']), INK, 0.009 * h)
        d.line([S(cx), S(geo['top'] + 0.01 * h), S(cx), S(geo['top'] - 0.07 * h)], fill=rgb(C['leaf_d']), width=int(S(0.022 * h)))
    if kind == 'banana':
        tx, ty = geo['xc'](geo['top']), geo['top']
        d.line([S(tx), S(ty + 0.01 * h), S(tx - 0.03 * h), S(ty - 0.06 * h)], fill=rgb((0.45, 0.32, 0.15)), width=int(S(0.035 * h)))
        circle(d, geo['xc'](geo['bot']), geo['bot'] - 0.005 * h, 0.018 * h, rgb((0.40, 0.28, 0.14)))
    if kind == 'lemon':
        for yy in (geo['top'], geo['bot']):
            circle(d, cx, yy, 0.035 * h, rgb(C['lemon']), INK, 0.012 * h)
    if sil:
        # silhouette : fleur d'hibiscus, aucun visage
        for k in range(5):
            a = k * 2 * math.pi / 5
            circle(d, fx + 0.20 * h + math.cos(a) * 0.04 * h, fy - 0.10 * h + math.sin(a) * 0.04 * h, 0.035 * h, rgb((0.07, 0.06, 0.13)))
    else:
        lid = geo['col']
        ex = 0.085 * h
        for side in (-1, 1):
            _eye(d, fx + side * ex, fy, h, blink, gaze, expr, lid, lashes=(who == 'berenice'), wink=(wink and side > 0))
            _brows(d, fx + side * ex, fy, h, expr, side, thick=(who == 'cyril'))
        if who in ('pepin', 'berenice', 'fanny') or expr == 'shy':
            bl = Image.new('RGBA', img.size, (0, 0, 0, 0)); bd = ImageDraw.Draw(bl)
            for side in (-1, 1):
                bx = fx + side * 0.15 * h
                bd.ellipse([S(bx - 0.04 * h), S(fy + 0.055 * h), S(bx + 0.04 * h), S(fy + 0.085 * h)], fill=(255, 110, 150, 120 if expr == 'shy' else 70))
            img.alpha_composite(bl)
        _mouth(d, fx, fy + 0.13 * h, h, mouth, expr, lip=(1.0, 0.35, 0.55) if who == 'berenice' else None)
        # accessoires
        if who == 'pepin':
            for side in (-1, 1):
                circle(d, fx + side * ex, fy, 0.078 * h, None, INK, 0.014 * h)
            d.line([S(fx - ex + 0.078 * h), S(fy), S(fx + ex - 0.078 * h), S(fy)], fill=INK, width=int(S(0.012 * h)))
        if who == 'kiki' or shades:
            gy = fy if shades else geo['top'] + 0.085 * h
            for side in (-1, 1):
                rrect(d, fx + side * ex - 0.065 * h, gy - 0.04 * h, fx + side * ex + 0.065 * h, gy + 0.04 * h, 0.03 * h, rgb((0.10, 0.10, 0.16)), INK, 0.01 * h)
                d.line([S(fx + side * ex - 0.035 * h), S(gy - 0.02 * h), S(fx + side * ex - 0.005 * h), S(gy - 0.02 * h)], fill=(255, 255, 255, 170), width=int(S(0.01 * h)))
            d.line([S(fx - ex + 0.065 * h), S(gy - 0.01 * h), S(fx + ex - 0.065 * h), S(gy - 0.01 * h)], fill=INK, width=int(S(0.012 * h)))
        if who == 'kiki':
            pts = [(fx + 0.17 * h * math.cos(a), fy + 0.20 * h + 0.06 * h * math.sin(a)) for a in np.linspace(0.15, math.pi - 0.15, 11)]
            for x, y in pts:
                circle(d, x, y, 0.014 * h, rgb(C['gold']), INK, 0.004 * h)
        if who == 'berenice':
            for side in (-1, 1):
                d.ellipse([S(fx + side * 0.155 * h - 0.022 * h), S(fy + 0.04 * h), S(fx + side * 0.155 * h + 0.022 * h), S(fy + 0.09 * h)],
                          outline=rgb(C['gold']), width=int(S(0.009 * h)))
        if who == 'ananas':
            by = fy + 0.27 * h
            poly(d, [(fx, by), (fx - 0.09 * h, by - 0.05 * h), (fx - 0.09 * h, by + 0.05 * h)], rgb((0.88, 0.15, 0.20)), INK, 0.01 * h)
            poly(d, [(fx, by), (fx + 0.09 * h, by - 0.05 * h), (fx + 0.09 * h, by + 0.05 * h)], rgb((0.88, 0.15, 0.20)), INK, 0.01 * h)
            circle(d, fx, by, 0.022 * h, rgb((0.70, 0.08, 0.12)), INK, 0.008 * h)
    # mains (au-dessus) et objets tenus
    for side, (x, y) in hands:
        if side > 0 and arms == 'phone':
            rrect(d, x - 0.035 * h, y - 0.11 * h, x + 0.035 * h, y + 0.01 * h, 0.012 * h, rgb((1.0, 0.45, 0.70)), INK, 0.009 * h)
            rrect(d, x - 0.025 * h, y - 0.10 * h, x + 0.025 * h, y - 0.01 * h, 0.006 * h, rgb((0.75, 0.92, 1.0)))
        if side > 0 and arms == 'cards':
            rrect(d, x - 0.05 * h, y - 0.12 * h, x + 0.03 * h, y + 0.0 * h, 0.008 * h, rgb((1.0, 0.98, 0.92)), INK, 0.008 * h)
        if side > 0 and arms == 'key':
            circle(d, x + 0.03 * h, y - 0.06 * h, 0.03 * h, None, rgb(C['gold']), 0.014 * h)
            d.line([S(x + 0.03 * h), S(y - 0.03 * h), S(x + 0.03 * h), S(y + 0.06 * h)], fill=rgb(C['gold']), width=int(S(0.014 * h)))
        if side > 0 and arms == 'glass':
            poly(d, [(x - 0.04 * h, y - 0.13 * h), (x + 0.04 * h, y - 0.13 * h), (x + 0.03 * h, y + 0.0), (x - 0.03 * h, y + 0.0)], rgb((1.0, 0.65, 0.20), 230), INK, 0.008 * h)
        _hand(d, x, y, h, handcol)
    if arms == 'cross':
        yc = geo['top'] + 0.80 * (geo['bot'] - geo['top'])
        hwc = geo['hw'](yc)
        for side in (-1, 1):
            a = (geo['xc'](yc) + side * hwc * 0.98, yc - 0.06 * h)
            b = (geo['xc'](yc) - side * hwc * 0.45, yc + 0.01 * h)
            _limb(d, a, b, h)
            _hand(d, b[0], b[1], h, handcol)
    return finish(img)


class Fruit(Layer):
    """Personnage-fruit posé au sol en pos=(x, y_pieds). talk=marque(s) de segment : bouche animée sur les mots.
    Images clés possibles : pos, rot (degrés), expr [(t, 'shock')...], arms [(t, 'open')...]."""
    def __init__(self, who, pos, h=480, expr='smile', arms='down', talk=(), flip=False, t0=0.0, pop=0.0, gaze=0.0,
                 shades=False, wink=None, rot=0.0, alpha=1.0, shadow=True, legs=True, ctx=None, bounce=True, bob=3.0, phase=0.0):
        self.__dict__.update(locals()); del self.__dict__['self']
        self.windows = []
        if ctx is not None:
            for m in (talk if isinstance(talk, (list, tuple)) else [talk]):
                if not m:
                    continue
                for spec, seg in zip(ctx.video['segments'], ctx.tl['segments']):
                    if spec.get('mark') == m:
                        self.windows += [(w['s'] - ctx.start, w['e'] - ctx.start) for w in seg['words']]

    def _v(self, v, t):
        if isinstance(v, list):
            if v and isinstance(v[0][1], str):
                cur = v[0][1]
                for tt, val in v:
                    if t >= tt:
                        cur = val
                return cur
            return kf(v, t)
        return v

    def mouth(self, t):
        for s, e in self.windows:
            if s - 0.02 <= t <= e:
                ph = (t - s) * 15.0
                return 2 if math.sin(ph * 1.0) > 0.1 else 1
        return 0

    def draw(self, f, t, dur):
        if t < self.t0:
            return f
        lt = t - self.t0
        x, y = self._v(self.pos, t)
        moving = False
        if isinstance(self.pos, list):
            x2, y2 = self._v(self.pos, t + 0.05)
            moving = abs(x2 - x) + abs(y2 - y) > 1.0
        hop = abs(math.sin(lt * 9.0)) * 0.05 * self.h if (moving and self.bounce) else 0.0
        bob = self.bob * math.sin(lt * 2.2 + self.phase) if not moving else 0.0
        blink = ((lt + self.phase) % 3.3) < 0.11
        wink = self.wink is not None and self.wink[0] <= t <= self.wink[1]
        expr = self._v(self.expr, t); arms = self._v(self.arms, t)
        spr = spr_fruit(self.who, int(self.h), self.mouth(t), blink and not wink, expr, arms, float(self._v(self.gaze, t)), self.shades, wink, self.legs)
        if self.flip:
            spr = spr[:, ::-1].copy()
        sc = 1.0
        if self.pop:
            sc = max(0.02, ease_out_back(min(1.0, lt / self.pop)))
        ang = float(self._v(self.rot, t))
        hh = spr.shape[0]
        foot = 1.11 * self.h
        if self.shadow and abs(ang) < 30:
            ov = f.copy()
            cv2.ellipse(ov, (int(x), int(y + 0.005 * self.h)), (int(0.24 * self.h * sc), int(0.042 * self.h * sc)), 0, 0, 360, C['shadow'], -1, cv2.LINE_AA)
            f[:] = f * 0.72 + ov * 0.28
        img = scale_sprite(spr, sc) if abs(sc - 1) > 1e-3 else spr
        off = (foot - hh / 2) * sc
        cxs, cys = x, y - off - hop + bob
        if abs(ang) > 0.1:
            hh2, ww2 = img.shape[:2]
            M = cv2.getRotationMatrix2D((ww2 / 2, hh2 / 2), ang, 1.0)
            cs, sn = abs(M[0, 0]), abs(M[0, 1])
            nw, nh = int(hh2 * sn + ww2 * cs) + 2, int(hh2 * cs + ww2 * sn) + 2
            M[0, 2] += nw / 2 - ww2 / 2; M[1, 2] += nh / 2 - hh2 / 2
            img = cv2.warpAffine(img, M, (nw, nh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
            th = math.radians(ang)
            cxs, cys = x - math.sin(th) * off, y - math.cos(th) * off - hop
        blit_rgba(f, img, cxs, cys, self.alpha)
        return f


# ----------------------------------------------------------------------------- objets
@functools.lru_cache(maxsize=16)
def spr_suitcase(s, col=(1.0, 0.75, 0.25), sticker=None):
    img, d = canvas(s * 0.8, s * 1.15)
    rrect(d, s * 0.28, s * 0.02, s * 0.52, s * 0.18, s * 0.04, None, INK, s * 0.03)
    rrect(d, s * 0.06, s * 0.14, s * 0.74, s * 1.0, s * 0.08, rgb(col), INK, s * 0.025)
    for x in (0.25, 0.55):
        d.line([S(s * x), S(s * 0.2), S(s * x), S(s * 0.95)], fill=rgb(tuple(c * 0.8 for c in col)), width=int(S(s * 0.03)))
    for x in (0.2, 0.6):
        circle(d, s * x, s * 1.06, s * 0.05, rgb((0.15, 0.15, 0.2)))
    if sticker:
        circle(d, s * 0.45, s * 0.55, s * 0.13, rgb(sticker), INK, s * 0.015)
        poly(d, [(s * 0.45, s * 0.44), (s * 0.55, s * 0.36), (s * 0.58, s * 0.44)], rgb(C['leaf']))
    return finish(img)


@functools.lru_cache(maxsize=4)
def spr_cushion(w, h):
    img, d = canvas(w, h)
    rrect(d, 4, 4, w - 4, h - 4, h * 0.45, rgb((0.62, 0.92, 0.82)), INK, 4)
    d.line([S(w * 0.2), S(h * 0.5), S(w * 0.8), S(h * 0.5)], fill=rgb((0.50, 0.80, 0.70)), width=int(S(3)))
    return finish(img)


@functools.lru_cache(maxsize=4)
def spr_stars_dizzy(r):
    img, d = canvas(r * 2.6, r * 1.2)
    for k in range(3):
        x = r * (0.4 + k * 0.9); y = r * 0.6
        pts = [(x + (r * 0.32 if j % 2 == 0 else r * 0.13) * math.cos(-math.pi / 2 + j * math.pi / 5),
                y + (r * 0.32 if j % 2 == 0 else r * 0.13) * math.sin(-math.pi / 2 + j * math.pi / 5)) for j in range(10)]
        poly(d, pts, rgb(C['gold']), INK, 3)
    return finish(img)


# ----------------------------------------------------------------------------- décors (plein écran)
def _sky(d, top, bot, y1, y0=0):
    for y in range(y0, y1, 6):
        k = (y - y0) / max(1, y1 - y0)
        c = tuple(a * (1 - k) + b * k for a, b in zip(top, bot))
        d.rectangle([0, S(y), S(W), S(y + 6)], fill=rgb(c))


def _palm(d, x, y, hgt, lean=1):
    pts = [(x + lean * 40 * math.sin(k / 10 * 1.4), y - hgt * k / 10) for k in range(11)]
    for (a, b), (c, e) in zip(pts, pts[1:]):
        d.line([S(a), S(b), S(c), S(e)], fill=rgb((0.55, 0.38, 0.22)), width=int(S(30)))
    for (a, b) in pts[1::2]:
        d.line([S(a - 15), S(b), S(a + 15), S(b + 6)], fill=rgb((0.45, 0.30, 0.16)), width=int(S(4)))
    tx, ty = pts[-1]
    for k, ang in enumerate(np.linspace(-170, -10, 7)):
        a = math.radians(ang); L = 210
        tip = (tx + math.cos(a) * L, ty + math.sin(a) * L * 0.6 + 70)
        mid = (tx + math.cos(a) * L * 0.5, ty + math.sin(a) * L * 0.5 - 20)
        n = 26
        poly(d, [(tx, ty), (mid[0] - n * math.sin(a), mid[1] + n * math.cos(a) * 0.5), tip, (mid[0] + n * math.sin(a), mid[1] - n * math.cos(a) * 0.5)],
             rgb(C['leaf'] if k % 2 else C['leaf_d']), INK, 3)


def _cloud(d, x, y, s):
    for dx, dy, r in ((0, 0, 1.0), (0.9, 0.1, 0.8), (-0.9, 0.15, 0.75), (0.4, -0.45, 0.8)):
        circle(d, x + dx * s, y + dy * s, r * s, rgb((1, 1, 1)))


def _pool(d, x0, y0, x1, y1):
    rrect(d, x0 - 26, y0 - 26, x1 + 26, y1 + 26, 34, rgb((0.97, 0.96, 0.92)), INK, 4)
    rrect(d, x0, y0, x1, y1, 22, rgb((0.25, 0.80, 0.90)))
    rng = np.random.default_rng(3)
    for _ in range(int((x1 - x0) * (y1 - y0) / 9000)):
        x = rng.uniform(x0 + 40, x1 - 80); y = rng.uniform(y0 + 30, y1 - 20)
        d.arc([S(x), S(y), S(x + 70), S(y + 22)], 200, 340, fill=rgb((0.75, 0.97, 1.0)), width=int(S(5)))


def _villa_house(d, x0, y0, x1, y1):
    rrect(d, x0 + (x1 - x0) * 0.18, y0 - 150, x0 + (x1 - x0) * 0.78, y0 + 10, 6, rgb((0.98, 0.97, 0.94)), INK, 4)
    rrect(d, x0, y0, x1, y1, 6, rgb((0.98, 0.97, 0.94)), INK, 4)
    d.rectangle([S(x0 + 4), S(y1 - 60), S(x1 - 4), S(y1 - 4)], fill=rgb((0.90, 0.88, 0.84)))
    for k in range(4):
        wx = x0 + 40 + k * (x1 - x0 - 80) / 4
        rrect(d, wx + 10, y0 + 70, wx + (x1 - x0 - 80) / 4 - 10, y1 - 70, 4, rgb((0.45, 0.75, 0.95)), INK, 3)
        d.line([S(wx + 30), S(y0 + 90), S(wx + 60), S(y0 + 130)], fill=rgb((0.85, 0.95, 1.0)), width=int(S(6)))
    for k in range(3):
        wx = x0 + (x1 - x0) * 0.22 + k * (x1 - x0) * 0.19
        rrect(d, wx, y0 - 120, wx + (x1 - x0) * 0.15, y0 - 25, 4, rgb((0.45, 0.75, 0.95)), INK, 3)
    d.line([S(x0 + (x1 - x0) * 0.18), S(y0 - 12), S(x0 + (x1 - x0) * 0.78), S(y0 - 12)], fill=INK, width=int(S(5)))


@functools.lru_cache(maxsize=12)
def spr_set(name):
    img, d = canvas(W, H)
    if name in ('villa', 'piscine'):
        horizon = 880 if name == 'villa' else 640
        _sky(d, (0.36, 0.72, 1.0), (0.78, 0.92, 1.0), horizon)
        circle(d, 190, 260, 95, rgb((1.0, 0.92, 0.45)))
        circle(d, 190, 260, 72, rgb((1.0, 0.82, 0.25)))
        _cloud(d, 640, 230, 55); _cloud(d, 930, 400, 40)
        d.rectangle([0, S(horizon - 70), S(W), S(horizon)], fill=rgb((0.20, 0.60, 0.92)))
        for k in range(8):
            d.line([S(60 + k * 130), S(horizon - 40 + (k % 3) * 10), S(120 + k * 130), S(horizon - 40 + (k % 3) * 10)], fill=rgb((0.70, 0.88, 1.0)), width=int(S(4)))
        if name == 'villa':
            d.ellipse([S(-200), S(700), S(700), S(1000)], fill=rgb((0.55, 0.78, 0.50)))
            d.ellipse([S(500), S(720), S(1350), S(1020)], fill=rgb((0.50, 0.74, 0.46)))
            d.rectangle([0, S(horizon), S(W), S(H)], fill=rgb((0.95, 0.86, 0.68)))
            _villa_house(d, 150, 640, 930, 1060)
            for k in range(10):
                d.line([0, S(1100 + k * 55), S(W), S(1100 + k * 55)], fill=rgb((0.90, 0.80, 0.60)), width=int(S(3)))
            _palm(d, 80, 1180, 760, 1); _palm(d, 1010, 1200, 700, -1)
            for x in (300, 790):
                circle(d, x, 1090, 48, rgb((0.62, 0.45, 0.85)), INK, 3)
                rrect(d, x - 40, 1090, x + 40, 1170, 8, rgb((0.85, 0.55, 0.35)), INK, 3)
            _pool(d, 110, 1600, 970, 1880)
        else:
            d.rectangle([0, S(horizon), S(W), S(H)], fill=rgb((0.95, 0.86, 0.68)))
            for k in range(14):
                d.line([0, S(horizon + 30 + k * 50), S(W), S(horizon + 30 + k * 50)], fill=rgb((0.90, 0.80, 0.60)), width=int(S(3)))
            _palm(d, 960, 1000, 620, -1)
            for x in (690, 900):
                rrect(d, x - 90, 980, x + 90, 1040, 18, rgb((1.0, 0.62, 0.75)), INK, 3)
                rrect(d, x - 90, 920, x - 30, 1000, 14, rgb((1.0, 0.62, 0.75)), INK, 3)
            poly(d, [(250, 620), (520, 720), (-20, 720)], rgb((1.0, 0.45, 0.45)), INK, 3)
            d.line([S(250), S(620), S(250), S(1040)], fill=INK, width=int(S(8)))
            _pool(d, 60, 1360, 1020, 1900)
    elif name == 'conf':
        d.rectangle([0, 0, S(W), S(H)], fill=rgb((1.0, 0.86, 0.90)))
        for k in range(0, W, 90):
            d.rectangle([S(k), 0, S(k + 45), S(1500)], fill=rgb((1.0, 0.90, 0.93)))
        rrect(d, 60, 260, 470, 760, 10, rgb((0.98, 0.98, 1.0)), INK, 4)
        _sky(d, (0.50, 0.80, 1.0), (0.85, 0.95, 1.0), 560, 280)
        d.rectangle([S(80), S(280), S(450), S(560)], outline=None)
        d.rectangle([S(80), S(560), S(450), S(740)], fill=rgb((0.25, 0.80, 0.90)))
        d.rectangle([0, 0, S(80), S(H)], fill=rgb((1.0, 0.86, 0.90)))
        d.rectangle([S(450), S(260), S(W), S(280)], fill=rgb((1.0, 0.86, 0.90)))
        rrect(d, 60, 260, 470, 760, 10, None, INK, 4)
        d.line([S(265), S(260), S(265), S(760)], fill=INK, width=int(S(4)))
        rrect(d, 850, 980, 990, 1140, 12, rgb((0.85, 0.55, 0.35)), INK, 3)
        for k, a in enumerate(np.linspace(-150, -30, 6)):
            r = math.radians(a)
            poly(d, [(920, 990), (920 + math.cos(r) * 190, 990 + math.sin(r) * 210), (920 + math.cos(r + 0.18) * 120, 990 + math.sin(r + 0.18) * 140)], rgb(C['leaf'] if k % 2 else C['leaf_d']), INK, 3)
        d.rectangle([0, S(1500), S(W), S(H)], fill=rgb((0.85, 0.70, 0.55)))
        rrect(d, 200, 560, 880, 1320, 160, rgb((0.98, 0.68, 0.80)), INK, 5)
        rrect(d, 250, 640, 430, 800, 50, rgb((0.62, 0.92, 0.82)), INK, 4)
        rrect(d, 650, 640, 830, 800, 50, rgb((1.0, 0.85, 0.40)), INK, 4)
    elif name == 'salon':
        d.rectangle([0, 0, S(W), S(H)], fill=rgb((0.99, 0.95, 0.88)))
        rrect(d, 120, 280, 960, 980, 8, rgb((0.98, 0.98, 1.0)), INK, 4)
        _sky(d, (0.45, 0.78, 1.0), (0.85, 0.95, 1.0), 800, 300)
        d.rectangle([S(140), S(800), S(940), S(960)], fill=rgb((0.20, 0.60, 0.92)))
        d.rectangle([0, 0, S(140), S(H)], fill=rgb((0.99, 0.95, 0.88))); d.rectangle([S(940), 0, S(W), S(H)], fill=rgb((0.99, 0.95, 0.88)))
        d.rectangle([0, 0, S(W), S(300)], fill=rgb((0.99, 0.95, 0.88)))
        rrect(d, 120, 280, 960, 980, 8, None, INK, 4)
        d.line([S(540), S(280), S(540), S(980)], fill=INK, width=int(S(4)))
        d.rectangle([0, S(1250), S(W), S(H)], fill=rgb((0.88, 0.72, 0.52)))
        for k in range(8):
            d.line([0, S(1290 + k * 80), S(W), S(1290 + k * 80)], fill=rgb((0.80, 0.64, 0.45)), width=int(S(3)))
        d.ellipse([S(140), S(1400), S(940), S(1640)], fill=rgb((0.62, 0.90, 0.85)))
        rrect(d, 80, 1010, 640, 1220, 40, rgb((0.97, 0.97, 0.95)), INK, 4)
        rrect(d, 60, 1140, 660, 1290, 36, rgb((0.97, 0.97, 0.95)), INK, 4)
        for x, col in ((150, (1.0, 0.62, 0.75)), (330, (1.0, 0.85, 0.40)), (500, (0.62, 0.92, 0.82))):
            rrect(d, x, 1060, x + 130, 1170, 30, rgb(col), INK, 3)
        rrect(d, 860, 1130, 1000, 1300, 12, rgb((0.85, 0.55, 0.35)), INK, 3)
        for k, a in enumerate(np.linspace(-150, -30, 6)):
            r = math.radians(a)
            poly(d, [(930, 1140), (930 + math.cos(r) * 200, 1140 + math.sin(r) * 240), (930 + math.cos(r + 0.18) * 130, 1140 + math.sin(r + 0.18) * 150)], rgb(C['leaf'] if k % 2 else C['leaf_d']), INK, 3)
    elif name == 'cuisine':
        d.rectangle([0, 0, S(W), S(H)], fill=rgb((0.96, 0.98, 1.0)))
        for y in range(0, 1200, 70):
            d.line([0, S(y), S(W), S(y)], fill=rgb((0.82, 0.90, 0.98)), width=int(S(3)))
        for x in range(0, W, 70):
            d.line([S(x), 0, S(x), S(1200)], fill=rgb((0.82, 0.90, 0.98)), width=int(S(3)))
        rrect(d, 300, 260, 780, 760, 8, rgb((0.98, 0.98, 1.0)), INK, 4)
        _sky(d, (0.45, 0.78, 1.0), (0.85, 0.95, 1.0), 640, 280)
        d.rectangle([S(320), S(640), S(760), S(740)], fill=rgb((0.20, 0.60, 0.92)))
        d.rectangle([0, 0, S(300), S(1200)], fill=None)
        rrect(d, 300, 260, 780, 760, 8, None, INK, 4)
        for x in (250, 830):
            d.line([S(x), 0, S(x), S(170)], fill=INK, width=int(S(4)))
            d.chord([S(x - 70), S(150), S(x + 70), S(260)], 180, 360, fill=rgb((1.0, 0.75, 0.30)), outline=INK, width=int(S(4)))
        rrect(d, 0, 1150, W, 1210, 6, rgb((0.92, 0.88, 0.82)), INK, 4)
        d.rectangle([0, S(1210), S(W), S(1560)], fill=rgb((0.62, 0.92, 0.82)))
        for x in range(0, W, 270):
            rrect(d, x + 12, 1230, x + 258, 1540, 10, None, INK, 3)
            d.line([S(x + 110), S(1380), S(x + 160), S(1380)], fill=INK, width=int(S(6)))
        d.rectangle([0, S(1560), S(W), S(H)], fill=rgb((0.90, 0.85, 0.80)))
        rrect(d, 160, 960, 260, 1150, 14, rgb((0.85, 0.92, 1.0), 220), INK, 4)
        rrect(d, 150, 1110, 270, 1150, 8, rgb((0.3, 0.3, 0.35)), INK, 3)
        d.ellipse([S(780), S(1090), S(960), S(1160)], fill=rgb((0.98, 0.98, 0.98)), outline=INK, width=int(S(4)))
    elif name == 'portail':
        _sky(d, (0.04, 0.05, 0.16), (0.12, 0.13, 0.32), 1300)
        rng = np.random.default_rng(9)
        for _ in range(120):
            x, y, r = rng.uniform(0, W), rng.uniform(0, 1100), rng.choice([1.5, 2.2, 3.2])
            circle(d, x, y, r, rgb((0.95, 0.95, 1.0)))
        circle(d, 860, 260, 70, rgb((0.97, 0.96, 0.86)))
        circle(d, 890, 240, 62, rgb((0.10, 0.11, 0.28)))
        d.rectangle([0, S(1300), S(W), S(H)], fill=rgb((0.30, 0.32, 0.42)))
        for _ in range(260):
            x, y = rng.uniform(0, W), rng.uniform(1310, H)
            circle(d, x, y, rng.uniform(2, 5), rgb((0.40, 0.42, 0.52)))
        for x0 in (-60, 760):
            rrect(d, x0, 900, x0 + 380, 1330, 120, rgb((0.10, 0.28, 0.18)), INK, 4)
        for x in (250, 830):
            rrect(d, x - 50, 700, x + 50, 1330, 6, rgb((0.85, 0.82, 0.78)), INK, 4)
            circle(d, x, 690, 40, rgb((0.85, 0.82, 0.78)), INK, 4)
        for x in range(320, 780, 46):
            d.line([S(x), S(820), S(x), S(1320)], fill=rgb((0.12, 0.12, 0.16)), width=int(S(9)))
            poly(d, [(x - 12, 830), (x, 800), (x + 12, 830)], rgb((0.12, 0.12, 0.16)))
        d.line([S(300), S(900), S(780), S(900)], fill=rgb((0.12, 0.12, 0.16)), width=int(S(9)))
        d.line([S(110), S(520), S(110), S(1330)], fill=rgb((0.15, 0.15, 0.20)), width=int(S(16)))
        rrect(d, 70, 470, 150, 540, 12, rgb((1.0, 0.85, 0.45)), INK, 4)
    return finish(img)


@functools.lru_cache(maxsize=2)
def spr_conf_front():
    img, d = canvas(W, H)
    rrect(d, 150, 1130, 930, 1480, 90, rgb((0.98, 0.68, 0.80)), INK, 5)
    rrect(d, 120, 930, 300, 1460, 80, rgb((0.96, 0.62, 0.76)), INK, 5)
    rrect(d, 780, 930, 960, 1460, 80, rgb((0.96, 0.62, 0.76)), INK, 5)
    d.line([S(330), S(1200), S(750), S(1200)], fill=rgb((0.92, 0.58, 0.72)), width=int(S(5)))
    return finish(img)


class Set(Layer):
    """Décor plein écran (opaque). glow : halo du lampadaire (portail)."""
    def __init__(self, name):
        self.name = name

    def draw(self, f, t, dur):
        spr = spr_set(self.name)
        f[:] = spr[..., :3]
        if self.name == 'portail':
            ov = f.copy()
            pts = np.array([[110, 520], [-200, 1500], [520, 1500]], np.int32)
            cv2.fillPoly(ov, [pts], (1.0, 0.85, 0.45))
            f[:] = f * 0.86 + ov * 0.14
        return f


class ConfFront(Layer):
    def draw(self, f, t, dur):
        blit_rgba(f, spr_conf_front(), W / 2, H / 2)
        return f


# ----------------------------------------------------------------------------- habillage télé-réalité
@functools.lru_cache(maxsize=4)
def spr_logo(scale=1.0):
    t1 = text_sprite('VILLA', 'poppins_black', int(150 * scale), (255, 214, 61), int(14 * scale), (22, 23, 58), None, 0, 1000)
    t2 = text_sprite('VITAMINE', 'poppins_black', int(150 * scale), (255, 105, 160), int(14 * scale), (22, 23, 58), None, 0, 1000)
    w = max(t1.shape[1], t2.shape[1]); hgt = t1.shape[0] + t2.shape[0] - int(40 * scale)
    out = np.zeros((hgt, w, 4), np.float32)
    blit_rgba(out, t1, w / 2, t1.shape[0] / 2)
    blit_rgba(out, t2, w / 2, hgt - t2.shape[0] / 2)
    return out


class Logo(Layer):
    """Grand logo de l'émission (générique)."""
    def __init__(self, y=700, t0=0.2, sub=None):
        self.__dict__.update(locals()); del self.__dict__['self']

    def draw(self, f, t, dur):
        if t < self.t0:
            return f
        lt = t - self.t0
        sc = max(0.02, ease_out_back(min(1.0, lt / 0.45)))
        ang = 4 * math.sin(lt * 2.0)
        img = scale_sprite(spr_logo(1.0), sc)
        hh, ww = img.shape[:2]
        M = cv2.getRotationMatrix2D((ww / 2, hh / 2), ang, 1.0)
        img = cv2.warpAffine(img, M, (ww, hh), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
        blit_rgba(f, img, W / 2, self.y)
        if self.sub and lt > 0.5:
            s = text_sprite(self.sub, 'poppins_black', 56, (255, 255, 255), 8, (22, 23, 58), None, 0, 980)
            blit_rgba(f, scale_sprite(s, max(0.02, ease_out_back(min(1.0, (lt - 0.5) / 0.35)))), W / 2, self.y + 250)
        return f


class Bug(Layer):
    """Petit logo de chaîne en haut à gauche (comme à la télé)."""
    def draw(self, f, t, dur):
        blit_rgba(f, scale_sprite(spr_logo(1.0), 0.28), 175, 175, 0.92)
        return f


@functools.lru_cache(maxsize=16)
def spr_nametag(name, role, col):
    n = text_sprite(name, 'poppins_black', 64, (22, 23, 58), 0, (0, 0, 0), None, 0, 900)
    r = text_sprite(role, 'poppins_sb', 40, (90, 90, 110), 0, (0, 0, 0), None, 0, 900)
    w = max(n.shape[1], r.shape[1]) + 90; hgt = n.shape[0] + r.shape[0] + 30
    img, d = canvas(w, hgt)
    rrect(d, 0, 0, w, hgt, 24, rgb((1, 1, 1), 245), INK, 4)
    rrect(d, 0, 0, 34, hgt, 16, rgb(col))
    out = finish(img)
    blit_rgba(out, n, 60 + n.shape[1] / 2, 14 + n.shape[0] / 2)
    blit_rgba(out, r, 60 + r.shape[1] / 2, 14 + n.shape[0] + r.shape[0] / 2 - 4)
    return out


class NameTag(Layer):
    def __init__(self, name, role, col, y=1130, t0=0.25):
        self.__dict__.update(locals()); del self.__dict__['self']

    def draw(self, f, t, dur):
        if t < self.t0:
            return f
        spr = spr_nametag(self.name, self.role, tuple(self.col))
        k = ease_out(min(1.0, (t - self.t0) / 0.35))
        x = -spr.shape[1] / 2 + (60 + spr.shape[1]) * k
        blit_rgba(f, spr, x, self.y)
        return f


class Pill(Layer):
    """Étiquette (compteur « Chutes de Pépin », « Épisode 1 »...)."""
    def __init__(self, text, pos, t0=0.0, col=(1.0, 0.83, 0.24), size=46, tcol=(22, 23, 58)):
        self.__dict__.update(locals()); del self.__dict__['self']

    def draw(self, f, t, dur):
        if t < self.t0:
            return f
        s = text_sprite(self.text, 'poppins_black', self.size, self.tcol, 0, (0, 0, 0), None, 0, 1000)
        w, hgt = s.shape[1] + 60, s.shape[0] + 26
        img, d = canvas(w, hgt)
        rrect(d, 0, 0, w, hgt, hgt / 2, rgb(self.col), INK, 4)
        out = finish(img)
        blit_rgba(out, s, w / 2, hgt / 2)
        sc = max(0.02, ease_out_back(min(1.0, (t - self.t0) / 0.3)))
        blit_rgba(f, scale_sprite(out, sc), self.pos[0], self.pos[1])
        return f


class Prop(Layer):
    """Objet animé (valise, coussin, verre, clé...) : pos/rot en images clés."""
    def __init__(self, spr, pos, rot=0.0, t0=0.0, t1=None, alpha=1.0):
        self.__dict__.update(locals()); del self.__dict__['self']

    def draw(self, f, t, dur):
        if t < self.t0 or (self.t1 is not None and t > self.t1):
            return f
        x, y = kf(self.pos, t) if isinstance(self.pos, list) else self.pos
        ang = kf(self.rot, t) if isinstance(self.rot, list) else self.rot
        img = self.spr() if callable(self.spr) else self.spr
        if abs(ang) > 0.1:
            hh, ww = img.shape[:2]
            M = cv2.getRotationMatrix2D((ww / 2, hh / 2), ang, 1.0)
            cs, sn = abs(M[0, 0]), abs(M[0, 1])
            nw, nh = int(hh * sn + ww * cs) + 2, int(hh * cs + ww * sn) + 2
            M[0, 2] += nw / 2 - ww / 2; M[1, 2] += nh / 2 - hh / 2
            img = cv2.warpAffine(img, M, (nw, nh), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
        blit_rgba(f, img, x, y, self.alpha)
        return f


class Splash(Layer):
    """Éclaboussure de jus (verre qui tombe)."""
    def __init__(self, pos, t0, col=(1.0, 0.62, 0.18)):
        self.__dict__.update(locals()); del self.__dict__['self']

    def draw(self, f, t, dur):
        lt = t - self.t0
        if lt < 0:
            return f
        rng = np.random.default_rng(4)
        for k in range(16):
            a = rng.uniform(math.pi * 1.05, math.pi * 1.95); v = rng.uniform(250, 600)
            x = self.pos[0] + math.cos(a) * v * lt; y = self.pos[1] + math.sin(a) * v * lt + 900 * lt * lt
            if lt < 0.8:
                cv2.circle(f, (int(x), int(y)), int(rng.uniform(6, 14)), self.col, -1, cv2.LINE_AA)
        cv2.ellipse(f, (int(self.pos[0]), int(self.pos[1] + 10)), (int(min(1, lt / 0.3) * 120), int(min(1, lt / 0.3) * 22)), 0, 0, 360, self.col, -1, cv2.LINE_AA)
        return f


class Vignette(Layer):
    """Assombrit les bords (suspense)."""
    def __init__(self, amount=0.5):
        self.amount = amount; self.m = None

    def draw(self, f, t, dur):
        if self.m is None:
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2)
            self.m = (1 - self.amount * np.clip(r / 0.7, 0, 1) ** 2)[..., None]
        f *= self.m
        return f
