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



# ============================================================================= format « phrase + ambiance »
# Une seule phrase (fait vérifié) posée sur un diaporama lent d'images NASA/Hubble/Webb, musique d'ambiance, 10–15 s.
import numpy as np
from layers_base import Fn
from videos_real import P, SATURN

CARINA = 'nasa:carina_nebula'                                   # Webb, « falaises cosmiques » de la nébuleuse de la Carène
PILLARS = 'nasa:GSFC_20171208_Archive_e000842'                  # Hubble, piliers de la Création (infrarouge)
HORSEHEAD = 'nasa:GSFC_20171208_Archive_e001518'                # Hubble, nébuleuse de la Tête de Cheval
SUNFLOWER = 'nasa:hubble-sees-a-galactic-sunflower_21136469209_o'  # Hubble, galaxie du Tournesol (M63)
SOMBRERO = 'nasa:PIA15426'                                      # Spitzer/Hubble, galaxie du Sombrero


def mono(contrast=1.15):
    """Noir et blanc contrasté (style « edit » monochrome)."""
    def make():
        def draw(f, t, dur):
            g = f[..., 0] * 0.3 + f[..., 1] * 0.59 + f[..., 2] * 0.11
            g = np.clip((g - 0.5) * contrast + 0.5, 0, 1)
            return np.repeat(g[..., None], 3, axis=2)
        return Fn(draw)
    return make


def still(ref, cx=0.5, cy=0.5, zoom=1.0, bw=True, n=1):
    extra = [mono()] if bw else []
    return seg('', P(ref, cx=cx, cy=cy, zoom=zoom, extra=extra), 'slow_in', 'fade', hold=round(1.5 * n, 3), music=0.8)


AMB01 = dict(
    id='ambiance_01', niche='NICHE_1', theme='space', speed=1.0, grain=0.04, vignette=0.35,
    title="Plus d'étoiles que de grains de sable",
    overlay=dict(text="Il y a plus d'étoiles dans l'Univers\nque de grains de sable\nsur toutes les plages de la Terre.", y=960, size=56),
    music=dict(style='space', prog='minor_drift', key=43, bpm=80, seed=3201, start=0.0),
    segments=[
        still(CARINA, cx=0.45),
        still(PILLARS, cx=0.42, cy=0.5),
        still(SUNFLOWER),
        still(HORSEHEAD, cx=0.45, cy=0.45),
        still(SOMBRERO),
        still(SATURN),
        still(CARINA, cx=0.75, zoom=1.4),
        still(PILLARS, cx=0.5, cy=0.4, zoom=1.6, n=2),
    ])



# ============================================================================= série du 8 au 15 novembre (4 publications par jour)
from videos_real import BH_ORBIT, BH_TDE, BH_PLUNGE, EARTH, ISS, AUR_ISS, BERYL, PV, DAV, VM, MILKYWAY, SUN171, SUN193, SUN131
from videos_space2 import SDO304, SDO131, MAG, PULSAR, APOLLO11, MARS_ROLL
from videos_space3 import MERC, P_PULL, P_SHIELD, EUR, CASSINI, TITAN_PIC, VOY_FLY, HELIO, ENC_JETS

CRAB = 'nasa:PIA03606'
ORION = 'nasa:PIA01322'
HELIX = 'nasa:PIA15658'
RING = 'nasa:southern_ring_nebula'
EARTHSET = 'nasa:art002e021278'          # Artemis II, la Terre se couche derrière la Lune (2026)
NEPTUNE = 'nasa:PIA01492'                # Neptune vue par Voyager 2


F0 = 'fit0'    # cadre entier sur fond noir (sources HD sur fond d'espace)
CV = 'cover!'  # plein écran même pour une source HD (ambiances : pas de bandes floutées)


def clipd(scene, n=1):
    """Plan d'ambiance (vidéo) de n × 1,5 s."""
    return seg('', scene, 'slow_in', 'fade', hold=round(1.5 * n, 3), music=0.8)


def _mono_scene(scene):
    def make():
        c = scene()
        c.layers = list(c.layers) + [mono()()]
        return c
    return make


def amb(id, title, text, segs, seed, prog='minor_drift', key=43, bw=False):
    if bw:
        for sg in segs:
            sg['scene'] = _mono_scene(sg['scene'])
    return dict(id=id, niche='NICHE_1', theme='space', speed=1.0, grain=0.04 if bw else 0.0, vignette=0.35, title=title,
                overlay=dict(text=text, y=960, size=56),
                music=dict(style='space', prog=prog, key=key, bpm=80, seed=seed, start=0.0), segments=segs)


def edit(id, title, hook, end, cuts, seed, prog='minor_epic', key=45):
    segs = list(cuts) + [cut(cuts_end(end), 3, trans='black', cam='slow_in', sfx=['boom'])]
    return dict(id=id, niche='NICHE_1', theme='space', speed=1.0, grain=0.0, vignette=0.3, title=title,
                hook_text=hook, hook_min=1.8, music=dict(style='space', prog=prog, key=key, bpm=BPM, seed=seed, start=0.0), segments=segs)


def cuts_end(text):
    return sc(lambda: L.StarField(seed=7, bright=0.8), lambda: L.Rays(center=MID),
              lambda: L.Globe(night=EARTH_N, r=[(0, 260), (2.8, 330)], c=MID, lon0=10, spin=3.0), final_text(text, t0=0.6))


# ----------------------------------------------------------------------------- format D : phrase + ambiance
AMB02 = amb('ambiance_02', "Le Soleil avec 8 minutes de retard",
            "Tu ne vois jamais le Soleil tel qu'il est.\nSa lumière met 8 minutes\npour arriver jusqu'à toi.",
            [clipd(V(SDO171, 0.0, speed=0.4)), clipd(V(SUN193, 1.0, speed=0.5)), clipd(V(P_PULL, 0.5, speed=0.5)),
             clipd(V(SDO304, 0.0, speed=0.4)), clipd(V(P_PULL, 7.0, speed=0.5)), clipd(V(SUN131, 1.0, speed=0.5)),
             clipd(V(SDO131, 0.0, speed=0.4)), clipd(V(SUN171, 2.0, speed=0.5), 2)], 3301)

AMB03 = amb('ambiance_03', "Une journée plus longue qu'une année",
            "Sur Vénus, une journée\ndure plus longtemps\nqu'une année entière.",
            [clipd(V(PV, 163.0, speed=0.6, mode=CV)), clipd(V(VM, 104.0, speed=0.6, mode=CV)), clipd(V(DAV, 21.5, speed=0.6)),
             clipd(V(PV, 166.0, speed=0.6, mode=CV)), clipd(V(VM, 137.5, speed=0.6, mode=CV)), clipd(V(DAV, 70.0, speed=0.6)),
             clipd(V(PV, 168.5, speed=0.5, mode=CV)), clipd(V(VM, 106.0, speed=0.5, mode=CV), 2)], 3302, key=41)

AMB04 = amb('ambiance_04', "L'espace est à une heure de route",
            "Si tu pouvais rouler en voiture\nvers le ciel, tu serais\ndans l'espace en une heure.",
            [clipd(V(ISS, 606.0, speed=0.8)), clipd(V(ISS, 1830.0, cx=0.85, speed=0.8)), clipd(V(ISS, 990.0, speed=0.8)),
             clipd(V(AUR_ISS, 24.0, speed=0.8)), still(EARTHSET, cx=0.72, bw=False), clipd(V(ISS, 2930.0, speed=0.8)),
             clipd(V(ISS, 1310.0, speed=0.8)), clipd(V(ISS, 3038.0, speed=0.6), 2)], 3303, prog='minor_float', key=45)

AMB05 = amb('ambiance_05', "Les traces de pas sur la Lune",
            "Les traces de pas des astronautes\nsont toujours sur la Lune.\nAucun vent ne peut les effacer.",
            [clipd(V(APOLLO11, 2.0, speed=0.6, mode=CV)), clipd(V(MOONTOUR, 183.0, speed=0.6)), still(EARTHSET, cx=0.72, bw=True),
             clipd(V(APOLLO11, 12.0, speed=0.6, mode=CV)), clipd(V(MOONTOUR, 26.0, speed=0.6)), clipd(V(MOONTOUR, 148.0, speed=0.6)),
             clipd(V(MOONTOUR, 264.0, speed=0.5)), clipd(V(APOLLO11, 8.0, speed=0.5, mode=CV), 2)], 3304, bw=True)

AMB06 = amb('ambiance_06', "Tu es fait d'étoiles",
            "Le carbone, l'oxygène et le fer\nde ton corps ont été fabriqués\ndans des étoiles.",
            [still(CRAB, bw=False), still(ORION, cx=0.45, bw=False), still(HELIX, bw=False), still(RING, cx=0.25, bw=False),
             still(PILLARS, cx=0.42, bw=False), still(CARINA, cx=0.45, bw=False), still(HORSEHEAD, cx=0.45, bw=False),
             still(CRAB, zoom=1.8, bw=False, n=2)], 3305, prog='minor_wonder', key=45)

AMB07 = amb('ambiance_07', "Neptune n'a fait qu'un tour",
            "Depuis sa découverte en 1846,\nNeptune n'a fait qu'un seul tour\ndu Soleil.",
            [still(NEPTUNE, bw=False), clipd(sc(lambda: L.StarField(seed=31, n=1500, bright=1.0, speed=0.35))),
             still(NEPTUNE, zoom=1.6, cy=0.45, bw=False), clipd(V(HELIO, 1.5, speed=0.5)), still(NEPTUNE, zoom=2.4, cx=0.55, cy=0.45, bw=False),
             clipd(sc(lambda: L.StarField(seed=33, bright=0.8, drift=(0, -10)), lambda: L.Halo(center=(W * 0.5, H * 0.32), color=(0.45, 0.65, 1.0), size=1.8))), clipd(sc(lambda: L.StarField(seed=32, bright=0.9), lambda: L.Halo(center=(W / 2, H * 0.3), color=(1.0, 0.88, 0.65), size=2.2))), still(NEPTUNE, bw=False, n=2)], 3306, key=40)

AMB08 = amb('ambiance_08', "Une cuillère d'étoile à neutrons",
            "Une petite cuillère d'étoile à neutrons\npèserait environ\nun milliard de tonnes.",
            [clipd(V(MAG, 3.0, speed=0.6, mode=F0)), clipd(V(PULSAR, 2.0, speed=0.6)), clipd(V(SN, 26.0, speed=0.5)),
             clipd(V(NSM, 11.5, speed=0.5)), clipd(V(MAG, 10.0, speed=0.6, mode=F0)), clipd(V(PULSAR, 7.0, speed=0.6)),
             clipd(V(SN, 30.0, speed=0.5)), clipd(V(NSM, 18.0, speed=0.5), 2)], 3307, prog='minor_dark', key=44)

AMB09 = amb('ambiance_09', "Plus d'arbres que d'étoiles",
            "Il y a plus d'arbres sur Terre\nque d'étoiles\ndans toute la Voie lactée.",
            [clipd(V(EARTH, 30.0, speed=0.6)), clipd(sc(lambda: L.StarField(seed=2, bright=0.8), lambda: L.Globe(night=EARTH_N, r=520, c=MID, lon0=-60, spin=4.0))),
             still(MILKYWAY, bw=False), clipd(V(ISS, 2462.0, speed=0.6)), clipd(sc(lambda: L.StarField(seed=9, bright=0.5), lambda: L.Galaxy(center=MID, r=520, spin=0.1))),
             clipd(V(EARTH, 70.0, speed=0.6)), clipd(V(ISS, 1438.0, speed=0.6)), clipd(V(EARTH, 85.0, speed=0.5), 2)], 3308, prog='minor_float', key=46)

# ----------------------------------------------------------------------------- format C : edits rythmés
EDIT02 = edit('edit_02', "Les trous noirs en 20 secondes", "TU NE VEUX PAS\\NTOMBER ICI", "PERSONNE N'EN EST JAMAIS REVENU.", [
    cut(V(BH_DISK, 2.0), 2, cam='in', sfx=['boom']), cut(V(BH_ORBIT, 1.0, speed=1.2), sfx=['impact']), cut(V(BH_TDE, 12.5, mode=F0)),
    cut(V(BH_TDE, 15.0, mode=F0), trans='flash', sfx=['impact']), cut(V(BH_TDE, 26.0, mode=F0)), cut(V(BH_DISK, 16.0, zoom=1.3)),
    cut(V(BH_ORBIT, 6.0, speed=1.2), trans='zoom', sfx=['whoosh']), cut(V(BH_DISK, 24.0, zoom=1.15)), cut(V(BH_TDE, 30.0, mode=F0)),
    cut(V(BH_ORBIT, 11.0, speed=1.2), trans='flash', sfx=['impact']), cut(V(BH_DISK, 8.0, zoom=1.6)), cut(V(BH_DISK, 30.0, speed=0.6)),
    cut(sc(lambda: L.StarField(seed=21, n=1500, bright=1.0, speed=0.8)), trans='zoom', sfx=['whoosh']), cut(V(BH_DISK, 33.0, speed=0.5)),
    cut(V(BH_TDE, 33.5, mode=F0), sfx=[('riser', 0.0)])], 3401, prog='minor_dark', key=44)

EDIT03 = edit('edit_03', "Le système solaire en 20 secondes", "TON QUARTIER\\NDANS L'UNIVERS", "ET TOUT ÇA TOURNE AUTOUR D'UNE ÉTOILE.", [
    cut(V(SDO171, 0.0, speed=0.8), 2, cam='in', sfx=['boom']), cut(V(MERC, 0.0, mode=F0, fit_scale=2.0), sfx=['impact']),
    cut(V(PV, 166.0, mode=F0)), cut(V(EARTH, 30.0), trans='flash', sfx=['impact']),
    cut(sc(lambda: L.StarField(seed=3, bright=0.8), lambda: L.Globe(day='moon_lroc_4k.jpg', r=600, c=MID, lon0=0, spin=8.0, atmos_w=0.001, spec=0, atmos=(0, 0, 0)))),
    cut(V(MARS_ROLL, 10.0, mode=F0)), cut(V(GRS, 75.0, speed=1.2, mode=F0), trans='zoom', sfx=['whoosh']), cut(V(SAT_RINGS, 9.0)),
    cut(V(SAT_RINGS, 42.0), trans='flash', sfx=['impact']), cut(P(TITAN_PIC)), cut(P(NEPTUNE)),
    cut(V(HELIO, 1.5, speed=1.0), trans='zoom', sfx=['whoosh']), cut(V(MOONTOUR, 183.0, speed=1.5)),
    cut(V(TITAN_TL, 18.0, speed=1.3, mode=CV)), cut(V(ENC_GEY, 2.0, mode=CV), sfx=[('riser', 0.0)])], 3402)

EDIT04 = edit('edit_04', "Le Soleil comme tu ne l'as jamais vu", "NE REGARDE PAS\\NTROP LONGTEMPS", "IL BRÛLE DEPUIS 4,6 MILLIARDS D'ANNÉES.", [
    cut(V(SUN171, 1.0, speed=0.8), 2, cam='in', sfx=['boom']), cut(V(P_PULL, 10.5, speed=1.0), sfx=['impact']), cut(V(SDO304, 0.0, speed=0.8)),
    cut(V(P_SWING, 4.0, speed=1.2, cx=0.4), trans='flash', sfx=['impact']), cut(V(SUN193, 1.0)), cut(V(SDO131, 0.0, speed=0.8)),
    cut(V(P_PULL, 0.3, speed=1.0), trans='zoom', sfx=['whoosh']), cut(V(SUN131, 1.0)), cut(V(P_SHIELD, 0.0, cx=0.15)),
    cut(V(SDO171, 2.0, speed=0.8), trans='flash', sfx=['impact']), cut(V(P_PULL, 2.5, speed=1.0)), cut(V(SUN171, 5.0)),
    cut(V(P_PULL, 6.0, speed=1.0), trans='zoom', sfx=['whoosh']), cut(V(SDO304, 2.0, speed=0.8)), cut(V(SUN193, 6.0), sfx=[('riser', 0.0)])],
    3403, prog='minor_epic', key=47)

EDIT05 = edit('edit_05', "Les lunes les plus folles", "CES LUNES\\NSONT INCROYABLES", "PLUS DE 400 LUNES DANS LE SYSTÈME SOLAIRE.", [
    cut(V(ENC_GEY, 1.0, speed=1.0, mode=CV), 2, cam='in', sfx=['boom']), cut(V(EUR, 566.0, mode='cover!'), sfx=['impact']), cut(V(TITAN_TL, 20.0, speed=1.3, mode=CV)),
    cut(V(MOONTOUR, 183.0, speed=1.5), trans='flash', sfx=['impact']), cut(V(CASSINI, 178.4, speed=0.6, mode=CV, cx=0.56)), cut(P(TITAN_PIC)),
    cut(V(EUR, 459.0, mode='cover!'), trans='zoom', sfx=['whoosh']), cut(V(APOLLO11, 2.0, speed=1.2, mode=CV)), cut(V(ENC_GEY, 6.0, mode=CV)),
    cut(V(TITAN_TL, 28.0, speed=1.3, mode=CV), trans='flash', sfx=['impact']), cut(V(EUR, 593.0, mode='cover!')), cut(V(MOONTOUR, 26.0, speed=1.5)),
    cut(sc(lambda: L.StarField(seed=3, bright=0.8), lambda: L.Globe(day='moon_lroc_4k.jpg', r=700, c=MID, lon0=60, spin=10.0, atmos_w=0.001, spec=0, atmos=(0, 0, 0))), trans='zoom', sfx=['whoosh']),
    cut(P(ENC_JETS)), cut(V(ENC_GEY, 9.0, mode=CV), sfx=[('riser', 0.0)])], 3404, prog='minor_wonder', key=46)

EDIT06 = edit('edit_06', "Ce n'est pas une peinture", "CE N'EST PAS\\NUNE PEINTURE", "CE SONT DE VRAIES IMAGES DE TÉLESCOPES.", [
    cut(P(CARINA, cx=0.45), 2, cam='in', sfx=['boom']), cut(P(PILLARS, cx=0.42), sfx=['impact']), cut(P(CRAB)),
    cut(P(ORION, cx=0.45), trans='flash', sfx=['impact']), cut(P(HELIX)), cut(P(RING, cx=0.25)),
    cut(P(HORSEHEAD, cx=0.45), trans='zoom', sfx=['whoosh']), cut(P(SUNFLOWER)), cut(P(SOMBRERO)),
    cut(P(CARINA, cx=0.75, zoom=1.5), trans='flash', sfx=['impact']), cut(P(CRAB, zoom=2.0)), cut(P(ORION, cx=0.6, cy=0.4, zoom=2.0)),
    cut(P(RING, cx=0.75), trans='zoom', sfx=['whoosh']), cut(P(PILLARS, cx=0.5, cy=0.4, zoom=1.8)), cut(P(HELIX, zoom=1.8), sfx=[('riser', 0.0)])],
    3405, prog='minor_wonder', key=44)

EDIT07 = edit('edit_07', "La Terre vue de l'espace", "TA MAISON\\NVUE D'EN HAUT", "C'EST LA SEULE QU'ON A.", [
    cut(V(ISS, 1830.0, cx=0.85), 2, cam='in', sfx=['boom']), cut(V(AUR_ISS, 24.0), sfx=['impact']), cut(V(BERYL, 46.0, cx=0.36, mode=CV)),
    cut(P(EARTHSET, cx=0.72), trans='flash', sfx=['impact']), cut(V(ISS, 1310.0, speed=1.5)), cut(V(EARTH, 30.0)),
    cut(V(AUR_ISS, 72.0), trans='zoom', sfx=['whoosh']), cut(V(ISS, 2014.0)), cut(V(BERYL, 502.0, cx=0.47, mode=CV)),
    cut(V(ISS, 990.0, speed=1.5), trans='flash', sfx=['impact']), cut(sc(lambda: L.StarField(seed=2, bright=0.8), lambda: L.Globe(night=EARTH_N, r=[(0, 900), (1.0, 640)], c=MID, lon0=-90, spin=6.0))),
    cut(V(ISS, 3038.0)), cut(V(AUR_ISS, 0.0, cx=0.15), trans='zoom', sfx=['whoosh']), cut(V(ISS, 2930.0)), cut(V(EARTH, 70.0), sfx=[('riser', 0.0)])],
    3406, prog='minor_float', key=45)

EDIT08 = edit('edit_08', "Voyage à travers l'Univers", "ACCROCHE-TOI", "BIENVENUE DANS L'UNIVERS.", [
    cut(sc(lambda: L.StarField(seed=21, n=1500, bright=1.0, speed=0.8)), 4, cam='static', sfx=['boom']),
    cut(P(CARINA, cx=0.45), trans='flash', sfx=['impact']), cut(V(BH_DISK, 12.0)), cut(sc(lambda: L.StarField(seed=9, bright=0.5), lambda: L.Galaxy(center=MID, r=[(0, 380), (1.0, 560)], spin=0.4))),
    cut(P(CRAB), trans='flash', sfx=['impact']), cut(P(RING, cx=0.25)), cut(sc(lambda: L.Nebula(seed=5, amount=0.32), lambda: L.DeepField(zoom=(1.0, 1.6)))),
    cut(V(NSM, 14.0), trans='zoom', sfx=['whoosh']), cut(P(ORION, cx=0.45)), cut(V(SN, 24.0)),
    cut(sc(lambda: L.StarField(seed=22, n=1500, bright=1.0, speed=0.8)), 2, trans='zoom', sfx=['whoosh']), cut(P(PILLARS, cx=0.42), sfx=[('riser', 0.0)])],
    3407, prog='minor_epic', key=43)

VIDEOS = [EDIT01, AMB01, AMB02, AMB03, AMB04, AMB05, AMB06, AMB07, AMB08, AMB09, EDIT02, EDIT03, EDIT04, EDIT05, EDIT06, EDIT07, EDIT08]
