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
    'video_07_v1': ["Addams (1834) — observation aux chutes de Foyers (« waterfall illusion »)", "Aristote, *Parva Naturalia* — mention de l'effet", "Aires MT/V5 et MST : sélectivité au mouvement/expansion"],
    'video_08_v1': ["Troxler (1804) — disparition des stimuli périphériques fixés", "Lilac chaser — Jeremy Hinton (vers 2005)"],
    'video_09_v1': ["Mariotte (vers 1660, publié en 1668) — découverte de la tache aveugle", "Anatomie : papille optique dépourvue de photorécepteurs"],
    'video_10_v1': ["Adelson (1995) — « checkershadow illusion » (MIT) ; visuel de la vidéo recréé en code (image originale non utilisée)", "« La robe » (février 2015) — études sur les présupposés d'éclairage"],
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
              f"**Niche :** {NICHES[v['niche']]['nom']}  ", f"**Accroche à l'écran :** {v['hook_text'].replace(chr(92) + 'N', ' ')}  ",
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
