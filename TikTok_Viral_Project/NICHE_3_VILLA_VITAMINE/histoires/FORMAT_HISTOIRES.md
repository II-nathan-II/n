# Les histoires de la Villa : format court entre les épisodes

À publier sur le compte **Villa Vitamine**, en alternance avec les épisodes. Inspiré du genre des vidéos que tu
m'as montrées (mini-drames de fruits à corps humain), avec **nos** personnages et **nos** histoires : on ne reprend
ni les personnages ni les intrigues des autres créateurs.

## Le format

- **Durée :** 60 à 75 s, une histoire complète par vidéo (on peut la regarder sans connaître la série).
- **Recette :** une situation de tous les jours, de l'humour, un **retournement à la fin**, puis une question en commentaire.
- **Style :** les personnages de la série dans le nouveau style (corps humain, tenues, décors détaillés :
  `personnages/distribution_nouveau_style.jpg`). Les personnages parlent en français, en plans moyens.
- **Sous-titres :** blocs de 2–3 mots en majuscules blanches, **un mot en jaune** (le mot fort).
- **Ouverture :** accroche en bandeau jaune pendant les 2–3 premières secondes, sur le plan le plus fort.
- **Couverture :** même affiche dorée que les épisodes, avec « Les histoires de la Villa » au lieu de « Épisode N ».
- **Rythme conseillé :** épisodes le mardi et le vendredi, histoires le jeudi et le dimanche (18 h 30).

## Les 4 premières histoires (scénarios prêts)

| # | Titre | Accroche à l'écran | L'histoire | La chute |
|---|---|---|---|---|
| 1 | **La première tache** | ELLE A TROUVÉ SA 1RE TACHE… | Bérénice découvre une tache brune sur sa joue et panique : institut de beauté, parasol géant, elle dort dans le frigo (Pépin la découvre et tombe). | Kiki lui fait un banana bread : « les meilleures bananes, c'est celles qui ont des taches ». |
| 2 | **L'héritage de Papi Kiwi** | PAPI A LAISSÉ UN TRÉSOR… | Chez le notaire, Kiki et son cousin Cyril se battent pour le « trésor » de Papi Kiwi : un sachet de graines. | Kiki les plante ; le verger devient une affaire qui marche, et Cyril finit… à l'arrosage. |
| 3 | **Le rencard acide** | IL EST TROP ACIDE POUR DRAGUER ? | Fanny souffle à Cyril quoi dire avec une oreillette pendant son rencard avec Margaux ; il rate tout (« tes yeux sont… acceptables »). | Margaux adore son citron pressé sans sucre : « enfin quelqu'un qui me comprend ». |
| 4 | **24 h sans téléphone** | ELLE A PERDU SON TÉLÉPHONE… | Sans téléphone, Fanny doit parler aux autres en vrai et découvre les secrets de chacun. | Le téléphone était dans son chapeau… et elle le range dans un tiroir. |

Scénarios complets, plan par plan, avec les répliques : `pipeline/fruits_histoires.py`.

## Ce qu'il faut pour les produire

- **12 plans par histoire**, générés avec Veo (Ace Data) : environ **8,6 crédits par histoire**.
- Pour des visages encore plus réguliers d'un plan à l'autre : une image de départ par plan (Runway, environ
  240 crédits par histoire), comme pour l'épisode 2. Sans ces images, Veo s'appuie sur les descriptions détaillées.
- Le montage est prêt : `python3 pipeline/ai_assemble.py histoire_01` (accroche, sous-titres 2–3 mots avec mot jaune,
  carton de fin « FIN » et question en commentaire). Les vidéos sortent dans `NICHE_3_VILLA_VITAMINE/histoires/`.
