"""Métadonnées de publication TikTok pour les 10 vidéos (heures : Europe/Paris, à tester)."""

NICHES = {
    'NICHE_1': dict(nom='Les secrets de l\'Univers', compte='@vertige.cosmique (Vertige Cosmique)', theme='Espace, astronomie, phénomènes cosmiques réels'),
    'NICHE_2': dict(nom='Planète extrême', compte='ex. @planete.extreme', theme='Phénomènes naturels réels filmés depuis l\'espace et la Terre'),
}

PUB = {
    'video_01': dict(
        titre="Il pleut du verre sur cette planète 😳",
        description="HD 189733 b : une planète bleue à 64 années-lumière où il pleuvrait du verre… à l'horizontale. Et Webb y a détecté une odeur d'œuf pourri. Tu irais la voir ? 👇 (Images : NASA — illustrations scientifiques et vues d'artiste.)",
        hashtags=['#espace', '#astronomie', '#exoplanete', '#jameswebb', '#science'],
        accroche="Il existe une planète où il pleut du verre.",
        couverture="Gros plan de la planète bleu cobalt avec traînées de verre ; texte : « IL PLEUT DU VERRE ICI » en jaune sur fond bleu nuit.",
        horaire="Mardi 19 h 00",
        potentiel="Hook visuel + paradoxe (« pluie de verre ») immédiatement compréhensible, fait réel vérifiable (NASA/Hubble 2013, Webb 2024), chute humoristique (œuf pourri) qui favorise les partages et une question binaire en fin de vidéo qui pousse aux commentaires."),
    'video_02': dict(
        titre="Si le Soleil disparaissait, tu ne le saurais pas avant 8 min",
        description="La lumière ET la gravité mettent 8 min 20 s à nous parvenir. Après ? La nuit, -73 °C en un an… et Saturne qui brille encore 2 h. Toi, tu ferais quoi pendant ces 8 minutes ? 👇 (Images : NASA)",
        hashtags=['#soleil', '#espace', '#astronomie', '#physique', '#science'],
        accroche="Si le Soleil disparaissait maintenant… tu ne le saurais pas avant huit minutes.",
        couverture="Soleil qui s'éteint à moitié (dégradé noir) + chrono « 08:20 » en grand.",
        horaire="Mercredi 12 h 30",
        potentiel="Scénario « et si… » universel, détail contre-intuitif (la gravité n'est pas instantanée) prouvé par un événement réel (GW170817), compte à rebours qui crée de la tension et question ouverte très facile à commenter."),
    'video_03': dict(
        titre="La zone la plus vide de l'Univers existe vraiment",
        description="Le vide du Bouvier : 330 millions d'années-lumière de diamètre, environ 60 galaxies au lieu de ~2 000. Et nous aussi, on vit au bord d'un vide. Centre du Grand Vide ou ici ? 👇 (Images : NASA — simulations et vues d'artiste.)",
        hashtags=['#univers', '#cosmos', '#astronomie', '#espace', '#mystere'],
        accroche="Il existe une zone de l'Univers tellement vide qu'on la surnomme simplement : le Grand Vide.",
        couverture="Toile cosmique bleue avec un cercle doré vide au centre ; texte : « 60 GALAXIES AU LIEU DE 2 000 ».",
        horaire="Jeudi 21 h 00",
        potentiel="Mystère cosmique avec chiffres chocs (2 000 → 60), citation vertigineuse, démystification des théories farfelues (renforce la crédibilité) et twist final personnel (« le Vide local »)."),
    'video_04': dict(
        titre="Voici ce qui t'arrive si tu tombes dans un trou noir",
        description="Petit trou noir : spaghettification. Supermassif : tu ne sens rien… mais ton ami te voit te figer pour toujours. Tu choisis lequel ? 👇 (Images : NASA Goddard — visualisations scientifiques.)",
        hashtags=['#trounoir', '#espace', '#relativite', '#einstein', '#astronomie'],
        accroche="Voici ce qui t'arriverait si tu tombais dans un trou noir.",
        couverture="Trou noir doré façon disque d'accrétion + silhouette d'astronaute étirée ; texte : « TU TOMBES… ».",
        horaire="Vendredi 18 h 00",
        potentiel="Sujet spatial le plus recherché, narration à la 2e personne (immersion), mot mémorable (« spaghettification »), opposition petit/supermassif qui structure la vidéo et alimente les commentaires."),
    'video_05': dict(
        titre="Sur Vénus, un jour dure plus longtemps qu'un an",
        description="243 jours pour tourner sur elle-même, 225 pour faire le tour du Soleil. 465 °C, pluie acide… et pourtant la NASA a imaginé des dirigeables habités. Tu monterais à bord ? 👇 (Images : NASA)",
        hashtags=['#venus', '#systemesolaire', '#espace', '#nasa', '#astronomie'],
        accroche="Sur Vénus, une journée dure plus longtemps qu'une année.",
        couverture="Vénus jaune-orangé + dirigeable au-dessus des nuages ; texte : « 1 JOUR > 1 AN ».",
        horaire="Samedi 11 h 00",
        potentiel="Paradoxe dès la 1re seconde, avalanche de faits extrêmes (plomb fondu, 900 m sous l'eau), histoire vraie de la sonde Venera 13 et twist final optimiste (villes flottantes) ; CTA oui/non à faible friction."),
    'video_06': dict(
        titre="Un ouragan vu depuis la Station spatiale 🌀",
        description="Images réelles de l'ISS au-dessus des ouragans Beryl, Franklin et Milton. Énergie, œil, vents à 250 km/h : voici comment naît un monstre. Tu as déjà vécu une tempête ? 👇 (Images : NASA)",
        hashtags=['#ouragan', '#espace', '#meteo', '#nasa', '#planete'],
        accroche="Voici ce que voient les astronautes quand un ouragan passe sous la Station spatiale.",
        couverture="Œil de l'ouragan Beryl vu de l'ISS ; texte : « UN OURAGAN VU DE L'ESPACE ».",
        horaire="Mardi 19 h 30",
        potentiel="Images réelles et spectaculaires dès la 1re seconde, point de vue rare (astronautes), chiffres chocs et question personnelle en fin de vidéo qui déclenche des témoignages."),
    'video_07': dict(
        titre="L'explosion la plus puissante jamais mesurée 🌋",
        description="Hunga Tonga, 15 janvier 2022 : panache à 57 km, onde de choc qui fait le tour de la Terre, 146 millions de tonnes d'eau dans la stratosphère. Tu en avais entendu parler ? 👇 (Images : NASA / NOAA GOES)",
        hashtags=['#volcan', '#tonga', '#eruption', '#science', '#planete'],
        accroche="Un volcan sous-marin a explosé avec une puissance jamais enregistrée par nos instruments modernes.",
        couverture="Panache vu par satellite ; texte : « PLUS PUISSANT QU'HIROSHIMA ×100 ».",
        horaire="Mercredi 20 h 30",
        potentiel="Événement réel récent et méconnu, données satellites inédites (onde de choc visible), lien avec la France (baromètres) et twist final (l'eau dans la stratosphère)."),
    'video_08': dict(
        titre="Ce qui se passe AU-DESSUS des orages ⚡",
        description="Sprites rouges filmés depuis l'ISS, 44 éclairs par seconde, éclair de 829 km, rayons gamma et antimatière… La foudre est bien plus folle que tu crois. Raconte ton orage le plus fou 👇 (Images : NASA)",
        hashtags=['#foudre', '#orage', '#espace', '#science', '#nasa'],
        accroche="Ce flash rouge au-dessus des nuages, ce n'est pas un effet spécial.",
        couverture="Flash rouge au-dessus d'un orage vu de l'ISS ; texte : « CE N'EST PAS UN EFFET SPÉCIAL ».",
        horaire="Jeudi 21 h 00",
        potentiel="Hook mystérieux (phénomène que peu connaissent), accumulation de records et faits contre-intuitifs (antimatière), sujet universel qui pousse aux anecdotes en commentaire."),
    'video_09': dict(
        titre="Les aurores boréales vues depuis l'espace 🌌",
        description="Vues de l'ISS, les aurores ondulent sous les astronautes. D'où vient la lumière, pourquoi le vert et le rouge, la tempête de mai 2024 vue en France… Tu les as vues ? Dis-moi d'où 👇 (Images : NASA)",
        hashtags=['#aurore', '#auroreboreale', '#espace', '#nasa', '#soleil'],
        accroche="Voici des aurores boréales… vues d'en haut, depuis la Station spatiale.",
        couverture="Aurore verte et rouge au-dessus de la Terre vue de l'ISS ; texte : « VUES DE L'ESPACE ».",
        horaire="Vendredi 21 h 30",
        potentiel="Visuel parmi les plus partagés sur TikTok, souvenir collectif récent (mai 2024 en France) et question de localisation qui génère beaucoup de commentaires."),
    'video_10': dict(
        titre="Le Sahara nourrit l'Amazonie (et c'est prouvé)",
        description="182 millions de tonnes de poussière par an, 22 000 tonnes de phosphore pour la forêt, et une source étonnante : un ancien lac du Tchad. Ta voiture déjà couverte de sable ? 👇 (Images : NASA)",
        hashtags=['#sahara', '#amazonie', '#nature', '#nasa', '#science'],
        accroche="Chaque année, le plus grand désert chaud du monde nourrit la plus grande forêt tropicale du monde.",
        couverture="Globe avec le panache de poussière vers l'Amérique ; texte : « LE SAHARA NOURRIT L'AMAZONIE ».",
        horaire="Dimanche 18 h 00",
        potentiel="Paradoxe immédiat (désert → forêt), découverte satellite crédible, lien concret avec le quotidien en France (sable sur les voitures) et CTA d'expérience vécue."),
}
