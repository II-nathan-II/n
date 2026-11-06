"""Guide de lancement du compte espace « Vertige Cosmique » (TikTok + YouTube Shorts) à partir de publication_data."""
import os
import publication_data as P
from common import PROJECT

VIDS = ['video_01', 'video_02', 'video_03', 'video_04', 'video_05']


def main():
    L = ["# Lancement du compte « Vertige Cosmique » (TikTok + YouTube Shorts)", "",
         "## 1. Profil (identique sur les deux plateformes)", "",
         "| Élément | TikTok | YouTube |", "|---|---|---|",
         "| Nom | Vertige Cosmique | Vertige Cosmique |",
         "| Identifiant | @vertige.cosmique | @vertige.cosmique (ou @vertigecosmique) |",
         "| Photo | `photo_profil_vertige_cosmique.png` | `photo_profil_vertige_cosmique.png` |",
         "| Bannière | — | `banniere_youtube_vertige_cosmique.png` (2560×1440) |",
         "| Bio | L'Univers est plus fou que la science-fiction 🌌 Un fait réel par jour. Images : NASA | Description ci-dessous |",
         "", "Description de la chaîne YouTube :", "",
         "> L'Univers est plus fou que la science-fiction. Planètes où il pleut du verre, trous noirs, vide cosmique géant : chaque vidéo raconte un fait réel et vérifié, en moins de deux minutes, avec de vraies images de la NASA. Nouvelle vidéo chaque jour. 🌌",
         "> Images : NASA (domaine public). Voix de synthèse et musiques originales.", "",
         "## 2. Les fichiers à publier", "",
         "- Vidéos : `TikTok_Viral_Project/NICHE_1/video_01.mp4` … `video_05.mp4`. Sur GitHub, ouvre le fichier puis clique sur « Download raw file ». Tu peux aussi les télécharger depuis le chat.",
         "- Publie le **fichier d'origine** sur les deux plateformes. Ne republie jamais sur YouTube une vidéo téléchargée depuis TikTok : elle porte le filigrane TikTok et YouTube la pousse moins.",
         "- Couvertures : `PUBLICATION/couvertures/video_0X_couverture.jpg`. Sur TikTok, utilise « Modifier la couverture » → « Importer ». Sur YouTube Shorts, choisis une image de la vidéo dans l'appli mobile.", "",
         "## 3. Réglages à chaque publication", "",
         "- **TikTok** : activer « Contenu généré par IA » (la voix est synthétique). Mettre les 5 hashtags, épingler un commentaire avec la question de la vidéo.",
         "- **YouTube** : format Short (vertical, moins de 3 min : nos vidéos font 83 à 96 s), public « Non conçu pour les enfants ». La case « Contenu modifié ou synthétique » vise surtout les contenus réalistes qui imitent une vraie personne ou un faux événement : en principe, elle ne concerne pas un narrateur de synthèse sur de vraies images NASA. En cas de doute, coche-la : ça n'empêche pas la monétisation. Mentionne « Voix de synthèse » dans la description.", "",
         "## 4. Calendrier de la semaine 1", "",
         "Même jour sur les deux plateformes : TikTok à l'heure indiquée, YouTube une heure plus tard.", "",
         "| Jour | Vidéo | TikTok | YouTube |", "|---|---|---|---|"]
    for v in VIDS:
        p = P.PUB[v]; h = p['horaire']
        L.append(f"| {h.split()[0]} | {v[-2:]} — {p['titre']} | {' '.join(h.split()[1:])} | +1 h |")
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
          "| TikTok Creator Rewards | 18 ans et plus, 10 000 abonnés, 100 000 vues sur 30 jours, vidéos originales de plus d'une minute | ✅ 83 à 96 s, originales |",
          "| YouTube Partner Program | 1 000 abonnés et 10 millions de vues de Shorts sur 90 jours (ou 4 000 h de visionnage de vidéos longues sur 12 mois). YouTube a annoncé en août 2026 des seuils plus élevés pour les nouveaux candidats : vérifie dans YouTube Studio → Revenus | ✅ Shorts originaux |",
          "", "Le plus important est la régularité. Avec 5 vidéos, la semaine 1 est couverte. Cette niche coûte 0 € à produire (images NASA, voix et musique générées localement), donc de nouvelles vidéos peuvent suivre chaque semaine."]
    open(os.path.join(PROJECT, 'PUBLICATION', 'LANCEMENT_VERTIGE_COSMIQUE.md'), 'w').write('\n'.join(L) + '\n')


if __name__ == '__main__':
    main()
    print('guide écrit')
