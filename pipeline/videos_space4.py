"""NICHE_1 « Vertige Cosmique » — semaine du 16 au 22 novembre 2026 (vidéos 26 à 39, ambiances 10 à 14, edits 9 à 13).

Même chaîne que les séries précédentes, avec un montage plus sobre à la demande de l'utilisateur (« pas d'effets
moches ») : uniquement des coupes franches, des fondus et des fondus au noir ; mouvements de caméra lents
(pas de flash blanc, pas de coup de fouet, pas de zoom brutal, pas de bruitages d'impact).

Images : NASA (SVS, NASA Image and Video Library, JPL), domaine public ; bandes-son NASA retirées.
Faits vérifiés (sources dans docs.SOURCES) ; chiffres incertains formulés avec « environ », « près de », « plus de ».
"""
from videos_real import V, P, txt, back, counter, seg, REAL, EARTH, ISS, JUPITER, SUN171, SUN193, SUN131, \
    AUR_ISS, AUR_AUS, AUR_MAY, MILKYWAY, NSM, MOON, OU, OUSN, WEB, PV, DAV, VM, HUBBLE, BH_DISK, BH_TDE, BH_ORBIT, HOTJ_ORBIT
from videos_space2 import SN, PULSAR, MAG, MAG_WIDE, MOONTOUR, GRS, FUSION, SDO171, SDO304, SDO131
from videos_space3 import P_PULL, P_SWING, HELIO, GOLD, ICE, HOT
from videos_edits import clipd, amb, edit, cut, sc, CV, F0
import layers_cine as L

# ----------------------------------------------------------------------------- nouvelles sources (toutes déjà en cache)
TGF = 'svs:10706/10706_Fermi_TGF_H264_Best_1280x720_59.94.mov'        # Fermi : flashs gamma terrestres et antimatière
TGF_SPOT = 'svs:10707/10707_Fermi_Spots_TGF_MPEG4_1280X720_29.97.mp4'  # Fermi au-dessus de la Terre
FIREFLY = 'nasa:GSFC_20100917_Firefly_m10651_Pro_Elec_Gamma'           # électrons accélérés au-dessus d'un orage
ISS_LIGHT = 'nasa:311_ScienceCasts-observing-lightning-ISS'            # orages et éclairs vus de la Station spatiale
PERSEUS = 'svs:14799/PerseusSimulationReelFINAL.mp4'                   # amas de Persée, simulation verticale (1,8–14 s sans texte)
GALEVO = 'svs:10661/Galaxy_Evolution_wideshot-1080p.mov'                 # naissance d'une galaxie le long des filaments (simulation)
WISPR = 'svs:14095/WISPR_4thflyby.mp4'                                 # surface de Vénus vue par Parker (WISPR)
CRAB = 'nasa:PIA03606'                                                 # nébuleuse du Crabe (Hubble)
CARINA = 'nasa:carina_nebula'                                          # « Falaises cosmiques » de la Carène (Webb)
SRING = 'nasa:southern_ring_nebula'                                    # nébuleuse de l'Anneau austral (Webb, 2 vues côte à côte)
PILLARS = 'nasa:GSFC_20171208_Archive_e000842'                         # Piliers de la création (Hubble, infrarouge)
SUNFL = 'nasa:hubble-sees-a-galactic-sunflower_21136469209_o'          # galaxie du Tournesol (Hubble)
SOMB = 'nasa:PIA15426'                                                 # galaxie du Sombrero
HELIX = 'nasa:PIA15658'                                                # nébuleuse de l'Hélice
EARTHSET = 'nasa:art002e021278'                                        # coucher de Terre derrière la Lune (Artemis I)

CAM_IN, CAM_SLOW, CAM_DRIFT, CAM_OUT = 'in', 'slow_in', 'drift', 'out'


def _has_overlay(scene):
    """Vrai si le plan porte un texte incrusté (txt, compteur, bandeau) : V(..., extra=[...]) ou P(..., extra=[...])."""
    for c in getattr(scene, '__closure__', None) or ():
        v = c.cell_contents
        if isinstance(v, (list, tuple)) and v and all(callable(x) for x in v):
            return True
    return False


def _clean_transitions(segments):
    """Un fondu juste après un plan avec texte ou étiquette ferait se chevaucher deux textes : coupe franche à la place."""
    for a, b in zip(segments, segments[1:]):
        if b.get('trans') == 'fade' and (a.get('label') or _has_overlay(a.get('scene'))):
            b['trans'] = 'cut'
    return segments


def vid(id, title, hook, prog, key, seed, segments):
    segments = _clean_transitions(segments)
    return dict(id=id, niche='NICHE_1', theme='space', speed=1.08, voice_reverb=0.06, **REAL,
                title=title, hook_text=hook,
                music=dict(style='space', prog=prog, key=key, bpm=72, seed=seed, start=0.3), segments=segments)


# ============================================================================= 26 — L'événement de Carrington (1859)
R26 = vid('video_26', "Le jour où le ciel s'est embrasé", "EN 1859, LE CIEL\\NS'EST EMBRASÉ", 'minor_dark', 44, 2601, [
    seg("En {1859|dix-huit cent cinquante-neuf}, le ciel s'est mis à briller jusqu'aux Caraïbes, et les télégraphes ont craché des étincelles.",
        V(AUR_MAY, 0.0, speed=0.5), CAM_IN, sfx=['boom'], music=0.35, emph=['étincelles']),
    seg("Tout commence le {1|premier} septembre. L'astronome anglais Richard Carrington est en train de dessiner les taches du Soleil.",
        V(SDO171, 0.0, speed=0.5), CAM_SLOW, 'fade', label='1ER SEPTEMBRE 1859', emph=['Carrington']),
    seg("Soudain, deux points d'une lumière blanche aveuglante apparaissent, pendant à peine cinq minutes.", V(SUN131, 1.0, speed=0.6), CAM_IN, emph=['aveuglante']),
    seg("C'est la première éruption solaire jamais observée.", V(SDO131, 0.0, speed=0.5), CAM_SLOW, emph=['première']),
    seg("Moins de dix-huit heures plus tard, un nuage géant de particules frappe la Terre.", V(SDO304, 0.0, speed=0.5), CAM_DRIFT, 'fade', emph=['frappe']),
    seg("Des milliards de tonnes de plasma, lancées à plus de huit millions de kilomètres par heure.",
        V(SUN193, 2.0, speed=0.6, extra=[back(170, 560, 0.6), counter(0, 8000000, y=340, size=120, suffix=' km/h', color=HOT, t1=2.2, sub='la vitesse du nuage')]),
        CAM_SLOW, emph=['huit', 'millions']),
    seg("Des aurores apparaissent partout : à Cuba, à Hawaï, au Mexique.", V(AUR_ISS, 30.0), CAM_SLOW, 'fade', emph=['Cuba']),
    seg("Dans les montagnes Rocheuses, des mineurs se réveillent et préparent leur petit-déjeuner… en pleine nuit, tellement le ciel est lumineux.",
        V(AUR_AUS, 12.0), CAM_DRIFT, emph=['nuit']),
    seg("Les télégraphes deviennent fous : étincelles, employés électrisés, et certaines lignes fonctionnent même sans batterie, avec le seul courant de l'aurore.",
        V(AUR_AUS, 22.0), CAM_SLOW, emph=['batterie']),
    seg("C'est l'événement de Carrington, la plus puissante tempête solaire jamais enregistrée.", V(SUN171, 4.0, speed=0.6), CAM_IN, 'fade',
        label='ÉVÉNEMENT DE CARRINGTON', music=0.6),
    seg("Et si elle arrivait aujourd'hui ?", V(EARTH, 20.0), CAM_SLOW, 'black', sfx=[('riser', 0.0)], emph=['aujourd\'hui']),
    seg("Satellites en panne, GPS perturbé, réseaux électriques coupés pendant des semaines, voire des mois.", V(ISS, 1310.0), CAM_DRIFT, emph=['coupés']),
    seg("Une étude américaine de {2008|deux mille huit} estimait les dégâts à plus de mille milliards de dollars, rien que la première année.",
        V(EARTH, 50.0, extra=[back(170, 520), txt('> 1 000 MILLIARDS $', 330, 110)]), CAM_SLOW, emph=['mille', 'milliards']),
    seg("Et en juillet {2012|deux mille douze}, on l'a échappé belle : une éruption aussi puissante est partie dans une autre direction. Une semaine plus tôt, elle nous frappait.",
        V(P_PULL, 8.0, speed=0.6), CAM_SLOW, 'fade', label='JUILLET 2012', emph=['semaine'], music=0.7),
    seg("Rassure-toi : des satellites surveillent le Soleil en permanence, pour nous prévenir un à deux jours à l'avance.", V(SDO171, 2.0, speed=0.5), CAM_SLOW),
    seg("Tu as vu les aurores de mai {2024|deux mille vingt-quatre} ? Dis-le en commentaire.", V(AUR_MAY, 2.5, speed=0.5), CAM_OUT, 'fade', music=0.3),
])

# ============================================================================= 27 — L'or vient de collisions d'étoiles
R27 = vid('video_27', "L'or de ta bague vient d'une collision d'étoiles", "L'OR DE TA BAGUE\\NVIENT DE L'ESPACE", 'minor_wonder', 46, 2701, [
    seg("L'or de ta bague a été fabriqué… dans une collision d'étoiles.", V(NSM, 15.0, speed=0.7), CAM_IN, sfx=['boom'], music=0.35, emph=['collision']),
    seg("Sur Terre, impossible d'en fabriquer en grande quantité. Même le Soleil en est incapable.", V(SUN171, 1.0, speed=0.6), CAM_SLOW, 'fade', emph=['incapable']),
    seg("Il faut un événement bien plus violent : deux étoiles à neutrons qui tournent l'une autour de l'autre.", V(NSM, 3.0, speed=0.8), CAM_SLOW,
        label='DEUX ÉTOILES À NEUTRONS', emph=['neutrons']),
    seg("Des étoiles mortes, à peine plus grandes qu'une ville, mais plus lourdes que le Soleil.", V(NSM, 7.0, speed=0.8), CAM_IN, emph=['ville']),
    seg("Elles se rapprochent en spirale pendant des millions d'années… puis se percutent à une vitesse folle.", V(NSM, 11.0, speed=0.7), CAM_SLOW, emph=['percutent']),
    seg("L'explosion porte un nom : une kilonova.", V(NSM, 19.0, speed=0.7), CAM_IN, 'fade', label='KILONOVA', emph=['kilonova'], music=0.6),
    seg("Dans ses débris, des réactions nucléaires extrêmes forgent les éléments les plus lourds : l'or, le platine, l'uranium.",
        V(NSM, 22.0, speed=0.6), CAM_SLOW, emph=['or', 'platine']),
    seg("Et le {17|dix-sept} août {2017|deux mille dix-sept}, on en a vu une pour la première fois.", V(NSM, 14.0, speed=0.6), CAM_DRIFT, 'fade', label='17 AOÛT 2017'),
    seg("Les détecteurs LIGO et Virgo ont d'abord capté des ondes gravitationnelles : l'espace lui-même qui vibrait.", V(NSM, 12.5, speed=0.5), CAM_SLOW, emph=['vibrait']),
    seg("Moins de deux secondes plus tard, le télescope spatial Fermi recevait un éclair de rayons gamma venu du même endroit.", V(TGF_SPOT, 12.0, speed=0.6), CAM_SLOW, 'fade', emph=['éclair']),
    seg("La collision avait eu lieu il y a environ cent trente millions d'années, dans une autre galaxie.", V(OU, 33.0), CAM_SLOW, emph=['millions']),
    seg("Les astronomes estiment qu'elle a produit plusieurs fois la masse de la Terre… en or.",
        V(NSM, 24.0, speed=0.5, extra=[back(170, 520), txt('DES TERRES EN OR', 330, 120, GOLD)]), CAM_IN, 'fade', emph=['or'], music=0.7),
    seg("La plupart de l'or de notre planète a coulé dans son noyau. Celui qu'on extrait aurait été apporté plus tard par des météorites.",
        V(EARTH, 30.0), CAM_SLOW, emph=['météorites']),
    seg("La prochaine fois que tu vois un bijou en or, souviens-toi : il vient d'une explosion d'étoiles. Tu le savais ? Dis-le en commentaire.",
        V(NSM, 23.0, speed=0.4), CAM_OUT, 'fade', music=0.3),
])

# ============================================================================= 28 — Le magnétar
R28 = vid('video_28', "L'aimant le plus puissant de l'Univers", "L'AIMANT LE PLUS\\NPUISSANT DE L'UNIVERS", 'minor_float', 45, 2801, [
    seg("Voici l'aimant le plus puissant de l'Univers.", V(MAG, 3.0), CAM_IN, sfx=['boom'], music=0.35, emph=['puissant']),
    seg("C'est un magnétar : une étoile à neutrons, le cœur mort d'une étoile qui a explosé.", V(SN, 25.0, speed=0.6), CAM_SLOW, 'fade', label='MAGNÉTAR', emph=['magnétar']),
    seg("Elle ne mesure qu'une vingtaine de kilomètres, mais elle pèse plus lourd que le Soleil.", V(MAG, 10.0), CAM_SLOW, emph=['vingtaine']),
    seg("Son champ magnétique est environ un million de milliards de fois plus fort que celui de la Terre.",
        V(MAG_WIDE, 4.0, extra=[back(170, 520), txt('× 1 000 000 000 000 000', 330, 72, ICE)]), CAM_IN, 'fade', emph=['million', 'milliards']),
    seg("S'il passait à mi-chemin entre la Terre et la Lune, il effacerait toutes les cartes bancaires de la planète.", V(MAG_WIDE, 9.0), CAM_SLOW, emph=['cartes']),
    seg("Et à mille kilomètres, il te tuerait : son champ déformerait les atomes de ton corps.", V(MAG, 17.0), CAM_IN, emph=['atomes'], music=0.6),
    seg("Parfois, sa croûte se fissure. Les astronomes parlent de tremblement d'étoile.", V(MAG_WIDE, 14.0), CAM_DRIFT, 'fade', label="TREMBLEMENT D'ÉTOILE"),
    seg("Le {27|vingt-sept} décembre {2004|deux mille quatre}, l'un d'eux a libéré en un dixième de seconde plus d'énergie que le Soleil en cent mille ans.",
        V(MAG_WIDE, 18.0), CAM_SLOW, 'black', sfx=[('riser', 0.0)], label='27 DÉCEMBRE 2004', emph=['dixième']),
    seg("Il se trouvait à environ cinquante mille années-lumière. Et pourtant, son éclair a perturbé la haute atmosphère de la Terre.",
        V(EARTH, 70.0), CAM_SLOW, emph=['Terre'], music=0.7),
    seg("Heureusement, aucun magnétar connu n'est assez proche pour nous menacer.", P(MILKYWAY), CAM_SLOW, 'fade', emph=['menacer']),
    seg("On en connaît une trentaine dans notre galaxie.", V(PULSAR, 6.0, speed=0.6), CAM_DRIFT, emph=['trentaine']),
    seg("Tu savais que ça existait ? Dis-le en commentaire.", V(MAG, 24.0), CAM_OUT, 'fade', music=0.3),
])

# ============================================================================= 29 — La supernova
R29 = vid('video_29', "Une étoile qui brille autant qu'une galaxie", "UNE SEULE ÉTOILE\\NAUSSI BRILLANTE\\NQU'UNE GALAXIE", 'minor_epic', 45, 2901, [
    seg("Quand cette étoile explose, elle brille autant que toute sa galaxie : des milliards d'étoiles.", V(SN, 21.0, speed=0.6), CAM_IN, sfx=['boom'], music=0.35, emph=['galaxie']),
    seg("C'est une supernova : la mort d'une étoile au moins huit fois plus lourde que le Soleil.", V(SN, 3.0, speed=0.7), CAM_SLOW, 'fade', label='SUPERNOVA', emph=['supernova']),
    seg("À la fin de sa vie, son cœur n'a plus de carburant. Il s'effondre sur lui-même… en moins d'une seconde.", V(SN, 4.5, speed=0.5), CAM_IN, emph=['seconde']),
    seg("Puis tout rebondit, dans une explosion qui projette la matière à des dizaines de milliers de kilomètres par seconde.", V(SN, 19.5, speed=0.6, mode=F0, fit_scale=1.5), CAM_SLOW, emph=['explosion'], music=0.6),
    seg("En {1054|mille cinquante-quatre}, des astronomes chinois en ont vu une en plein jour, pendant plus de trois semaines.", P(CRAB, zoom=1.4), CAM_SLOW, 'fade', label='AN 1054', emph=['jour']),
    seg("Ce qu'il en reste aujourd'hui, c'est ça : la nébuleuse du Crabe.", P(CRAB), CAM_OUT, emph=['Crabe']),
    seg("Et au centre, une étoile à neutrons qui tourne sur elle-même trente fois par seconde.", V(PULSAR, 2.0, speed=0.6), CAM_SLOW, 'fade', emph=['trente']),
    seg("Dans notre galaxie, il y en aurait environ deux ou trois par siècle. Mais la dernière vue à l'œil nu date de {1604|seize cent quatre}.",
        V(OUSN, 22.0, speed=0.7), CAM_SLOW, label='DERNIÈRE : 1604', emph=['seize', 'cent', 'quatre']),
    seg("Bételgeuse, l'étoile rouge de la constellation d'Orion, pourrait être la prochaine… d'ici cent mille ans.", V(SN, 1.0, speed=0.6), CAM_DRIFT, 'fade', emph=['Bételgeuse']),
    seg("Et sans ces explosions, tu n'existerais pas : une partie du calcium de tes os et du fer de ton sang a été dispersée par des supernovas.",
        V(SN, 30.0, speed=0.5), CAM_SLOW, emph=['calcium', 'fer'], music=0.7),
    seg("Tu aimerais voir une supernova de ton vivant ? Dis-le en commentaire.", V(SN, 37.0, speed=0.4), CAM_OUT, 'fade', music=0.3),
])

# ============================================================================= 30 — La toile cosmique
R30 = vid('video_30', "L'Univers ressemble à ça", "L'UNIVERS\\NRESSEMBLE À ÇA", 'minor_wonder', 43, 3001, [
    seg("Si tu pouvais voir l'Univers en entier, il ressemblerait à ça.", V(WEB, 5.0, speed=0.7, mode=CV), CAM_IN, sfx=['boom'], music=0.35, emph=['Univers']),
    seg("Une immense toile : des filaments de galaxies, autour de gigantesques vides.", V(WEB, 14.0, speed=0.7, mode=CV, cx=0.3), CAM_SLOW, 'fade', label='LA TOILE COSMIQUE', emph=['toile']),
    seg("Chaque petit point lumineux est une galaxie, avec des milliards d'étoiles.", V(GALEVO, 12.5, speed=0.6, mode=CV), CAM_IN, emph=['galaxie']),
    seg("Ces filaments mesurent des centaines de millions d'années-lumière.", V(WEB, 22.0, speed=0.7, mode=CV, cx=0.7), CAM_SLOW, emph=['centaines']),
    seg("Et entre eux, des vides presque déserts, où tu pourrais voyager des millions d'années sans croiser une seule galaxie.", V(OU, 12.0), CAM_DRIFT, 'fade', emph=['vides']),
    seg("Pourquoi cette forme ? À cause de la matière noire.", V(WEB, 1.0, speed=0.6, mode=CV), CAM_SLOW, 'black', sfx=[('riser', 0.0)], emph=['noire'], music=0.6),
    seg("Une matière invisible, environ cinq fois plus abondante que la matière ordinaire.",
        V(WEB, 9.0, speed=0.6, mode=CV, cx=0.4, extra=[back(170, 520), txt('× 5', 330, 200, ICE)]), CAM_IN, emph=['invisible']),
    seg("Sa gravité a formé une sorte de squelette, et les galaxies s'y sont accrochées comme des gouttes de rosée sur une toile d'araignée.",
        V(GALEVO, 3.5, speed=0.6, mode=CV), CAM_SLOW, 'fade', emph=['rosée']),
    seg("Personne ne l'a jamais vue directement : on la devine à sa gravité.", V(OU, 36.0), CAM_SLOW, emph=['gravité']),
    seg("Et en {2025|deux mille vingt-cinq}, des astronomes ont réussi à obtenir une image de l'un de ces filaments de gaz.", V(GALEVO, 6.0, speed=0.6, mode=CV), CAM_IN, 'fade', label='2025'),
    seg("Des chercheurs ont même remarqué que cette toile ressemble étrangement… au réseau de neurones de notre cerveau.", V(WEB, 26.0, speed=0.5, mode=CV, cx=0.6), CAM_SLOW, emph=['cerveau'], music=0.7),
    seg("Et si l'Univers était un cerveau géant ? Dis-le en commentaire.", V(WEB, 18.0, speed=0.4, mode=CV), CAM_OUT, 'fade', music=0.3),
])

# ============================================================================= 31 — La face cachée de la Lune
R31 = vid('video_31', "On ne voit jamais l'autre face de la Lune", "TU N'AS JAMAIS VU\\NL'AUTRE FACE\\NDE LA LUNE", 'minor_drift', 43, 3101, [
    seg("Depuis la Terre, on voit toujours la même face de la Lune. Jamais l'autre.", V(MOON, 73.0, speed=0.6), CAM_IN, sfx=['boom'], music=0.35, emph=['jamais']),
    seg("Parce qu'elle tourne sur elle-même exactement à la même vitesse qu'elle tourne autour de nous.", V(MOON, 102.0, speed=0.6), CAM_SLOW, 'fade', emph=['vitesse']),
    seg("Un tour en vingt-sept jours, dans les deux cas.", V(MOONTOUR, 268.5, speed=0.8), CAM_SLOW, label='27 JOURS', emph=['vingt-sept']),
    seg("Ce n'est pas un hasard : au début, elle tournait plus vite, mais la gravité de la Terre l'a freinée.", V(MOONTOUR, 4.5, speed=0.6), CAM_DRIFT, emph=['freinée']),
    seg("On l'appelle la face cachée, mais elle n'est pas dans le noir : elle reçoit autant de soleil que l'autre.", V(MOONTOUR, 150.0, speed=0.8), CAM_SLOW, 'fade', emph=['soleil']),
    seg("Et petit secret : grâce à un léger balancement, on voit en fait cinquante-neuf pour cent de sa surface.",
        V(MOON, 190.0, speed=0.6, extra=[back(170, 520), txt('59 %', 330, 200, GOLD)]), CAM_IN, emph=['cinquante-neuf'], music=0.6),
    seg("La première photo de l'autre face a été prise en {1959|dix-neuf cent cinquante-neuf}, par une sonde soviétique : Luna 3.", V(MOONTOUR, 125.0, speed=0.8), CAM_SLOW, 'fade',
        label='LUNA 3 • 1959'),
    seg("Et elle ne ressemble pas du tout à celle qu'on connaît : presque pas de grandes taches sombres, mais des cratères partout.", V(MOONTOUR, 237.0, speed=0.8), CAM_DRIFT, emph=['cratères']),
    seg("Les premiers humains à la voir de leurs propres yeux sont les astronautes d'Apollo 8, en {1968|dix-neuf cent soixante-huit}.", P(EARTHSET), CAM_SLOW, 'fade',
        label='APOLLO 8 • 1968', emph=['yeux']),
    seg("En {2019|deux mille dix-neuf}, la Chine y a posé un robot pour la première fois. Et en {2024|deux mille vingt-quatre}, elle en a même rapporté des échantillons.",
        V(MOONTOUR, 181.0, speed=0.8), CAM_SLOW, emph=['échantillons'], music=0.7),
    seg("Tu savais qu'on en voyait cinquante-neuf pour cent ? Dis-le en commentaire.", V(MOON, 219.0, speed=0.5), CAM_OUT, 'fade', music=0.3),
])

# ============================================================================= 32 — La surface de Vénus à travers les nuages
R32 = vid('video_32', "On a vu la surface de Vénus à travers ses nuages", "ON A VU SOUS\\NLES NUAGES DE VÉNUS", 'minor_dark', 41, 3201, [
    seg("Pour la première fois, une sonde a photographié la surface de Vénus… à travers ses nuages.", V(WISPR, 0.0, speed=0.5), CAM_IN, sfx=['boom'], music=0.35, emph=['surface']),
    seg("Vénus est couverte d'une épaisse couche de nuages d'acide sulfurique. Impossible de voir le sol en lumière visible.", V(VM, 108.0, speed=0.6, mode=CV), CAM_SLOW, 'fade',
        emph=['acide']),
    seg("Mais en {2020|deux mille vingt} et {2021|deux mille vingt et un}, la sonde Parker Solar Probe l'a frôlée pour prendre de l'élan.", V(PV, 182.0, speed=0.6, mode=CV), CAM_SLOW,
        label='PARKER SOLAR PROBE', emph=['élan']),
    seg("Sa caméra, pointée vers la face de nuit, a capté une lueur venue du sol.", V(WISPR, 1.6, speed=0.5), CAM_IN, 'fade', emph=['lueur']),
    seg("Le sol de Vénus est si chaud qu'il brille dans l'obscurité, comme du métal chauffé.", V(PV, 108.0, speed=0.5, mode=CV), CAM_SLOW, emph=['brille']),
    seg("Environ quatre cent soixante degrés : assez pour faire fondre le plomb.",
        V(VM, 134.0, speed=0.6, mode=CV, extra=[back(170, 520), txt('≈ 460 °C', 330, 170, HOT)]), CAM_IN, 'fade', emph=['plomb'], music=0.6),
    seg("Sur ces images, on distingue des continents, des plaines et des plateaux.", V(PV, 92.0, speed=0.6, mode=CV), CAM_SLOW, emph=['continents']),
    seg("La pression y est quatre-vingt-dix fois plus forte que sur Terre : comme à neuf cents mètres sous la mer.", V(DAV, 68.0, speed=0.6), CAM_DRIFT, 'fade', emph=['quatre-vingt-dix']),
    seg("Les sondes soviétiques qui s'y sont posées n'ont survécu qu'un peu plus de deux heures au maximum.", V(PV, 154.0, speed=0.6, mode=CV), CAM_SLOW, emph=['survécu']),
    seg("Pourtant, Vénus est presque la jumelle de la Terre : à peu près la même taille, et presque la même masse.", V(PV, 166.0, speed=0.6, mode=CV), CAM_SLOW, 'fade', emph=['jumelle']),
    seg("Elle a peut-être eu des océans, avant qu'un effet de serre incontrôlable ne la transforme en fournaise.", V(VM, 37.0, speed=0.6, mode=CV), CAM_SLOW, emph=['océans'], music=0.7),
    seg("Tu irais sur Vénus ? Dis-le en commentaire.", V(VM, 61.0, speed=0.5, mode=CV), CAM_OUT, 'fade', music=0.3),
])

# ============================================================================= 33 — Jupiter et le barycentre
R33 = vid('video_33', "Jupiter ne tourne pas autour du Soleil", "JUPITER NE TOURNE PAS\\NAUTOUR DU SOLEIL", 'minor_float', 44, 3301, [
    seg("Jupiter ne tourne pas vraiment autour du Soleil.", V(JUPITER, 4.0, speed=0.6), CAM_IN, sfx=['boom'], music=0.35, emph=['vraiment']),
    seg("En réalité, Jupiter et le Soleil tournent tous les deux autour d'un point commun.", V(JUPITER, 9.0, speed=0.6), CAM_SLOW, 'fade', emph=['tous', 'deux']),
    seg("Ce point s'appelle le barycentre : leur centre de gravité.", V(HELIO, 2.0, speed=0.6), CAM_SLOW, label='LE BARYCENTRE', emph=['barycentre']),
    seg("Pour la Terre et le Soleil, il se trouve presque au centre du Soleil.", V(SUN171, 1.0, speed=0.6), CAM_SLOW, 'fade'),
    seg("Mais Jupiter est si lourde que ce point se trouve… en dehors du Soleil, juste au-dessus de sa surface.", V(P_PULL, 11.0, speed=0.5), CAM_IN, emph=['dehors'], music=0.6),
    seg("Résultat : le Soleil lui-même dessine de petits cercles dans l'espace, un tour tous les douze ans environ.", V(SDO304, 0.0, speed=0.5), CAM_DRIFT, 'fade', emph=['cercles']),
    seg("Jupiter pèse deux fois et demie plus lourd que toutes les autres planètes réunies.",
        V(JUPITER, 38.5, speed=0.6, extra=[back(170, 520), txt('× 2,5', 330, 200, GOLD)]), CAM_SLOW, emph=['réunies']),
    seg("Tu pourrais faire rentrer plus de mille trois cents Terres à l'intérieur.", V(GRS, 26.0, speed=0.6, mode=CV), CAM_IN, 'fade', emph=['mille', 'trois', 'cents']),
    seg("Et ce petit mouvement des étoiles nous sert à trouver d'autres planètes.", V(HOTJ_ORBIT, 1.0, speed=0.6), CAM_SLOW, emph=['planètes']),
    seg("Quand une étoile oscille légèrement, c'est qu'une planète tourne autour et la tire. C'est comme ça qu'on a découvert la première planète autour d'une étoile semblable au Soleil, en {1995|dix-neuf cent quatre-vingt-quinze}.",
        V(HOTJ_ORBIT, 6.0, speed=0.5), CAM_DRIFT, 'fade', label='1995', emph=['oscille']),
    seg("Par deux astronomes suisses, Michel Mayor et Didier Queloz, prix Nobel de physique en {2019|deux mille dix-neuf}.", P(MILKYWAY), CAM_SLOW, emph=['Nobel'], music=0.7),
    seg("Tu savais que le Soleil bougeait ? Dis-le en commentaire.", V(GRS, 34.0, speed=0.4, mode=CV), CAM_OUT, 'fade', music=0.3),
])

# ============================================================================= 34 — Webb voit le passé
R34 = vid('video_34', "Plus tu regardes loin, plus tu vois le passé", "PLUS TU REGARDES LOIN\\NPLUS TU VOIS LE PASSÉ", 'minor_wonder', 46, 3401, [
    seg("Quand tu regardes le ciel, tu regardes le passé.", P(CARINA, cx=0.35), CAM_IN, sfx=['boom'], music=0.35, emph=['passé']),
    seg("La lumière va très vite, mais pas instantanément : environ trois cent mille kilomètres par seconde.", P(MILKYWAY), CAM_SLOW, 'fade', emph=['trois', 'cent', 'mille']),
    seg("La Lune que tu vois, c'est celle d'il y a un peu plus d'une seconde. Le Soleil, celui d'il y a huit minutes.", V(MOON, 73.0, speed=0.6), CAM_SLOW, emph=['huit', 'minutes']),
    seg("Les étoiles, celles d'il y a des dizaines, des centaines, ou des milliers d'années.", V(OU, 25.0), CAM_DRIFT, 'fade', emph=['milliers']),
    seg("Alors les télescopes sont de vraies machines à remonter le temps.", V(HUBBLE, 6.0, speed=0.7), CAM_SLOW, emph=['temps'], music=0.6),
    seg("Et le plus puissant d'entre eux, c'est le télescope spatial James Webb, lancé le {25|vingt-cinq} décembre {2021|deux mille vingt et un}.",
        P(SRING, cx=0.25), CAM_SLOW, 'fade', label='JAMES WEBB • 2021', emph=['Webb']),
    seg("Son miroir mesure six mètres et demi, et il observe depuis un point situé à un million et demi de kilomètres de la Terre.", P(CARINA, cx=0.7), CAM_DRIFT,
        emph=['six', 'mètres']),
    seg("Il voit en infrarouge : la lumière des galaxies les plus lointaines, étirée par l'expansion de l'Univers.", P(PILLARS), CAM_SLOW, 'fade', emph=['infrarouge']),
    seg("Il a observé des galaxies telles qu'elles étaient moins de trois cents millions d'années après le Big Bang.", V(OU, 34.0), CAM_IN, emph=['Big', 'Bang'], music=0.7),
    seg("Sur les treize milliards huit cents millions d'années de l'Univers, c'est comme regarder sa photo de bébé.", P(SUNFL), CAM_SLOW, 'fade', emph=['bébé']),
    seg("Si tu pouvais voir n'importe quel moment du passé, tu choisirais lequel ? Dis-le en commentaire.", P(CARINA, cx=0.5), CAM_OUT, 'fade', music=0.3),
])

# ============================================================================= 35 — Le trou noir qui chante (Persée)
R35 = vid('video_35', "Ce trou noir chante", "CE TROU NOIR\\NCHANTE", 'minor_dark', 43, 3501, [
    seg("Dans l'espace, il n'y a pas de son. Pourtant… ce trou noir chante.", V(PERSEUS, 9.0, speed=0.8), CAM_IN, sfx=['boom'], music=0.35, emph=['chante']),
    seg("Il se trouve au cœur de l'amas de galaxies de Persée, à environ deux cent quarante millions d'années-lumière.", V(PERSEUS, 2.0, speed=0.8), CAM_SLOW, 'fade',
        label='AMAS DE PERSÉE', emph=['Persée']),
    seg("L'espace est presque vide, alors le son ne s'y propage pas. Mais ici, les galaxies baignent dans un immense nuage de gaz très chaud.", V(WEB, 12.0, speed=0.6), CAM_SLOW,
        emph=['gaz']),
    seg("En avalant de la matière, le trou noir envoie des ondes de pression dans ce gaz. Comme des vagues.", V(PERSEUS, 12.0, speed=0.6), CAM_IN, 'fade', emph=['vagues']),
    seg("Des ondes de pression… c'est exactement ce qu'est un son.", V(BH_DISK, 2.0, speed=0.6), CAM_SLOW, emph=['son'], music=0.6),
    seg("En {2003|deux mille trois}, le télescope spatial Chandra les a repérées. Et on a pu calculer la note.", V(BH_DISK, 10.0, speed=0.6), CAM_DRIFT, 'fade', label='CHANDRA • 2003'),
    seg("C'est un si bémol.", V(PERSEUS, 6.0, speed=0.6), CAM_IN, emph=['bémol']),
    seg("Mais cinquante-sept octaves plus grave que le do du milieu d'un piano.",
        V(BH_DISK, 16.0, speed=0.6, extra=[back(170, 520), txt('57 OCTAVES', 330, 160, ICE)]), CAM_SLOW, 'fade', emph=['cinquante-sept']),
    seg("La note la plus grave jamais détectée : une seule vibration dure des millions d'années.", V(BH_ORBIT, 6.0, speed=0.6), CAM_SLOW, emph=['millions'], music=0.7),
    seg("Aucune oreille humaine ne pourra jamais l'entendre. Alors en {2022|deux mille vingt-deux}, la NASA l'a remontée de plusieurs dizaines d'octaves pour la rendre audible.",
        V(PERSEUS, 3.0, speed=0.6), CAM_DRIFT, 'fade', label='2022', emph=['audible']),
    seg("Tu aimerais entendre le chant d'un trou noir ? Dis-le en commentaire.", V(BH_DISK, 24.0, speed=0.4), CAM_OUT, 'fade', music=0.3),
])

# ============================================================================= 36 — Un trou noir déchire une étoile
R36 = vid('video_36', "Un trou noir déchire une étoile", "UN TROU NOIR\\NDÉCHIRE UNE ÉTOILE", 'minor_dark', 44, 3601, [
    seg("Voici ce qui arrive quand une étoile passe trop près d'un trou noir géant.", V(BH_TDE, 15.0, mode=CV), CAM_IN, sfx=['boom'], music=0.35, emph=['trop']),
    seg("La gravité est tellement plus forte du côté du trou noir que l'étoile est étirée… comme un spaghetti.", V(BH_TDE, 17.0, mode=CV), CAM_SLOW, 'fade', emph=['spaghetti']),
    seg("Les astronomes appellent vraiment ça la spaghettification.", V(BH_TDE, 19.0, mode=CV), CAM_SLOW, label='SPAGHETTIFICATION', emph=['spaghettification']),
    seg("Une partie de l'étoile est avalée. Le reste est éjecté dans l'espace.", V(BH_TDE, 23.0, mode=CV), CAM_DRIFT, 'fade', emph=['avalée']),
    seg("En tombant, le gaz forme un disque qui chauffe à des millions de degrés, et brille plus fort que des milliards d'étoiles.", V(BH_TDE, 28.0, mode=CV), CAM_IN, emph=['millions'],
        music=0.6),
    seg("En {2011|deux mille onze}, le satellite Swift de la NASA en a surpris un, à près de quatre milliards d'années-lumière.", V(BH_TDE, 31.0, mode=CV), CAM_SLOW, 'fade', label='2011'),
    seg("Le trou noir lançait même un jet de matière pointé droit vers la Terre.", V(BH_TDE, 34.0, mode=CV), CAM_IN, emph=['Terre']),
    seg("Ces drames sont rares : dans une galaxie, ça arrive environ une fois tous les dix mille à cent mille ans.", V(BH_DISK, 8.0, speed=0.6), CAM_SLOW, 'fade', emph=['rares']),
    seg("Au centre de notre galaxie aussi, il y a un trou noir géant : Sagittarius A étoile, quatre millions de fois la masse du Soleil.",
        V(BH_DISK, 16.0, speed=0.6, extra=[back(170, 520), txt('4 MILLIONS DE SOLEILS', 330, 100)]), CAM_SLOW, label='SAGITTARIUS A*', emph=['millions'], music=0.7),
    seg("Mais rassure-toi : il est à vingt-six mille années-lumière, et le Soleil ne s'en approchera jamais.", V(BH_ORBIT, 5.0, speed=0.6), CAM_DRIFT, 'fade', emph=['jamais']),
    seg("Tu voudrais voir un trou noir de près ? Dis-le en commentaire.", V(BH_DISK, 24.0, speed=0.4), CAM_OUT, 'fade', music=0.3),
])

# ============================================================================= 37 — Les orages fabriquent de l'antimatière
R37 = vid('video_37', "Les orages fabriquent de l'antimatière", "LES ORAGES FABRIQUENT\\NDE L'ANTIMATIÈRE", 'minor_epic', 45, 3701, [
    seg("Au-dessus de nos têtes, les orages fabriquent… de l'antimatière.", V(ISS_LIGHT, 241.0, speed=0.6), CAM_IN, sfx=['boom'], music=0.35, emph=['antimatière']),
    seg("Oui, l'antimatière : celle de la science-fiction, la substance la plus chère du monde à produire.", V(ISS_LIGHT, 28.0, speed=0.6), CAM_SLOW, 'fade', emph=['chère']),
    seg("Dans un nuage d'orage, des champs électriques géants accélèrent des électrons presque à la vitesse de la lumière.", V(FIREFLY, 1.0, speed=0.6), CAM_SLOW, emph=['lumière']),
    seg("En percutant l'air, ils produisent un éclair invisible : un flash de rayons gamma, la lumière la plus énergétique qui existe.", V(TGF, 74.0, speed=0.6), CAM_IN, 'fade',
        label='FLASH GAMMA', emph=['gamma']),
    seg("Il dure moins d'une milliseconde.", V(TGF, 78.0, speed=0.6), CAM_SLOW, emph=['milliseconde']),
    seg("Et ces rayons gamma créent des paires de particules : un électron, et son jumeau d'antimatière, le positron.", V(TGF, 92.0, speed=0.6), CAM_SLOW, 'fade', emph=['positron'],
        music=0.6),
    seg("C'est le télescope spatial Fermi de la NASA qui l'a découvert, en {2009|deux mille neuf}… un peu par hasard.", V(TGF_SPOT, 12.0, speed=0.6), CAM_SLOW, label='FERMI • 2009',
        emph=['hasard']),
    seg("Il a capté la signature de l'antimatière d'un orage en Zambie… alors qu'il survolait l'Égypte, à des milliers de kilomètres.", V(TGF, 108.0, speed=0.6), CAM_DRIFT, 'fade',
        emph=['Zambie', 'Égypte']),
    seg("Les particules avaient suivi le champ magnétique de la Terre jusque dans l'espace.", V(TGF, 112.0, speed=0.6), CAM_SLOW, emph=['magnétique']),
    seg("Il y aurait environ cinq cents de ces flashs gamma chaque jour sur Terre.",
        V(TGF_SPOT, 4.0, speed=0.6, extra=[back(170, 520), txt('≈ 500 PAR JOUR', 330, 140, GOLD)]), CAM_IN, 'fade', emph=['cinq', 'cents'], music=0.7),
    seg("Rassure-toi : cette antimatière disparaît aussitôt. Dès qu'un positron rencontre un électron, les deux s'annihilent dans un éclair de lumière.", V(FIREFLY, 6.0, speed=0.6), CAM_SLOW,
        emph=['annihilent']),
    seg("Les orages sont de vrais accélérateurs de particules naturels. Tu le savais ? Dis-le en commentaire.", V(ISS_LIGHT, 244.0, speed=0.5), CAM_OUT, 'fade', music=0.3),
])

# ============================================================================= 38 — Pourquoi le ciel est noir la nuit (paradoxe d'Olbers)
R38 = vid('video_38', "Pourquoi le ciel est noir la nuit ?", "POURQUOI LE CIEL\\NEST NOIR LA NUIT ?", 'minor_drift', 44, 3801, [
    seg("Pourquoi le ciel est-il noir la nuit ? La question est beaucoup plus profonde qu'elle n'en a l'air.", V(OU, 20.0), CAM_IN, sfx=['boom'], music=0.35, emph=['noir']),
    seg("Imagine un Univers infini, rempli d'étoiles partout.", V(OU, 32.0), CAM_SLOW, 'fade', emph=['infini']),
    seg("Dans n'importe quelle direction, ton regard finirait toujours par tomber sur une étoile. Comme dans une forêt immense : où que tu regardes, tu vois un tronc.",
        P(MILKYWAY), CAM_SLOW, emph=['forêt']),
    seg("Alors le ciel entier devrait briller… aussi fort que la surface du Soleil.", V(SUN171, 2.0, speed=0.6), CAM_IN, 'fade', emph=['briller'], music=0.6),
    seg("C'est le paradoxe d'Olbers, du nom d'un astronome allemand du dix-neuvième siècle.", V(OU, 30.0), CAM_SLOW, label="PARADOXE D'OLBERS", emph=['Olbers']),
    seg("La réponse : l'Univers a un âge. Environ treize milliards huit cents millions d'années.",
        V(WEB, 8.0, speed=0.6, extra=[back(170, 520), txt('13,8 MILLIARDS D\'ANNÉES', 330, 90)]), CAM_SLOW, 'fade', emph=['âge']),
    seg("La lumière des étoiles trop lointaines n'a pas encore eu le temps d'arriver jusqu'à nous.", V(WEB, 16.0, speed=0.6), CAM_DRIFT, emph=['temps']),
    seg("Et l'Univers est en expansion : la lumière des galaxies lointaines est étirée, affaiblie, jusqu'à devenir invisible à nos yeux.", V(OU, 34.0), CAM_SLOW, 'fade', emph=['expansion']),
    seg("Le premier à avoir eu la bonne intuition n'était pas un astronome, mais l'écrivain Edgar Allan Poe, en {1848|dix-huit cent quarante-huit}.", P(SOMB), CAM_SLOW,
        label='EDGAR ALLAN POE • 1848', emph=['Poe'], music=0.7),
    seg("Et en vérité, le ciel n'est pas totalement noir : il brille encore de la lumière du Big Bang. Mais en micro-ondes, invisibles pour nous.", V(WEB, 24.0, speed=0.5), CAM_SLOW,
        'fade', emph=['Big', 'Bang']),
    seg("Tu t'étais déjà posé la question ? Dis-le en commentaire.", P(MILKYWAY), CAM_OUT, 'fade', music=0.3),
])

# ============================================================================= 39 — Le Soleil perd 4 millions de tonnes par seconde
R39 = vid('video_39', "Le Soleil perd 4 millions de tonnes par seconde", "LE SOLEIL PERD\\N4 MILLIONS DE TONNES\\NPAR SECONDE", 'minor_epic', 46, 3901, [
    seg("Chaque seconde, le Soleil perd quatre millions de tonnes.",
        V(SUN171, 1.0, speed=0.6, extra=[back(170, 560, 0.6), counter(0, 4000000, y=340, size=130, suffix=' t', color=HOT, t1=2.0, sub='chaque seconde')]),
        CAM_IN, sfx=['boom'], music=0.35, emph=['quatre', 'millions']),
    seg("Quatre millions de tonnes : à peu près le poids de quarante porte-avions.", V(P_PULL, 10.0, speed=0.5), CAM_SLOW, 'fade', emph=['porte-avions']),
    seg("Où passe toute cette matière ? Elle se transforme… en lumière.", V(SDO304, 0.0, speed=0.5), CAM_SLOW, emph=['lumière']),
    seg("Au cœur du Soleil, à environ quinze millions de degrés, des noyaux d'hydrogène fusionnent pour former de l'hélium.", V(FUSION, 2.0, speed=0.7), CAM_IN, 'fade',
        label='15 MILLIONS DE °C', emph=['fusionnent']),
    seg("Environ six cents millions de tonnes d'hydrogène, chaque seconde.", V(FUSION, 9.0, speed=0.7), CAM_SLOW, emph=['six', 'cents']),
    seg("Mais l'hélium obtenu pèse un tout petit peu moins lourd. Et cette différence devient de l'énergie.", V(FUSION, 20.0, speed=0.7), CAM_SLOW, 'fade', emph=['énergie'], music=0.6),
    seg("C'est la formule la plus célèbre du monde, celle d'Einstein : E égale m c deux.",
        V(SDO131, 0.0, speed=0.5, extra=[back(170, 520), txt('E = mc²', 330, 190, GOLD)]), CAM_IN, emph=['Einstein']),
    seg("Un tout petit peu de masse donne une énergie gigantesque, parce que la vitesse de la lumière au carré est un nombre énorme.", V(SUN193, 2.0, speed=0.6), CAM_SLOW, 'fade',
        emph=['gigantesque']),
    seg("C'est cette énergie qui te réchauffe la peau, qui fait pousser les plantes, qui fait vivre toute la Terre.", V(EARTH, 40.0), CAM_DRIFT, emph=['vivre']),
    seg("Et en plus, le vent solaire lui arrache encore environ un million de tonnes de matière par seconde.", V(HELIO, 10.0, speed=0.6), CAM_SLOW, 'fade', emph=['vent']),
    seg("Pas d'inquiétude : depuis sa naissance, il y a quatre milliards six cents millions d'années, il n'a pas perdu un millième de sa masse.", V(P_SWING, 3.0, speed=0.6), CAM_SLOW,
        emph=['millième'], music=0.7),
    seg("Il a encore de quoi briller pendant environ cinq milliards d'années. Tu savais que le Soleil maigrissait ? Dis-le en commentaire.", V(SUN171, 3.0, speed=0.4), CAM_OUT,
        'fade', music=0.3),
])


# ----------------------------------------------------------------------------- format D : phrase + ambiance (8 h)
AMB10 = amb('ambiance_10', "Tu files à 30 km par seconde",
            "Assis sans bouger,\ntu traverses l'espace\nà 30 km par seconde\nautour du Soleil.",
            [clipd(V(EARTH, 10.0, speed=0.6)), clipd(V(ISS, 1310.0, speed=0.7)), clipd(V(ISS, 350.0, speed=0.7)), clipd(V(EARTH, 35.0, speed=0.6)),
             clipd(V(ISS, 990.0, speed=0.7)), clipd(V(HELIO, 2.0, speed=0.6)), clipd(V(ISS, 2930.0, speed=0.7)), clipd(V(EARTH, 60.0, speed=0.5), 2)], 4310)

AMB11 = amb('ambiance_11', "Une année galactique",
            "Le Soleil met environ 230 millions d'années\nà faire le tour de la galaxie.\nAu dernier tour, les dinosaures\napparaissaient à peine.",
            [clipd(P(MILKYWAY)), clipd(V(OU, 30.0)), clipd(P(SOMB)), clipd(V(OU, 38.0)), clipd(P(SUNFL)), clipd(V(WEB, 20.0, speed=0.6, mode=CV)),
             clipd(P(HELIX)), clipd(P(MILKYWAY, zoom=1.3), 2)], 4311, key=44)

AMB12 = amb('ambiance_12', "Saturne flotterait sur l'eau",
            "Saturne est moins dense que l'eau.\nDans une baignoire assez grande,\nelle flotterait.",
            [clipd(V('svs:12672/12672_SaturnRingsDisappearing_YouTubeHD.mp4', 9.0, speed=0.6)), clipd(V('nasa:GSFC_20170912_Cassini_m12709_CIRS_Short', 20.0, speed=0.6)),
             clipd(V('svs:12672/12672_SaturnRingsDisappearing_YouTubeHD.mp4', 42.0, speed=0.6)), clipd(P('nasa:PIA06594')),
             clipd(V('svs:12672/12672_SaturnRingsDisappearing_YouTubeHD.mp4', 60.0, speed=0.6)), clipd(V('nasa:GSFC_20170912_Cassini_m12709_CIRS_Short', 60.0, speed=0.6)),
             clipd(P('nasa:PIA06594', zoom=1.3)), clipd(V('svs:12672/12672_SaturnRingsDisappearing_YouTubeHD.mp4', 20.0, speed=0.5), 2)], 4312, key=42)

AMB13 = amb('ambiance_13', "Un éclair plus chaud que le Soleil",
            "Un éclair chauffe l'air\nà près de 30 000 °C :\ncinq fois plus que\nla surface du Soleil.",
            [clipd(V(ISS_LIGHT, 241.0, speed=0.5)), clipd(V(ISS_LIGHT, 28.0, speed=0.6)), clipd(V(SUN171, 1.0, speed=0.5)), clipd(V(ISS_LIGHT, 244.0, speed=0.5)),
             clipd(V(SDO304, 0.0, speed=0.4)), clipd(V(ISS_LIGHT, 30.5, speed=0.6)), clipd(V(SUN193, 2.0, speed=0.5)), clipd(V(ISS_LIGHT, 246.0, speed=0.5), 2)], 4313, key=45)

AMB14 = amb('ambiance_14', "Dans l'espace, tu grandis",
            "Dans l'espace, sans gravité,\nta colonne vertébrale s'étire :\nles astronautes grandissent\nde quelques centimètres.",
            [clipd(V(ISS, 606.0, speed=0.7)), clipd(V(ISS, 1950.0, speed=0.7)), clipd(V(ISS, 2075.0, speed=0.7)), clipd(V(AUR_ISS, 30.0, speed=0.7)),
             clipd(V(ISS, 1118.0, speed=0.7)), clipd(V(ISS, 2014.0, speed=0.7)), clipd(V(ISS, 1870.0, speed=0.7)), clipd(V(ISS, 3038.0, speed=0.6), 2)], 4314, key=43)


# ----------------------------------------------------------------------------- format C : edits propres (21 h 30) — coupes nettes sur le rythme, aucun effet
def c(scene, n=2, **kw):
    """Plan d'edit de n × 2 temps, coupe franche, caméra lente."""
    return cut(scene, n, trans='cut', cam='slow_in', **kw)


EDIT09 = edit('edit_09', "Les explosions de l'Univers", "LES PLUS GROSSES\\NEXPLOSIONS DE L'UNIVERS", "ET ON EST FAITS DE LEURS POUSSIÈRES.", [
    c(V(SN, 21.0, speed=0.7), 2, sfx=['boom']), c(V(SN, 19.5, speed=0.7, mode=F0, fit_scale=1.5)), c(V(NSM, 15.0, speed=0.8)), c(V(NSM, 20.0, speed=0.8)),
    c(V(MAG_WIDE, 8.0)), c(V(BH_TDE, 28.0, mode=CV)), c(P(CRAB)), c(V(SN, 26.0, speed=0.6)), c(V(SN, 34.0, speed=0.5), sfx=[('riser', 0.0)])], 4409, prog='minor_dark', key=44)

EDIT10 = edit('edit_10', "La Lune comme tu ne l'as jamais vue", "LA LUNE COMME TU NE\\NL'AS JAMAIS VUE", "ELLE S'ÉLOIGNE DE 3,8 CM PAR AN.", [
    c(V(MOON, 73.0, speed=0.6), 2, sfx=['boom']), c(V(MOONTOUR, 14.0, speed=0.8)), c(V(MOONTOUR, 125.0, speed=0.8)), c(V(MOONTOUR, 181.0, speed=0.8)),
    c(V('svs:4185/apollo11_flyover_1080p30.mp4', 8.0, speed=0.8)), c(V(MOONTOUR, 237.0, speed=0.8)), c(P(EARTHSET)), c(V(MOONTOUR, 269.0, speed=0.8)),
    c(V(MOON, 219.0, speed=0.5), sfx=[('riser', 0.0)])], 4410, prog='minor_drift', key=43)

EDIT11 = edit('edit_11', "Les plus belles images de l'espace", "LES PLUS BELLES\\NIMAGES DE L'ESPACE", "CE SONT DE VRAIES PHOTOS.", [
    c(P(CARINA, cx=0.35), 2, sfx=['boom']), c(P(PILLARS)), c(P(SRING, cx=0.25)), c(P(CRAB)), c(P(HELIX)), c(P(SUNFL)), c(P(SOMB)), c(P(CARINA, cx=0.75)),
    c(P(SRING, cx=0.75), sfx=[('riser', 0.0)])], 4411, prog='minor_wonder', key=46)

EDIT12 = edit('edit_12', "Les colères du Soleil", "LES COLÈRES\\NDU SOLEIL", "À 150 MILLIONS DE KM DE TOI.", [
    c(V(SUN171, 1.0, speed=0.7), 2, sfx=['boom']), c(V(SDO304, 0.0, speed=0.5)), c(V(SUN131, 1.0, speed=0.7)), c(V(P_PULL, 1.0, speed=0.7)),
    c(V(SDO131, 0.0, speed=0.5)), c(V(SUN193, 2.0, speed=0.7)), c(V(P_SWING, 4.0, speed=0.7)), c(V(HELIO, 2.0, speed=0.7)),
    c(V(SUN171, 3.0, speed=0.5), sfx=[('riser', 0.0)])], 4412, prog='minor_epic', key=45)

EDIT13 = edit('edit_13', "Les aurores vues de l'espace", "LES AURORES\\NVUES DE L'ESPACE", "VUES DEPUIS LA STATION SPATIALE.", [
    c(V(AUR_ISS, 30.0, speed=0.8), 2, sfx=['boom']), c(V(AUR_AUS, 7.0)), c(V(AUR_ISS, 45.0, speed=0.8)), c(V(AUR_MAY, 0.0, speed=0.5)),
    c(V(AUR_AUS, 17.0)), c(V(AUR_ISS, 60.0, speed=0.8)), c(V(AUR_AUS, 27.0)), c(V(AUR_ISS, 75.0, speed=0.8)),
    c(V(AUR_AUS, 37.0), sfx=[('riser', 0.0)])], 4413, prog='minor_float', key=44)


VIDEOS = [R26, R27, R28, R29, R30, R31, R32, R33, R34, R35, R36, R37, R38, R39,
          AMB10, AMB11, AMB12, AMB13, AMB14, EDIT09, EDIT10, EDIT11, EDIT12, EDIT13]
