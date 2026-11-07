"""NICHE_1 « Vertige Cosmique » — format « flash noir et blanc » (≈ 20 s, sans voix).

Visualisations scientifiques NASA (domaine public) passées en noir et blanc très contrasté, qui s'allument et
s'éteignent sur le temps (stroboscope), barres d'égaliseur sur les côtés, musique phonk originale (audio.compose_phonk).
Une seule phrase-choc discrète au début. Les coupes tombent sur les temps à 120 BPM (1 temps = 0,5 s) :
l'utilisateur peut aussi mettre un son phonk tendance dans l'appli TikTok.
"""
import numpy as np
from layers_base import Composite as C, Fn, Solid
import layers_cine as L
from videos_real import seg, V, BH_DISK, BH_ORBIT, BH_APPROACH, BH_TDE, NSM
from videos_space2 import PULSAR, MAG, MAG_WIDE, SN

BEAT = 0.5   # 120 BPM


def hard_mono(contrast=1.8, gain=1.0):
    """Noir et blanc dur : noirs écrasés, blancs brûlés (×2 pour compenser le tonemap du rendu)."""
    def make():
        def draw(f, t, dur):
            g = (f[..., 0] * 0.3 + f[..., 1] * 0.59 + f[..., 2] * 0.11) * gain
            g = np.clip((g - 0.05) * 1.12, 0, 1)
            g = np.clip((g - 0.42) * contrast + 0.42, 0, 1)
            return np.repeat((g * 2.0)[..., None], 3, axis=2)
        return Fn(draw)
    return make


GAIN = {BH_ORBIT: 2.6, BH_APPROACH: 2.6, SN: 0.5, NSM: 0.6, MAG: 0.7, MAG_WIDE: 0.8}   # sources sombres remontées, sources très claires baissées
FIT = {MAG: 1.5, MAG_WIDE: 1.7}                                                      # objet entier sur fond noir (sinon il remplit l'écran)
CX = {PULSAR: 0.42}


def on(ref_or_scene, at=0.0, n=1.0, speed=1.0, cam='in', **kw):
    """Plan allumé pendant n temps (vidéo NASA en N&B, ou scène calculée)."""
    if isinstance(ref_or_scene, str):
        r = ref_or_scene
        if r in FIT:
            scene = V(r, at, speed=speed, mode='fit0', fit_scale=FIT[r], extra=[hard_mono(gain=GAIN.get(r, 1.0))], **kw)
        else:
            kw.setdefault('cx', CX.get(r, 0.5))
            scene = V(r, at, speed=speed, mode='cover!', extra=[hard_mono(gain=GAIN.get(r, 1.0))], **kw)
    else:
        base = ref_or_scene
        scene = lambda: C(list(base().layers) + [hard_mono()()])
    return seg('', scene, cam, 'cut', hold=round(BEAT * n, 4), music=0.9)


def off(n=1.0):
    return seg('', lambda: C([Solid((0, 0, 0))]), 'static', 'cut', hold=round(BEAT * n, 4), music=0.9)


def flash(n=0.5):
    return seg('', lambda: C([Solid((510, 510, 510))]), 'static', 'cut', hold=round(BEAT * n, 4), music=0.9)


def warp(seed=4):
    return lambda: C([L.StarField(seed=seed, n=2200, bright=1.3, speed=1.1)])


def flashvid(id, title, hook, segs, seed, key=41):
    return dict(id=id, niche='NICHE_1', theme='space', speed=1.0, grain=0.05, vignette=0.45, title=title,
                hook_text=hook, hook_y=1580, hook_min=3.6,
                caption_theme=dict(hook_font='Poppins SemiBold', hook_size=60, hook_color='FFFFFF', hook_box='000000'),
                visualizer=True,
                music=dict(style='phonk', key=key, bpm=120, seed=seed, drop=2, start=0.0, db=-14.0), segments=segs)


FLASH01 = flashvid('flash_01', "Pulsars et étoiles à neutrons", "UN PULSAR PEUT TOURNER\\N716 FOIS PAR SECONDE", [
    # intro (2 mesures, musique filtrée) : 1 temps allumé / 1 temps noir
    on(PULSAR, 1.0), off(), on(MAG, 4.0), off(), on(SN, 11.0, speed=0.6), off(), on(PULSAR, 9.0), off(0.5), flash(0.5),
    # drop
    on(NSM, 13.2, 2, speed=0.8), off(0.5), on(NSM, 18.5, 1), off(0.5), on(SN, 15.0, 1), off(0.5), on(MAG_WIDE, 6.0, 0.5), off(0.5), on(PULSAR, 14.0, 1), off(0.5),
    on(SN, 22.0, 2, speed=0.8), off(0.5), on(NSM, 9.0, 1), off(0.5), on(warp(4), 0, 1), off(0.5), flash(0.5), on(MAG, 18.0, 1), off(0.5),
    on(PULSAR, 4.0, 0.5), off(0.5), on(SN, 30.0, 1), off(0.5), on(NSM, 22.0, 1), off(0.5), on(MAG_WIDE, 16.0, 1), off(0.5),
    on(SN, 34.0, 1), off(0.5), on(NSM, 16.0, 0.5), off(0.5), on(warp(9), 0, 1), off(0.5), on(PULSAR, 18.0, 3, cam='slow_in'), off(1),
], seed=5101, key=41)

FLASH02 = flashvid('flash_02', "Trous noirs", "MÊME LA LUMIÈRE\\NNE S'EN ÉCHAPPE PAS", [
    on(BH_DISK, 2.0), off(), on(BH_ORBIT, 1.0), off(), on(BH_APPROACH, 2.0), off(), on(BH_TDE, 26.0), off(0.5), flash(0.5),
    on(BH_DISK, 16.0, 2, speed=0.8), off(0.5), on(BH_TDE, 30.0, 1), off(0.5), on(BH_ORBIT, 6.0, 1), off(0.5), on(BH_DISK, 8.0, 0.5, zoom=1.5), off(0.5),
    on(BH_TDE, 13.0, 1), off(0.5), on(BH_APPROACH, 8.0, 2, speed=0.9), off(0.5), on(warp(6), 0, 1), off(0.5), flash(0.5), on(BH_DISK, 24.0, 1), off(0.5),
    on(BH_ORBIT, 11.0, 0.5), off(0.5), on(BH_TDE, 33.0, 1), off(0.5), on(BH_DISK, 30.0, 1, zoom=1.3), off(0.5), on(BH_APPROACH, 12.0, 1), off(0.5),
    on(BH_TDE, 20.0, 1), off(0.5), on(BH_ORBIT, 13.0, 0.5), off(0.5), on(warp(12), 0, 1), off(0.5), on(BH_DISK, 33.0, 3, speed=0.5, cam='slow_in'), off(1),
], seed=5201, key=38)

VIDEOS = [FLASH01, FLASH02]
