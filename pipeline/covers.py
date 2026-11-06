"""Génère une image de couverture 1080×1920 par vidéo (image clé + titre court), à importer comme couverture TikTok."""
import os, sys, subprocess
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import build

COVERS = {  # (index du segment, fraction du plan, texte, couleur)
    'video_01': (0, 0.5, 'IL PLEUT\nDU VERRE ICI', (255, 216, 74)),
    'video_02': (0, 0.25, 'LE SOLEIL\nDISPARAÎT', (255, 216, 74)),
    'video_03': (0, 0.5, '60 GALAXIES\nAU LIEU DE 2 000', (255, 216, 74)),
    'video_04': (0, 0.5, 'TU TOMBES DANS\nUN TROU NOIR', (255, 216, 74)),
    'video_05': (0, 0.5, '1 JOUR\n> 1 AN', (255, 216, 74)),
    'video_06': (0, 0.5, "UN OURAGAN\nVU DE L'ESPACE", (255, 216, 74)),
    'video_07': (2, 0.5, "100× PLUS\nPUISSANT\nQU'HIROSHIMA", (255, 216, 74)),
    'video_08': (0, 0.5, "CE N'EST PAS UN\nEFFET SPÉCIAL", (255, 216, 74)),
    'video_09': (0, 0.5, "LES AURORES\nVUES DE L'ESPACE", (255, 216, 74)),
    'video_10': (0, 0.5, "LE SAHARA NOURRIT\nL'AMAZONIE", (255, 216, 74)),
    'video_11': (0, 0.5, "1 CUILLÈRE =\n1 MILLIARD DE TONNES", (255, 216, 74)),
    'video_12': (0, 0.5, "LA LUNE\nS'ÉLOIGNE", (255, 216, 74)),
    'video_13': (1, 0.5, "LE VOLCAN\nGÉANT DE MARS", (255, 216, 74)),
    'video_14': (1, 0.5, "PLUS GRANDE\nQUE LA TERRE", (255, 216, 74)),
    'video_15': (0, 0.5, "CETTE LUMIÈRE\nA 100 000 ANS", (255, 216, 74)),
}

def main():
    import json, render
    vids = build.all_videos()
    out = os.path.join(PROJECT, 'PUBLICATION', 'couvertures')
    os.makedirs(out, exist_ok=True)
    for vid, (si, frac, txt, col) in COVERS.items():
        v = vids[vid]
        tlp = os.path.join(WORK, vid, f'{vid}_timeline.json')
        if not os.path.exists(tlp):
            continue
        tl = json.load(open(tlp))
        shots = render.build_shots(v, tl, setup=False)
        t0 = tl['segments'][si]['start']
        k = max(i for i, sh in enumerate(shots) if sh.start <= t0 + 0.07)
        sh = shots[k]
        sh.scene.setup(sh.dur)
        t = sh.start + sh.dur * frac
        img = sh.scene.render(t - sh.start, sh.dur)
        if not getattr(sh.scene, 'clean', False):
            img = render.tonemap(np.maximum(img, 0)) * vignette(v.get('vignette', 0.4))
        g = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        img = img * (1 - 0.45 * np.clip((0.32 - g) / 0.32, 0, 1))
        size = 150 if v['theme'] != 'psy' else 120
        while True:  # le titre doit tenir dans 92 % de la largeur
            spr = text_sprite(txt, 'anton' if v['theme'] != 'psy' else 'poppins_black', size, col,
                              10, (0, 0, 0), None, 10, None, 0, 'center')
            if spr.shape[1] <= W * 0.92 or size <= 90:
                break
            size -= 6
        blit_rgba(img, spr, W / 2, max(330, spr.shape[0] / 2 + 150))  # titre sous la zone d'interface TikTok
        cv2.imwrite(os.path.join(out, f'{vid}_couverture.jpg'), cv2.cvtColor(to_u8(np.clip(img, 0, 1)), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])
        print('couverture', vid, flush=True)

if __name__ == '__main__':
    main()
