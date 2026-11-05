"""Textures planétaires procédurales (équirectangulaires 2:1) — entièrement générées, libres de droits."""
import json, functools, os
import numpy as np
import cv2
from common import fbm_noise, palette_map, smoothstep, ridged, ASSETS

TW, TH = 2048, 1024


def _lat():
    return np.linspace(np.pi / 2, -np.pi / 2, TH, dtype=np.float32)[:, None] * np.ones((1, TW), np.float32)


def _warped(seed, beta=2.2, amp=0.08):
    n = fbm_noise(TH, TW, beta=beta, seed=seed)
    w1 = fbm_noise(TH, TW, beta=2.6, seed=seed + 11)
    w2 = fbm_noise(TH, TW, beta=2.6, seed=seed + 12)
    yy, xx = np.mgrid[0:TH, 0:TW].astype(np.float32)
    mx = (xx + (w1 - 0.5) * amp * TW) % TW
    my = np.clip(yy + (w2 - 0.5) * amp * TH, 0, TH - 1)
    return cv2.remap(n, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)


@functools.lru_cache(maxsize=8)
def gas_giant(seed=1, palette='cobalt'):
    lat = _lat()
    turb = fbm_noise(TH, TW, beta=2.4, seed=seed)
    fine = fbm_noise(TH, TW, beta=1.6, seed=seed + 5)
    # écoulement en bandes : on étire le bruit horizontalement
    turb_h = cv2.resize(cv2.resize(turb, (TW // 16, TH)), (TW, TH), interpolation=cv2.INTER_CUBIC)
    bands = np.sin(lat * 9 + (turb_h - 0.5) * 4.0 + np.sin(lat * 23) * 0.6) * 0.5 + 0.5
    v = bands * 0.6 + fine * 0.15 + turb * 0.25
    pals = {
        'cobalt': [(0, (8, 24, 80)), (0.35, (20, 60, 160)), (0.6, (40, 110, 220)), (0.8, (100, 170, 255)), (1, (200, 230, 255))],
        'jupiter': [(0, (90, 50, 30)), (0.35, (170, 110, 70)), (0.6, (220, 180, 140)), (0.8, (240, 225, 200)), (1, (255, 250, 240))],
        'saturn': [(0, (120, 100, 60)), (0.5, (210, 180, 120)), (1, (250, 235, 190))],
    }
    tex = palette_map(v, pals[palette])
    # tempêtes ovales
    rng = np.random.default_rng(seed)
    for _ in range(5):
        cx, cy = rng.uniform(0, TW), rng.uniform(TH * 0.25, TH * 0.75)
        rx, ry = rng.uniform(40, 110), rng.uniform(18, 40)
        yy, xx = np.ogrid[0:TH, 0:TW]
        d = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
        m = np.exp(-d * 1.5)[..., None]
        tex = tex * (1 - m * 0.5) + m * 0.5 * (tex * 1.4 + 0.1)
    return np.clip(tex, 0, 1.2).astype(np.float32)


@functools.lru_cache(maxsize=2)
def land_mask():
    path = os.path.join(ASSETS, 'geo', 'ne_50m_land.geojson')
    g = json.load(open(path))
    m = np.zeros((TH, TW), np.uint8)
    def tr(ring):
        a = np.array(ring, np.float64)
        x = (a[:, 0] + 180) / 360 * TW; y = (90 - a[:, 1]) / 180 * TH
        return (np.stack([x, y], 1) * 8).astype(np.int32)
    for feat in g['features']:
        geom = feat['geometry']
        polys = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
        for poly in polys:
            cv2.fillPoly(m, [tr(poly[0])], 255, cv2.LINE_AA, 3)
            for hole in poly[1:]:
                cv2.fillPoly(m, [tr(hole)], 0, cv2.LINE_AA, 3)
    return m.astype(np.float32) / 255


@functools.lru_cache(maxsize=4)
def earth(frozen=False, seed=3):
    land = cv2.GaussianBlur(land_mask(), (0, 0), 0.8)
    lat = _lat()
    n = fbm_noise(TH, TW, beta=2.0, seed=seed)
    n2 = fbm_noise(TH, TW, beta=1.4, seed=seed + 1)
    alat = np.abs(lat) / (np.pi / 2)
    ocean = palette_map(n * 0.4 + (1 - alat) * 0.3, [(0, (3, 18, 55)), (0.5, (8, 45, 110)), (1, (20, 80, 150))])
    green = palette_map(n2, [(0, (30, 70, 25)), (0.5, (60, 100, 40)), (1, (110, 120, 70))])
    desert = palette_map(n2, [(0, (150, 120, 70)), (1, (210, 180, 130))])
    dry = smoothstep(0.55, 0.75, n) * (1 - smoothstep(0.35, 0.55, alat)) * smoothstep(0.08, 0.2, alat)
    landc = green * (1 - dry[..., None]) + desert * dry[..., None]
    ice = smoothstep(0.78, 0.86, alat + (n - 0.5) * 0.08)
    if frozen:
        landc = palette_map(n2, [(0, (200, 215, 230)), (1, (245, 250, 255))])
        ocean = palette_map(n, [(0, (120, 160, 190)), (0.5, (170, 205, 225)), (1, (210, 235, 245))])
        cracks = (ridged(fbm_noise(TH, TW, beta=1.7, seed=seed + 7)) > 0.97).astype(np.float32)
        ocean = ocean * (1 - 0.35 * cracks[..., None])
        ice = np.ones_like(ice) * 0.0
    tex = ocean * (1 - land[..., None]) + landc * land[..., None]
    tex = tex * (1 - ice[..., None]) + np.array([0.92, 0.95, 1.0]) * ice[..., None]
    return tex.astype(np.float32)


@functools.lru_cache(maxsize=4)
def clouds(seed=9, cover=0.55):
    n = _warped(seed, beta=2.0, amp=0.06)
    lat = _lat()
    band = 0.5 + 0.5 * np.cos(lat * 6)
    c = smoothstep(cover - 0.05, cover + 0.25, n * 0.8 + band * 0.2)
    return c.astype(np.float32)


@functools.lru_cache(maxsize=4)
def venus(seed=4):
    lat = _lat()
    n = _warped(seed, beta=2.3, amp=0.12)
    streak = cv2.resize(cv2.resize(fbm_noise(TH, TW, beta=2.0, seed=seed + 3), (TW // 24, TH)), (TW, TH))
    v = n * 0.55 + streak * 0.3 + (np.cos(lat * 3) * 0.5 + 0.5) * 0.15
    # motif en Y caractéristique
    yy = lat / (np.pi / 2)
    xx = np.linspace(0, 2 * np.pi, TW, dtype=np.float32)[None, :]
    v += 0.08 * np.sin(xx * 2 + np.abs(yy) * 4)
    tex = palette_map(v, [(0, (120, 80, 30)), (0.4, (190, 145, 70)), (0.7, (230, 200, 130)), (1, (255, 245, 210))])
    return tex.astype(np.float32)


@functools.lru_cache(maxsize=4)
def sun(seed=2):
    g = fbm_noise(TH, TW, beta=0.9, seed=seed)
    g2 = fbm_noise(TH, TW, beta=2.2, seed=seed + 1)
    v = g * 0.5 + g2 * 0.5
    tex = palette_map(v, [(0, (200, 60, 5)), (0.4, (250, 130, 20)), (0.7, (255, 190, 60)), (1, (255, 240, 170))])
    rng = np.random.default_rng(seed)
    yy, xx = np.ogrid[0:TH, 0:TW]
    for _ in range(6):
        cx, cy, r = rng.uniform(0, TW), rng.uniform(TH * 0.3, TH * 0.7), rng.uniform(6, 16)
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        tex *= (1 - 0.75 * np.exp(-(d / r) ** 2))[..., None]
    return (tex * 1.5).astype(np.float32)


@functools.lru_cache(maxsize=4)
def rocky(seed=5, palette='grey'):
    n = fbm_noise(TH, TW, beta=2.2, seed=seed)
    r = ridged(fbm_noise(TH, TW, beta=1.9, seed=seed + 1))
    v = n * 0.6 + r * 0.4
    pals = {'grey': [(0, (40, 38, 36)), (0.5, (110, 105, 100)), (1, (190, 185, 175))],
            'red': [(0, (60, 20, 10)), (0.5, (150, 70, 35)), (1, (220, 150, 100))]}
    tex = palette_map(v, pals[palette])
    rng = np.random.default_rng(seed)
    yy, xx = np.ogrid[0:TH, 0:TW]
    for _ in range(60):
        cx, cy, rr = rng.uniform(0, TW), rng.uniform(0, TH), rng.uniform(4, 30)
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / rr
        rim = np.exp(-((d - 1) * 4) ** 2) * 0.25 - np.exp(-(d * 1.4) ** 2) * 0.2
        tex = tex * (1 + rim[..., None])
    return np.clip(tex, 0, 1).astype(np.float32)
