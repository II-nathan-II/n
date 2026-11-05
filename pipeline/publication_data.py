"""Métadonnées de publication TikTok pour les 10 vidéos (heures : Europe/Paris, à tester)."""

NICHES = {
    'NICHE_1': dict(nom='Les secrets de l\'Univers', compte='ex. @univers.secret', theme='Espace, astronomie, phénomènes cosmiques réels'),
    'NICHE_2': dict(nom='Ton cerveau te ment', compte='ex. @cerveau.bug', theme='Psychologie de la perception : illusions et expériences interactives'),
}

PUB = {
    'video_01': dict(
        titre="Il pleut du verre sur cette planète 😳",
        description="HD 189733 b : une planète bleue à 64 années-lumière où il pleuvrait du verre… à l'horizontale. Et Webb y a détecté une odeur d'œuf pourri. Tu irais la voir ? 👇 (Illustrations générées par ordinateur, vue d'artiste.)",
        hashtags=['#espace', '#astronomie', '#exoplanete', '#jameswebb', '#science'],
        accroche="Il existe une planète où il pleut du verre.",
        couverture="Gros plan de la planète bleu cobalt avec traînées de verre ; texte : « IL PLEUT DU VERRE ICI » en jaune sur fond bleu nuit.",
        horaire="Mardi 19 h 00",
        potentiel="Hook visuel + paradoxe (« pluie de verre ») immédiatement compréhensible, fait réel vérifiable (NASA/Hubble 2013, Webb 2024), chute humoristique (œuf pourri) qui favorise les partages et une question binaire en fin de vidéo qui pousse aux commentaires."),
    'video_02': dict(
        titre="Si le Soleil disparaissait, tu ne le saurais pas avant 8 min",
        description="La lumière ET la gravité mettent 8 min 20 s à nous parvenir. Après ? La nuit, -73 °C en un an… et Saturne qui brille encore 2 h. Toi, tu ferais quoi pendant ces 8 minutes ? 👇",
        hashtags=['#soleil', '#espace', '#astronomie', '#physique', '#science'],
        accroche="Si le Soleil disparaissait maintenant… tu ne le saurais pas avant huit minutes.",
        couverture="Soleil qui s'éteint à moitié (dégradé noir) + chrono « 08:20 » en grand.",
        horaire="Mercredi 12 h 30",
        potentiel="Scénario « et si… » universel, détail contre-intuitif (la gravité n'est pas instantanée) prouvé par un événement réel (GW170817), compte à rebours qui crée de la tension et question ouverte très facile à commenter."),
    'video_03': dict(
        titre="La zone la plus vide de l'Univers existe vraiment",
        description="Le vide du Bouvier : 330 millions d'années-lumière de diamètre, environ 60 galaxies au lieu de ~2 000. Et nous aussi, on vit au bord d'un vide. Centre du Grand Vide ou ici ? 👇",
        hashtags=['#univers', '#cosmos', '#astronomie', '#espace', '#mystere'],
        accroche="Il existe une zone de l'Univers tellement vide qu'on la surnomme simplement : le Grand Vide.",
        couverture="Toile cosmique bleue avec un cercle doré vide au centre ; texte : « 60 GALAXIES AU LIEU DE 2 000 ».",
        horaire="Jeudi 21 h 00",
        potentiel="Mystère cosmique avec chiffres chocs (2 000 → 60), citation vertigineuse, démystification des théories farfelues (renforce la crédibilité) et twist final personnel (« le Vide local »)."),
    'video_04': dict(
        titre="Voici ce qui t'arrive si tu tombes dans un trou noir",
        description="Petit trou noir : spaghettification. Supermassif : tu ne sens rien… mais ton ami te voit te figer pour toujours. Tu choisis lequel ? 👇 (Illustrations générées par ordinateur.)",
        hashtags=['#trounoir', '#espace', '#relativite', '#einstein', '#astronomie'],
        accroche="Voici ce qui t'arriverait si tu tombais dans un trou noir.",
        couverture="Trou noir doré façon disque d'accrétion + silhouette d'astronaute étirée ; texte : « TU TOMBES… ».",
        horaire="Vendredi 18 h 00",
        potentiel="Sujet spatial le plus recherché, narration à la 2e personne (immersion), mot mémorable (« spaghettification »), opposition petit/supermassif qui structure la vidéo et alimente les commentaires."),
    'video_05': dict(
        titre="Sur Vénus, un jour dure plus longtemps qu'un an",
        description="243 jours pour tourner sur elle-même, 225 pour faire le tour du Soleil. 465 °C, pluie acide… et pourtant la NASA a imaginé des dirigeables habités. Tu monterais à bord ? 👇",
        hashtags=['#venus', '#systemesolaire', '#espace', '#nasa', '#astronomie'],
        accroche="Sur Vénus, une journée dure plus longtemps qu'une année.",
        couverture="Vénus jaune-orangé + dirigeable au-dessus des nuages ; texte : « 1 JOUR > 1 AN ».",
        horaire="Samedi 11 h 00",
        potentiel="Paradoxe dès la 1re seconde, avalanche de faits extrêmes (plomb fondu, 900 m sous l'eau), histoire vraie de la sonde Venera 13 et twist final optimiste (villes flottantes) ; CTA oui/non à faible friction."),
    'video_06': dict(
        titre="Fixe le point 30 secondes : ton cerveau va recolorer ce drapeau 🇫🇷",
        description="Expérience : fixe le point blanc sans bouger les yeux… puis regarde l'écran blanc. Tu as vu bleu-blanc-rouge ? Écris-le en commentaire ! Explication : image rémanente et couleurs opposées (Hering).",
        hashtags=['#illusionoptique', '#cerveau', '#psychologie', '#experience', '#drapeaufrancais'],
        accroche="Ce drapeau n'a pas les bonnes couleurs. Mais dans trente secondes, tu vas voir le vrai.",
        couverture="Drapeau aux couleurs inversées (orange-noir-cyan) avec le point blanc ; texte : « FIXE LE POINT 30 s ».",
        horaire="Mardi 20 h 30",
        potentiel="Expérience interactive à fort taux de complétion (il faut rester jusqu'au bout pour voir l'effet), forte identité française (drapeau), rejouabilité (re-visionnages) et commentaire guidé « bleu blanc rouge »."),
    'video_07': dict(
        titre="Regarde cette spirale 30 secondes… puis regarde ta main",
        description="L'illusion de la cascade (effet consécutif de mouvement), décrite dès Aristote. Fixe le point rouge jusqu'au bout. Ça a duré combien de temps pour toi ? 👇 ⚠️ Arrête si tu ressens un inconfort.",
        hashtags=['#illusionoptique', '#cerveau', '#spirale', '#neurosciences', '#psychologie'],
        accroche="Regarde cette spirale pendant trente secondes… et le monde autour de toi va se mettre à bouger.",
        couverture="Spirale noir et blanc hypnotique avec point rouge ; texte : « NE QUITTE PAS LE CENTRE ».",
        horaire="Mercredi 21 h 00",
        potentiel="Format « défi » éprouvé sur TikTok, effet spectaculaire ressenti physiquement, explication neuroscientifique claire (neurones du mouvement) et question chiffrée qui génère beaucoup de réponses."),
    'video_08': dict(
        titre="Fixe la croix : les couleurs vont disparaître",
        description="Niveau 1 : l'effet Troxler (1804). Niveau 2 : le « lilac chaser » où un point vert qui n'existe pas apparaît. Tu l'as vu ? Écris « vert » 👇",
        hashtags=['#illusionoptique', '#cerveau', '#testvisuel', '#psychologie', '#couleurs'],
        accroche="Fixe la croix au centre… et ces couleurs vont disparaître sous tes yeux.",
        couverture="Cercle de points roses flous autour d'une croix ; texte : « TU VAS VOIR UN POINT VERT ».",
        horaire="Jeudi 12 h 30",
        potentiel="Deux illusions en escalade (« niveau 2 ») qui retiennent jusqu'à la fin, révélation « il n'y a jamais eu de vert » très partageable et engagement par mot-clé simple en commentaire."),
    'video_09': dict(
        titre="Tu as un trou dans ta vision (et je te le prouve)",
        description="Ferme l'œil gauche, fixe la croix avec l'œil droit, approche ton téléphone… le point disparaît. C'est ta tache aveugle, découverte par Edme Mariotte vers 1660. À quelle distance pour toi ? 👇",
        hashtags=['#tacheaveugle', '#cerveau', '#illusionoptique', '#oeil', '#science'],
        accroche="Il y a un trou dans ta vision. En ce moment même. Et ton cerveau te le cache.",
        couverture="Fond blanc, croix noire à gauche et gros point noir à droite ; texte : « FERME L'ŒIL GAUCHE ».",
        horaire="Vendredi 20 h 00",
        potentiel="Test participatif réalisable par 100 % des spectateurs sur téléphone, révélation corporelle surprenante, anecdote historique amusante (la tête des courtisans) et question de distance qui déclenche des comparaisons."),
    'video_10': dict(
        titre="A et B sont EXACTEMENT de la même couleur",
        description="Je relie les deux cases, j'efface le reste… et pourtant ton cerveau continue de mentir. Constance des couleurs, l'illusion d'Adelson et… la robe de 2015. Bleue/noire ou blanche/dorée ? 👇",
        hashtags=['#illusionoptique', '#cerveau', '#psychologie', '#couleurs', '#larobe'],
        accroche="Les cases A et B sont exactement de la même couleur.",
        couverture="Échiquier avec cylindre vert, cases A et B entourées ; texte : « MÊME COULEUR ?! ».",
        horaire="Dimanche 18 h 30",
        potentiel="Affirmation incroyable prouvée en direct (bande de gris, effacement), débat garanti en commentaires, rappel de « la robe » (référence virale connue) qui relance la discussion."),
}
