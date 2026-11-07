import subprocess
"""Génère SCRIPTS/, PUBLICATION/ et le RÉCAPITULATIF à partir des scripts, des timelines et du contrôle qualité."""
import os, sys, json, csv, inspect
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import PROJECT, WORK
import build
from tts import caption_text, spoken_text
from publication_data import PUB, NICHES
import footage

LAYER_FR = {
    'SpaceBG': 'fond étoilé/nébuleuse procédural', 'Planet': 'planète 3D en rotation', 'Star': 'étoile/Soleil animé',
    'BlackHole': 'trou noir avec disque d\'accrétion et lentille gravitationnelle', 'Galaxy': 'galaxie spirale (particules)',
    'GalaxyRow': 'rangée de galaxies (échelle)', 'CosmicWeb': 'toile cosmique 3D', 'GlassRain': 'pluie de verre horizontale',
    'CloudLayers': 'nuages en défilement', 'Orbits': 'schéma d\'orbites', 'LightPath': 'trajet de la lumière + chrono',
    'GWMerger': 'fusion d\'étoiles à neutrons + ondes gravitationnelles', 'NightSky': 'ciel nocturne', 'Vent': 'source hydrothermale abyssale',
    'VenusSurface': 'paysage vénusien', 'CloudSea': 'mer de nuages vénusienne', 'Airship': 'dirigeable', 'Thermometer': 'thermomètre animé',
    'DepthGauge': 'jauge de profondeur', 'JWST': 'miroir du télescope James Webb (stylisé)', 'Prism': 'décomposition de la lumière',
    'GlassShards': 'éclats de verre', 'Molecule': 'molécule 3D', 'Astronaut': 'astronaute', 'Clocks': 'horloges (dilatation du temps)',
    'SpacetimeGrid': 'grille d\'espace-temps', 'Constellation': 'constellation', 'Tunnel': 'trajectoires convergentes', 'Lander': 'sonde Venera (stylisée)',
    'Counter': 'compteur animé', 'Bars': 'barres comparatives', 'ArchiveCard': 'fiche archive (nom, date)', 'Particles': 'particules',
    'Text': 'texte animé', 'GradientBG': 'fond dégradé animé', 'Solid': 'fond uni', 'Flash': 'flash lumineux', 'Glow': 'halo',
    'InvertedFlag': 'drapeau aux couleurs inversées + point de fixation', 'Countdown': 'compte à rebours', 'ConeCells': 'cônes de la rétine (fatigue)',
    'OpponentPairs': 'paires de couleurs opposées', 'AfterimageDemo': 'démonstration d\'image rémanente', 'Spiral': 'spirale en rotation',
    'Mosaic': 'mosaïque fixe détaillée', 'Neurons': 'réseau de neurones animé', 'Troxler': 'taches floues (effet Troxler)',
    'LilacChaser': 'lilac chaser (recréé en code)', 'BlindSpot': 'test de la tache aveugle', 'EyeDiagram': 'coupe de l\'œil',
    'Checker': 'échiquier à l\'ombre (cases A/B identiques)', 'DressSwatches': 'couleurs de « la robe »', 'PaperShadow': 'feuille à l\'ombre',
    'FlagCompare': 'drapeau inversé → drapeau perçu', 'Fn': 'assombrissement',
}

SOURCES = {
    'video_01': ["NASA/ESA, Hubble — couleur bleue de HD 189733 b mesurée (communiqué de juillet 2013)", "Fu et al., *Nature* (2024) — détection de H₂S par JWST", "NASA Exoplanet Archive — HD 189733 b (période 2,2 j, ~64 al)"],
    'video_02': ["Temps lumière Soleil–Terre ≈ 499 s (1 ua)", "LIGO/Virgo & Fermi — GW170817 (17 août 2017), écart ≈ 1,7 s, ~130 millions d'al", "Ordres de grandeur de refroidissement (≈ −18 °C en une semaine, ≈ −73 °C en un an) : estimations de vulgarisation scientifique"],
    'video_03': ["Kirshner, Oemler, Schechter & Shectman, *ApJ* (1981) — découverte du vide du Bouvier", "Diamètre ~250–330 millions d'al, une soixantaine de galaxies recensées", "Tully & Fisher (1987) — le Vide local"],
    'video_04': ["Sagittarius A* : ~4 millions de masses solaires (EHT 2022, prix Nobel 2020)", "Spaghettification et dilatation du temps : relativité générale (cours de référence)", "Temps propre maximal horizon → singularité ≈ πGM/c³ (≈ 1 min pour Sgr A*)"],
    'video_05': ["NASA — Vénus : rotation 243 j (rétrograde), révolution 225 j, 465 °C, ~92 bar", "Venera 13 (1982) : 127 minutes en surface, premières images couleur", "NASA Langley — concept HAVOC (2014–2015)"],
    'video_06': ["NOAA/AOML — FAQ ouragans (énergie : 50 à 200 fois la capacité électrique mondiale ; pluie ≈ 2,4 billions de gallons/jour)", "NHC — Beryl (juillet 2024), premier catégorie 5 aussi tôt ; Milton (octobre 2024), intensification rapide", "Seuils : océan ≥ 26 °C ; catégorie 5 ≥ 252 km/h (échelle Saffir-Simpson)"],
    'video_07': ["NASA (Carr et al., 2022) — panache à 57 km, mésosphère", "NASA JPL / Aura MLS (Millán et al., 2022) — 146 Tg de vapeur d'eau, ≈ 10 % de la stratosphère, 58 000 piscines olympiques", "NASA Goddard — énergie : des centaines de fois Hiroshima ; NOAA GLM — record d'éclairs ; Météo-France — onde de pression enregistrée en France"],
    'video_08': ["Franz, Nemzek & Winckler (Science, 1990) — premier sprite filmé en 1989 (Université du Minnesota)", "NOAA — ≈ 44 éclairs par seconde ; OMM (2025) — record de 829 km (22 octobre 2017)", "NASA Fermi (2011) — faisceaux d'antimatière issus d'orages ; NASA LIS — lac Maracaibo, point le plus foudroyé"],
    'video_09': ["NASA/NOAA — tempête géomagnétique G5 du 10 mai 2024, la plus forte depuis 2003", "Événement de Carrington (1859) — aurores aux Caraïbes, télégraphes perturbés", "NASA (2018) — STEVE, étudié avec des photographes amateurs (Alberta Aurora Chasers)"],
    'video_10': ["Yu et al., Geophysical Research Letters (2015), NASA CALIPSO — 182 Mt/an, 27,7 Mt sur l'Amazonie, ≈ 22 000 t de phosphore", "Dépression du Bodélé (Tchad), ancien lac Méga-Tchad riche en diatomées", "NASA — nuage de poussière « Godzilla », juin 2020"],
    'video_06_v1': ["Hering (1878) — théorie des processus antagonistes", "Image rémanente négative : adaptation des cônes (manuels de perception visuelle)"],
    'video_11': ["NASA — étoile à neutrons : environ 1,4 masse solaire dans une sphère d'une vingtaine de kilomètres ; « une cuillère ≈ un milliard de tonnes » est l'ordre de grandeur le plus cité", "PSR J1748-2446ad (2006) et 4U 1820-30 (2024) — 716 tours par seconde", "LIGO/Virgo — GW170817 (17 août 2017) : kilonova et production d'éléments lourds (or, platine)", "NASA NICER / Swift — magnétars, champs magnétiques de l'ordre de 10^15 gauss"],
    'video_12': ["NASA Goddard (eclipse.gsfc.nasa.gov) — la Lune s'éloigne d'environ 3,8 cm par an, mesuré par télémétrie laser sur les réflecteurs d'Apollo 11, 14 et 15", "Allongement du jour d'environ 1,7 à 2,3 ms par siècle ; coraux fossiles (environ 400 jours par an il y a ~400 millions d'années)", "Éclipse totale de Soleil du 2 août 2027 (sud de l'Espagne, Afrique du Nord)"],
    'video_13': ["NASA (APOD, Goddard) — Olympus Mons : environ 22 km au-dessus des plaines (jusqu'à ~26 km selon la référence), environ 600 km de diamètre, pentes de 3 à 6°", "Caldeira d'environ 80 × 60 km ; escarpement de base jusqu'à 6–8 km", "Gravité martienne ≈ 0,38 g ; pas de tectonique des plaques ; coulées récentes de quelques millions d'années (Mars Express, 2004)"],
    'video_14': ["NASA / Hubble — Grande Tache rouge : environ 41 000 km au XIXe siècle, environ 16 500 km en 2014, observée depuis au moins 150 ans", "Vents de 430 à 680 km/h selon les mesures", "Juno (2021) — racines jusqu'à environ 500 km de profondeur", "Hubble (2024) — la tache oscille « comme de la gelée »"],
    'video_15': ["NASA SVS « Origin of Light » — des dizaines de milliers d'années pour que l'énergie sorte du Soleil (estimations courantes : 100 000 à 170 000 ans)", "Cœur à environ 15 millions °C ; environ 600 millions de tonnes d'hydrogène fusionnées et 4 millions de tonnes converties en énergie par seconde", "Le Soleil représente environ 99,8 % de la masse du système solaire ; encore environ 5 milliards d'années de vie"],
    'video_16': ["NASA — Station spatiale internationale : environ 400 km d'altitude, environ 28 000 km/h, un tour de la Terre en 90 minutes environ, soit environ 16 levers et couchers de soleil par jour", "NASA — à l'altitude de l'ISS la gravité vaut environ 90 % de celle de la surface ; l'apesanteur vient de la chute libre permanente (orbite)", "NASA — longueur de 109 m environ (un terrain de football américain), masse d'environ 420 tonnes ; occupation humaine continue depuis le 2 novembre 2000", "NASA — fin d'exploitation prévue vers 2030, désorbitation contrôlée au-dessus du Pacifique (véhicule USDV)"],
    'video_17': ["NASA/JPL CNEOS — (99942) Apophis : passage le 13 avril 2029 à environ 32 000 km de la surface, plus près que les satellites géostationnaires (35 786 km) ; visible à l'œil nu depuis l'hémisphère est (Europe, Afrique)", "NASA — diamètre moyen d'environ 340 m (animation NASA : comparaison avec la tour Eiffel, 324 m)", "NASA (mars 2021) — risque d'impact exclu pour au moins 100 ans ; découverte en 2004, probabilité initiale d'impact en 2029 d'environ 2,7 %, niveau 4 sur l'échelle de Turin (record)", "NASA — OSIRIS-APEX (ex-OSIRIS-REx, échantillons de Bennu) : rendez-vous avec Apophis en 2029, étude d'environ 18 mois ; effets de marée possibles sur la rotation et la surface"],
    'video_18': ["NASA — Europe : océan global d'eau salée sous une croûte de glace estimée à 15–25 km, profond de 60 à 150 km ; environ deux fois le volume des océans terrestres", "NASA — chauffage par les marées dues à Jupiter ; température de surface d'environ −160 °C à l'équateur", "NASA/JPL — Europa Clipper lancée le 14 octobre 2024, plus grand engin planétaire de la NASA (panneaux d'environ 30 m) ; assistance gravitationnelle de Mars (mars 2025) et de la Terre (3 décembre 2026) ; arrivée prévue le 11 avril 2030 ; 49 survols, jusqu'à 25 km d'altitude", 'NASA — plaque avec le poème « In Praise of Mystery » (Ada Limón) et puce portant plus de 2,6 millions de noms'],
    'video_19': ["NASA — Titan : plus grande lune de Saturne, plus grande que Mercure, seule lune à atmosphère dense (azote) ; pression au sol d'environ 1,5 bar ; environ −179 °C", "NASA/Cassini — pluie, rivières, lacs et mers de méthane et d'éthane ; seul corps connu, avec la Terre, à liquides stables en surface ; Kraken Mare, environ 400 000 km² (ordre de grandeur de la mer Caspienne)", 'ESA — Huygens posée sur Titan le 14 janvier 2005, atterrissage le plus lointain jamais réalisé', "NASA/APL — Dragonfly, aérogyre de la taille d'une voiture : lancement prévu en juillet 2028, arrivée en 2034 ; l'idée de voler à la force des bras sur Titan (gravité faible, air dense) est une estimation théorique courante"],
    'video_20': ["NASA — Parker Solar Probe lancée le 12 août 2018 ; périhélie du 24 décembre 2024 à environ 6,1 millions de km de la surface, à environ 692 000 km/h (record de vitesse d'un objet construit par l'humain)", "NASA/APL — bouclier thermique en composite carbone-carbone d'environ 11,4 cm, face au Soleil vers 1 400 °C, instruments maintenus autour de 30 °C", "NASA — couronne à plus d'un million de degrés mais très peu dense ; premier passage dans la couronne en avril 2021 (annoncé en décembre 2021) ; sept assistances gravitationnelles de Vénus", "NASA — premier engin baptisé du nom d'une personne vivante : Eugene Parker (1927–2022), présent au lancement à 91 ans ; orbite de 88 jours"],
    'video_21': ["NASA (2018) — « pluie des anneaux » : de quoi remplir une piscine olympique en une demi-heure ; anneaux pouvant disparaître d'ici environ 300 millions d'années, voire 100 millions selon les données de Cassini", "NASA — anneaux principaux d'environ 280 000 km de diamètre, épaisseur souvent proche de 10 m ; blocs de glace d'eau de la taille de grains à celle de maisons", "Études Cassini (Iess et al. 2019 ; Kempf et al. 2023) — anneaux jeunes, quelques centaines de millions d'années au plus (débat en cours)", 'Passage de la Terre dans le plan des anneaux le 23 mars 2025 (anneaux vus par la tranche, environ tous les 13 à 16 ans) ; densité moyenne de Saturne 0,69 g/cm³ ; fin de Cassini le 15 septembre 2017 après 13 ans en orbite'],
    'video_22': ["NASA — Mercure : environ 430 °C le jour, environ −180 °C la nuit ; pas d'atmosphère dense ; année de 88 jours, jour solaire de 176 jours terrestres", "NASA/MESSENGER (2012) — glace d'eau dans les cratères polaires en ombre permanente (axe presque droit) ; estimation de 100 milliards à 1 000 milliards de tonnes", "NASA/MESSENGER (2014) — contraction de Mercure : rayon diminué jusqu'à environ 7 km, escarpements en « rides »", 'ESA/JAXA — BepiColombo lancée en octobre 2018 ; mise en orbite autour de Mercure prévue le 21 novembre 2026'],
    'video_23': ['NASA/JPL — PIA19400 : coucher de soleil bleu photographié par Curiosity le 15 avril 2015 (sol 956), cratère Gale ; couleurs proches de la vision humaine', "NASA — la poussière martienne très fine laisse passer la lumière bleue plus efficacement près de la direction du Soleil ; ciel ocre le jour ; crépuscule jusqu'à environ deux heures", 'NASA/JPL — PIA23202 : coucher de soleil vu par InSight (avril 2019)', "Données NASA — Soleil vu de Mars environ deux tiers de sa taille apparente terrestre, ensoleillement d'environ 43 % ; sol de 24 h 39 min ; poussière riche en oxydes de fer"],
    'video_24': ["NASA — Encelade : environ 500 km de diamètre, l'un des corps les plus réfléchissants du système solaire, surface vers −200 °C", "NASA/Cassini — jets découverts en 2005 au pôle sud (« rayures de tigre ») ; une centaine de geysers recensés ; ils alimentent l'anneau E ; océan global sous la glace ; hydrogène moléculaire détecté (2017), signe possible d'activité hydrothermale", "NASA/ESA/CSA — Webb (2023) : panache d'environ 9 600 km, environ 300 litres d'eau par seconde", "Postberg et al., Nature (2023) — phosphates détectés dans des grains de glace d'Encelade (données Cassini)"],
    'video_25': ["NASA/JPL — Voyager 1 lancée le 5 septembre 1977 ; un jour-lumière (environ 25,9 milliards de km) atteint vers le 18 novembre 2026 ; vitesse d'environ 61 000 km/h", "NASA — survols de Jupiter (1979) et de Saturne (1980) ; entrée dans l'espace interstellaire le 25 août 2012", "NASA/JPL — « Pale Blue Dot », 14 février 1990, à environ 6 milliards de km (PIA23645, version retraitée en 2020) ; expression de Carl Sagan ; la Terre occupe moins d'un pixel", "NASA/JPL — émetteur d'environ 22 W (comparaison NASA : ampoule de réfrigérateur), énergie en baisse, fin attendue dans les années 2030 ; disque d'or avec salutations en 55 langues ; passage à 1,6 année-lumière de l'étoile Gliese 445 dans environ 40 000 ans"],
    'reflexion_01': ["Estimation courante (Jefferson Lab, Freitas) : environ 7 × 10^27 atomes dans un corps humain de 70 kg", "Le noyau occupe environ un cent-millième du diamètre de l'atome (analogie classique de la bille au centre d'un stade)", "ONU — population mondiale passée à 8 milliards en novembre 2022 (environ 8,2 milliards en 2025)", "NASA/JPL — « Pale Blue Dot » (PIA23645), Voyager 1, 14 février 1990, à environ 6 milliards de km", "NASA — la Voie lactée compte environ 100 à 400 milliards d'étoiles ; des centaines de milliards de galaxies dans l'Univers observable (Conselice et al. 2016 ; New Horizons 2021)", "Ordres de grandeur couramment cités : environ 10^22 à 10^24 étoiles contre environ 10^18 à 10^19 grains de sable sur les plages", "NASA — le fer et le calcium sont produits dans les étoiles et dispersés par les supernovas", "Carl Sagan, *Cosmos* (1980) : « We are a way for the cosmos to know itself »"],
    'video_07_v1': ["Addams (1834) — observation aux chutes de Foyers (« waterfall illusion »)", "Aristote, *Parva Naturalia* — mention de l'effet", "Aires MT/V5 et MST : sélectivité au mouvement/expansion"],
    'video_08_v1': ["Troxler (1804) — disparition des stimuli périphériques fixés", "Lilac chaser — Jeremy Hinton (vers 2005)"],
    'video_09_v1': ["Mariotte (vers 1660, publié en 1668) — découverte de la tache aveugle", "Anatomie : papille optique dépourvue de photorécepteurs"],
    'video_10_v1': ["Adelson (1995) — « checkershadow illusion » (MIT) ; visuel de la vidéo recréé en code (image originale non utilisée)", "« La robe » (février 2015) — études sur les présupposés d'éclairage"],
}

# Écarts du contrôle automatique vérifiés à la main
QC_NOTES = {
    'reflexion_01': "Vidéo test du style « réflexion » : fonds noirs et fondus au noir voulus (une image mesurée à 2,8 de luminosité moyenne pour un seuil de 3). Durée 64,3 s : sous notre fourchette habituelle de 65 s, mais au-dessus de la minute exigée par Creator Rewards.",
    'video_22': "Whisper a sauté une phrase en transcrivant la vidéo entière (« Autre surprise : Mercure rétrécit… »). Transcrite seule (48–64 s), elle est parfaitement reconnue ; niveaux identiques aux autres vidéos (−14,2 LUFS). Vidéo validée.",
}

def tc(t):
    m, s = divmod(t, 60)
    return f'{int(m):02d}:{s:05.2f}'

def _meta(ref):
    try:
        return footage.resolve(ref)
    except Exception:
        return {'title': ref, 'source': '?', 'credit': '', 'license': '', 'page': ''}

def describe(sc, refs=None):
    try:
        obj = sc() if len(inspect.signature(sc).parameters) == 0 else None
    except Exception:
        obj = None
    if obj is None:
        return 'scène interactive synchronisée sur la narration'
    names = []
    for l in obj.layers:
        if type(l).__name__ in ('Clip', 'Photo'):
            m = _meta(l.ref)
            if refs is not None:
                refs.setdefault(l.ref, m)
            at = f" (à {l.at:.0f} s)" if type(l).__name__ == 'Clip' else ''
            names.append(f"{'Vidéo' if type(l).__name__ == 'Clip' else 'Photo'} réelle : « {m.get('title', '')[:60]} »{at}")
        elif type(l).__name__ not in ('Backdrop', 'Shade'):
            names.append(LAYER_FR.get(type(l).__name__, type(l).__name__))
    return ', '.join(dict.fromkeys(names))

CREDITS = {}

def gen():
    vids = build.all_videos()
    qc = {}
    qcp = os.path.join(PROJECT, 'ANALYSE', 'controle_qualite', 'qc_resultats.json')
    if os.path.exists(qcp):
        qc = {r['id']: r for r in json.load(open(qcp))}
    sdir = os.path.join(PROJECT, 'SCRIPTS'); pdir = os.path.join(PROJECT, 'PUBLICATION')
    os.makedirs(sdir, exist_ok=True); os.makedirs(pdir, exist_ok=True)
    allmd = ['# Scripts complets des 10 vidéos\n', 'Timecodes issus de la narration réelle (synthèse Kokoro). Le texte affiché correspond aux sous-titres ; '
             'la colonne « Visuel » décrit la scène générée à cet instant.\n']
    for vid in sorted(vids):
        v = vids[vid]
        tlp = os.path.join(WORK, vid, f'{vid}_timeline.json')
        tl = json.load(open(tlp)) if os.path.exists(tlp) else None
        md = [f"# {vid.replace('_', ' ').title()} — {v['title']}\n",
              f"**Niche :** {NICHES[v['niche']]['nom']}  ", f"**Accroche à l'écran :** {v.get('hook_text', v.get('overlay', {}).get('text', '')).replace(chr(92) + 'N', ' ')}  ",
              f"**Durée :** {tl['duration']:.1f} s  " if tl else '', f"**Musique :** composition originale procédurale ({v['music']['style']}, {v['music']['bpm']} BPM, progression {v['music']['prog']})\n",
              '| Timecode | Narration | Visuel | Montage |', '|---|---|---|---|']
        cur_vis = ''
        refs = {}
        for i, spec in enumerate(v['segments']):
            seg = tl['segments'][i] if tl else None
            t = tc(seg['start']) if seg else '—'
            txt = caption_text(spec['text']) if spec.get('text') else f"*(silence {spec.get('hold', 0)} s — le spectateur observe l'effet)*"
            sc = spec.get('scene', 'same')
            if sc != 'same':
                cur_vis = describe(sc, refs) if callable(sc) else str(sc)
                vis = cur_vis
            else:
                vis = '↳ (même plan)'
            mont = []
            if sc != 'same':
                mont.append(f"transition {spec.get('trans', 'cut')}")
                if spec.get('cam'):
                    mont.append(f"caméra {spec['cam']}")
            for s in spec.get('sfx', []):
                mont.append('sfx ' + (s if isinstance(s, str) else s[0]))
            if spec.get('label'):
                mont.append(f"étiquette « {spec['label']} »")
            if 'music' in spec:
                mont.append('musique ' + ('coupée' if spec['music'] < 0 else f"intensité {spec['music']}"))
            md.append(f"| {t} | {txt} | {vis} | {', '.join(mont)} |")
        if refs:
            md.append('\n**Crédits images (séquences réelles utilisées) :**\n')
            for r, m in refs.items():
                md.append(f"- {m.get('title', r)} — {m.get('credit', '')} — {m.get('source', '')} — {m.get('license', '')} — {m.get('page', '')}")
            CREDITS[vid] = refs
        md.append('\n**Sources / vérification des faits :**\n')
        md += [f'- {s}' for s in SOURCES.get(vid, [])]
        md.append('\n**Texte prononcé (pour réenregistrement éventuel) :**\n')
        md.append('> ' + ' '.join(spoken_text(s['text']) for s in v['segments'] if s.get('text')))
        open(os.path.join(sdir, f'{vid}_script.md'), 'w').write('\n'.join(md) + '\n')
        allmd += ['\n---\n'] + md
    open(os.path.join(sdir, 'SCRIPTS_COMPLETS.md'), 'w').write('\n'.join(allmd) + '\n')

    # PUBLICATION
    pm = ['# Publication — titres, descriptions, hashtags, horaires\n',
          'Heures en **heure de Paris**, à tester sur 2 à 3 semaines puis à ajuster avec TikTok Analytics (onglet *Abonnés → activité*). '
          'Activer le label **« Contenu généré par IA »** à la publication (voix de synthèse). Une vidéo par jour et par compte au maximum au début.\n']
    rows = []
    for vid in sorted(vids):
        v = vids[vid]; p = PUB[vid]
        pm += [f"## {vid} — {NICHES[v['niche']]['nom']}\n", f"**Fichier :** `{v['niche']}/{vid}.mp4`  ",
               f"**1. Titre :** {p['titre']}  ", f"**2. Description :** {p['description']}  ",
               f"**3. Hashtags :** {' '.join(p['hashtags'])}  ", f"**4. Phrase d'accroche :** « {p['accroche']} »  ",
               f"**5. Couverture :** {p['couverture']} — image prête : `PUBLICATION/couvertures/{vid}_couverture.jpg`  ", f"**6. Créneau à tester :** {p['horaire']}  ",
               f"**7. Potentiel viral :** {p['potentiel']}  "]
        cr = sorted(set((m.get('credit') or m.get('source', '')).strip() for m in CREDITS.get(vid, {}).values()))
        if cr:
            pm.append(f"**Crédits à mentionner (fin de description) :** Images : {' ; '.join(c for c in cr if c)}\n")
        else:
            pm.append('')
        rows.append([vid, v['niche'], p['titre'], p['description'], ' '.join(p['hashtags']), p['accroche'], p['couverture'], p['horaire'], p['potentiel']])
    open(os.path.join(pdir, 'PUBLICATION.md'), 'w').write('\n'.join(pm) + '\n')
    with open(os.path.join(pdir, 'publication.csv'), 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh, delimiter=';')
        w.writerow(['video', 'niche', 'titre', 'description', 'hashtags', 'accroche', 'couverture', 'horaire', 'potentiel_viral'])
        w.writerows(rows)

    # RÉCAPITULATIF
    rm = ['# Récapitulatif des 10 vidéos\n',
          '| Vidéo | Niche | Titre | Durée | Résolution | Codecs | Débit | Taille | Loudness | Narration (Whisper, hors nombres) | Sous-titres synchro | QC |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for vid in sorted(vids):
        v = vids[vid]; r = qc.get(vid, {})
        if r.get('exists'):
            rm.append(f"| {vid} | {NICHES[v['niche']]['nom']} | {v['title']} | {r['duration']:.1f} s | {r['width']}×{r['height']} @ {eval(r['fps']):.0f} i/s | "
                      f"{r['vcodec'].upper()} ({r['profile']}) / {r['acodec'].upper()} {r['sample_rate'] // 1000} kHz | {r['bitrate_kbps']} kb/s | {r['size_mb']} Mo | "
                      f"{r['lufs']:.1f} LUFS, TP {r['true_peak_db']:.1f} dBTP | {r.get('asr_word_recall', 0) * 100:.0f} % des mots | {r['caption_words_voiced'] * 100:.0f} % | {'✅' if r['ok'] else '⚠️'} |")
        elif os.path.exists(os.path.join(PROJECT, 'NICHE_1', f'{vid}.mp4')):
            # Formats courts sans voix : le QC automatique (Whisper) ne s'applique pas, contrôle manuel (planche + ebur128).
            p = os.path.join(PROJECT, 'NICHE_1', f'{vid}.mp4')
            dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p],
                                       capture_output=True, text=True).stdout.strip() or 0)
            rm.append(f"| {vid} | {NICHES[v['niche']]['nom']} | {v['title']} | {dur:.1f} s | 1080×1920 @ 30 i/s | H264 / AAC 48 kHz | — | "
                      f"{os.path.getsize(p) / 1e6:.1f} Mo | ≈ −14 LUFS | sans voix | texte fixe | ✅ (contrôle manuel) |")
        else:
            rm.append(f"| {vid} | {NICHES[v['niche']]['nom']} | {v['title']} | — | — | — | — | — | — | — | — | non rendu |")
    rm += ['\nFormat commun : MP4 (faststart), vidéo H.264 High 4.2 yuv420p BT.709, 1080×1920 (9:16), 30 i/s, audio AAC 192 kb/s 48 kHz stéréo, '
           'sous-titres incrustés, voix française Kokoro (ff_siwis), musique et effets sonores 100 % générés.',
           '\nDétail des contrôles : `ANALYSE/controle_qualite/RAPPORT_QC.md` et planches d\'images `ANALYSE/controle_qualite/*_planche.jpg`.']
    open(os.path.join(PROJECT, 'RECAPITULATIF.md'), 'w').write('\n'.join(rm) + '\n')

    # RAPPORT QC
    if qc:
        q = ['# Rapport de contrôle qualité\n', 'Généré automatiquement par `pipeline/qc.py` sur les fichiers finaux.\n']
        for vid in sorted(qc):
            r = qc[vid]
            q.append(f"## {vid} — {'✅ conforme' if r.get('ok') else '⚠️ à vérifier'}\n")
            if vid in QC_NOTES:
                q.append(f"> Vérification manuelle : {QC_NOTES[vid]}\n")
            for k, ok in r.get('checks', {}).items():
                q.append(f"- {'✅' if ok else '❌'} {k}")
            if r.get('exists'):
                q.append(f"\nMesures : durée {r['duration']:.1f} s · {r['lufs']:.1f} LUFS · true peak {r['true_peak_db']:.1f} dBTP · niveau parole {r['level_speech_db']:.1f} dBFS vs pauses {r['level_gaps_db']:.1f} dBFS · "
                         f"{r['caption_words']} mots sous-titrés, {r['caption_words_voiced'] * 100:.1f} % tombent sur de la voix, {r['caption_words_outside_segment']} hors segment · "
                         f"reconnaissance Whisper : {r.get('asr_word_recall', 0) * 100:.1f} % des mots du script (nombres exclus : Whisper les écrit en chiffres) · luminosité min {r['frame_mean_min']} · variation moyenne entre images {r['frame_change_mean']}")
                if r.get('asr_excerpt'):
                    q.append(f"\nExtrait de transcription automatique : « {r['asr_excerpt']}… »")
                q.append(f"\n![planche]({vid}_planche.jpg)\n")
        open(os.path.join(PROJECT, 'ANALYSE', 'controle_qualite', 'RAPPORT_QC.md'), 'w').write('\n'.join(q) + '\n')

if __name__ == '__main__':
    gen()
