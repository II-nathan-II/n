"""Génère une image de couverture 1080×1920 par vidéo (image clé + titre court), à importer comme couverture TikTok."""
import os, sys, subprocess
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import build

COVERS = {  # (index du segment, fraction du plan, texte, couleur)
    'video_01': (0, 0.6, 'IL PLEUT\nDU VERRE ICI', (255, 216, 74)),
    'video_02': (0, 0.2, 'LE SOLEIL\nDISPARAÎT', (255, 216, 74)),
    'video_03': (0, 0.7, '60 GALAXIES\nAU LIEU DE 2 000', (255, 216, 74)),
    'video_04': (0, 0.6, 'TU TOMBES DANS\nUN TROU NOIR', (255, 216, 74)),
    'video_05': (18, 0.5, '1 JOUR\n> 1 AN', (255, 216, 74)),
    'video_06': (0, 0.1, 'FIXE LE POINT\n30 SECONDES', (255, 225, 53)),
    'video_07': (0, 0.1, 'NE QUITTE PAS\nLE CENTRE', (255, 225, 53)),
    'video_08': (11, 0.3, 'TU VAS VOIR\nUN POINT VERT', (255, 225, 53)),
    'video_09': (0, 0.5, "FERME L'ŒIL\nGAUCHE", (255, 225, 53)),
    'video_10': (0, 0.5, 'MÊME\nCOULEUR ?!', (255, 225, 53)),
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
        shots = render.build_shots(v, tl)
        t0 = tl['segments'][si]['start']
        k = max(i for i, sh in enumerate(shots) if sh.start <= t0 + 0.07)
        sh = shots[k]
        t = sh.start + sh.dur * frac
        img = sh.scene.render(t - sh.start, sh.dur)
        if not getattr(sh.scene, 'clean', False):
            img = render.tonemap(np.maximum(img, 0)) * vignette(0.5)
        g = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        img = img * (1 - 0.45 * np.clip((0.32 - g) / 0.32, 0, 1))
        spr = text_sprite(txt, 'anton' if v['theme'] == 'space' else 'poppins_black', 160 if v['theme'] == 'space' else 120, col,
                          10, (0, 0, 0), None, 10, None, 0, 'center')
        blit_rgba(img, spr, W / 2, 330)
        cv2.imwrite(os.path.join(out, f'{vid}_couverture.jpg'), cv2.cvtColor(to_u8(np.clip(img, 0, 1)), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])
        print('couverture', vid, flush=True)

if __name__ == '__main__':
    main()
