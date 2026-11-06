# Niche 3 (proposition) — « ASMR & fruits IA »

*6 novembre 2026. Cette niche n'est pas encore produite : il manque les crédits de génération vidéo IA (voir § 4).*

> **Mise à jour :** la proposition est devenue deux séries complètes, prêtes à produire. Voir `NICHE_3_VILLA_VITAMINE/` (saison 1, 10 épisodes), `NICHE_4_CRISTAL_ASMR/` (10 vidéos de 90 s), `PLAN_VIRALITE_MONETISATION_NICHES_3_4.md` et `budget_niches_3_4.md`.

## 1. Pourquoi ces formats marchent

| Format | Exemple connu | Ce qui le rend viral | Source |
|---|---|---|---|
| ASMR « fruits en verre » : un couteau tranche des fruits en verre, cristal, glace ou lave, avec un son de craquement | Tendance mondiale depuis juin 2025 | Satisfaisant, sans langue (audience mondiale), boucle, regardé jusqu'au bout | Cyberlink, Pollo.ai, The Grocer, Tribune.com.pk |
| Mini-télé-réalité de fruits humanisés | « L'Île de la Skibidi Tentafruit » (France, mars 2026) | Parodie de télé-réalité, personnages récurrents, épisodes qui donnent envie de voir la suite | Siècle Digital, L'ADN, CB News, Gens d'Internet |

Ces vidéos sont **entièrement générées par IA vidéo**, comme Kling, Seedance, Wan ou Veo. Aucune image réelle libre de droits ne permet de les reproduire, et le serveur de production n'a pas de GPU : il faut passer par un service de génération (Higgsfield est connecté à ce projet).

## 2. Concepts originaux proposés

On ne copie pas Tentafruit : ses noms, ses personnages et son univers appartiennent à leurs créateurs. On reprend le **genre** (fruits humanisés + télé-réalité) avec un univers à nous.

### Format A — « Cristal ASMR » (5 vidéos de 65 à 75 s)
- 13 à 14 plans de 5 s par vidéo : fraise, kiwi, pastèque, citron, raisin… en verre, cristal, glace, ambre ou gelée, tranchés au ralenti en macro.
- Son ASMR **natif** généré avec l'image (craquements, tintements) ; pas de voix, pas de musique protégée.
- Habillage : accroche à l'écran (« Le n°9 m'a donné des frissons »), compteur 1/14, vote final (« Ton préféré ? Mets le numéro 👇 »).
- Thème par vidéo : 1. Fruits rouges en verre · 2. Agrumes en cristal · 3. Fruits gelés qui craquent · 4. Fruits en ambre · 5. Le fruit le plus dur à couper (gradation).

### Format B — « Villa Vitamine » (5 épisodes de 60 à 90 s)
Mini-télé-réalité dans une villa au soleil, avec des personnages originaux en style 3D cartoon, tout public :
- **Kiki** le kiwi, le séducteur sûr de lui ;
- **Bérénice** la banane, la reine du drama ;
- **Cyril** le citron, toujours acide, commente tout ;
- **Pépin** la pomme, le timide qui surprend tout le monde ;
- **Margaux** la mangue, la nouvelle qui bouleverse la villa.

Chaque épisode alterne scènes, « confessionnaux » face caméra et cliffhanger final (« Qui doit quitter la villa ? 👇 »). Les dialogues sont en français, avec sous-titres dynamiques et musique originale.

## 3. Production prévue

1. **Fiches personnages** : une image de référence par fruit, pour garder les mêmes visages d'un plan à l'autre.
2. **Génération des plans** : Wan 3.0 (son natif) pour l'ASMR et les plans d'ambiance ; Kling 3.0 ou Seedance 2.5 à partir des images de référence pour les personnages.
3. **Montage local** (pipeline de ce dépôt) : passage en 1080×1920, enchaînements, compteur et accroches, sous-titres, mixage à −14 LUFS, export H.264/AAC, contrôle qualité.

## 4. Budget (prix relevés sur le compte Higgsfield le 6 novembre 2026)

| Plan généré | Coût |
|---|---|
| Wan 3.0 — 5 s, 480p | 5 crédits |
| Wan 3.0 — 5 s, 720p | 8,75 crédits |
| Wan 3.0 — 10 s, 720p | 17,5 crédits |
| Wan 3.0 — 10 s, 1080p | 35 crédits |
| Kling 3.0 — 5 s, standard, avec son | 10 crédits |
| Seedance 2.5 — 5 s, 480p / 720p | 15 / 35 crédits |

Estimation, en comptant environ 30 % de plans ratés à refaire :

| Lot | Crédits |
|---|---|
| 1 vidéo Cristal ASMR (14 plans Wan 720p) | ≈ 160 |
| 1 épisode Villa Vitamine (≈ 9 plans de 10 s + fiches personnages) | ≈ 200 |
| 5 vidéos ASMR | ≈ 800 |
| 5 vidéos ASMR + 5 épisodes | ≈ 1 800 |

Le compte connecté est sur le **plan gratuit, avec 8 crédits** : de quoi faire un seul plan test, mais pas une vidéo complète. Offres Higgsfield (hors TVA) :

| Offre | Crédits | Prix | Couvre |
|---|---|---|---|
| Essai Plus | 100 crédits, 3 jours | 0 € puis **49 €/mois si non résilié** (carte requise) | ≈ 1 vidéo ASMR en 480p |
| Plus | 1 000 / mois | 49 €/mois ou 39 €/mois en annuel | les 5 vidéos ASMR |
| Ultra | 3 000 / mois | 129 €/mois ou 99 €/mois en annuel | les 10 vidéos, avec de la marge |

## 5. Monétisation : ce qu'il faut savoir

- **Étiquette IA obligatoire** : TikTok impose de signaler les contenus IA réalistes et les détecte souvent tout seul (métadonnées C2PA).
- **Creator Rewards** : seules les vidéos de plus d'une minute comptent, d'où des compilations ASMR de 65 à 75 s et des épisodes de plus de 60 s.
  - Les contenus jugés « produits en masse » ou peu originaux peuvent être exclus, et l'ASMR IA brut est de plus en plus concurrencé.
  - La série (thèmes, compteur, vote, personnages récurrents, scénario) est ce qui apporte l'originalité.
- **Saturation** : la tendance des fruits en verre date de 2025. Elle tourne encore, mais il faut se démarquer (matières nouvelles, gradation « le plus dur à couper », vote du public).
  - La télé-réalité de fruits est plus récente ; son potentiel repose sur l'écriture et l'attachement aux personnages.
  - Ces tendances n'ont pas pu être vérifiées dans le TikTok Creative Center depuis ce serveur.
- **Droits** : les visuels et le son générés appartiennent à l'utilisateur selon les conditions de Higgsfield et du modèle ; la musique est originale ; les personnages sont originaux.
