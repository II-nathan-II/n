"""Couvertures « affiche de film » pour Villa Vitamine (1080×1920).

Grand titre doré en relief, « Épisode N » au-dessus, petit logo de la série en haut.
Tout le texte tient dans la zone centrale 3:4 (y 240–1680) : c'est ce que montre la grille du profil TikTok.

Usage : python3 covers_villa.py fond.jpg sortie.jpg "LA NOUVELLE" "Épisode 2"
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
SERIF = '/opt/assets/fonts/DMSerifDisplay-Regular.ttf'
SANS = '/opt/assets/fonts/Poppins-ExtraBold.ttf'
GOLD = [(255, 247, 196), (255, 222, 120), (240, 180, 50), (196, 124, 20), (250, 214, 110), (255, 240, 170)]


def cover_fit(img):
    """Recadre l'image en 9:16 et la met à 1080×1920."""
    w, h = img.size
    tr = W / H
    if w / h > tr:
        nw = int(h * tr)
        img = img.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w / tr)
        img = img.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    return img.resize((W, H), Image.LANCZOS)


def gradient(h, stops):
    """Dégradé vertical métallique de hauteur h."""
    ys = np.linspace(0, 1, h)
    xs = np.linspace(0, 1, len(stops))
    arr = np.stack([np.interp(ys, xs, [c[i] for c in stops]) for i in range(3)], axis=1)
    return arr.astype(np.uint8)


def fit_font(text, path, max_w, size, min_size=60):
    while size > min_size:
        f = ImageFont.truetype(path, size)
        if f.getbbox(text)[2] - f.getbbox(text)[0] <= max_w:
            return f
        size -= 4
    return ImageFont.truetype(path, min_size)


def gold_line(canvas, text, font, cy, depth=12):
    """Écrit une ligne de titre dorée en relief, centrée en x, centrée verticalement sur cy."""
    bb = font.getbbox(text)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x = (W - tw) // 2 - bb[0]
    y = cy - th // 2 - bb[1]
    # masque du texte
    mask = Image.new('L', (W, H), 0)
    ImageDraw.Draw(mask).text((x, y), text, font=font, fill=255)
    stroke = Image.new('L', (W, H), 0)
    ImageDraw.Draw(stroke).text((x, y), text, font=font, fill=255, stroke_width=7)
    # ombre portée
    shadow = stroke.filter(ImageFilter.GaussianBlur(14))
    canvas.paste((0, 0, 0), (10, 16), shadow.point(lambda v: int(v * 0.85)))
    # relief (extrusion brun-or vers le bas)
    for k in range(depth, 0, -1):
        shade = int(70 + 50 * (1 - k / depth))
        canvas.paste((shade + 40, shade, 10), (0, k), stroke)
    # contour sombre
    canvas.paste((58, 32, 6), (0, 0), stroke)
    # remplissage doré
    top, bot = y + bb[1], y + bb[3]
    g = gradient(max(bot - top, 2), GOLD)
    fill = np.zeros((H, W, 3), np.uint8)
    fill[top:bot] = g[:, None, :]
    canvas.paste(Image.fromarray(fill), (0, 0), mask)
    # reflet clair en haut des lettres
    hi = mask.filter(ImageFilter.GaussianBlur(1)).point(lambda v: v)
    hi_shift = Image.new('L', (W, H), 0)
    hi_shift.paste(hi, (0, 3))
    edge = Image.fromarray(np.clip(np.asarray(mask, np.int16) - np.asarray(hi_shift, np.int16), 0, 255).astype(np.uint8))
    canvas.paste((255, 255, 235), (0, 0), edge.point(lambda v: int(v * 0.8)))
    return th


def soft_text(canvas, text, font, cy, color=(255, 255, 255), stroke_col=(40, 22, 4), sw=4):
    bb = font.getbbox(text)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x = (W - tw) // 2 - bb[0]
    y = cy - th // 2 - bb[1]
    sh = Image.new('L', (W, H), 0)
    ImageDraw.Draw(sh).text((x, y), text, font=font, fill=255, stroke_width=sw + 2)
    canvas.paste((0, 0, 0), (4, 8), sh.filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * 0.8)))
    ImageDraw.Draw(canvas).text((x, y), text, font=font, fill=color, stroke_width=sw, stroke_fill=stroke_col)


def make_cover(bg, out, title, label, title_bottom=1560):
    img = cover_fit(Image.open(bg).convert('RGB'))
    # assombrit le bas pour que le titre ressorte
    grad = np.clip((np.arange(H) - 950) / 750, 0, 1) ** 1.3 * 0.62
    arr = np.asarray(img, np.float32) * (1 - grad[:, None, None])
    img = Image.fromarray(arr.astype(np.uint8))
    # titre : 1 ou 2 lignes (séparées par « | »)
    lines = [t.strip() for t in title.split('|')]
    fonts = [fit_font(l, SERIF, 980, 230 if len(lines) == 1 else 190) for l in lines]
    heights = [f.getbbox(l)[3] - f.getbbox(l)[1] for f, l in zip(fonts, lines)]
    gap = 26
    total = sum(heights) + gap * (len(lines) - 1)
    y = title_bottom - total
    lab_font = ImageFont.truetype(SERIF, 78)
    soft_text(img, label, lab_font, y - 70, color=(255, 255, 255), stroke_col=(60, 34, 6), sw=3)
    for f, l, h in zip(fonts, lines, heights):
        gold_line(img, l, f, y + h // 2)
        y += h + gap
    # logo de la série en haut (dans la zone visible de la grille)
    logo_font = ImageFont.truetype(SANS, 46)
    soft_text(img, 'VILLA VITAMINE', logo_font, 300, color=(255, 214, 90), stroke_col=(70, 30, 0), sw=4)
    img.save(out, quality=93)
    return out


if __name__ == '__main__':
    make_cover(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else '')
