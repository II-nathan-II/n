"""Génère SCRIPTS/, PUBLICATION/ et le RÉCAPITULATIF à partir des scripts, des timelines et du contrôle qualité."""
import os, sys, json, csv, inspect
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import PROJECT, WORK
import build
from tts import caption_text, spoken_text
from publication_data import PUB, NICHES

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
    'video_06': ["Hering (1878) — théorie des processus antagonistes", "Image rémanente négative : adaptation des cônes (manuels de perception visuelle)"],
    'video_07': ["Addams (1834) — observation aux chutes de Foyers (« waterfall illusion »)", "Aristote, *Parva Naturalia* — mention de l'effet", "Aires MT/V5 et MST : sélectivité au mouvement/expansion"],
    'video_08': ["Troxler (1804) — disparition des stimuli périphériques fixés", "Lilac chaser — Jeremy Hinton (vers 2005)"],
    'video_09': ["Mariotte (vers 1660, publié en 1668) — découverte de la tache aveugle", "Anatomie : papille optique dépourvue de photorécepteurs"],
    'video_10': ["Adelson (1995) — « checkershadow illusion » (MIT) ; visuel de la vidéo recréé en code (image originale non utilisée)", "« La robe » (février 2015) — études sur les présupposés d'éclairage"],
}

def tc(t):
    m, s = divmod(t, 60)
    return f'{int(m):02d}:{s:05.2f}'

def describe(sc):
    try:
        obj = sc() if len(inspect.signature(sc).parameters) == 0 else None
    except Exception:
        obj = None
    if obj is None:
        return 'scène interactive synchronisée sur la narration'
    names = [LAYER_FR.get(type(l).__name__, type(l).__name__) for l in obj.layers]
    return ', '.join(dict.fromkeys(names))

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
        for i, spec in enumerate(v['segments']):
            seg = tl['segments'][i] if tl else None
            t = tc(seg['start']) if seg else '—'
            txt = caption_text(spec['text']) if spec.get('text') else f"*(silence {spec.get('hold', 0)} s — le spectateur observe l'effet)*"
            sc = spec.get('scene', 'same')
            if sc != 'same':
                cur_vis = describe(sc) if callable(sc) else str(sc)
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
               f"**7. Potentiel viral :** {p['potentiel']}\n"]
        rows.append([vid, v['niche'], p['titre'], p['description'], ' '.join(p['hashtags']), p['accroche'], p['couverture'], p['horaire'], p['potentiel']])
    open(os.path.join(pdir, 'PUBLICATION.md'), 'w').write('\n'.join(pm) + '\n')
    with open(os.path.join(pdir, 'publication.csv'), 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh, delimiter=';')
        w.writerow(['video', 'niche', 'titre', 'description', 'hashtags', 'accroche', 'couverture', 'horaire', 'potentiel_viral'])
        w.writerows(rows)

    # RÉCAPITULATIF
    rm = ['# Récapitulatif des 10 vidéos\n',
          '| Vidéo | Niche | Titre | Durée | Résolution | Codecs | Débit | Taille | Loudness | Narration (Whisper) | Sous-titres synchro | QC |',
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
                         f"reconnaissance Whisper : {r.get('asr_word_recall', 0) * 100:.1f} % des mots du script · luminosité min {r['frame_mean_min']} · variation moyenne entre images {r['frame_change_mean']}")
                if r.get('asr_excerpt'):
                    q.append(f"\nExtrait de transcription automatique : « {r['asr_excerpt']}… »")
                q.append(f"\n![planche]({vid}_planche.jpg)\n")
        open(os.path.join(PROJECT, 'ANALYSE', 'controle_qualite', 'RAPPORT_QC.md'), 'w').write('\n'.join(q) + '\n')

if __name__ == '__main__':
    gen()
