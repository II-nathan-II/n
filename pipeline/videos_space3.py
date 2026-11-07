"""NICHE_1 « Vertige Cosmique » — série 3 (vidéos 16 à 25), même chaîne de production que les séries 1 et 2.

Images : NASA (SVS, NASA Image and Video Library, JPL), domaine public ; bandes-son NASA retirées.
Faits vérifiés (sources dans docs.SOURCES) ; chiffres incertains formulés avec « environ », « près de », « plus de ».
Les dates à venir (BepiColombo, Voyager 1, Europa Clipper) sont celles annoncées par l'ESA et la NASA en novembre 2026.
"""
import cv2
import numpy as np
from videos_real import V, P, txt, back, counter, shade, seg, REAL, \
    EARTH, ISS, JUPITER, SUN171, SUN193, SUN131, PV, AUR_ISS, MILKYWAY, SATURN
from videos_space2 import GRS, MARS_TOPO, MARS_ROLL, HELICITY, SDO171, SDO304
from layers_base import Flash, Fn, Composite as C
from common import W, H
import layers_cine as L

# ----------------------------------------------------------------------------- nouvelles sources
# Apophis (NASA Goddard / OSIRIS-APEX)
APO_SIZE = 'svs:20414/APEX_APOPHIS_Size_Comparison_vert_4k_59.94fps_h264.mp4'   # Apophis à côté de la tour Eiffel (vertical 4K)
APO_DIST = 'svs:20414/Apophis_Distance_Animation_Vertical_4k.mp4'               # distance du passage de 2029 (vertical 4K)
APO_RDV = 'svs:20414/OREX_APEX_Rendezvous_4k_30fps_h264.mp4'                    # OSIRIS-APEX rejoint Apophis (4K)
# Europe (JPL)
EUR = 'nasa:JPL-20220310-CLIPPRf-0001-Europa Clipper Mission Animations'         # animations de la mission Europa Clipper
OCEAN_VENTS = 'svs:20384/OceanVents_web.mp4'                                    # sources hydrothermales sous la glace
ICE_PAN = 'svs:20384/IceLayerPan_web.mp4'                                       # coupe de la couche de glace
ENC_GEY = 'svs:20384/EnceladusGeyser_web.mp4'                                   # geyser d'Encelade devant Saturne
# Titan
TITAN_INTRO = 'svs:20403/JWST_Titan_Intro_Final_V001.mp4'                       # Webb, Saturne et Titan (4K)
TITAN_TL = 'svs:20403/Titan_Timelapse_1080_h264.mp4'                            # lacs de Titan, Saturne dans le ciel
TITAN_CLIMATE = 'svs:20403/Titan_Climate_1080_h264.mp4'                         # paysage de Titan
METHANE = 'svs:20403/Methane_1080_h264_V2.mp4'                                  # molécules de méthane au-dessus de Titan
DF_PAN = 'svs:20311/DF_End_Pan_4K_H264.mp4'                                     # Dragonfly posé sur Titan (4K)
CASSINI = 'nasa:GSFC_20170912_Cassini_m12709_CIRS_Short'                        # Cassini : Saturne, Titan, Encelade
TITAN_PIC = 'nasa:PIA14909'                                                     # Titan devant Saturne, vraies couleurs (Cassini)
# Parker Solar Probe
P_SWING = 'svs:14045/YOUTUBE_4K_SwingbySunCloseupSun-4K_youtube_4k.mp4'         # Parker devant le Soleil (4K)
P_PULL = 'svs:14045/YOUTUBE_4K_Goddard-Scene2CamPullBack-4K_youtube_4k.mp4'     # gros plan puis recul (4K)
P_SHIELD = 'svs:14045/YOUTUBE_4K_Goddard-FieldAntennasGlow-4K_youtube_4k.mp4'   # bouclier thermique et antennes (4K)
HELIO = 'svs:20363/H_0322_HeliopauseCycle_v01.mp4'                              # Soleil, planètes, héliosphère (4K)
# Saturne
SAT_RINGS = 'svs:12672/12672_SaturnRingsDisappearing_YouTubeHD.mp4'             # pluie des anneaux (NASA Goddard)
# Mercure
MERC = 'svs:14110/Mercury_Globe_MESSENGER_Large.mp4'                            # globe de Mercure, MESSENGER (4K)
MERC_POLE = 'nasa:PIA19411'                                                     # pôle nord de Mercure, glace en jaune (MESSENGER, 4000 px)
# Mars
MARS_SUNSET_PIC = 'nasa:PIA19400'                                               # coucher de soleil bleu, Curiosity, 2015
INSIGHT_SUNSET = 'nasa:PIA23202'                                                # coucher de soleil, InSight, 2019
MARS_SUNSET = 'svs:11875/WC_MarsSunset-1920-MASTER_baron.mp4'                   # séquence Curiosity (0–8 s uniquement)
# Encelade
ENC_OCEAN = 'nasa:PIA19656'                                                     # océan global d'Encelade (vue en coupe JPL, 8534 px)
ENC_JETS = 'nasa:PIA11688'                                                      # vraie photo Cassini des jets d'Encelade
# Voyager
VOY_CRAFT = 'svs:20390/Shot5_4k_mp4.mp4'                                        # sonde Voyager en gros plan (4K)
VOY_FLY = 'svs:20390/Shot_5_AltVoyager_4k_mp4.mp4'                              # Voyager s'éloigne (4K)
VOY_ART = 'nasa:PIA21839'                                                       # Voyager dans l'espace (vue d'artiste JPL)
VOY_ART2 = 'nasa:PIA17049'                                                      # Voyager sur fond d'étoiles (vue d'artiste JPL)
VOY_SPEED = 'nasa:PIA26353'                                                     # Voyager file dans l'espace (vue d'artiste JPL, 2025)
PBD = 'nasa:PIA23645'                                                           # « Pale Blue Dot » retraitée (2020)
PBD_X, PBD_Y = 0.5946, 0.5196                                                   # position de la Terre dans l'image

GOLD = (255, 216, 74)
ICE = (150, 220, 255)
HOT = (255, 150, 90)


def ring(x=540, y=960, r=46, t0=0.6, color=GOLD):
    """Cercle qui apparaît autour d'un point de l'image (suit la caméra du plan)."""
    def make():
        def draw(f, t, dur):
            a = min(1.0, max(0.0, (t - t0) / 0.4))
            if a <= 0:
                return f
            ov = f.copy()
            cv2.circle(ov, (int(x), int(y)), int(r + 14 * (1 - a)), tuple(c / 255 for c in color), 5, cv2.LINE_AA)
            return f * (1 - a) + ov * a
        return Fn(draw)
    return make


def lift(gamma=1.8, contrast=1.3):
    """Éclaircit un plan trop sombre (gamma + contraste), comme un étalonnage."""
    def make():
        def draw(f, t, dur):
            return np.clip((np.power(np.clip(f, 0, 1), 1 / gamma) - 0.5) * contrast + 0.53, 0, 1)
        return Fn(draw)
    return make


# ============================================================================= 16 — ISS : seize levers de soleil
R16 = dict(
    id='video_16', niche='NICHE_1', theme='space', speed=1.08, voice_reverb=0.06, **REAL,
    title='16 levers de soleil par jour',
    hook_text='16 LEVERS DE SOLEIL\\NPAR JOUR',
    music=dict(style='space', prog='minor_float', key=45, bpm=72, seed=1601, start=0.3),
    segments=[
        seg("Les astronautes de la Station spatiale voient le Soleil se lever seize fois par jour.", V(ISS, 1830.0, cx=0.85), 'in', sfx=['boom'], music=0.35, emph=['seize']),
        seg("Et se coucher seize fois. Parce que la station fait le tour de la Terre en à peu près une heure et demie.",
            V(AUR_ISS, 0.0, speed=0.6, cx=0.15), 'slow_in', 'whip', label='1 TOUR ≈ 90 MINUTES', emph=['heure', 'demie']),
        seg("Elle file à environ vingt-huit mille kilomètres par heure, à quatre cents kilomètres au-dessus de nos têtes.",
            V(ISS, 1310.0, extra=[back(170, 560), counter(0, 28000, y=340, size=150, suffix=' km/h', color=GOLD, t1=2.2, sub='à 400 km d\'altitude')]),
            'push', 'zoom', emph=['vingt-huit']),
        seg("À cette vitesse, Paris-Marseille, c'est moins d'une minute et demie.", V(ISS, 1374.0, extra=[back(170, 520), txt('PARIS → MARSEILLE', 300, 110), txt('< 1 MIN 30', 430, 130, (255, 255, 255))]),
            'drift', 'cut', emph=['Marseille']),
        seg("Résultat : un jour et une nuit toutes les quatre-vingt-dix minutes environ. Le Soleil se lève, se couche… et recommence.",
            V(ISS, 350.0), 'slow_in', 'fade'),
        seg("La nuit, ils survolent les aurores polaires… par-dessus.", V(AUR_ISS, 24.0), 'in', 'flash', sfx=['shimmer'], emph=['aurores'], music=0.5),
        seg("Alors comment dormir ? Ils vivent à l'heure de Greenwich, ferment les volets des hublots, et dorment dans des sacs de couchage accrochés au mur.",
            V(ISS, 2014.0, cx=0.5), 'right', 'whip', emph=['dormir']),
        seg("Et pourquoi flottent-ils ? Ce n'est pas parce qu'il n'y a pas de gravité.", V(ISS, 1950.0, cx=0.5), 'slow_in', 'black', sfx=[('riser', 0.0)], emph=['flottent']),
        seg("À quatre cents kilomètres, la gravité atteint encore environ quatre-vingt-dix pour cent de celle qu'on ressent au sol.",
            V(ISS, 990.0, extra=[back(170, 560), counter(0, 90, y=340, size=210, suffix=' %', color=GOLD, t1=2.0, sub='de la gravité au sol')]),
            'in', 'cut', emph=['quatre-vingt-dix']),
        seg("En réalité, ils tombent. En permanence.", V(ISS, 606.0), 'push', 'whip', sfx=['whoosh'], emph=['tombent'], music=0.65),
        seg("Mais ils vont tellement vite sur le côté qu'ils ratent la Terre à chaque fois. C'est ça, une orbite : une chute sans fin.",
            V(ISS, 1118.0), 'drift', 'zoom', emph=['chute']),
        seg("La station est la plus grande structure jamais assemblée dans l'espace : à peu près la taille d'un terrain de foot, pour plus de quatre cents tonnes.",
            V(ISS, 2075.0, cx=0.3), 'slow_in', 'fade', emph=['terrain']),
        seg("Et on peut la voir à l'œil nu : un point très brillant qui traverse le ciel en quelques minutes, sans clignoter.",
            V(AUR_ISS, 72.0), 'in', 'cut', emph=['œil']),
        seg("Depuis le {2|deux} novembre {2000|deux mille}, il y a toujours eu des humains à bord. Plus de vingt-six ans sans interruption.",
            V(ISS, 2930.0), 'push', 'flash', label='DEPUIS LE 2 NOVEMBRE 2000', emph=['toujours'], music=0.75),
        seg("Mais son histoire touche à sa fin : elle doit prendre sa retraite vers {2030|deux mille trente}, puis retomber dans l'océan Pacifique.",
            V(ISS, 3038.0), 'slow_in', 'fade', emph=['Pacifique']),
        seg("Tu aimerais voir seize levers de soleil par jour ? Dis-le en commentaire.", V(ISS, 1870.0, cx=0.85), 'out', 'fade', music=0.3),
    ])

# ============================================================================= 17 — Apophis, vendredi 13 avril 2029
R17 = dict(
    id='video_17', niche='NICHE_1', theme='space', speed=1.08, voice_reverb=0.06, **REAL,
    title='Vendredi 13 avril 2029, un astéroïde va frôler la Terre',
    hook_text='VENDREDI 13 AVRIL 2029',
    music=dict(style='space', prog='minor_dark', key=44, bpm=74, seed=1701, start=0.3),
    segments=[
        seg("Le vendredi {13|treize} avril {2029|deux mille vingt-neuf}, un astéroïde va frôler la Terre.", V(APO_RDV, 26.0, speed=0.5, cx=0.6), 'in', sfx=['boom'], music=0.35, emph=['frôler']),
        seg("Il s'appelle Apophis, comme le dieu égyptien du chaos.", V(APO_SIZE, 0.0, speed=0.8), 'slow_in', 'whip', label='APOPHIS', emph=['Apophis']),
        seg("Il mesure environ trois cent quarante mètres : à peu près la hauteur de la tour Eiffel.", V(APO_SIZE, 4.0, speed=0.8), 'drift', 'cut', emph=['Eiffel']),
        seg("Et il va passer à environ trente-deux mille kilomètres de nous.",
            V(APO_RDV, 27.5, speed=0.4, cx=0.62, extra=[back(170, 560, 0.7), counter(0, 32000, y=340, size=190, suffix=' km', color=HOT, t1=2.0, sub='de la Terre')]),
            'push', 'zoom', emph=['trente-deux'], sfx=['impact']),
        seg("Plus près que les satellites de télévision, en orbite à près de trente-six mille kilomètres.", V(APO_DIST, 19.6, speed=0.5), 'slow_in', 'fade', emph=['satellites']),
        seg("Jamais un astéroïde aussi gros n'a été observé en passant aussi près.", V(APO_RDV, 30.0, speed=0.5), 'in', 'flash', emph=['jamais'], music=0.6),
        seg("Ce soir-là, il sera visible à l'œil nu, comme un point lumineux qui glisse parmi les étoiles. Notamment depuis l'Europe et l'Afrique.",
            P(MILKYWAY), 'slow_in', 'fade', emph=['œil', 'nu']),
        seg("Au début, il a fait très peur. Après sa découverte en {2004|deux mille quatre}, les calculs lui donnaient près de trois chances sur cent de nous percuter en {2029|deux mille vingt-neuf}.",
            V(APO_SIZE, 10.0, speed=0.8), 'push', 'black', sfx=[('riser', 0.0)], label='DÉCOUVERT EN 2004', emph=['percuter']),
        seg("Il a atteint le niveau quatre sur l'échelle de Turin, qui mesure le danger des astéroïdes. Du jamais-vu.",
            V(APO_RDV, 28.5, speed=0.4, cx=0.3, extra=[back(170, 520), txt('NIVEAU 4', 330, 170, HOT)]), 'in', 'cut', emph=['jamais-vu']),
        seg("Mais rassure-toi : avec des mesures plus précises, la NASA a exclu tout risque de collision pour au moins cent ans.",
            V(EARTH, 40.0), 'slow_in', 'fade', emph=['exclu'], music=0.4),
        seg("En revanche, c'est la Terre qui va le secouer.", V(EARTH, 60.0), 'push', 'whip', emph=['secouer']),
        seg("Notre gravité va modifier son orbite, changer sa rotation… et peut-être provoquer de petits glissements de terrain à sa surface.",
            V(APO_RDV, 23.5, speed=0.6, cx=0.42), 'drift', 'zoom', music=0.65),
        seg("Et une sonde sera là pour l'observer : OSIRIS-APEX.", V(APO_RDV, 11.0, speed=0.8, cx=0.38), 'in', 'flash', label='OSIRIS-APEX', emph=['OSIRIS-APEX']),
        seg("C'est l'ancienne sonde OSIRIS-REx, celle qui a rapporté sur Terre des échantillons de l'astéroïde Bennu.", V(APO_RDV, 1.0, speed=0.8, cx=0.6), 'slow_in', 'cut', emph=['Bennu']),
        seg("Elle doit rejoindre Apophis juste après son passage, et l'étudier pendant environ un an et demi.", V(APO_RDV, 17.0, speed=0.7, cx=0.4), 'push', 'fade'),
        seg("Vendredi {13|treize} avril {2029|deux mille vingt-neuf} : note bien la date. Tu le regarderas ? Dis-le en commentaire.",
            V(APO_RDV, 29.0, speed=0.4), 'out', 'fade', music=0.3),
    ])

# ============================================================================= 18 — Europe, l'océan sous la glace
R18 = dict(
    id='video_18', niche='NICHE_1', theme='space', speed=1.08, voice_reverb=0.06, **REAL,
    title='Plus d\'eau que dans tous les océans de la Terre',
    hook_text='PLUS D\'EAU QUE\\NSUR TOUTE LA TERRE',
    music=dict(style='space', prog='minor_wonder', key=46, bpm=70, seed=1801, start=0.3),
    segments=[
        seg("Sous la glace de cette lune, il y aurait plus d'eau que dans tous les océans de la Terre réunis.", V(EUR, 566.0, mode='cover!', speed=0.7), 'in', sfx=['boom'], music=0.35, emph=['eau']),
        seg("Elle s'appelle Europe, et elle tourne autour de Jupiter.", V(EUR, 449.0), 'slow_in', 'whip', label='EUROPE • LUNE DE JUPITER', emph=['Europe']),
        seg("Elle est un peu plus petite que notre Lune, et sa surface est une coquille de glace, striée de fissures.", V(EUR, 461.0, mode='cover!', speed=0.7), 'drift', 'cut', emph=['glace']),
        seg("Cette glace ferait quinze à vingt-cinq kilomètres d'épaisseur.",
            V(EUR, 520.0, mode='cover!', cx=0.4, speed=0.7, extra=[back(170, 520, 0.7), txt('15 À 25 KM', 330, 170, (255, 255, 255))]), 'push', 'zoom', emph=['épaisseur']),
        seg("Et dessous, un océan d'eau salée, profond de peut-être cent kilomètres. Environ deux fois plus d'eau que sur toute la Terre.",
            V(EARTH, 30.0, extra=[back(170, 520), txt('× 2', 330, 200, ICE)]), 'slow_in', 'fade', emph=['deux', 'fois']),
        seg("Mais comment cette eau peut-elle rester liquide, si loin du Soleil, alors qu'en surface il fait moins cent soixante degrés ?",
            V(EUR, 414.0), 'in', 'black', sfx=[('riser', 0.0)], emph=['liquide']),
        seg("Grâce à Jupiter. Sa gravité étire et comprime Europe en permanence, ce qui chauffe son intérieur. Comme une balle antistress qu'on malaxe.",
            V(JUPITER, 6.0), 'push', 'flash', emph=['Jupiter'], music=0.6),
        seg("Au fond de cet océan, il pourrait même y avoir des sources chaudes. Sur Terre, ces endroits grouillent de vie.", V(OCEAN_VENTS, 0.0, speed=0.7, extra=[lift()]), 'slow_in', 'fade', emph=['vie']),
        seg("Pour en avoir le cœur net, la NASA a lancé en octobre {2024|deux mille vingt-quatre} la sonde Europa Clipper.", V(EUR, 17.0), 'in', 'cut', label='EUROPA CLIPPER • 2024'),
        seg("C'est le plus grand engin jamais construit par la NASA pour explorer une planète : ses panneaux solaires mesurent environ trente mètres d'un bout à l'autre.",
            V(EUR, 380.0, extra=[back(170, 520), txt('≈ 30 M', 330, 170)]), 'out', 'zoom', emph=['trente']),
        seg("Elle est passée près de Mars en {2025|deux mille vingt-cinq} pour prendre de l'élan, et doit frôler la Terre le {3|trois} décembre.",
            V(EUR, 244.0), 'drift', 'whip', label='3 DÉCEMBRE 2026', emph=['élan']),
        seg("Elle arrivera autour de Jupiter en {2030|deux mille trente}, et survolera Europe près de cinquante fois, parfois à seulement vingt-cinq kilomètres de sa surface.",
            V(EUR, 467.0, mode='cover!', speed=0.7, extra=[back(170, 520, 0.7), txt('49 SURVOLS', 330, 160)]), 'push', 'flash', emph=['cinquante'], music=0.75),
        seg("Son but n'est pas de trouver des extraterrestres, mais de savoir si cet océan pourrait abriter la vie.", V(EUR, 512.0), 'slow_in', 'fade'),
        seg("Elle emporte même une plaque gravée d'un poème… et les noms de plus de deux millions et demi de personnes.", V(EUR, 387.0), 'in', 'cut', emph=['noms']),
        seg("Le premier signe de vie hors de la Terre se cache peut-être… sous cette glace.", V(EUR, 593.0, mode='cover!', speed=0.6), 'slow_in', 'zoom', emph=['glace']),
        seg("Tu crois qu'il y a de la vie là-dessous ? Réponds en commentaire.", V(EUR, 568.0, mode='cover!', speed=0.5), 'out', 'fade', music=0.3),
    ])

# ============================================================================= 19 — Titan, il pleut du méthane
R19 = dict(
    id='video_19', niche='NICHE_1', theme='space', speed=1.08, voice_reverb=0.06, **REAL,
    title='Sur cette lune, il pleut… mais pas de l\'eau',
    hook_text='DES LACS, DE LA PLUIE…\\NMAIS PAS D\'EAU',
    music=dict(style='space', prog='minor_drift', key=43, bpm=70, seed=1901, start=0.3),
    segments=[
        seg("Il existe un monde avec des lacs, des rivières et de la pluie. Mais ce n'est pas de l'eau.", V(TITAN_TL, 17.0, speed=0.7), 'in', sfx=['boom'], music=0.35, emph=['eau']),
        seg("Bienvenue sur Titan, la plus grande lune de Saturne.", V(TITAN_INTRO, 28.0, speed=0.8, cx=0.55), 'slow_in', 'whip', label='TITAN • LUNE DE SATURNE', emph=['Titan']),
        seg("Elle est plus grande que la planète Mercure, et c'est la seule lune connue à avoir une atmosphère épaisse.",
            P(TITAN_PIC, cx=0.5), 'push', 'zoom', emph=['Mercure']),
        seg("Son air est même plus dense que le nôtre : au sol, la pression est environ une fois et demie celle de la Terre.",
            V(TITAN_CLIMATE, 0.0, speed=0.8, extra=[back(170, 520), txt('× 1,5', 330, 200)]), 'drift', 'cut', emph=['dense']),
        seg("Mais il y fait environ moins cent quatre-vingts degrés.",
            V(TITAN_TL, 3.0, speed=0.8, extra=[back(170, 560), counter(0, -180, y=340, size=210, suffix=' °C', color=ICE, t1=1.8)]), 'in', 'flash', sfx=['impact'], emph=['cent', 'quatre-vingts']),
        seg("À cette température, le méthane, le principal composant du gaz de nos cuisinières, devient liquide.", V(METHANE, 0.0, speed=0.8), 'slow_in', 'fade', emph=['méthane']),
        seg("Alors sur Titan, il pleut du méthane. Il coule en rivières, et remplit des lacs et des mers.", V(TITAN_TL, 8.0, speed=0.7), 'push', 'whip', emph=['pleut'], music=0.6),
        seg("La plus grande, Kraken Mare, est à peu près aussi vaste que la mer Caspienne.", V(TITAN_TL, 20.0, speed=0.7), 'drift', 'cut', label='KRAKEN MARE', emph=['Caspienne']),
        seg("À part la Terre, c'est le seul endroit connu où des liquides restent stables à la surface.", V(TITAN_TL, 24.0, speed=0.6), 'slow_in', 'fade', emph=['seul']),
        seg("Et avec sa faible gravité et son air épais, un humain pourrait, en théorie, y voler… avec des ailes attachées aux bras.",
            V(TITAN_TL, 28.0, speed=0.6), 'in', 'zoom', emph=['voler'], music=0.7),
        seg("En {2005|deux mille cinq}, la sonde européenne Huygens s'y est posée : l'atterrissage le plus lointain jamais réalisé.",
            V(TITAN_CLIMATE, 4.0, speed=0.7), 'push', 'black', sfx=[('riser', 0.0)], label='HUYGENS • JANVIER 2005', emph=['lointain']),
        seg("Et la prochaine mission est encore plus folle : Dragonfly, un drone de la taille d'une voiture, qui volera de site en site.",
            V(DF_PAN, 0.0, speed=0.7), 'slow_in', 'flash', label='DRAGONFLY', emph=['drone']),
        seg("Lancement prévu en {2028|deux mille vingt-huit}, arrivée sur Titan en {2034|deux mille trente-quatre}.",
            V(DF_PAN, 6.0, speed=0.7, extra=[back(170, 520), txt('2028 → 2034', 330, 160)]), 'in', 'cut'),
        seg("Son objectif : chercher les ingrédients chimiques de la vie, sur un monde qui rappelle la Terre à ses débuts.", V(TITAN_TL, 31.0, speed=0.6), 'slow_in', 'fade', emph=['vie']),
        seg("Tu irais te baigner dans un lac de méthane ? Dis-le en commentaire.", V(TITAN_TL, 15.0, speed=0.5), 'out', 'fade', music=0.3),
    ])

# ============================================================================= 20 — Parker, l'objet le plus rapide
R20 = dict(
    id='video_20', niche='NICHE_1', theme='space', speed=1.08, voice_reverb=0.06, **REAL,
    title='L\'objet le plus rapide jamais construit',
    hook_text='L\'OBJET LE PLUS RAPIDE\\NJAMAIS CONSTRUIT',
    music=dict(style='space', prog='minor_epic', key=45, bpm=78, seed=2001, start=0.3),
    segments=[
        seg("L'objet le plus rapide jamais construit par l'humanité… fonce droit vers le Soleil.", V(P_SWING, 3.0, speed=0.7, cx=0.35), 'in', sfx=['boom'], music=0.35, emph=['rapide']),
        seg("C'est la sonde Parker Solar Probe, lancée par la NASA en {2018|deux mille dix-huit}.", V(P_PULL, 0.3, speed=0.5), 'slow_in', 'whip', label='PARKER SOLAR PROBE', emph=['Parker']),
        seg("Le {24|vingt-quatre} décembre {2024|deux mille vingt-quatre}, elle est passée à environ six millions de kilomètres de la surface du Soleil.",
            V(P_SHIELD, 0.0, speed=0.7, cx=0.15), 'push', 'zoom', label='24 DÉCEMBRE 2024', emph=['six', 'millions']),
        seg("Jamais un engin n'était allé aussi près.", V(SUN171, 1.0, speed=0.6), 'in', 'flash', emph=['jamais']),
        seg("À ce moment-là, elle filait à environ six cent quatre-vingt-dix mille kilomètres par heure.",
            V(P_SWING, 5.0, speed=0.6, extra=[back(170, 560), counter(0, 692000, y=340, size=128, suffix=' km/h', color=GOLD, t1=2.2)]), 'push', 'cut', sfx=['impact'], emph=['six', 'cent']),
        seg("À cette vitesse, Paris-New York, ça prend… une trentaine de secondes.",
            V(PV, 180.0, speed=0.7, extra=[back(170, 520), txt('PARIS → NEW YORK', 300, 105), txt('≈ 30 S', 430, 150, (255, 255, 255))]), 'drift', 'whip', emph=['secondes'], music=0.6),
        seg("Mais comment ne fond-elle pas ?", V(HELICITY, 2.0), 'slow_in', 'black', sfx=[('riser', 0.0)], emph=['fond']),
        seg("Grâce à un bouclier thermique d'à peine onze centimètres d'épaisseur, en composite de carbone.", V(P_SHIELD, 2.5, speed=0.6, cx=0.72), 'in', 'cut', emph=['bouclier']),
        seg("Côté Soleil, il encaisse près de mille quatre cents degrés. Juste derrière, les instruments restent autour de trente degrés.",
            V(P_PULL, 1.5, speed=0.5, extra=[back(170, 560), counter(0, 1400, y=340, size=200, suffix=' °C', color=HOT, t1=2.0, sub='côté Soleil')]), 'push', 'zoom', emph=['mille', 'quatre']),
        seg("Et il y a un paradoxe : la couronne du Soleil, son atmosphère, dépasse le million de degrés.", V(SDO171, 0.0, speed=0.5), 'slow_in', 'fade', emph=['million']),
        seg("Mais elle est si peu dense qu'elle chauffe peu. Comme dans un four : l'air est brûlant, mais il te brûle bien moins vite que la plaque en métal.",
            V(SUN193, 1.0, speed=0.6), 'drift', 'whip', emph=['four']),
        seg("En {2021|deux mille vingt et un}, Parker est devenue le premier engin à « toucher » le Soleil, en traversant sa couronne.", V(SDO304, 0.0, speed=0.5), 'in', 'flash', label='2021', emph=['toucher'], music=0.75),
        seg("Pour se rapprocher autant, elle s'est servie sept fois de la gravité de Vénus pour freiner.", V(PV, 184.0, speed=0.7), 'slow_in', 'cut', emph=['Vénus']),
        seg("Son nom rend hommage à Eugene Parker, l'astrophysicien qui avait prédit le vent solaire. Il a assisté au lancement, à quatre-vingt-onze ans.",
            V(HELIO, 1.5, speed=0.6), 'push', 'fade', emph=['Parker']),
        seg("Depuis, elle repasse à cette distance record environ tous les trois mois.", V(P_SWING, 6.5, speed=0.5), 'in', 'cut'),
        seg("Tu aurais cru qu'on était allés aussi près du Soleil ? Dis-le en commentaire.", V(P_PULL, 6.0, speed=0.5), 'out', 'fade', music=0.3),
    ])

# ============================================================================= 21 — Saturne, les anneaux disparaissent
R21 = dict(
    id='video_21', niche='NICHE_1', theme='space', speed=1.08, voice_reverb=0.06, **REAL,
    title='Les anneaux de Saturne sont en train de disparaître',
    hook_text='LES ANNEAUX DE SATURNE\\NDISPARAISSENT',
    music=dict(style='space', prog='minor_wonder', key=44, bpm=72, seed=2101, start=0.3),
    segments=[
        seg("Les anneaux de Saturne… sont en train de disparaître.", V(SAT_RINGS, 3.0, speed=0.6), 'in', sfx=['boom'], music=0.35, emph=['disparaître']),
        seg("Ils sont faits de milliards de morceaux de glace, du grain de poussière au bloc gros comme une maison.", V(SAT_RINGS, 24.0, speed=0.6), 'slow_in', 'whip', emph=['glace']),
        seg("Ils s'étendent sur près de trois cent mille kilomètres d'un bord à l'autre… mais ils ne font souvent qu'une dizaine de mètres d'épaisseur.",
            V(SAT_RINGS, 86.5, speed=0.45, extra=[back(170, 520), txt('≈ 10 M D\'ÉPAISSEUR', 330, 110)]), 'push', 'zoom', emph=['dizaine']),
        seg("Et peu à peu, ils tombent sur la planète.", V(SAT_RINGS, 33.0, speed=0.6), 'in', 'cut', emph=['tombent']),
        seg("Le champ magnétique et la gravité de Saturne attirent la glace des anneaux vers son atmosphère. C'est la « pluie des anneaux ».",
            V(SAT_RINGS, 36.0, speed=0.5), 'slow_in', 'fade', label='PLUIE DES ANNEAUX', emph=['pluie']),
        seg("Selon la NASA, il en tombe de quoi remplir une piscine olympique… toutes les demi-heures.",
            V(SAT_RINGS, 46.0, speed=0.6, extra=[back(170, 520), txt('1 PISCINE / 30 MIN', 330, 130)]), 'push', 'flash', sfx=['impact'], emph=['piscine'], music=0.6),
        seg("À ce rythme, les anneaux pourraient disparaître d'ici trois cents millions d'années. Peut-être même moins.", V(SAT_RINGS, 52.0, speed=0.6), 'drift', 'whip', emph=['trois', 'cents']),
        seg("Et ils seraient plutôt jeunes : quelques centaines de millions d'années tout au plus, selon plusieurs études.",
            V(SAT_RINGS, 64.0, speed=0.6), 'slow_in', 'black', sfx=[('riser', 0.0)], emph=['jeunes']),
        seg("À l'échelle de l'Univers, on a eu de la chance d'arriver au bon moment pour les voir.", V(SAT_RINGS, 9.0, speed=0.6), 'in', 'cut', emph=['chance']),
        seg("En mars {2025|deux mille vingt-cinq}, ils ont même semblé disparaître depuis la Terre.", V(SAT_RINGS, 88.5, speed=0.4), 'push', 'zoom', label='MARS 2025', music=0.7),
        seg("Vus pile par la tranche, ils étaient trop fins pour être visibles. Ce phénomène revient environ tous les quinze ans.", P(SATURN), 'slow_in', 'fade', emph=['tranche']),
        seg("Autre bizarrerie : Saturne est moins dense que l'eau. Dans une baignoire assez grande, elle flotterait.", V(SAT_RINGS, 77.0, speed=0.6), 'in', 'whip', emph=['flotterait']),
        seg("Et c'est en plongeant entre la planète et ses anneaux que la sonde Cassini a terminé sa mission, le {15|quinze} septembre {2017|deux mille dix-sept}.",
            V(CASSINI, 354.0), 'drift', 'flash', label='CASSINI • 2017', emph=['Cassini']),
        seg("Après treize ans autour de Saturne, elle s'est désintégrée dans son atmosphère.", V(CASSINI, 375.0, speed=0.8), 'slow_in', 'fade', emph=['désintégrée']),
        seg("Tu savais que les anneaux de Saturne allaient disparaître ? Dis-le en commentaire.", V(SAT_RINGS, 12.0, speed=0.5), 'out', 'fade', music=0.3),
    ])

# ============================================================================= 22 — Mercure, de la glace près du Soleil
R22 = dict(
    id='video_22', niche='NICHE_1', theme='space', speed=1.08, voice_reverb=0.06, **REAL,
    title='La planète la plus proche du Soleil cache de la glace',
    hook_text='DE LA GLACE\\NSUR MERCURE',
    music=dict(style='space', prog='minor_float', key=47, bpm=74, seed=2201, start=0.3),
    segments=[
        seg("La planète la plus proche du Soleil… cache de la glace.", V(MERC, 0.0, speed=0.8, mode='fit', fit_scale=2.0), 'in', sfx=['boom'], music=0.35, emph=['glace']),
        seg("Sur Mercure, le jour, il fait environ quatre cent trente degrés. Assez pour faire fondre du plomb.",
            V(SUN193, 0.5, speed=0.6, extra=[back(170, 560), counter(0, 430, y=340, size=210, suffix=' °C', color=HOT, t1=2.0, sub='le jour')]), 'push', 'whip', sfx=['impact'], emph=['plomb']),
        seg("Et la nuit, la température chute à environ moins cent quatre-vingts degrés.",
            V(MERC, 18.0, speed=0.8, extra=[back(170, 560), counter(0, -180, y=340, size=210, suffix=' °C', color=ICE, t1=2.0, sub='la nuit')]), 'slow_in', 'cut', emph=['nuit']),
        seg("Pourquoi un tel écart ? Parce que Mercure n'a presque pas d'atmosphère pour garder la chaleur.", V(MERC, 28.0, speed=0.8, mode='fit', fit_scale=2.0), 'drift', 'fade', emph=['atmosphère']),
        seg("Et ses journées sont interminables : entre deux levers de soleil, il s'écoule cent soixante-seize jours terrestres.",
            V(MERC, 38.0, speed=0.8, extra=[back(170, 560), counter(0, 176, y=340, size=210, color=GOLD, t1=2.0, sub='jours terrestres')]), 'push', 'zoom', emph=['interminables']),
        seg("Alors que son année ne dure que quatre-vingt-huit jours. Sur Mercure, une journée dure… deux ans.",
            V(HELIO, 1.5, speed=0.6, extra=[back(170, 520), txt('1 JOUR = 2 ANS', 330, 150)]), 'in', 'flash', emph=['deux', 'ans'], music=0.6),
        seg("Mais alors, de la glace, où ça ?", P(MERC_POLE, cx=0.3, cy=0.5), 'slow_in', 'black', sfx=[('riser', 0.0)]),
        seg("Au fond de cratères, près des pôles.", P(MERC_POLE, cx=0.47, cy=0.5), 'in', 'cut', label='EN JAUNE : LA GLACE', emph=['cratères']),
        seg("L'axe de Mercure est presque parfaitement droit. Résultat : le fond de ces cratères ne voit jamais le Soleil.", P(MERC_POLE, cx=0.47, cy=0.52, zoom=1.8), 'push', 'fade', emph=['jamais']),
        seg("Il y fait si froid que la glace d'eau peut y rester piégée pendant des millions d'années.", P(MERC_POLE, cx=0.55, cy=0.6, zoom=2.6), 'slow_in', 'zoom', emph=['piégée']),
        seg("C'est la sonde MESSENGER de la NASA qui l'a confirmé en {2012|deux mille douze}.", P(MERC_POLE, cx=0.62, cy=0.45, zoom=1.3), 'in', 'cut', label='MESSENGER • 2012'),
        seg("Et il y en aurait beaucoup : entre cent milliards et mille milliards de tonnes.",
            V(MERC, 46.0, speed=0.8, extra=[back(170, 560), txt('100 À 1 000', 300, 150), txt('MILLIARDS DE TONNES', 440, 90, (255, 255, 255))]), 'push', 'flash', emph=['milliards'], music=0.75),
        seg("Autre surprise : Mercure rétrécit. En refroidissant, son rayon a diminué de plusieurs kilomètres, et sa surface s'est ridée comme une pomme qui sèche.",
            V(MERC, 52.0, speed=0.6, zoom=1.4), 'drift', 'whip', emph=['rétrécit']),
        seg("Et une nouvelle visite approche : la mission BepiColombo, des agences spatiales européenne et japonaise.", V(MERC, 30.0, speed=0.8, mode='fit', fit_scale=2.0), 'slow_in', 'fade', label='BEPICOLOMBO', emph=['BepiColombo']),
        seg("Après huit ans de voyage, elle doit se placer en orbite autour de Mercure le {21|vingt et un} novembre.", V(MERC, 4.0, speed=0.6), 'in', 'cut', label='21 NOVEMBRE 2026'),
        seg("Tu aurais cru qu'il y avait de la glace sur Mercure ? Dis-le en commentaire.", V(MERC, 0.0, speed=0.5, mode='fit', fit_scale=2.0), 'out', 'fade', music=0.3),
    ])

# ============================================================================= 23 — Mars, couchers de soleil bleus
R23 = dict(
    id='video_23', niche='NICHE_1', theme='space', speed=1.08, voice_reverb=0.06, **REAL,
    title='Sur Mars, les couchers de soleil sont bleus',
    hook_text='SUR MARS, LE COUCHER\\NDE SOLEIL EST BLEU',
    music=dict(style='space', prog='minor_drift', key=45, bpm=70, seed=2301, start=0.3),
    segments=[
        seg("Sur Mars, les couchers de soleil sont bleus.", P(MARS_SUNSET_PIC, cx=0.345), 'in', sfx=['boom'], music=0.35, emph=['bleus']),
        seg("Cette photo a été prise par le robot Curiosity, en avril {2015|deux mille quinze}, dans le cratère Gale.", P(MARS_SUNSET_PIC, mode='fit'), 'slow_in', 'whip', label='CURIOSITY • AVRIL 2015', emph=['Curiosity']),
        seg("Ce n'est pas un filtre : c'est à peu près ce que verraient tes yeux.", V(MARS_SUNSET, 0.0, speed=0.5), 'drift', 'cut', emph=['filtre']),
        seg("Et c'est l'inverse de chez nous : sur Terre, le ciel est bleu le jour et rouge au coucher du soleil.", V(ISS, 606.0), 'push', 'fade', emph=['inverse']),
        seg("Sur Mars, le ciel est plutôt beige orangé en journée… et bleu quand le Soleil se couche.", V(MARS_TOPO, 10.0, speed=0.8), 'slow_in', 'whip', emph=['bleu']),
        seg("Pourquoi ? À cause de la poussière.", V(MARS_ROLL, 10.0), 'in', 'black', sfx=[('riser', 0.0)], emph=['poussière']),
        seg("Mars est rouge parce que sa poussière contient de l'oxyde de fer : en gros, de la rouille.", V(MARS_ROLL, 20.0), 'drift', 'cut', emph=['rouille']),
        seg("Et ces grains, très fins, ont la bonne taille pour laisser passer la lumière bleue plus facilement… dans la direction du Soleil.",
            V(MARS_TOPO, 25.0, speed=0.8), 'push', 'zoom', music=0.6),
        seg("Le jour, la poussière répand des teintes ocre dans tout le ciel. Mais au coucher, il ne reste qu'un halo bleu autour du Soleil.",
            V(MARS_SUNSET, 3.0, speed=0.5), 'slow_in', 'fade', emph=['halo']),
        seg("En {2019|deux mille dix-neuf}, l'atterrisseur InSight a lui aussi photographié un coucher de soleil martien.", P(INSIGHT_SUNSET, cx=0.615), 'in', 'flash', label='INSIGHT • 2019'),
        seg("Là-bas, le Soleil paraît plus petit : environ deux tiers de la taille qu'on lui voit depuis la Terre.",
            P(MARS_SUNSET_PIC, cx=0.345, cy=0.6, zoom=1.5, extra=[back(170, 520), txt('≈ 2/3', 330, 200)]), 'push', 'cut', emph=['petit']),
        seg("Et sa lumière est moins forte : moins de la moitié de ce qu'on reçoit chez nous.", V(MARS_ROLL, 30.0), 'drift', 'whip', emph=['moitié']),
        seg("Le crépuscule, lui, dure longtemps : la poussière en altitude continue d'éclairer le ciel jusqu'à deux heures après le coucher.",
            V(MARS_SUNSET, 0.0, speed=0.35), 'slow_in', 'fade', emph=['deux', 'heures'], music=0.7),
        seg("Et une journée martienne ne dure que quarante minutes de plus qu'une journée sur Terre.",
            V(MARS_TOPO, 40.0, speed=0.8, extra=[back(170, 520), txt('24 H 39 MIN', 330, 160)]), 'in', 'cut', emph=['quarante']),
        seg("Un jour, peut-être, des humains regarderont ce Soleil bleu se coucher… depuis Mars.", V(MARS_TOPO, 50.0, speed=0.7), 'push', 'zoom', emph=['humains']),
        seg("Et toi, tu préfères les couchers de soleil d'ici ou de là-bas ? Dis-le en commentaire.", P(MARS_SUNSET_PIC, cx=0.345), 'out', 'fade', music=0.3),
    ])

# ============================================================================= 24 — Encelade, la lune qui crache de l'eau
R24 = dict(
    id='video_24', niche='NICHE_1', theme='space', speed=1.08, voice_reverb=0.06, **REAL,
    title='Cette lune crache de l\'eau dans l\'espace',
    hook_text='UNE LUNE QUI CRACHE\\NDE L\'EAU',
    music=dict(style='space', prog='minor_float', key=46, bpm=72, seed=2401, start=0.3),
    segments=[
        seg("Cette petite lune de Saturne crache de l'eau dans l'espace.", V(ENC_GEY, 0.8, speed=0.6), 'in', sfx=['boom'], music=0.35, emph=['eau']),
        seg("Elle s'appelle Encelade, et elle ne fait qu'environ cinq cents kilomètres de diamètre.",
            V(CASSINI, 177.5, speed=0.45, extra=[back(390, 760), counter(0, 500, y=560, size=200, suffix=' km', color=ICE, t1=1.8, sub='de diamètre')]), 'slow_in', 'whip', label='ENCELADE • LUNE DE SATURNE', emph=['Encelade']),
        seg("C'est l'un des objets les plus brillants du système solaire : sa glace renvoie presque toute la lumière du Soleil.", V(CASSINI, 175.0), 'drift', 'cut', emph=['brillants']),
        seg("Et en surface, il fait environ moins deux cents degrés.",
            V(ENC_GEY, 9.4, speed=0.5, extra=[back(170, 560), counter(0, -200, y=340, size=210, suffix=' °C', color=ICE, t1=1.8)]), 'push', 'zoom', emph=['deux', 'cents']),
        seg("En {2005|deux mille cinq}, la sonde Cassini a découvert quelque chose d'incroyable près de son pôle sud.", P(ENC_JETS, cx=0.62, cy=0.55), 'slow_in', 'black', sfx=[('riser', 0.0)], label='CASSINI • 2005'),
        seg("Des geysers. Une centaine de jets de vapeur d'eau et de glace, qui jaillissent de grandes fractures surnommées les « rayures de tigre ».",
            P(ENC_JETS, mode='fit'), 'in', 'flash', sfx=['impact'], emph=['geysers'], music=0.6),
        seg("Cette glace est si abondante qu'elle alimente l'un des anneaux de Saturne : l'anneau E.", V(ENC_GEY, 5.6, speed=0.6), 'drift', 'whip', emph=['anneaux']),
        seg("En {2023|deux mille vingt-trois}, le télescope James Webb a repéré un panache de vapeur d'eau long d'environ dix mille kilomètres.",
            V(TITAN_INTRO, 12.0, speed=0.8), 'push', 'cut', label='JAMES WEBB • 2023', emph=['dix', 'mille']),
        seg("Près de vingt fois la taille d'Encelade elle-même.", P(ENC_JETS, cx=0.4, cy=0.55, zoom=1.3), 'in', 'zoom', emph=['vingt']),
        seg("Il rejette environ trois cents litres d'eau par seconde. De quoi remplir une piscine olympique en quelques heures.",
            V(ENC_GEY, 7.4, speed=0.5, extra=[back(170, 520), txt('300 L / SECONDE', 330, 140)]), 'slow_in', 'fade', emph=['piscine']),
        seg("D'où vient toute cette eau ? D'un océan caché sous la glace, qui fait le tour de la lune entière.", P(ENC_OCEAN, cx=0.53, cy=0.5), 'push', 'whip', emph=['océan']),
        seg("En traversant ces panaches, Cassini y a trouvé du sel, des molécules organiques… et de l'hydrogène, le signe possible de sources chaudes au fond de l'océan.",
            V(OCEAN_VENTS, 0.0, speed=0.7, extra=[lift()]), 'slow_in', 'fade', emph=['hydrogène']),
        seg("Et en {2023|deux mille vingt-trois}, des chercheurs y ont aussi détecté du phosphore, un ingrédient indispensable à la vie telle qu'on la connaît.",
            V(CASSINI, 222.0, speed=0.6, zoom=1.15), 'in', 'flash', emph=['phosphore'], music=0.75),
        seg("Eau liquide, énergie, chimie : Encelade réunit presque tout ce qu'il faut pour abriter la vie.", V(ENC_GEY, 6.6, speed=0.5), 'drift', 'zoom', emph=['vie']),
        seg("C'est l'un des meilleurs endroits du système solaire pour chercher des êtres vivants.", V(SAT_RINGS, 15.0, speed=0.6), 'slow_in', 'fade'),
        seg("Tu penses qu'il y a de la vie dans cet océan ? Dis-le en commentaire.", V(ENC_GEY, 2.0, speed=0.5), 'out', 'fade', music=0.3),
    ])

# ============================================================================= 25 — Voyager 1, à un jour-lumière
PBD_CENTER = dict(z=(1.0, 1.3), focus=(540, 960))
R25 = dict(
    id='video_25', niche='NICHE_1', theme='space', speed=1.08, voice_reverb=0.06, **REAL,
    title='Cette sonde sera bientôt à un jour-lumière de la Terre',
    hook_text='À 1 JOUR-LUMIÈRE\\NDE LA TERRE',
    music=dict(style='space', prog='minor_wonder', key=43, bpm=68, seed=2501, start=0.3),
    segments=[
        seg("Dans quelques jours, cette sonde sera à un jour-lumière de la Terre.", V(VOY_CRAFT, 0.0, speed=0.4, cx=0.3), 'in', sfx=['boom'], music=0.35, emph=['jour-lumière']),
        seg("C'est Voyager {1|un}, lancée en {1977|mille neuf cent soixante-dix-sept}. Elle voyage depuis quarante-neuf ans.", P(VOY_ART, mode='fit'), 'slow_in', 'whip', label='VOYAGER 1 • 1977', emph=['quarante-neuf']),
        seg("Vers le {18|dix-huit} novembre, elle sera à environ vingt-cinq milliards neuf cents millions de kilomètres.",
            V(HELIO, 7.0, speed=0.5, extra=[back(390, 760), counter(0, 25.9, y=560, size=200, fmt='float', decimals=1, color=GOLD, t1=2.2, sub='milliards de kilomètres')]),
            'push', 'zoom', label='18 NOVEMBRE 2026', emph=['milliards']),
        seg("Si loin qu'un message envoyé depuis la Terre mettra une journée entière pour l'atteindre. Et autant pour revenir.",
            P(VOY_ART2, mode='fit', extra=[back(170, 520), txt('24 H ALLER • 24 H RETOUR', 330, 100)]), 'slow_in', 'fade', emph=['journée']),
        seg("Elle file à environ soixante et un mille kilomètres par heure.",
            P(VOY_SPEED, cx=0.4, extra=[back(170, 560), counter(0, 61000, y=340, size=180, suffix=' km/h', color=GOLD, t1=2.0)]), 'in', 'cut', sfx=['impact'], emph=['soixante']),
        seg("En chemin, elle a survolé Jupiter en {1979|mille neuf cent soixante-dix-neuf}…", V(GRS, 35.0, speed=0.7), 'drift', 'whip', label='JUPITER • 1979'),
        seg("… et Saturne en {1980|mille neuf cent quatre-vingts}.", V(SAT_RINGS, 6.0, speed=0.6), 'push', 'cut', label='SATURNE • 1980'),
        seg("En {2012|deux mille douze}, elle est devenue le premier objet humain à entrer dans l'espace interstellaire, hors de la bulle du vent solaire.",
            V(HELIO, 11.0, speed=0.7), 'slow_in', 'flash', label='2012', emph=['interstellaire'], music=0.6),
        seg("Mais sa photo la plus célèbre, elle l'a prise en se retournant.",
            lambda: C([L.StarField(seed=4, bright=0.8), L.Halo(center=(W / 2, H * 0.44), color=(1.0, 0.88, 0.65), size=5.0)]),
            'slow_in', 'black', sfx=[('riser', 0.0)], emph=['retournant']),
        seg("Le {14|quatorze} février {1990|mille neuf cent quatre-vingt-dix}, à six milliards de kilomètres, elle a photographié la Terre.",
            P(PBD, cx=PBD_X, cy=PBD_Y), PBD_CENTER, 'fade', label='14 FÉVRIER 1990', emph=['Terre']),
        seg("La voici.", P(PBD, cx=PBD_X, cy=PBD_Y, zoom=2.6, extra=[ring(r=60, t0=0.3)]), PBD_CENTER, 'zoom', emph=['voici'], music=0.2),
        seg("Ce petit point, plus petit qu'un pixel, c'est nous. Tous les humains qui ont jamais vécu sont là.",
            P(PBD, cx=PBD_X, cy=PBD_Y, zoom=4.0, extra=[ring(r=70, t0=0.2)]), PBD_CENTER, 'cut', emph=['nous']),
        seg("L'astronome Carl Sagan l'a appelée : le « point bleu pâle ».", V(EARTH, 50.0), 'slow_in', 'fade', emph=['point', 'bleu', 'pâle'], music=0.7),
        seg("Aujourd'hui, Voyager {1|un} émet avec la puissance d'une ampoule de frigo… et on capte encore son signal.", V(EARTH, 70.0), 'drift', 'whip', emph=['frigo']),
        seg("Mais son énergie baisse chaque année. Elle devrait se taire dans les années {2030|deux mille trente}.", V(HELIO, 20.0, speed=0.6), 'slow_in', 'fade', emph=['taire']),
        seg("À bord, un disque en or : des sons, de la musique, et des salutations en cinquante-cinq langues. Un message pour qui le trouvera.",
            V(VOY_CRAFT, 0.0, speed=0.3, cx=0.3, zoom=1.3), 'push', 'zoom', emph=['or']),
        seg("Dans environ quarante mille ans, elle passera près d'une autre étoile.", P(MILKYWAY, zoom=1.3), 'in', 'cut', emph=['étoile']),
        seg("Tu imagines ? Dis-moi en commentaire ce que tu mettrais sur ce disque.", P(PBD, cx=PBD_X, cy=PBD_Y, zoom=2.0), 'out', 'fade', music=0.3),
    ])

VIDEOS = [R16, R17, R18, R19, R20, R21, R22, R23, R24, R25]
