"""Version « images réelles » : montage d'extraits NASA / NOAA / Wikimedia Commons (libres de droits).

NICHE_1 « Les secrets de l'Univers » : mêmes scripts vérifiés que la v1, visuels réels.
NICHE_2 « Planète extrême »        : 5 nouveaux scripts sur des phénomènes naturels filmés pour de vrai.
"""
import copy
from common import W, H
from layers_base import Composite, Text, Counter, Bars, Shade, Backdrop, Flash
from layers_space import Thermometer, GlassRain
from layers_footage import Clip, Photo
import videos_space as VS

C = Composite

def V(ref, at=0.0, speed=1.0, mode='cover', cx=0.5, cy=0.5, zoom=1.0, extra=(), flip=False, fit_scale=1.0):
    """Plan vidéo réel + couches éventuelles (créées à chaque appel)."""
    def make():
        return C([Clip(ref, at, speed, mode, cx, cy, zoom, flip, fit_scale=fit_scale)] + [e() for e in extra])
    return make

def P(ref, mode='cover', cx=0.5, cy=0.5, zoom=1.0, extra=()):
    def make():
        return C([Photo(ref, mode, cx, cy, zoom)] + [e() for e in extra])
    return make

def txt(s, y=330, size=120, color=(255, 216, 74), t0=0.2, **kw):
    return lambda: Text(s, W / 2, y, size, 'anton', color, t0=t0, max_width=960, **kw)

def back(y0=180, y1=560, a=0.55):
    return lambda: Backdrop(y0, y1, a)

def counter(v0, v1, **kw):
    return lambda: Counter(v0, v1, **kw)

def shade(a0, a1=None, t0=0.0, t1=1.0, color=(0, 0, 0)):
    return lambda: Shade(a0, a1, t0, t1, color)

def remap(old, scenes, **over):
    """Reprend une vidéo v1 (texte, emphases, sons, étiquettes) en remplaçant les plans."""
    v = copy.copy(old)
    v.update(over)
    segs = []
    assert len(scenes) == len(old['segments']), (old['id'], len(scenes), len(old['segments']))
    for s, sc in zip(old['segments'], scenes):
        n = {k: s[k] for k in s if k not in ('scene', 'cam', 'trans')}
        if sc == 'same':
            n['scene'] = 'same'
        else:
            scene, cam, trans = sc
            n.update(scene=scene, cam=cam, trans=trans)
        segs.append(n)
    v['segments'] = segs
    return v

# ----------------------------------------------------------------------------- sources (NASA SVS / NASA Image Library / Commons)
BH_DISK = 'svs:13326/Black_Hole_Accretion_Disk_Sim_4k.mp4'
BH_PLUNGE = 'svs:14576/14576_BH_Plunge_Zoom2b_4k60.mp4'
BH_TDE = 'svs:12005/12005_Swift_Tidal_Music_MPEG4_1920X1080_2997.mp4'
BH_APPROACH = 'svs:14620/2-Approaching_a_bare_black_hole-4K.mp4'
BH_ORBIT = 'svs:14620/1-Orbiting_a_bare_black_hole-4K.mp4'
HOTJ = 'svs:13635/kelt9_planet_CU.mp4'
HOTJ_ORBIT = 'svs:13635/kelt9_wide_orbit.mp4'
HD189 = 'svs:11686/11019-540-MASTER_high.mp4'
WEBB_SPEC = 'svs:14799/WEBB_Wasp_107_Spectrum_VERT.mp4'
HUBBLE = 'svs:20314/HST_BP_Two_2160p60.mp4'
SUN171 = 'svs:14592/20240514_AR13664X87_171A_4k.mp4'
SUN193 = 'svs:14592/20240514_AR13664X87_193A_4k.mp4'
SUN131 = 'svs:14592/20240514_AR13664X87_131A_4k.mp4'
ART_HD = 'nasa:PIA10364'
EARTH = 'svs:5570/Earth_wAtmos_spin_02_2160p30.mp4'
NSM = 'svs:12740/12740_NS_Merger_4k_Update_H264.mp4'
MOON = 'svs:5587/phases_2026_fancy_2160p30.mp4'
ISS = 'nasar:jsc2021m000138_4K_Earth_Views_Extended_Cut_for_Earth_Day_ 2021_210422-4KMP4'
JUPITER = 'svs:12021/G2015-085_Jupiter4k_MASTER_YouTube.mp4'
SATURN = 'nasa:PIA06594'
MILKYWAY = 'nasa:PIA10748'
MILKYWAY2 = 'nasa:PIA10748'
OU = 'svs:14749/OpenUniverseFullZoom_4k_Best.mp4'
OUSN = 'svs:14749/OpenUniverseSuperNovaTimeLapse_5k.mp4'
WEB = 'svs:10118/CosmicWeb4_HD_LARGE_QT_Video_1.mp4'
REION = 'svs:10663/Re-Ionization-Galaxy_Evolution-tracking_shot-1080p.mov'
PV = 'svs:14095/14095_ParkerVenus_YouTube_NoText_NoMusic.mp4'
DAV = 'svs:14735/DAVINCI_REEL_1.mp4'
VM = 'svs:13972/13972_venusmysteries.mp4'
BERYL = 'nasar:jsc2024m000130_Expedition_71_International_Space_Station_Flyover_of_Hurricane_Beryl_240701'
MILTON_ISS = 'nasar:jsc2024m000173_International_Space_Station_Cameras_Capture_New_Views_Of_Hurricane_Milton_241008'
HELENE = 'nasar:iss072m262701649_Live_Views_of_Hurricane_Helene_from_the_International_Space_Station_240926'
FRANKLIN = 'nasar:Expedition_69_Space_Station_Flies_Over_Hurricane_Franklin_Replay'
MILTON_VIZ = 'svs:5401/milton_v02_1080p30.mp4'
MILTON_RAIN = 'svs:5401/Milton1008_1080p30.mp4'
HHTH = 'svs:14214/HHTH_Final.mp4'
GW_TONGA = 'svs:31277/hunga_tonga_btemp_diff_g17_b08_crop_2160p15.mp4'
GW3 = 'svs:31277/hunga_tonga_three_geo_sats_1080p15.mp4'
TONGA_CU = 'commons:File:Close-Up View of Hunga Tonga-Hunga Ha‘apai Eruption (CIRA 2022-01-15 - nolabels).webm'
TONGA_BROAD = 'commons:File:Broad View of Hunga Tonga-Hunga Ha‘apai Eruption (CIRA 2022-01-15 - nolabels).webm'
CIRA_LIGHT = 'commons:File:Lightning Flashes From Line of Thunderstorms at Night (CIRA 2026-03-16 - nolabels portrait).webm'
ESO_SPRITES = 'commons:File:ESOcast 81 - Red Sprites.webm'
RED_SPRITE = 'commons:File:Red Sprite.ogv'
SPRITE_ISS = 'svs:11059/ISS-540-MASTER_high.mp4'
ROLLA = 'commons:File:Lightning Storm in Rolla.webm'
BLITZE = 'commons:File:Blitze während Tief Lambert in Hof (Saale), 20230622 001.webm'
AUR_ISS = 'svs:31375/ISS_20251112_071350-20251112_073549_2160p30.mp4'
AUR_AUS = 'svs:31281/ISS067_20220817_aurora_2160p25.mp4'
AUR_MAY = 'svs:14835/BillDunford_May2024Aurora2_H264.mp4'
ENLIL = 'svs:5375/enlil_BMag_anicamA.mp4'
STEVE_ANIM = 'nasa:GSFC_20180314_Aurora_m12865_Steve'
GZ1 = 'svs:4849/GodzillaShot1_3840x2160p30.mp4'
GZ2 = 'svs:4849/GodzillaShot2_3840x2160p30.mp4'
CAL_T = 'nasa:GSFC_20150224_CALIPSO_m11775_Dust_Transport'
CAL_MAP = 'nasa:GSFC_20150224_CALIPSO_m11775_Sahara_Map'
CAL_SD = 'nasa:GSFC_20150224_CALIPSO_m11775_Saharan_Dust_CloseUp'
CAL_AM = 'nasa:GSFC_20150224_CALIPSO_m11775_Amazon_Transport_CloseUp'
AMZ = 'nasa:GSFC_20180612_Amazon_m12982_Lidar_2018yr'
MARS = 'nasa:PIA16026'
GW17 = 'svs:31277/hunga_tonga_btemp_diff_g17_b08_2160p15.mp4'
GW16 = 'svs:31277/hunga_tonga_btemp_diff_g16_b08_2160p15.mp4'
SC311 = 'nasa:311_ScienceCasts-observing-lightning-ISS'
IAN = 'svs:5131/Hurricane_Ian_comp_v03_4k_1080p60.mp4'
AFRC_ER2 = "nasa:AFRC_2023_14007_02_Studying Thunderstorms with NASA’s ER-2 Aircraft_HD"
DCOTSS = 'nasa:AFRC-2022-13772-ER-2_DCOTTS_VideoFile_May2022'
TGF = 'svs:10706/10706_Fermi_TGF_H264_Best_1280x720_59.94.mov'
TGF2 = 'svs:10707/10707_Fermi_Spots_TGF_MPEG4_1280X720_29.97.mp4'

REAL = dict(grain=0.006, vignette=0.38)

# ============================================================================= NICHE 1 — vidéos 01 à 05
R01 = remap(VS.V01, [
    (V(HOTJ, 0.5, cx=0.62), 'in', 'cut'),
    (V(HOTJ, 5.0, speed=1.6, cx=0.55, zoom=1.5, extra=[lambda: GlassRain(n=160, alpha=0.35, speed=3000)]), 'drift', 'whip'),
    (P(ART_HD, cx=0.5), 'slow_in', 'zoom'),
    (V(OU, 3.0, speed=0.3), 'push', 'flash'),
    (V(HD189, 116.0, mode='fit', fit_scale=1.35), 'left', 'fade'),
    (V(HOTJ, 8.5, cx=0.6, zoom=1.25), 'drift', 'cut'),
    (V(HOTJ_ORBIT, 1.0, zoom=1.1), 'slow_in', 'whip'),
    (V(HD189, 38.5, mode='fit', fit_scale=1.25, extra=[back(950, 1250, 0.5), txt('13 FOIS PLUS PRÈS', 1110, 96)]), 'in', 'zoom'),
    (V(HOTJ_ORBIT, 8.0, speed=1.5), 'out', 'cut'),
    (P(ART_HD, cx=0.45, zoom=1.2), 'left', 'fade'),
    (V(HOTJ, 10.0, cx=0.68, zoom=1.15, extra=[back(170, 520), txt('+1 000 °C', 330, 150, (255, 140, 70))]), 'in', 'cut'),
    (V(HOTJ, 1.5, speed=2.2, cx=0.6, zoom=1.4, extra=[lambda: GlassRain(n=120, angle=-4, alpha=0.35, speed=3400)]), 'drift', 'whip'),
    (V(SUN171, 1.0, zoom=1.0, extra=[shade(0.0, 0.5, 0.5, 2.5)]), 'push', 'black'),
    (V(HUBBLE, 1.0), 'slow_in', 'flash'),
    'same',
    (V(HOTJ, 3.5, cx=0.6, cy=0.45, zoom=1.7), 'in', 'zoom'),
    (V(HOTJ, 11.0, cx=0.62, cy=0.5, zoom=2.0), 'drift', 'cut'),
    (V(HOTJ, 0.0, speed=2.5, cx=0.6, zoom=1.3, extra=[lambda: GlassRain(n=380, alpha=0.6, speed=3400)]), 'right', 'whip'),
    (V(WEBB_SPEC, 0.3, speed=0.6), 'slow_in', 'zoom'),
    (V(WEBB_SPEC, 1.5, speed=0.5, zoom=1.15, extra=[back(980, 1240, 0.5), txt('H2S', 1110, 150, (255, 230, 120))]), 'in', 'cut'),
    'same',
    (P(ART_HD, cx=0.5), 'out', 'fade'),
    (V(HD189, 116.0, mode='fit', fit_scale=1.35), 'slow_in', 'whip'),
], theme='space', **REAL)

R02 = remap(VS.V02, [
    (V(SUN193, 0.0, extra=[shade(0.0, 1.0, 2.6, 3.4)]), 'in', 'cut'),
    (V(EARTH, 8.0), 'slow_in', 'fade'),
    (V(ISS, 592.0, cx=0.55), 'up', 'whip'),
    (V(SUN193, 3.0, zoom=0.9, extra=[back(560, 960, 0.6), counter(0, 500, y=760, size=230, fmt='time', color=(255, 225, 120), sub='150 millions de km', t0=0.2, ease='inout')]), 'static', 'zoom'),
    (V(EARTH, 40.0), 'push', 'black'),
    (V(EARTH, 62.0, extra=[txt('?', 760, 260)]), 'in', 'flash'),
    (V(NSM, 2.5, speed=0.8), 'drift', 'zoom'),
    (V(NSM, 8.0, speed=0.8), 'slow_in', 'flash'),
    (V(NSM, 14.0, speed=0.7), 'in', 'cut'),
    (V(EARTH, 80.0, extra=[shade(0.0, 0.92, 1.4, 2.2)]), 'slow_in', 'black'),
    (V(MOON, 164.0, zoom=1.0, extra=[shade(0.0, 0.92, 1.6, 2.4)]), 'in', 'fade'),
    (V(EARTH, 70.0, speed=2.0, extra=[shade(0.6)]), 'right', 'whip'),
    (V(OU, 3.0, speed=0.3), 'up', 'fade'),
    (V(JUPITER, 8.0, extra=[back(180, 520), txt('+1 h', 330, 150), shade(0.0, 0.9, 2.2, 3.0)]), 'static', 'cut'),
    (P(SATURN, cx=0.5, extra=[back(180, 520), txt('+2 h', 330, 150), shade(0.0, 0.9, 2.0, 3.2)]), 'static', 'fade'),
    (V(ISS, 2958.0, extra=[shade(0.25, color=(30, 60, 110)), back(180, 520), counter(15, -73, y=330, size=170, suffix=' °C', color=(170, 220, 255), t0=0.3)]), 'in', 'flash'),
    (V(ISS, 2563.0, extra=[shade(0.3, color=(20, 40, 80))]), 'drift', 'fade'),
    (V(ISS, 1617.0, extra=[shade(0.62, color=(0, 12, 40))]), 'down', 'zoom'),
    'same',
    (V(SUN171, 2.0), 'out', 'flash'),
    (V(EARTH, 30.0), 'static', 'whip'),
], theme='space', **REAL)

R03 = remap(VS.V03, [
    (V(OU, 1.0, speed=0.6), 'in', 'cut'),
    (V(OU, 6.0, speed=0.6, extra=[lambda: __import__('layers_space').Constellation(VS.BOOTES_STARS, VS.BOOTES_LINES, 'LE BOUVIER')]), 'slow_in', 'fade'),
    (V(OU, 12.0, speed=0.6, extra=[back(170, 520), txt('1981', 330, 170)]), 'slow_in', 'whip'),
    (V(OU, 18.0, speed=0.8, extra=[back(520, 1000, 0.6), counter(0, 330, y=700, size=300, color=(255, 216, 74), sub="millions d'années-lumière", t1=2.2)]), 'in', 'zoom'),
    (P(MILKYWAY, cx=0.5, extra=[back(950, 1230, 0.5), txt('× 3 000', 1090, 140)]), 'right', 'whip'),
    (V(OU, 36.0, speed=0.5, extra=[back(520, 1000, 0.6), counter(0, 2000, y=760, size=280, t1=2.0, sub='galaxies attendues')]), 'slow_in', 'fade'),
    (V(OU, 2.0, speed=0.5, extra=[back(520, 1000, 0.6), counter(2000, 60, y=760, size=280, t0=0.6, t1=1.6, color=(255, 90, 90), sub='galaxies trouvées', ease='inout')]), 'in', 'cut'),
    (V(OU, 3.0, speed=0.4), 'out', 'black'),
    (P(MILKYWAY2, cx=0.5, extra=[shade(0.35)]), 'slow_in', 'fade'),
    (P(MILKYWAY2, cx=0.5, zoom=1.3), 'push', 'zoom'),
    (V(OU, 5.0, speed=0.3), 'up', 'fade'),
    (V(OUSN, 8.0, extra=[txt('?!', 760, 320, (255, 80, 80))]), 'drift', 'glitch'),
    (V(WEB, 2.0), 'slow_in', 'flash'),
    'same',
    (V(WEB, 20.0), 'in', 'zoom'),
    'same',
    (V(OU, 40.0, speed=0.5), 'push', 'cut'),
    (P(MILKYWAY, cx=0.42, zoom=1.15), 'left', 'whip'),
    (V(WEB, 40.0), 'slow_in', 'fade'),
], theme='space', **REAL)

R04 = remap(VS.V04, [
    (V(BH_DISK, 2.0), 'in', 'cut'),
    (V(BH_ORBIT, 1.0), 'slow_in', 'whip'),
    (V(BH_APPROACH, 0.5), 'in', 'zoom'),
    (V(BH_TDE, 10.0), 'down', 'fade'),
    (V(BH_TDE, 17.0, extra=[]), 'in', 'cut'),
    (V(BH_TDE, 23.0, extra=[lambda: Flash(0.5, (255, 200, 150), 0.5, 0.8)]), 'push', 'flash'),
    (V(BH_DISK, 12.0), 'slow_in', 'zoom'),
    (V(BH_DISK, 18.0, extra=[back(170, 560), counter(0, 4000000, y=340, size=150, sub='masses solaires', t1=2.2, color=(255, 216, 74))]), 'static', 'cut'),
    (V(BH_PLUNGE, 0.0, speed=0.7), 'down', 'fade'),
    (V(BH_APPROACH, 8.0, extra=[back(980, 1240, 0.5), txt('POINT DE NON-RETOUR', 1110, 84, t0=1.0)]), 'in', 'cut'),
    (V(BH_ORBIT, 6.0), 'out', 'whip'),
    (V(BH_DISK, 30.0, speed=0.35), 'static', 'fade'),
    (V(BH_DISK, 33.0, speed=0.3, extra=[shade(0.0, 0.55, 0.3, 4.0, (255, 30, 10)), shade(0.0, 0.7, 1.5, 6.0)]), 'slow_in', 'fade'),
    'same',
    (V(BH_PLUNGE, 10.0, speed=0.8), 'down', 'whip'),
    (V(BH_ORBIT, 11.0), 'drift', 'zoom'),
    (V(BH_PLUNGE, 28.0, speed=0.8), 'push', 'black'),
    (V(BH_PLUNGE, 36.0, speed=0.6), 'in', 'cut'),
    (V(BH_DISK, 16.0, zoom=1.3), 'push', 'flash'),
    (V(BH_DISK, 3.0), 'slow_in', 'whip'),
], theme='space', **REAL)

R05 = remap(VS.V05, [
    (V(PV, 163.0), 'in', 'cut'),
    (V(PV, 14.5, cx=0.3), 'drift', 'whip'),
    (V(PV, 168.0, extra=[shade(0.45), lambda: Bars([('1 tour sur elle-même', 243, (255, 190, 90)), ('1 tour du Soleil', 225, (110, 180, 255))], 243, y0=720, t0=0.3, t1=7.5)]), 'static', 'zoom'),
    'same',
    (V(DAV, 23.5, extra=[lambda: Text('OUEST', 170, 1110, 70, 'anton'), lambda: Text('EST', W - 150, 1110, 70, 'anton')]), 'slow_in', 'fade'),
    (V(PV, 37.0, cx=0.45), 'slow_in', 'whip'),
    (V(VM, 137.0, extra=[lambda: Flash(0.1, (255, 120, 40), 0.6, 0.7)]), 'push', 'cut'),
    (V(VM, 198.0, extra=[shade(0.5), lambda: Thermometer()]), 'static', 'fade'),
    (V(SUN171, 4.0, extra=[back(170, 560), txt('2× PLUS LOIN', 330, 120)]), 'in', 'zoom'),
    (V(VM, 108.0, extra=[back(170, 520), txt('96 % DE CO2', 330, 130)]), 'slow_in', 'fade'),
    (V(VM, 104.0), 'up', 'whip'),
    (V(DAV, 69.0, extra=[back(170, 560), txt('= 900 M SOUS L\'EAU', 330, 110)]), 'static', 'slide'),
    (V(VM, 137.5), 'slow_in', 'fade'),
    (V(VM, 198.5, extra=[shade(0.35), back(200, 640), counter(0, 127, y=420, size=230, suffix=' min', color=(255, 216, 74), t1=2.0)]), 'in', 'cut'),
    (V(DAV, 70.0), 'right', 'flash'),
    (V(DAV, 24.0, extra=[shade(0.0, 0.85, 0.3, 2.4)]), 'slow_in', 'glitch'),
    (V(PV, 89.0), 'push', 'black'),
    (V(VM, 106.0), 'slow_in', 'flash'),
    (V(DAV, 21.5), 'in', 'whip'),
    'same',
    (V(PV, 165.0), 'out', 'fade'),
], theme='space', **REAL)

# ============================================================================= NICHE 2 — « Planète extrême »
def seg(text, scene='same', cam=None, trans='cut', **kw):
    d = dict(text=text, scene=scene, cam=cam, trans=trans); d.update(kw); return d

R06 = dict(
    id='video_06', niche='NICHE_2', theme='earth', speed=1.08, voice_reverb=0.05, **REAL,
    title='Un ouragan vu depuis la Station spatiale',
    hook_text='UN OURAGAN\\NVU DE L\'ESPACE',
    music=dict(style='space', prog='minor_epic', key=45, bpm=78, seed=601, start=0.3),
    segments=[
        seg("Voici ce que voient les astronautes quand un ouragan passe sous la Station spatiale.", V(BERYL, 46.0, cx=0.45), 'in', sfx=['boom'], music=0.35, emph=['ouragan']),
        seg("On est à {400|quatre cents} kilomètres d'altitude, et cette spirale de nuages fait plusieurs centaines de kilomètres de large.", V(BERYL, 410.0, cx=0.4), 'slow_in', 'whip', label='400 KM D\'ALTITUDE'),
        seg("Celui-ci, c'est Beryl, en juillet {2024|deux mille vingt-quatre} : le premier ouragan de catégorie cinq jamais observé aussi tôt dans la saison atlantique.", V(BERYL, 502.0, cx=0.5), 'in', 'zoom', label='BERYL • JUILLET 2024', emph=['Beryl']),
        seg("Et l'énergie qu'il libère est vertigineuse.", V(FRANKLIN, 318.0, cx=0.5), 'push', 'cut', sfx=[('riser', 0.0)], music=0.6),
        seg("Un ouragan moyen dégage, sous forme de chaleur, l'équivalent de cinquante à deux cents fois toute la capacité électrique de la planète.",
            V(FRANKLIN, 388.0, cx=0.45, extra=[back(170, 560), txt('× 50 À 200', 330, 140)]), 'slow_in', 'flash', emph=['cinquante', 'deux', 'cents']),
        seg("Il peut déverser plus de {9 000 milliards|neuf mille milliards} de litres de pluie… en une seule journée.",
            V(MILTON_RAIN, 0.5, speed=0.6, extra=[back(170, 560), txt('9 000 MILLIARDS DE LITRES', 330, 96)]), 'in', 'zoom', emph=['9 000 milliards']),
        seg("Tout commence au-dessus d'un océan chauffé à plus de {26 °C|vingt-six degrés}.", V(HELENE, 38.0, cx=0.55, extra=[back(170, 520), txt('+26 °C', 330, 160, (255, 140, 70))]), 'slow_in', 'fade', emph=['26 °C']),
        seg("L'air chaud et humide s'élève, se refroidit, et la vapeur se transforme en nuages… en libérant sa chaleur.", V(MILTON_ISS, 18.0, cx=0.5), 'up', 'whip'),
        seg("Cette chaleur aspire encore plus d'air vers le haut. Le moteur s'emballe.", V(MILTON_ISS, 57.0, cx=0.45), 'push', 'cut', emph=['emballe']),
        seg("Et la rotation de la Terre fait tourner l'ensemble : dans le sens inverse des aiguilles d'une montre au nord… et dans l'autre sens au sud.",
            V(FRANKLIN, 34.0, cx=0.5), 'tilt', 'zoom', music=0.7),
        seg("Au centre, il y a ce trou parfait : l'œil.", V(BERYL, 44.0, cx=0.42, zoom=1.6), 'in', 'cut', sfx=['impact'], emph=['œil']),
        seg("Là-dedans, le vent tombe presque à zéro… et on peut parfois apercevoir le ciel bleu.", V(BERYL, 48.0, cx=0.42, zoom=2.0), 'slow_in', 'fade'),
        seg("Mais tout autour, dans le mur de l'œil, soufflent les vents les plus violents : plus de {250 km/h|deux cent cinquante kilomètres par heure} en catégorie cinq.",
            V(FRANKLIN, 320.0, cx=0.5, zoom=1.4, extra=[back(170, 520), txt('250 KM/H', 330, 160, (255, 120, 80))]), 'push', 'whip', emph=['250 km/h']),
        seg("En octobre {2024|deux mille vingt-quatre}, les vents de l'ouragan Milton ont augmenté de plus de {140 km/h|cent quarante kilomètres par heure} en vingt-quatre heures.",
            V(MILTON_ISS, 95.0, cx=0.5), 'in', 'flash', label='MILTON • OCTOBRE 2024', emph=['140 km/h'], music=0.85),
        seg("Les scientifiques appellent ça l'intensification rapide. Et avec des océans plus chauds, elle devient plus fréquente.", V(MILTON_VIZ, 4.0, speed=0.7), 'slow_in', 'zoom', emph=['intensification', 'rapide']),
        seg("Ouragan, typhon, cyclone : c'est en réalité le même phénomène. Seul le nom change selon l'océan.", V(EARTH, 70.0), 'drift', 'fade', music=0.5),
        seg("Et vu d'en haut, c'est l'une des choses les plus belles… et les plus terrifiantes de notre planète.", V(BERYL, 594.0, cx=0.45), 'slow_in', 'whip'),
        seg("Tu as déjà vécu une tempête ou un cyclone ? Raconte en commentaire.", V(BERYL, 138.0, cx=0.5), 'out', 'fade', music=0.3),
    ])

R07 = dict(
    id='video_07', niche='NICHE_2', theme='earth', speed=1.08, voice_reverb=0.05, **REAL,
    title='Hunga Tonga : l\'explosion la plus puissante jamais mesurée',
    hook_text='L\'EXPLOSION LA PLUS\\NPUISSANTE JAMAIS MESURÉE',
    music=dict(style='space', prog='minor_dark', key=43, bpm=72, seed=701, start=0.3),
    segments=[
        seg("Le {15|quinze} janvier {2022|deux mille vingt-deux}, un volcan sous-marin a explosé avec une puissance jamais enregistrée par nos instruments modernes.",
            V(HHTH, 17.0, speed=0.35), 'in', sfx=['boom'], music=0.35, emph=['explosé']),
        seg("Son nom : Hunga Tonga-Hunga Haʻapai, dans le Pacifique Sud.", V(EARTH, 17.0), 'slow_in', 'whip', label='PACIFIQUE SUD • TONGA'),
        seg("Regarde ces images satellites : en quelques minutes, une colonne de cendres a jailli de l'océan.", V(HHTH, 17.3, speed=0.35, zoom=1.3), 'in', 'zoom'),
        seg("Elle est montée jusqu'à {57|cinquante-sept} kilomètres d'altitude. Plus haut que n'importe quel panache volcanique jamais observé.",
            V(HHTH, 18.0, speed=0.3, zoom=1.1, extra=[back(170, 560), counter(0, 57, y=340, size=200, suffix=' km', color=(255, 140, 70), t1=2.0)]), 'push', 'cut', emph=['57']),
        seg("Selon la NASA, l'explosion était des centaines de fois plus puissante que la bombe d'Hiroshima.", V(HHTH, 18.6, speed=0.3, zoom=1.6, extra=[lambda: Flash(0.2, (255, 220, 180), 0.5, 0.9)]), 'in', 'flash', sfx=['impact'], emph=['centaines']),
        seg("L'onde de choc a fait plusieurs fois le tour de la Terre.", V(GW_TONGA, 0.0, speed=0.55), 'slow_in', 'zoom', emph=['plusieurs', 'fois'], music=0.6),
        seg("En France aussi, les baromètres l'ont enregistrée.", V(GW_TONGA, 1.5, speed=0.6, zoom=1.5, cx=0.4), 'drift', 'whip', emph=['France']),
        seg("Son bruit a été entendu jusqu'en Alaska, à près de dix mille kilomètres.", V(GW_TONGA, 1.0, speed=0.5, zoom=1.2), 'in', 'cut'),
        seg("Un tsunami a traversé tout l'océan Pacifique, jusqu'aux côtes du Pérou.", V(EARTH, 21.0), 'right', 'fade'),
        seg("Pendant l'éruption, les satellites ont compté jusqu'à {2 600|deux mille six cents} éclairs par minute. Un record absolu.",
            V(SC311, 10.0, extra=[back(170, 560), txt('2 600 ÉCLAIRS / MIN', 330, 110)]), 'in', 'flash', emph=['2 600'], music=0.75),
        seg("Mais le plus étrange, ce n'est pas l'explosion. C'est ce qu'elle a envoyé dans le ciel.", V(ISS, 592.0), 'push', 'black', sfx=[('riser', 0.0)]),
        seg("Pas seulement des cendres : de l'eau.", V(ISS, 1065.0), 'in', 'cut', emph=['eau']),
        seg("Environ {146 millions|cent quarante-six millions} de tonnes de vapeur d'eau, propulsées dans la stratosphère.",
            V(ISS, 986.0, extra=[back(170, 560), counter(0, 146, y=340, size=200, suffix=' Mt', color=(120, 200, 255), t1=2.0)]), 'slow_in', 'zoom', emph=['146 millions'], music=0.9),
        seg("De quoi remplir plus de {58 000|cinquante-huit mille} piscines olympiques.", V(ISS, 1144.0, extra=[back(170, 560), txt('58 000 PISCINES', 330, 130, (120, 200, 255))]), 'in', 'whip', emph=['58 000']),
        seg("Cela a augmenté d'environ dix pour cent la quantité d'eau présente dans toute la stratosphère.", V(ISS, 39.0), 'up', 'fade', emph=['dix']),
        seg("Et cette eau va y rester plusieurs années, avec des effets que les scientifiques étudient encore.", V(ISS, 118.0), 'slow_in', 'zoom'),
        seg("Et l'île ? Avant l'éruption, la NASA l'étudiait pour mieux comprendre… certains paysages de Mars.", P(MARS, cx=0.5), 'slow_in', 'fade', music=0.5),
        seg("En une seule matinée, elle a presque entièrement disparu.", V(HHTH, 17.0, speed=0.3, zoom=1.8), 'out', 'cut', emph=['disparu']),
        seg("Tu avais entendu parler de cette éruption ? Dis-le en commentaire.", V(GW_TONGA, 2.5, speed=0.5, zoom=1.15, cx=0.6), 'slow_in', 'fade', music=0.3),
    ])

R08 = dict(
    id='video_08', niche='NICHE_2', theme='earth', speed=1.08, voice_reverb=0.05, **REAL,
    title='Ce qui se passe au-dessus des orages',
    hook_text='CE QUI SE PASSE\\NAU-DESSUS DES ORAGES',
    music=dict(style='space', prog='minor_float', key=46, bpm=76, seed=801, start=0.3),
    segments=[
        seg("Ce flash rouge au-dessus des nuages, ce n'est pas un effet spécial. Il a été filmé depuis la Station spatiale.", V(SPRITE_ISS, 18.0, mode='fit', fit_scale=1.5), 'in', sfx=['boom'], music=0.35, emph=['rouge']),
        seg("Ça s'appelle un sprite. Et pendant longtemps, presque personne n'y croyait.", V(SC311, 62.0, cx=0.45), 'slow_in', 'whip', label='SPRITE', emph=['sprite']),
        seg("Les pilotes de ligne en parlaient depuis des décennies. Mais aucune preuve… jusqu'en {1989|mille neuf cent quatre-vingt-neuf}.", V(DCOTSS, 437.0), 'slow_in', 'fade', emph=['1989']),
        seg("Cette année-là, des chercheurs de l'université du Minnesota en ont filmé un par hasard, en testant une caméra.", V(SC311, 11.0), 'in', 'zoom', label='1989 • MINNESOTA'),
        seg("Un sprite, c'est une décharge électrique géante qui jaillit vers le haut, entre {50|cinquante} et {90|quatre-vingt-dix} kilomètres d'altitude.",
            V(SC311, 152.0, cx=0.45, extra=[back(170, 520), txt('50 À 90 KM', 330, 150, (255, 90, 90))]), 'slow_in', 'cut', emph=['vers', 'le', 'haut']),
        seg("Il dure à peine quelques millisecondes. Voilà pourquoi personne ne le voyait.", V(SPRITE_ISS, 20.0, mode='fit', fit_scale=1.5, speed=0.5), 'in', 'flash', emph=['millisecondes']),
        seg("Et ce n'est qu'un des secrets de la foudre.", V(SC311, 33.0), 'push', 'black', sfx=[('riser', 0.0)], music=0.6),
        seg("Sur Terre, il tombe environ {44|quarante-quatre} éclairs… chaque seconde.", V(IAN, 6.0, speed=0.8, extra=[back(170, 560), counter(0, 44, y=340, size=220, suffix=' /s', color=(255, 230, 120), t1=1.6)]), 'in', 'cut', emph=['44']),
        seg("Un éclair peut atteindre {30 000 °C|trente mille degrés} : cinq fois plus chaud que la surface du Soleil.",
            V(SC311, 243.0, extra=[back(170, 520), txt('30 000 °C', 330, 160, (255, 230, 120))]), 'in', 'flash', sfx=['impact'], emph=['30 000 °C']),
        seg("Le record ? Un seul éclair de {829|huit cent vingt-neuf} kilomètres de long, au-dessus des États-Unis, en {2017|deux mille dix-sept}.",
            V(IAN, 14.0, speed=0.8, extra=[back(170, 560), txt('829 KM', 330, 170)]), 'slow_in', 'zoom', emph=['829'], music=0.8),
        seg("Plus que la distance entre Paris et Marseille.", V(AFRC_ER2, 193.0), 'in', 'cut'),
        seg("Et ça devient encore plus fou : certains orages produisent… des rayons gamma.", V(TGF, 71.0), 'push', 'glitch', emph=['gamma']),
        seg("En {2011|deux mille onze}, un télescope spatial de la NASA a même détecté de l'antimatière, projetée vers l'espace par des orages.", V(TGF2, 11.5, cx=0.62), 'slow_in', 'zoom', emph=['antimatière'], music=0.9),
        seg("L'endroit le plus foudroyé de la planète ? Le lac Maracaibo, au Venezuela.", V(EARTH, 4.0), 'in', 'fade', label='LAC MARACAIBO • VENEZUELA'),
        seg("Les orages y éclatent plus de {140|cent quarante} nuits par an.", V(SC311, 242.0), 'drift', 'whip', emph=['140']),
        seg("Les marins l'appelaient même : le phare de Maracaibo.", V(AFRC_ER2, 196.0, zoom=1.2), 'slow_in', 'fade', music=0.5),
        seg("Tu as déjà vu un éclair tomber tout près de toi ? Raconte en commentaire.", V(SPRITE_ISS, 24.0, mode='fit', fit_scale=1.5), 'out', 'whip', music=0.3),
    ])

R09 = dict(
    id='video_09', niche='NICHE_2', theme='earth', speed=1.08, voice_reverb=0.05, **REAL,
    title='Les aurores boréales vues depuis l\'espace',
    hook_text='LES AURORES\\NVUES DE L\'ESPACE',
    music=dict(style='space', prog='minor_wonder', key=48, bpm=70, seed=901, start=0.3),
    segments=[
        seg("Voici des aurores boréales… vues d'en haut, depuis la Station spatiale.", V(AUR_ISS, 16.0, cx=0.5), 'in', sfx=['shimmer'], music=0.35, emph=['aurores']),
        seg("Pour les astronautes, ce rideau de lumière ondule juste sous leurs pieds.", V(AUR_AUS, 14.0, cx=0.5), 'slow_in', 'whip'),
        seg("Mais d'où vient cette lumière ?", V(AUR_ISS, 48.0, cx=0.45), 'push', 'cut'),
        seg("Tout commence sur le Soleil, à {150 millions|cent cinquante millions} de kilomètres.", V(SUN193, 1.0), 'in', 'zoom', emph=['Soleil']),
        seg("Il projette en permanence des particules électriques dans l'espace : le vent solaire.", V(ENLIL, 2.0, speed=0.8), 'slow_in', 'fade', emph=['vent', 'solaire']),
        seg("Parfois, une éruption en envoie des milliards de tonnes d'un coup… vers nous.", V(SUN131, 3.0, zoom=1.2), 'push', 'flash', sfx=['impact'], music=0.6),
        seg("Le champ magnétique de la Terre nous protège… mais près des pôles, il guide une partie de ces particules vers l'atmosphère.", V(STEVE_ANIM, 41.0), 'slow_in', 'zoom', emph=['pôles']),
        seg("En percutant l'air, entre {100|cent} et {300|trois cents} kilomètres d'altitude, elles font briller les gaz.", V(STEVE_ANIM, 56.0), 'in', 'fade'),
        seg("L'oxygène donne le vert… et le rouge tout en haut. L'azote donne les teintes bleues et violettes.", V(AUR_AUS, 24.0, cx=0.5), 'up', 'whip', emph=['vert', 'rouge', 'bleues', 'violettes'], music=0.75),
        seg("En mai {2024|deux mille vingt-quatre}, la tempête solaire la plus forte depuis vingt ans a fait descendre les aurores très au sud.", V(AUR_MAY, 0.0, speed=0.45), 'slow_in', 'flash', label='10 MAI 2024'),
        seg("On les a vues partout en France, jusque sur la Côte d'Azur.", V(AUR_MAY, 1.8, speed=0.45, zoom=1.2), 'in', 'cut', emph=['France']),
        seg("Mais en {1859|dix-huit cent cinquante-neuf}, il y a eu bien pire : l'événement de Carrington.", V(SUN131, 6.0), 'push', 'black', label='1859', sfx=[('riser', 0.0)]),
        seg("Des aurores visibles jusqu'aux Caraïbes, et des télégraphes qui crépitaient d'étincelles.", V(ENLIL, 14.0, speed=0.8), 'slow_in', 'zoom', emph=['Caraïbes'], music=0.9),
        seg("Aujourd'hui, une tempête de cette ampleur pourrait perturber satellites, GPS et réseaux électriques.", V(AUR_ISS, 68.0, cx=0.5), 'drift', 'fade', emph=['GPS']),
        seg("Et en {2018|deux mille dix-huit}, des photographes amateurs ont même aidé la NASA à étudier une lueur inconnue, violette et rectiligne… qu'ils ont baptisée STEVE.",
            V(AUR_AUS, 36.0, cx=0.5), 'slow_in', 'whip', label='STEVE', music=0.5),
        seg("Tu les as vues en mai {2024|deux mille vingt-quatre} ? Dis-moi d'où en commentaire.", V(AUR_ISS, 58.0, cx=0.5), 'out', 'fade', music=0.3),
    ])

R10 = dict(
    id='video_10', niche='NICHE_2', theme='earth', speed=1.08, voice_reverb=0.05, **REAL,
    title='Le Sahara nourrit l\'Amazonie',
    hook_text='LE SAHARA NOURRIT\\NL\'AMAZONIE',
    music=dict(style='space', prog='minor_drift', key=50, bpm=74, seed=1001, start=0.3),
    segments=[
        seg("Chaque année, le plus grand désert chaud du monde nourrit la plus grande forêt tropicale du monde.", V(GZ1, 28.0, cx=0.48), 'in', sfx=['boom'], music=0.35, emph=['désert', 'forêt']),
        seg("Et ce n'est pas une image : c'est une découverte des satellites de la NASA.", V(CAL_T, 9.0, speed=0.8), 'slow_in', 'whip'),
        seg("Regarde ces nuages orange : c'est de la poussière du Sahara, soulevée par le vent.", V(GZ2, 34.0, cx=0.55), 'in', 'zoom', emph=['poussière']),
        seg("Environ {182 millions|cent quatre-vingt-deux millions} de tonnes s'envolent chaque année.",
            V(GZ2, 30.0, cx=0.55, extra=[back(170, 560), counter(0, 182, y=340, size=200, suffix=' Mt', color=(255, 200, 110), t1=2.0)]), 'push', 'cut', emph=['182 millions']),
        seg("Elles traversent tout l'océan Atlantique, sur des milliers de kilomètres.", V(CAL_SD, 0.5, speed=0.6), 'right', 'whip'),
        seg("Et environ {28 millions|vingt-huit millions} de tonnes retombent sur l'Amazonie.",
            V(CAL_AM, 0.5, speed=0.6, extra=[back(170, 560), counter(0, 28, y=340, size=200, suffix=' Mt', color=(140, 230, 120), t1=2.0)]), 'in', 'zoom', emph=['28 millions'], music=0.6),
        seg("Pourquoi c'est important ? Parce que le sol de l'Amazonie est étonnamment pauvre.", V(AMZ, 7.0), 'slow_in', 'fade', emph=['pauvre']),
        seg("Les pluies torrentielles lessivent sans cesse ses nutriments, notamment le phosphore, indispensable aux plantes.", V(AMZ, 22.0), 'up', 'whip', emph=['phosphore']),
        seg("Or, la poussière du Sahara en apporte environ {22 000|vingt-deux mille} tonnes par an… à peu près ce que la forêt perd.",
            V(CAL_T, 15.0, speed=0.7, extra=[back(170, 560), txt('22 000 TONNES / AN', 330, 110, (140, 230, 120))]), 'in', 'flash', emph=['22 000'], music=0.75),
        seg("Et le plus incroyable, c'est d'où vient ce phosphore.", V(CAL_MAP, 0.5, speed=0.6), 'push', 'black', sfx=[('riser', 0.0)]),
        seg("Une grande partie de la poussière part d'un seul endroit : la dépression du Bodélé, au Tchad.", V(CAL_MAP, 3.0, speed=0.6, zoom=1.4, cx=0.52, cy=0.42), 'in', 'zoom', label='BODÉLÉ • TCHAD', emph=['Bodélé']),
        seg("Il y a des milliers d'années, c'était le fond d'un immense lac.", V(CAL_MAP, 5.0, speed=0.6, zoom=1.6, cx=0.52, cy=0.42), 'slow_in', 'fade', emph=['lac']),
        seg("Le phosphore vient des restes de micro-organismes qui y vivaient.", V(CAL_SD, 4.0, speed=0.6), 'in', 'cut', music=0.9),
        seg("Autrement dit, une forêt vivante est en partie nourrie par les restes d'un ancien lac du Sahara.", V(AMZ, 9.0, speed=0.8), 'slow_in', 'whip'),
        seg("Et parfois, cette poussière arrive jusqu'à nous : les ciels orange et les voitures couvertes de sable en France, c'est elle.", V(GZ1, 14.0, cx=0.55), 'drift', 'fade', emph=['France'], music=0.6),
        seg("En juin {2020|deux mille vingt}, un nuage de poussière si énorme qu'on l'a surnommé « Godzilla » a même atteint les États-Unis.", V(GZ1, 44.0, cx=0.42), 'in', 'zoom', label='JUIN 2020 • « GODZILLA »', emph=['Godzilla']),
        seg("Tu as déjà retrouvé ta voiture couverte de sable du Sahara ? Dis-le en commentaire.", V(GZ2, 40.0, cx=0.5), 'out', 'fade', music=0.3),
    ])

for _v, _n in ((R01, 'NICHE_1'), (R02, 'NICHE_1'), (R03, 'NICHE_1'), (R04, 'NICHE_1'), (R05, 'NICHE_1')):
    _v['niche'] = _n

VIDEOS = [R01, R02, R03, R04, R05, R06, R07, R08, R09, R10]
