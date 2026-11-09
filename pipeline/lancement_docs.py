"""Guide de lancement du compte espace « Vertige Cosmique » (TikTok + YouTube Shorts) à partir de publication_data."""
import os
import publication_data as P
from common import PROJECT

VIDS = ['video_01', 'video_02', 'video_03', 'video_04', 'video_05', 'video_11', 'video_12', 'video_13', 'video_14', 'video_15',
        'video_16', 'video_17', 'video_18', 'video_19', 'video_20', 'video_21', 'video_22', 'video_23', 'video_24', 'video_25']
# 2 vidéos par jour (décision de l'utilisateur), à partir du vendredi 6 novembre 2026
CALENDRIER = [
              ('Ven. 6 nov.', '20 h 45', 'video_01'),
              ('Ven. 6 nov.', '22 h 00', 'video_02'),
              ('Sam. 7 nov.', '12 h 30', 'video_03'),
              ('Sam. 7 nov.', '17 h 00', 'ambiance_01'),
              ('Sam. 7 nov.', '19 h 00', 'video_04'),
              ('Sam. 7 nov.', '21 h 30', 'edit_01'),
              ('Dim. 8 nov.', '08 h 00', 'ambiance_02'),
              ('Dim. 8 nov.', '12 h 30', 'video_05'),
              ('Dim. 8 nov.', '19 h 00', 'video_11'),
              ('Dim. 8 nov.', '21 h 30', 'reflexion_01'),
              ('Lun. 9 nov.', '08 h 00', 'ambiance_07'),
              ('Lun. 9 nov.', '12 h 30', 'video_12'),
              ('Lun. 9 nov.', '19 h 00', 'video_13'),
              ('Lun. 9 nov.', '21 h 30', 'edit_02'),
              ('Mar. 10 nov.', '08 h 00', 'anim_02'),
              ('Mar. 10 nov.', '12 h 30', 'video_14'),
              ('Mar. 10 nov.', '19 h 00', 'video_15'),
              ('Mar. 10 nov.', '21 h 30', 'edit_05'),
              ('Mer. 11 nov.', '08 h 00', 'ambiance_05'),
              ('Mer. 11 nov.', '12 h 30', 'video_16'),
              ('Mer. 11 nov.', '19 h 00', 'video_17'),
              ('Mer. 11 nov.', '21 h 30', 'flash_01'),
              ('Jeu. 12 nov.', '08 h 00', 'anim_01'),
              ('Jeu. 12 nov.', '12 h 30', 'video_18'),
              ('Jeu. 12 nov.', '19 h 00', 'video_19'),
              ('Jeu. 12 nov.', '21 h 30', 'edit_07'),
              ('Ven. 13 nov.', '08 h 00', 'ambiance_08'),
              ('Ven. 13 nov.', '12 h 30', 'video_20'),
              ('Ven. 13 nov.', '19 h 00', 'video_21'),
              ('Ven. 13 nov.', '21 h 30', 'edit_06'),
              ('Sam. 14 nov.', '08 h 00', 'ambiance_03'),
              ('Sam. 14 nov.', '12 h 30', 'video_22'),
              ('Sam. 14 nov.', '19 h 00', 'video_23'),
              ('Sam. 14 nov.', '21 h 30', 'flash_02'),
              ('Dim. 15 nov.', '08 h 00', 'ambiance_09'),
              ('Dim. 15 nov.', '12 h 30', 'video_24'),
              ('Dim. 15 nov.', '19 h 00', 'video_25'),
              ('Dim. 15 nov.', '21 h 30', 'edit_08'),
              ('Lun. 16 nov.', '08 h 00', 'ambiance_04'),
              ('Lun. 16 nov.', '21 h 30', 'edit_03'),
              ('Mar. 17 nov.', '08 h 00', 'ambiance_06'),
              ('Mar. 17 nov.', '21 h 30', 'edit_04')]


from publication_week4 import CALENDRIER4 as _CAL4
CALENDRIER = [c for c in CALENDRIER] + _CAL4

def main():
    L = ["# Lancement du compte « Vertige Cosmique » (TikTok + YouTube Shorts)", "",
         "## 1. Profil (identique sur les deux plateformes)", "",
         "| Élément | TikTok | YouTube |", "|---|---|---|",
         "| Nom | Vertige Cosmique | Vertige Cosmique |",
         "| Identifiant | @vertige_cosmique | @vertige.cosmique (ou @vertigecosmique) |",
         "| Photo | `photo_profil_vertige_cosmique.png` | `photo_profil_vertige_cosmique.png` |",
         "| Bannière | — | `banniere_youtube_vertige_cosmique.png` (2560×1440) |",
         "| Bio | L'Univers est plus fou que la science-fiction 🌌 Un fait réel par jour. Images : NASA | Description ci-dessous |",
         "", "Description de la chaîne YouTube :", "",
         "> L'Univers est plus fou que la science-fiction. Planètes où il pleut du verre, trous noirs, vide cosmique géant : chaque vidéo raconte un fait réel et vérifié, en moins de deux minutes, avec de vraies images de la NASA. Nouvelle vidéo chaque jour. 🌌",
         "> Images : NASA (domaine public). Voix de synthèse et musiques originales.", "",
         "## 2. Les fichiers à publier", "",
         "- Vidéos : `TikTok_Viral_Project/NICHE_1/video_01.mp4` … `video_05.mp4` et `video_11.mp4` … `video_25.mp4`. Sur GitHub, ouvre le fichier puis clique sur « Download raw file ». Tu peux aussi les télécharger depuis le chat.",
         "- Publie le **fichier d'origine** sur les deux plateformes. Ne republie jamais sur YouTube une vidéo téléchargée depuis TikTok : elle porte le filigrane TikTok et YouTube la pousse moins.",
         "- Couvertures : `PUBLICATION/couvertures/video_0X_couverture.jpg`. Sur TikTok, utilise « Modifier la couverture » → « Importer ». Sur YouTube Shorts, choisis une image de la vidéo dans l'appli mobile.", "",
         "## 3. Réglages à chaque publication", "",
         "- **TikTok** : activer « Contenu généré par IA » (la voix est synthétique). Mettre les 5 hashtags, épingler un commentaire avec la question de la vidéo.",
         "- **YouTube** : format Short (vertical, moins de 3 min : nos vidéos font 68 à 96 s), public « Non conçu pour les enfants ». La case « Contenu modifié ou synthétique » vise surtout les contenus réalistes qui imitent une vraie personne ou un faux événement : en principe, elle ne concerne pas un narrateur de synthèse sur de vraies images NASA. En cas de doute, coche-la : ça n'empêche pas la monétisation. Mentionne « Voix de synthèse » dans la description.", "",
         "## 4. Calendrier : 4 publications par jour (depuis le 8 novembre)", "",
         "Même heure sur TikTok et YouTube (programmation Metricool). 08 h 00 : phrase + ambiance (format D) ; 12 h 30 et 19 h 00 : faits commentés (format A) ; 21 h 30 : edit rythmé (format C) ou réflexion (format B). Voir `ANALYSE/ROTATION_FORMATS.md`.", "",
         "| Jour | Heure | Vidéo |", "|---|---|---|"]
    for day, hour, v in CALENDRIER:
        L.append(f"| {day} | {hour} | {v[-2:] if v.startswith('video') else v} — {P.PUB[v]['titre']} |")
    L += ["", "## 5. Textes à copier-coller", ""]
    for v in VIDS:
        p = P.PUB[v]
        desc = p['description']
        base = desc.split(' (Images')[0].rstrip()
        yt = (f"{base}\n\nImages : NASA (domaine public) — vues d'artiste et visualisations scientifiques présentées comme telles. "
              f"Voix de synthèse, musique originale.\n\n" + ' '.join(p['hashtags']) + " #Shorts")
        L += [f"### {v[-2:]} — {p['titre']}", "",
              "**TikTok** — légende :", "", "```", f"{desc} {' '.join(p['hashtags'])}", "```", "",
              "**YouTube** — titre :", "", "```", p['titre'][:100], "```", "",
              "**YouTube** — description :", "", "```", yt, "```", "",
              f"Tags YouTube : {', '.join(h.lstrip('#') for h in p['hashtags'])}, univers, documentaire", ""]
    L += ["## 6. Monétisation", "",
          "| Plateforme | Conditions (à vérifier dans l'appli, elles changent) | Nos vidéos |", "|---|---|---|",
          "| TikTok Creator Rewards | 18 ans et plus, 10 000 abonnés, 100 000 vues sur 30 jours, vidéos originales de plus d'une minute | ✅ 68 à 96 s, originales |",
          "| YouTube Partner Program | 1 000 abonnés et 10 millions de vues de Shorts sur 90 jours (ou 4 000 h de visionnage de vidéos longues sur 12 mois). YouTube a annoncé en août 2026 des seuils plus élevés pour les nouveaux candidats : vérifie dans YouTube Studio → Revenus | ✅ Shorts originaux |",
          "", "Le plus important est la régularité : 20 vidéos couvrent 10 jours à 2 par jour (jusqu'au dimanche 15 novembre). Cette niche coûte 0 € à produire (images NASA, voix et musique générées localement), donc de nouvelles vidéos peuvent suivre chaque semaine.",
          "", "## 7. Programmation Metricool (faite le 6 novembre 2026)", "",
          "Les 20 vidéos (01 à 05 et 11 à 25) sont programmées dans Metricool (marque 7923410) sur TikTok et YouTube, aux heures du § 4, en publication automatique : 01 à 15 le 6 novembre, 16 à 25 le 7 novembre (fichiers en haute qualité). Les publications du 6 au soir et du 7 midi sont bien parties sur les deux réseaux. Le 7 novembre, ajout des formats courts : `edit_01` (7 nov. 21 h 30), `ambiance_01` (7 nov. 17 h 00), `reflexion_01` (8 nov. 21 h 30), `ambiance_02` à `09` (8 au 15 nov. à 08 h 00) et `edit_02` à `08` (9 au 15 nov. à 21 h 30), soit 4 publications par jour. Ordre choisi pour ne jamais publier le même sujet deux fois de suite : Vénus et l'étoile à neutrons (déjà traitées le 8 en format long) reviennent en ambiance les 13 et 14 ; l'edit « lunes » passe le 10 pour ne pas tomber le jour de la vidéo sur Titan (12 nov.). Tous les fichiers ont été vérifiés image par image avant envoi (plans recadrés en plein écran, volume −14 LUFS). Le soir même, deux nouveaux formats ont été ajoutés pour varier : « animation 2D » (`anim_01` le 12 à 08 h 00, `anim_02` le 10 à 08 h 00 ; plus d'une minute, éligibles Creator Rewards) et « flash noir et blanc » (`flash_01` le 11 à 21 h 30, `flash_02` le 14 à 21 h 30). Les vidéos qu'ils remplacent (`ambiance_04`, `ambiance_06`, `edit_03`, `edit_04`) sont reprogrammées les 16 et 17 novembre à 08 h 00 et 21 h 30 : on reste à 4 publications par jour. Les formats courts (moins d'une minute) ne comptent pas pour Creator Rewards : ils servent à gagner des abonnés.",
          "", "Réglages appliqués à chaque publication :",
          "- **TikTok** : public, commentaires, duos et collages autorisés (favorise la diffusion), aucun contenu commercial déclaré, label « contenu généré par IA » activé (voix de synthèse).",
          "- **YouTube** : Short, public, « non conçu pour les enfants » (sinon pas de publicités personnalisées ni de commentaires), catégorie Science et technologie, mots-clés, case « contenu synthétique » non cochée (vraies images NASA, narrateur de synthèse mentionné dans la description).",
          "", "## 8. Réglages des comptes à faire soi-même (monétisation)", "",
          "Ces réglages ne se font que dans les applis ; ni Metricool ni Claude ne peuvent les modifier.", "",
          "**TikTok**",
          "1. Profil → ☰ → Paramètres et confidentialité → Compte → garder un compte **personnel / créateur**, pas « Entreprise » : Creator Rewards n'est ouvert qu'aux comptes personnels.",
          "2. Confidentialité → compte **public** ; autoriser les commentaires, les duos, les collages et les **téléchargements** (le partage aide la portée).",
          "3. TikTok Studio → Monétisation → **Creator Rewards** : s'inscrire dès les conditions remplies (18 ans et plus, 10 000 abonnés, 100 000 vues sur 30 jours, vidéos originales de plus d'une minute).",
          "4. Bio et lien : ajouter la chaîne YouTube dès que l'option « Lien » est disponible.",
          "",
          "**YouTube** (YouTube Studio sur ordinateur)",
          "1. Paramètres → Chaîne → Infos générales : **pays = France** (nécessaire pour le Programme Partenaire), mots-clés de la chaîne : espace, astronomie, univers, science, NASA.",
          "2. Paramètres → Chaîne → Paramètres avancés → Audience : **« Non, cette chaîne n'est pas conçue pour les enfants »**.",
          "3. Paramètres → Importation par défaut : catégorie **Science et technologie**, langue de la vidéo **français**, commentaires autorisés, licence YouTube standard.",
          "4. Compte Google : activer la **validation en deux étapes** (exigée pour la monétisation).",
          "5. Onglet **Revenus** : cliquer sur « M'avertir quand je suis éligible », puis postuler au Programme Partenaire et associer un compte AdSense quand les seuils sont atteints.",
          "6. Laisser activée l'option qui permet aux autres d'utiliser les Shorts en remix (plus de visibilité).",
          "", "Pendant la phase de lancement, ne pas acheter de vues ni d'abonnés et ne pas republier la même vidéo : c'est ce qui fait perdre l'éligibilité à la monétisation."]
    open(os.path.join(PROJECT, 'PUBLICATION', 'LANCEMENT_VERTIGE_COSMIQUE.md'), 'w').write('\n'.join(L) + '\n')


if __name__ == '__main__':
    main()
    print('guide écrit')
