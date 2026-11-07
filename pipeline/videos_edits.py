"""NICHE_1 « Vertige Cosmique » — format « space edit » : montage court (≈ 20 s) de plans spectaculaires,
coupés sur le rythme de la musique, sans narration.

La musique incluse est originale (générée). Pour suivre une tendance, l'utilisateur peut remplacer le son
dans l'appli TikTok par un son tendance (bibliothèque TikTok) : les coupes tombent toutes les 2 temps à 128 BPM,
un tempo très courant pour les sons d'edits.
"""
from common import W, H
from layers_base import Composite as C, Text
import layers_cine as L
from videos_real import V, seg, BH_APPROACH, BH_DISK, NSM
from videos_space2 import GRS, SN, MOONTOUR, MARS_TOPO, HELICITY, SDO171
from videos_space3 import SAT_RINGS, ENC_GEY, TITAN_TL, P_SWING

BPM = 128
B2 = 2 * 60.0 / BPM            # une coupe = 2 temps ≈ 0,94 s
EARTH_N = 'earth_night_4k.jpg'
MID = (W / 2, H * 0.46)


def cut(scene, n=1, trans='cut', cam='push', **kw):
    """Plan muet de n × 2 temps."""
    return seg('', scene, cam, trans, hold=round(B2 * n, 4), music=0.95, **kw)


def sc(*makers):
    return lambda: C([m() for m in makers])


def final_text(s, y=1330, t0=0.5):
    return lambda: Text(s, W / 2, y, 118, 'anton', (255, 255, 255), t0=t0, max_width=960)


EDIT01 = dict(
    id='edit_01', niche='NICHE_1', theme='space', speed=1.0, grain=0.0, vignette=0.3,
    title="L'Univers en 20 secondes",
    hook_text="L'UNIVERS EST\\NTERRIFIANT",
    hook_min=1.8,
    music=dict(style='space', prog='minor_epic', key=45, bpm=BPM, seed=3101, start=0.0),
    segments=[
        cut(V(BH_DISK, 12.0), 2, cam='in', sfx=['boom']),
        cut(sc(lambda: L.StarField(seed=2, bright=0.8), lambda: L.Globe(night=EARTH_N, r=[(0, 900), (1.0, 620)], c=MID, lon0=20, spin=6.0)), sfx=['impact']),
        cut(V(GRS, 35.0, speed=1.2)),
        cut(V(SAT_RINGS, 4.0, speed=1.0), trans='flash', sfx=['impact']),
        cut(V(SDO171, 0.0, speed=0.8)),
        cut(V(SN, 22.0, speed=0.9)),
        cut(sc(lambda: L.StarField(seed=9, bright=0.5), lambda: L.Galaxy(center=MID, r=[(0, 380), (1.0, 560)], spin=0.4)), trans='zoom', sfx=['whoosh']),
        cut(V(P_SWING, 4.0, speed=1.2, cx=0.4)),
        cut(V(MOONTOUR, 183.0, speed=1.5)),
        cut(V(ENC_GEY, 2.0, speed=1.0), trans='flash', sfx=['impact']),
        cut(V(TITAN_TL, 18.0, speed=1.3)),
        cut(V(BH_APPROACH, 0.5, speed=1.2)),
        cut(V(NSM, 14.0, speed=0.9), trans='flash', sfx=['impact']),
        cut(V(HELICITY, 2.0, speed=1.2)),
        cut(sc(lambda: L.StarField(seed=21, bright=0.7), lambda: L.Galaxy(center=MID, r=640, tilt=78, roll=-28, spin=0.6, seed=11)), trans='zoom', cam='in', sfx=['whoosh']),
        cut(sc(lambda: L.Filaments(seed=3, grow=[(0, 0.5), (0.9, 1.0)], center=MID, spin=0.5, scale=1.6))),
        cut(V(MARS_TOPO, 14.0, speed=1.4)),
        cut(sc(lambda: L.Nebula(seed=5, amount=0.32), lambda: L.DeepField(zoom=(1.0, 1.6))), sfx=[('riser', 0.0)]),
        cut(sc(lambda: L.StarField(seed=7, bright=0.8), lambda: L.Rays(center=MID),
               lambda: L.Globe(night=EARTH_N, r=[(0, 260), (2.8, 330)], c=MID, lon0=10, spin=3.0),
               final_text("ET NOUS, ON EST LÀ.", t0=0.6)), 3, trans='black', cam='slow_in', sfx=['boom']),
    ])

VIDEOS = [EDIT01]
