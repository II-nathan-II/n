"""NICHE_1 « Vertige Cosmique » — format « animation 2D » (explication illustrée, 60–80 s, voix off).

Illustrations plates dessinées par nos soins (layers_flat), un mot à la fois au centre, grands nombres qui « pop ».
Le récit compare les grandeurs à des objets du quotidien. Plus d'une minute : éligible Creator Rewards.
Faits vérifiés (sources dans docs.SOURCES).
"""
from common import W, H
from layers_base import Composite
import layers_flat as F
from videos_real import seg

P = F.PAL
MID = (W / 2, 900)
JUP = ((0.10, 0.10, (0.78, 0.50, 0.30)), (0.30, 0.08, (0.96, 0.84, 0.64)), (0.48, 0.12, (0.74, 0.44, 0.24)), (0.70, 0.07, (0.96, 0.84, 0.64)))


def fs(*makers):
    """Scène « dessin animé » (couleurs exactes : pas d'étalonnage)."""
    return lambda: Composite([F.FlatBG()] + [m() for m in makers], clean=True)


def spr(fn, *a, **k):
    return lambda: fn(*a, **k)


def S_(sprite, pos, **kw):
    return lambda: F.Sprite(sprite, pos, **kw)


def big(text, y=430, t0=0.2, **kw):
    return lambda: F.Big(text, y, t0, **kw)


def small(text, x, y, t0=0.3, color=P['white'], size=60):
    return lambda: F.Sprite(spr(F.spr_text, text, size, color, 8), (x, y), t0=t0, pop=0.3)


FOOT = spr(F.spr_football, 170)
FOOT_S = spr(F.spr_football, 60)
PONG = spr(F.spr_ball, 26, (1.0, 0.58, 0.22))

ANIM01 = dict(
    id='anim_01', niche='NICHE_1', theme='cartoon', speed=0.97, voice_reverb=0.03,
    title="Si le Soleil était un ballon de foot",
    hook_text="ET SI LE SOLEIL\\NÉTAIT UN BALLON ?", hook_y=270, caption_theme=dict(hook_size=104),
    music=dict(style='lofi', prog='lofi_c', key=50, bpm=84, seed=4101, start=0.25, db=-27.5),
    segments=[
        seg("Si le Soleil avait la taille d'un ballon de foot… où serait la Terre ?",
            fs(S_(spr(F.spr_sun, 230), MID, spin=4), S_(FOOT_S, (850, 1230), t0=1.5), big('?', 640, 2.4, x=880, size=230)),
            'static', sfx=['pop', ('pop', 1.5)], music=0.45, emph=['Soleil', 'ballon', 'Terre']),
        seg("Le Soleil mesure près de {1 400 000|un million quatre cent mille} kilomètres de diamètre.",
            fs(S_(spr(F.spr_sun, 290), MID, spin=4, pop=0), lambda: F.Ruler(250, 830, 900, 0.4, 1.3, P['white']), big('1 400 000 km', 430, 0.9, size=118)),
            'static', 'cut', sfx=[('ding', 0.9)], emph=['diamètre']),
        seg("On le réduit à {22|vingt-deux} centimètres : la taille d'un ballon.",
            fs(S_(spr(F.spr_sun, 290), MID, spin=4, pop=0, scale=[(0, 1.0), (1.0, 0.3)], alpha=[(0.0, 1.0), (0.85, 1.0), (1.1, 0.0)]),
               S_(FOOT, MID, t0=0.95), big('22 cm', 430, 1.2)),
            'static', 'cut', sfx=[('pop', 0.95), ('ding', 1.2)], emph=['ballon']),
        seg("À cette échelle, la Terre serait… un grain de poivre de {2|deux} millimètres !",
            fs(S_(spr(F.spr_football, 120), (290, 900), pop=0), S_(spr(F.spr_pepper, 8), (800, 900), t0=0.5),
               lambda: F.Lensed(F.FlatGlobe(c=(800, 900), r=128, spin=30, pop=0), (800, 900), r=150, t0=1.5), big('2 mm', 430, 1.8)),
            'static', 'cut', sfx=[('pop', 1.5), ('ding', 1.8)], emph=['Terre', 'poivre']),
        seg("Et elle tournerait autour du ballon… à {24|vingt-quatre} mètres de distance.",
            fs(S_(spr(F.spr_field, 820, 1120), (540, 1000), pop=0.3), S_(spr(F.spr_football, 34), (540, 1000), t0=0.2),
               lambda: F.Ring((540, 1000), 330, 0.6, 1.6, (1, 0.95, 0.6), 4), lambda: F.Mover(spr(F.spr_pepper, 9), (540, 1000), 330, 6.0, -1.57, 0.8),
               big('24 m', 330, 1.2)),
            'static', 'cut', sfx=[('ding', 1.2)], emph=['mètres'], cap_y=1640),
        seg("Et la Lune ? Un grain de sable… à seulement {6|six} centimètres de la Terre.",
            fs(lambda: F.FlatGlobe(c=(400, 900), r=170, spin=20, pop=0.3), S_(spr(F.spr_moon, 46), (800, 900), t0=0.6),
               lambda: F.Dashed((590, 900), (745, 900), 0.9, 1.6, P['white'], 6), small('LUNE', 800, 990, 0.7), big('6 cm', 430, 1.4)),
            'static', 'cut', sfx=[('pop', 0.6), ('ding', 1.4)], emph=['Lune', 'sable']),
        seg("Jupiter, la plus grosse planète ? Une bille… à {120|cent vingt} mètres.",
            fs(S_(FOOT_S, (150, 950), pop=0), S_(spr(F.spr_ball, 62, (0.92, 0.72, 0.50), JUP), (910, 950), t0=0.2),
               small('JUPITER', 910, 1070, 0.3), lambda: F.Dashed((215, 950), (840, 950), 0.6, 1.7), big('120 m', 430, 1.5)),
            'static', 'cut', sfx=[('pop', 0.2), ('ding', 1.5)], emph=['Jupiter', 'bille']),
        seg("Neptune, la plus lointaine ? Un petit pois… à {700|sept cents} mètres !",
            fs(S_(spr(F.spr_football, 22), (110, 950), pop=0), S_(spr(F.spr_ball, 24, (0.36, 0.62, 0.98)), (950, 950), t0=0.2),
               small('NEPTUNE', 950, 1040, 0.3), lambda: F.Dashed((140, 950), (920, 950), 0.5, 1.9, dash=20), big('700 m', 430, 1.7)),
            'static', 'cut', sfx=[('pop', 0.2), ('ding', 1.7)], emph=['Neptune', 'pois']),
        seg("Et la lumière du Soleil ? À cette échelle, elle avancerait à {5|cinq} centimètres par seconde… comme une tortue.",
            fs(S_(spr(F.spr_football, 90), (230, 950), pop=0), lambda: F.Dashed((330, 950), (1000, 950), 0.2, 0.8, (1, 1, 1), 4, dash=18),
               S_(spr(F.spr_ball, 14, P['yellow'], None, False, False), [(0.4, (330, 950)), (4.5, (420, 950))], t0=0.4), big('5 cm/s', 430, 1.0)),
            'static', 'cut', sfx=[('ding', 1.0)], emph=['lumière', 'tortue']),
        seg("Tout le système solaire tiendrait dans un cercle d'un kilomètre et demi.",
            fs(S_(spr(F.spr_city, 900, 900), MID, pop=0.4), S_(spr(F.spr_football, 22), MID, t0=0.3),
               *[(lambda rr=rr, k=k: F.Ring(MID, rr, 0.5 + 0.12 * k, 1.2 + 0.12 * k, P['yellow'], 4, alpha=0.9)) for k, rr in enumerate((60, 110, 190, 300, 420))],
               big('1,5 km', 330, 1.4)),
            'slow_in', 'cut', sfx=[('ding', 1.4)], emph=['système', 'solaire'], cap_y=1560),
        seg("Mais alors… où serait l'étoile la plus proche ?",
            fs(lambda: F.Sprite(spr(F.spr_text, '?', 520, P['yellow'], 18), MID, t0=0.3, bob=18)),
            'static', 'fade', sfx=[('pop', 0.3)], music=0.6, emph=['étoile', 'proche']),
        seg("Proxima du Centaure, une petite étoile rouge… serait une balle de ping-pong.",
            fs(S_(spr(F.spr_ball, 120, (1.0, 0.56, 0.20)), MID, t0=0.2, bob=10), small('PROXIMA DU CENTAURE', 540, 1110, 0.4, P['orange'], 64)),
            'static', 'cut', sfx=[('pop', 0.2)], emph=['Proxima', 'ping-pong']),
        seg("Et elle serait posée à {6 300|six mille trois cents} kilomètres de notre ballon.",
            fs(S_(FOOT_S, (160, 1000), pop=0), S_(PONG, (930, 1000), t0=0.1),
               lambda: F.Dashed((215, 960), (900, 960), 0.4, 1.8, bend=-230), big('6 300 km', 430, 1.4)),
            'static', 'cut', sfx=[('ding', 1.4)], emph=['kilomètres']),
        seg("Même la lumière met plus de quatre ans pour faire ce trajet.",
            fs(S_(FOOT_S, (160, 1000), pop=0), S_(PONG, (930, 1000), pop=0),
               lambda: F.Dashed((215, 960), (900, 960), 0.0, 0.01, bend=-230), big('4,2 ANS', 430, 0.5, size=150)),
            'static', 'cut', sfx=[('ding', 0.5)], emph=['quatre']),
        seg("Si le ballon était à Paris… la balle serait plus loin que New York !",
            fs(lambda: F.Ground(1400), S_(spr(F.spr_eiffel, 430), (200, 1190), t0=0.1), S_(spr(F.spr_football, 30), (330, 1372), t0=0.4),
               S_(spr(F.spr_skyline, 440, 280), (790, 1265), t0=0.9), S_(spr(F.spr_ball, 16, (1.0, 0.58, 0.22)), (1035, 1385), t0=2.1),
               lambda: F.Dashed((330, 1300), (1030, 1330), 1.0, 2.2, bend=-330), small('PARIS', 210, 1470, 0.3), small('NEW YORK', 790, 1470, 1.0)),
            'static', 'cut', sfx=[('pop', 0.4), ('whoosh', 1.0)], emph=['Paris', 'New', 'York'], cap_y=1690),
        seg("Et entre les deux ? Presque rien. Du vide.",
            fs(S_(spr(F.spr_football, 12), (120, 960), pop=0), S_(spr(F.spr_ball, 5, (1.0, 0.58, 0.22), None, False, False), (960, 960), pop=0)),
            'out', 'fade', music=0.3, emph=['vide']),
        seg("Voilà à quel point l'espace est immense… et vide. Tu t'en doutais ?",
            fs(lambda: F.FlatGlobe(c=(540, 980), r=250, spin=18), S_(spr(F.spr_sun, 70), (170, 470), t0=0.4, spin=6), big('?', 450, 2.0, x=880, size=200)),
            'slow_in', 'cut', sfx=[('pop', 0.4)], music=0.5, emph=['immense', 'vide']),
    ])

# ----------------------------------------------------------------------------- « Et si la Terre s'arrêtait de tourner ? »
GLOBE_C = (W / 2, 930)
HOUSE = spr(F.spr_house, 170)
TREE = spr(F.spr_tree, 170)

ANIM02 = dict(
    id='anim_02', niche='NICHE_1', theme='cartoon', speed=0.96, voice_reverb=0.03,
    title="Et si la Terre s'arrêtait de tourner ?",
    hook_text="ET SI LA TERRE\\NS'ARRÊTAIT ?", hook_y=270, caption_theme=dict(hook_size=104),
    music=dict(style='lofi', prog='lofi_a', key=48, bpm=86, seed=4201, start=0.25, db=-27.5),
    segments=[
        seg("Et si la Terre s'arrêtait de tourner… d'un seul coup ?",
            fs(lambda: F.FlatGlobe(c=GLOBE_C, r=320, lon=[(0, 0), (1.7, 200), (2.0, 212)]), big('STOP', 1330, 2.1, color=P['red'], size=120)),
            'static', sfx=[('impact', 2.0)], music=0.45, emph=['arrêtait']),
        seg("À l'équateur, le sol file à {1 670|mille six cent soixante-dix} kilomètres-heure… plus vite que le son !",
            fs(lambda: F.FlatGlobe(c=GLOBE_C, r=320, spin=45, tilt=0), lambda: F.Dashed((180, 930), (900, 930), 0.3, 1.0, P['yellow'], 8),
               big('1 670 km/h', 430, 0.9, size=124)),
            'static', 'cut', sfx=[('ding', 0.9)], emph=['équateur', 'son']),
        seg("Et en France, tu files déjà à plus de {1 100|mille cent} kilomètres-heure… sans rien sentir.",
            fs(lambda: F.FlatGlobe(c=GLOBE_C, r=320, lon=-2, spin=0, tilt=30), S_(spr(F.spr_text, '•', 160, P['red'], 6), (540, 690), t0=0.4),
               small('FRANCE', 540, 610, 0.5, P['white'], 56), big('1 100 km/h', 430, 1.0, size=124)),
            'static', 'cut', sfx=[('pop', 0.4), ('ding', 1.0)], emph=['France', 'rien']),
        seg("Tu ne sens rien, parce que tout tourne avec toi : le sol, l'air, les océans.",
            fs(lambda: F.FlatGlobe(c=(540, 1080), r=300, spin=12), S_(spr(F.spr_person, 150, P['pink']), (540, 712), t0=0.3),
               lambda: F.Ring((540, 1080), 370, 0.6, 1.6, (0.75, 0.9, 1.0), 5)),
            'static', 'cut', sfx=[('pop', 0.3)], emph=['rien'], cap_y=1580),
        seg("Mais si la planète freinait brutalement… l'air, lui, continuerait sur sa lancée.",
            fs(lambda: F.Ground(1330), S_(HOUSE, (290, 1235), t0=0.1), S_(TREE, (770, 1235), t0=0.2), S_(spr(F.spr_person, 130, P['cyan']), (540, 1270), t0=0.3),
               lambda: F.Wind(1.4, 26, 1600, 300, 1150)),
            'static', 'cut', sfx=[('whoosh', 1.4)], emph=['air']),
        seg("Des vents quatre fois plus forts que la pire rafale jamais mesurée balaieraient tout.",
            fs(lambda: F.Ground(1330), lambda: F.Wind(0.0, 60, 3000, 200, 1500),
               lambda: F.Flying([HOUSE, TREE, spr(F.spr_person, 120, P['pink']), TREE, spr(F.spr_house, 130), spr(F.spr_person, 120, P['yellow'])], 0.2),
               big('× 4', 430, 0.6, size=170)),
            'static', 'cut', sfx=[('whoosh', 0.2), ('impact', 0.6)], emph=['quatre', 'tout'], music=0.7),
        seg("Arbres, maisons, voitures : tout ce qui n'est pas solidement ancré serait emporté.",
            fs(lambda: F.Ground(1330), lambda: F.Wind(0.0, 60, 3000, 200, 1500, seed=8),
               lambda: F.Flying([TREE, spr(F.spr_house, 110), TREE, spr(F.spr_person, 110, P['cyan']), HOUSE, TREE, spr(F.spr_person, 110, P['green'])], 0.0, seed=9, speed=1800)),
            'static', 'cut', sfx=[('whoosh', 0.1)], emph=['emporté']),
        seg("Les océans aussi : des vagues géantes déferleraient sur les côtes.",
            fs(lambda: F.Ground(1380), S_(spr(F.spr_house, 120), (720, 1310), t0=0.1), S_(spr(F.spr_tree, 120), (930, 1300), t0=0.1),
               S_(spr(F.spr_wave, 1800, 700), [(0, (-1000, 1080)), (2.8, (380, 1080))], pop=0)),
            'static', 'cut', sfx=[('whoosh', 0.3)], emph=['vagues', 'géantes']),
        seg("Puis, lentement, l'eau glisserait vers les pôles…",
            fs(lambda: F.FlatGlobe(c=GLOBE_C, r=330, spin=10, lon=-40 + 0, poles=[(0.4, 0.0), (3.2, 1.0)])),
            'static', 'fade', emph=['pôles'], music=0.5),
        seg("…et un seul continent géant apparaîtrait autour de l'équateur.",
            fs(lambda: F.FlatGlobe(c=GLOBE_C, r=330, spin=10, lon=-10, poles=1.0, pop=0), big('1 SEUL CONTINENT', 430, 0.8, size=92)),
            'static', 'cut', sfx=[('ding', 0.8)], emph=['continent']),
        seg("Une journée durerait un an : six mois de jour… et six mois de nuit.",
            fs(lambda: F.FlatGlobe(c=(600, 1000), r=280, spin=0, lon=20, light=180), S_(spr(F.spr_sun, 80), (140, 600), t0=0.2, spin=5),
               big('1 JOUR = 1 AN', 430, 0.8, size=104)),
            'static', 'cut', sfx=[('ding', 0.8)], emph=['jour', 'nuit']),
        seg("Côté jour, une chaleur écrasante. Côté nuit, un froid glacial.",
            fs(lambda: F.FlatGlobe(c=(540, 960), r=300, spin=0, lon=20, light=180), small('CHAUD', 360, 960, 0.4, P['orange'], 80), small('FROID', 720, 960, 1.6, P['cyan'], 80)),
            'static', 'cut', sfx=[('pop', 0.4), ('pop', 1.6)], emph=['chaleur', 'froid']),
        seg("Heureusement, aucune force connue ne pourrait stopper la Terre aussi brutalement.",
            fs(lambda: F.FlatGlobe(c=GLOBE_C, r=300, spin=30), big('OUF !', 430, 0.3, color=P['green'], size=150)),
            'static', 'cut', sfx=[('pop', 0.3)], music=0.4),
        seg("La Terre ralentit bien… mais d'environ {2|deux} millisecondes par siècle.",
            fs(S_(spr(F.spr_clock, 240), MID, t0=0.1), lambda: F.Hands(MID, 240, fast=0.3, slow=0.02), big('2 ms / SIÈCLE', 430, 1.0, size=104)),
            'static', 'cut', sfx=[('ding', 1.0)], emph=['millisecondes']),
        seg("À ce rythme, il faudrait des dizaines de milliards d'années pour qu'elle s'arrête… bien plus que la vie du Soleil.",
            fs(S_(spr(F.spr_sun, 150), MID, t0=0.2, spin=5), lambda: F.Sprite(spr(F.spr_text, "DES DIZAINES DE MILLIARDS D'ANNÉES", 84, P['yellow'], 10), (540, 470), t0=0.8, pop=0.4)),
            'static', 'cut', sfx=[('ding', 0.8)], emph=['milliards', 'Soleil']),
        seg("Alors, tu choisirais six mois de jour… ou six mois de nuit ? Dis-le en commentaire !",
            fs(lambda: F.Split(), S_(spr(F.spr_sun, 110), (270, 820), t0=0.4, spin=6), S_(spr(F.spr_moon, 110), (810, 820), t0=0.8),
               small('JOUR', 270, 1080, 0.5, P['yellow'], 90), small('NUIT', 810, 1080, 0.9, P['white'], 90)),
            'static', 'cut', sfx=[('pop', 0.4), ('pop', 0.8)], music=0.6, emph=['jour', 'nuit'], cap_y=1480),
    ])

VIDEOS = [ANIM01, ANIM02]
