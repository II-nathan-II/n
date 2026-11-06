"""NICHE_1 « Vertige Cosmique » — série 2 (vidéos 11 à 15), même chaîne de production que la v2.

Images : NASA (SVS, NASA Image and Video Library), domaine public ; bandes-son NASA retirées.
Faits vérifiés (sources dans docs.SOURCES) ; chiffres incertains formulés avec « environ », « plus de ».
"""
from videos_real import V, P, txt, back, counter, shade, seg, REAL, \
    NSM, MOON, EARTH, ISS, JUPITER, SUN171, SUN193, SUN131
from layers_base import Flash

# ----------------------------------------------------------------------------- nouvelles sources
SN = 'svs:20413/SN_HQ_Full_H264_V001.mp4'                       # supernova → étoile à neutrons (4K)
PULSAR = 'svs:20417/XRISM_IM_SHOT_01_alt_30fps_4k_h264.mp4'     # pulsar et vent de son compagnon (4K)
MAG = 'svs:20359/01_MAGNETAR_fixed_view.mp4'                    # magnétar, points chauds (1080p)
MAG_WIDE = 'svs:20359/02_MAGNETAR_Wide_view_BlipFlares_1080.mp4'
MOONTOUR = 'svs:4619/moontour_notitle_2160p30.mp4'              # visite de la Lune, sans titres (4K)
APOLLO11 = 'svs:4185/apollo11_flyover_1080p30.mp4'              # site d'Apollo 11 vu par LRO
MARS_TOPO = 'svs:4635/Mars_topo_2160p30.mp4'                    # survol du relief martien (4K)
MARS_ROLL = 'svs:3896/mars_lite_1080p.mp4'                      # Mars en rotation (Tharsis, Olympus Mons)
OLYMPUS = 'nasa:PIA02982'                                       # mosaïque couleur d'Olympus Mons (Viking)
GRS = 'svs:12878/12878_GreatRedSpot_YouTubeHD.mp4'              # Grande Tache rouge (NASA Goddard)
FUSION = 'svs:11084/space_weather_fusioniPad450master_high.mp4' # fusion au cœur du Soleil (animation)
HELICITY = 'svs:31400/helicity_4k_full_color.mp4'               # simulation de convection solaire (4K)
SDO171 = 'svs:14709/SDO_X3pt3_10-23-2024_300to430_171.mp4'      # Soleil entier 4096², 171 Å
SDO304 = 'svs:14709/SDO_X3pt3_10-23-2024_300to430_304.mp4'      # 304 Å
SDO131 = 'svs:14710/SDO_10-26-24_0603to0730UT_131.mp4'          # 131 Å

GOLD = (255, 216, 74)

R11 = dict(
    id='video_11', niche='NICHE_1', theme='space', speed=1.08, voice_reverb=0.06, **REAL,
    title='Une cuillère de cette étoile pèse un milliard de tonnes',
    hook_text='UNE CUILLÈRE =\\N1 MILLIARD DE TONNES',
    music=dict(style='space', prog='minor_wonder', key=47, bpm=74, seed=1101, start=0.3),
    segments=[
        seg("Une petite cuillère de cette étoile pèserait environ un milliard de tonnes.", V(MAG, 3.0, zoom=1.15), 'in', sfx=['boom'], music=0.35, emph=['milliard']),
        seg("Bienvenue sur une étoile à neutrons : ce qui reste d'une étoile géante après sa mort.", V(PULSAR, 2.0), 'slow_in', 'whip', label='ÉTOILE À NEUTRONS'),
        seg("Tout commence avec une étoile bien plus massive que le Soleil, qui arrive au bout de son carburant.", V(SN, 0.5, speed=0.6), 'slow_in', 'fade'),
        seg("Son cœur s'effondre en une fraction de seconde… et l'étoile explose : c'est une supernova.",
            V(SN, 6.0, speed=0.8, extra=[lambda: Flash(0.3, (200, 230, 255), 0.4, 0.9)]), 'in', 'flash', sfx=['impact'], emph=['supernova'], music=0.6),
        seg("Au centre, il reste un objet incroyable : plus lourd que le Soleil, mais écrasé dans une boule d'une vingtaine de kilomètres.",
            V(SN, 26.0, speed=0.6, zoom=1.3, extra=[back(170, 560), counter(0, 20, y=340, size=200, suffix=' km', color=GOLD, t1=2.2, sub='de diamètre')]),
            'push', 'zoom', emph=['vingtaine']),
        seg("La matière y est tellement tassée que les atomes sont écrasés : il ne reste presque que des neutrons. D'où son nom.", V(MAG, 10.0), 'slow_in', 'fade', emph=['neutrons']),
        seg("Et cette étoile tourne sur elle-même. Vite. Très vite.", V(PULSAR, 7.0), 'push', 'whip', sfx=[('riser', 0.0)]),
        seg("Le record connu : {716|sept cent seize} tours… par seconde.",
            V(PULSAR, 10.0, zoom=1.3, extra=[back(170, 560), counter(0, 716, y=340, size=210, color=GOLD, t1=2.0, sub='tours par seconde')]), 'in', 'cut', emph=['716']),
        seg("En tournant, elle balaie l'espace de faisceaux, comme un phare. On appelle ça un pulsar.", V(PULSAR, 4.0, zoom=1.2, flip=True), 'slow_in', 'fade', emph=['pulsar']),
        seg("Sa gravité est monstrueuse : un objet lâché d'un mètre de haut toucherait le sol à plusieurs millions de kilomètres par heure.",
            V(MAG, 18.0, zoom=1.3), 'in', 'zoom', emph=['millions']),
        seg("Et certaines, les magnétars, ont un champ magnétique des millions de milliards de fois plus puissant que celui de la Terre.",
            V(MAG_WIDE, 8.0, zoom=1.6), 'push', 'flash', label='MAGNÉTAR', emph=['magnétars'], music=0.7),
        seg("Mais le plus fou arrive quand deux étoiles à neutrons se percutent.", V(NSM, 4.0, speed=0.7), 'slow_in', 'black', sfx=[('riser', 0.0)]),
        seg("Le {17|dix-sept} août {2017|deux mille dix-sept}, des détecteurs ont capté une collision de ce type.", V(NSM, 11.5, speed=0.6), 'in', 'cut', label='17 AOÛT 2017'),
        seg("Elle a projeté dans l'espace des métaux lourds, comme l'or et le platine… en quantités gigantesques.",
            V(NSM, 18.0, speed=0.6, extra=[lambda: Flash(0.2, (255, 230, 160), 0.4, 0.8)]), 'in', 'flash', sfx=['impact'], emph=['or'], music=0.85),
        seg("Une partie de l'or de tes bijoux vient peut-être… d'une collision d'étoiles.", V(NSM, 22.0, speed=0.5), 'slow_in', 'zoom', emph=['bijoux']),
        seg("Tu le savais ? Dis-moi en commentaire si ça t'a surpris.", V(PULSAR, 13.0), 'out', 'fade', music=0.3),
    ])

R12 = dict(
    id='video_12', niche='NICHE_1', theme='space', speed=1.08, voice_reverb=0.06, **REAL,
    title='La Lune s\'éloigne de nous chaque année',
    hook_text='LA LUNE\\NS\'ÉLOIGNE DE NOUS',
    music=dict(style='space', prog='minor_float', key=45, bpm=70, seed=1201, start=0.3),
    segments=[
        seg("Chaque année, la Lune s'éloigne un peu plus de nous.", V(MOONTOUR, 270.0, speed=0.5), 'out', sfx=['boom'], music=0.35, emph=['éloigne']),
        seg("De combien ? Environ trois virgule huit centimètres par an.",
            V(MOONTOUR, 22.0, extra=[back(170, 560), counter(0, 3.8, y=340, size=200, fmt='float', decimals=1, suffix=' cm', color=GOLD, t1=2.0, sub='par an')]),
            'slow_in', 'whip', emph=['huit']),
        seg("À peu près la vitesse à laquelle poussent tes ongles.", V(MOONTOUR, 44.0), 'drift', 'cut', emph=['ongles']),
        seg("Et ce sont les missions Apollo qui nous permettent de le mesurer.", V(APOLLO11, 2.0, speed=0.7), 'in', 'fade', label='APOLLO 11 • 1969'),
        seg("En {1969|mille neuf cent soixante-neuf}, les astronautes d'Apollo {11|onze} ont posé sur la Lune un panneau de petits miroirs.",
            V(APOLLO11, 12.0, speed=0.6), 'slow_in', 'zoom', emph=['miroirs']),
        seg("D'autres ont été installés ensuite par Apollo {14|quatorze} et Apollo {15|quinze}.", V(MOONTOUR, 166.0), 'right', 'whip'),
        seg("Depuis la Terre, des observatoires tirent un rayon laser sur ces miroirs… et chronomètrent le retour de la lumière.",
            V(MOONTOUR, 131.0), 'push', 'flash', sfx=['whoosh'], emph=['laser']),
        seg("Environ deux secondes et demie pour l'aller-retour. Et on obtient la distance… au millimètre près.",
            V(MOONTOUR, 148.0, extra=[back(170, 560), txt('± 1 MM', 330, 170)]), 'in', 'cut', emph=['millimètre']),
        seg("Mais pourquoi la Lune s'en va-t-elle ? À cause des marées.", V(EARTH, 50.0), 'slow_in', 'black', music=0.6, emph=['marées']),
        seg("La Lune attire les océans de la Terre et forme un renflement d'eau, qui agit comme un frein sur la rotation de notre planète.",
            V(ISS, 1400.0, cx=0.5), 'drift', 'fade'),
        seg("L'énergie perdue par la Terre est transmise à la Lune… qui grimpe peu à peu sur une orbite plus haute.", V(MOONTOUR, 255.0, speed=0.6), 'out', 'zoom'),
        seg("Conséquence : nos journées s'allongent. D'environ deux millièmes de seconde par siècle.", V(EARTH, 85.0), 'slow_in', 'whip', emph=['allongent']),
        seg("Il y a environ {400|quatre cents} millions d'années, une journée ne durait qu'à peu près vingt-deux heures… et une année comptait plus de quatre cents jours.",
            V(EARTH, 92.0, extra=[back(170, 560), txt('22 H PAR JOUR', 330, 140)]), 'in', 'flash', label='IL Y A 400 MILLIONS D\'ANNÉES', emph=['vingt-deux']),
        seg("Et dans un futur très lointain, la Lune paraîtra trop petite pour cacher entièrement le Soleil.", V(MOON, 46.0, zoom=1.15), 'slow_in', 'fade', music=0.7),
        seg("Les éclipses totales de Soleil disparaîtront. Mais pas de panique : il faudra des centaines de millions d'années.", V(MOON, 128.0, zoom=1.15), 'in', 'black', emph=['éclipses']),
        seg("D'ici là, la prochaine éclipse totale près de chez nous aura lieu le {2|deux} août {2027|deux mille vingt-sept}, dans le sud de l'Espagne.",
            V(MOONTOUR, 26.0), 'push', 'zoom', label='2 AOÛT 2027', music=0.5),
        seg("Tu savais que la Lune s'éloignait ? Dis-le en commentaire.", V(MOONTOUR, 274.0, speed=0.5), 'out', 'fade', music=0.3),
    ])

R13 = dict(
    id='video_13', niche='NICHE_1', theme='space', speed=1.08, voice_reverb=0.06, **REAL,
    title='Le plus grand volcan du système solaire est sur Mars',
    hook_text='LE PLUS GRAND VOLCAN\\NDU SYSTÈME SOLAIRE',
    music=dict(style='space', prog='minor_epic', key=43, bpm=76, seed=1301, start=0.3),
    segments=[
        seg("Sur Mars, il existe un volcan si grand… qu'au sommet, tu aurais du mal à voir que tu es sur une montagne.", V(MARS_TOPO, 4.0, speed=0.8), 'in', sfx=['boom'], music=0.35, emph=['grand']),
        seg("Il s'appelle Olympus Mons. C'est le plus grand volcan connu du système solaire.", P(OLYMPUS, mode='fit'), 'slow_in', 'whip', label='OLYMPUS MONS • MARS', emph=['Olympus', 'Mons']),
        seg("Il s'élève à plus de vingt kilomètres au-dessus des plaines : environ deux fois et demie l'Everest.",
            P(OLYMPUS, cx=0.5, zoom=1.1, extra=[back(170, 560), counter(0, 22, y=340, size=210, suffix=' km', color=(255, 150, 90), t1=2.0, sub='de haut')]),
            'push', 'zoom', emph=['Everest']),
        seg("Et il est encore plus impressionnant en largeur : environ six cents kilomètres.", V(MARS_TOPO, 14.0, speed=0.8), 'drift', 'cut', emph=['six', 'cents']),
        seg("Plus que la distance entre Paris et Bordeaux.", V(MARS_TOPO, 22.0, speed=0.8, extra=[back(170, 520), txt('≈ 600 KM', 330, 170, (255, 150, 90))]), 'right', 'whip'),
        seg("Ses pentes sont si douces, quelques degrés à peine, que ses bords disparaissent derrière l'horizon.", V(MARS_TOPO, 31.0, speed=0.8), 'slow_in', 'fade', emph=['horizon']),
        seg("Au sommet s'ouvre un cratère géant, la caldeira, d'environ quatre-vingts kilomètres de long.", P(OLYMPUS, cx=0.5, cy=0.45, zoom=1.5), 'in', 'zoom', emph=['caldeira']),
        seg("Et sa base est bordée de falaises qui dépassent par endroits six kilomètres de haut.", P(OLYMPUS, cx=0.3, cy=0.55, zoom=1.3), 'tilt', 'flash', emph=['falaises']),
        seg("Mais comment un volcan peut-il devenir aussi énorme ? Il y a deux raisons.", V(MARS_ROLL, 2.0), 'slow_in', 'black', sfx=[('riser', 0.0)], music=0.6),
        seg("D'abord, Mars n'a pas de tectonique des plaques comme la Terre.", V(MARS_ROLL, 8.0), 'in', 'cut', emph=['tectonique']),
        seg("Sur Terre, les plaques glissent au-dessus des points chauds : à Hawaï, ça a formé toute une chaîne d'îles.", V(EARTH, 30.0), 'drift', 'whip', emph=['Hawaï']),
        seg("Sur Mars, la croûte ne bouge pas : la lave s'est empilée au même endroit pendant des centaines de millions d'années.", V(MARS_TOPO, 40.0, speed=0.8), 'slow_in', 'fade'),
        seg("Ensuite, la gravité martienne est près de trois fois plus faible : les montagnes peuvent monter plus haut sans s'effondrer sous leur propre poids.",
            V(MARS_ROLL, 14.0, extra=[back(170, 520), txt('GRAVITÉ ÷ 3', 330, 150)]), 'push', 'zoom', emph=['gravité'], music=0.75),
        seg("Et il n'est pas seul : juste à côté, trois autres volcans géants s'alignent sur le plateau de Tharsis.", V(MARS_ROLL, 3.0, zoom=1.4, cx=0.4), 'in', 'flash', label='PLATEAU DE THARSIS'),
        seg("Est-il éteint ? Certaines coulées de lave sur ses flancs n'auraient que quelques millions d'années. À l'échelle d'une planète… c'est presque hier.",
            V(MARS_TOPO, 52.0, speed=0.8), 'slow_in', 'zoom', emph=['hier']),
        seg("Tu tenterais l'ascension ? Réponds en commentaire.", V(MARS_ROLL, 30.0), 'out', 'fade', music=0.3),
    ])

R14 = dict(
    id='video_14', niche='NICHE_1', theme='space', speed=1.08, voice_reverb=0.06, **REAL,
    title='Une tempête plus grande que la Terre',
    hook_text='UNE TEMPÊTE PLUS\\NGRANDE QUE LA TERRE',
    music=dict(style='space', prog='minor_dark', key=46, bpm=72, seed=1401, start=0.3),
    segments=[
        seg("Il existe une tempête plus grande que la Terre. Et elle souffle depuis au moins cent cinquante ans.", V(JUPITER, 13.0, zoom=1.4, cx=0.55), 'in', sfx=['boom'], music=0.35, emph=['Terre']),
        seg("Elle s'appelle la Grande Tache rouge, et elle tourbillonne sur Jupiter.", V(GRS, 35.0, speed=0.7), 'slow_in', 'whip', label='JUPITER', emph=['Tache', 'rouge']),
        seg("Jupiter est la plus grande planète du système solaire : on pourrait y faire entrer plus de mille Terres.",
            V(JUPITER, 2.0, extra=[back(170, 520), txt('> 1 000 TERRES', 330, 150)]), 'out', 'fade', emph=['mille']),
        seg("Et cette tempête, à elle seule, est plus large que notre planète entière.", V(GRS, 75.0, speed=0.7), 'in', 'cut'),
        seg("Au dix-neuvième siècle, elle était encore bien plus grande : environ quarante mille kilomètres. De quoi aligner trois Terres.",
            V(JUPITER, 26.0, zoom=1.2, extra=[back(170, 560), counter(0, 40000, y=340, size=180, suffix=' km', color=(255, 150, 90), t1=2.2)]), 'push', 'zoom', emph=['trois']),
        seg("Mais depuis, elle rétrécit. Aujourd'hui, elle n'est plus qu'un peu plus large que la Terre.", V(GRS, 114.0, speed=0.7), 'slow_in', 'fade', emph=['rétrécit']),
        seg("Ses vents tournent à plus de {400 km/h|quatre cents kilomètres par heure}.",
            V(GRS, 40.0, speed=0.8, extra=[back(170, 560), counter(0, 400, y=340, size=210, prefix='+ ', suffix=' km/h', color=GOLD, t1=1.8)]), 'in', 'flash', sfx=['impact'], emph=['400 km/h'], music=0.65),
        seg("Plus vite que les pires ouragans jamais mesurés sur Terre.", V(GRS, 72.0, speed=0.8, zoom=1.2), 'push', 'whip'),
        seg("Et elle est profonde : d'après la sonde Juno, ses racines plongent jusqu'à environ cinq cents kilomètres sous les nuages.",
            V(JUPITER, 20.0, zoom=1.2), 'slow_in', 'zoom', label='SONDE JUNO', emph=['cinq', 'cents']),
        seg("Pourquoi dure-t-elle aussi longtemps ? Parce que Jupiter n'a pas de sol.", V(GRS, 20.0, speed=0.8), 'in', 'black', sfx=[('riser', 0.0)], emph=['sol']),
        seg("Sur Terre, un ouragan s'épuise quand il touche la terre ferme. Là-bas, rien ne le freine.", V(JUPITER, 25.0), 'drift', 'fade'),
        seg("Et sa couleur rouge ? Les scientifiques ne savent toujours pas exactement d'où elle vient.", V(GRS, 112.0, speed=0.7, zoom=1.3), 'slow_in', 'zoom', emph=['rouge'], music=0.75),
        seg("En {2024|deux mille vingt-quatre}, le télescope Hubble l'a même vue… trembler, comme de la gelée.", V(GRS, 28.0, speed=0.8), 'in', 'flash', label='HUBBLE • 2024', emph=['trembler']),
        seg("Va-t-elle disparaître un jour ? Personne ne le sait encore.", V(JUPITER, 28.0, zoom=1.3), 'slow_in', 'fade'),
        seg("Tu crois qu'elle sera encore là dans cent ans ? Dis-le en commentaire.", V(GRS, 6.0, speed=0.7), 'out', 'fade', music=0.3),
    ])

R15 = dict(
    id='video_15', niche='NICHE_1', theme='space', speed=1.08, voice_reverb=0.06, **REAL,
    title='La lumière du Soleil a des milliers d\'années',
    hook_text='CETTE LUMIÈRE A DES\\NMILLIERS D\'ANNÉES',
    music=dict(style='space', prog='minor_drift', key=48, bpm=70, seed=1501, start=0.3),
    segments=[
        seg("La lumière qui te réchauffe aujourd'hui a commencé son voyage… il y a peut-être plus de cent mille ans.", V(SUN171, 2.0, speed=0.6), 'in', sfx=['boom'], music=0.35, emph=['cent', 'mille']),
        seg("Elle naît au cœur du Soleil, à environ quinze millions de degrés.",
            V(FUSION, 24.0, speed=0.7, extra=[back(170, 560), txt('15 MILLIONS °C', 330, 150, (255, 170, 80))]), 'slow_in', 'whip', emph=['quinze', 'millions']),
        seg("Là, chaque seconde, le Soleil fusionne environ six cents millions de tonnes d'hydrogène.", V(FUSION, 2.0, speed=0.6), 'in', 'fade', emph=['hydrogène']),
        seg("Et au passage, il perd quatre millions de tonnes de matière… transformées en énergie.", V(FUSION, 12.0, speed=0.6, extra=[lambda: Flash(0.3, (255, 240, 200), 0.5, 0.9)]),
            'push', 'flash', sfx=['impact'], emph=['quatre', 'millions'], music=0.55),
        seg("Mais cette énergie ne sort pas tout de suite.", V(HELICITY, 2.0, speed=0.7, zoom=1.4), 'slow_in', 'black', sfx=[('riser', 0.0)]),
        seg("Le Soleil est si dense que la lumière est sans cesse absorbée… puis réémise, dans n'importe quelle direction.", V(HELICITY, 9.0, speed=0.7, zoom=1.5), 'drift', 'fade', emph=['dense']),
        seg("Elle avance au hasard, comme quelqu'un qui chercherait la sortie dans une foule immense.", V(HELICITY, 16.0, speed=0.7, zoom=1.6), 'in', 'cut', emph=['hasard']),
        seg("Résultat : l'énergie met des dizaines, voire des centaines de milliers d'années pour remonter jusqu'à la surface.",
            V(SDO304, 0.0, speed=0.5, zoom=1.3, extra=[back(170, 560), txt('100 000 ANS ?', 330, 160, (255, 140, 70))]), 'push', 'zoom', emph=['milliers'], music=0.7),
        seg("Puis, une fois dehors… tout s'accélère.", V(SDO131, 0.5, speed=0.5, zoom=1.2), 'in', 'flash', sfx=['whoosh']),
        seg("Il ne lui faut plus que huit minutes et vingt secondes pour parcourir les cent cinquante millions de kilomètres jusqu'à la Terre.",
            V(EARTH, 12.0, extra=[back(170, 520), txt('8 MIN 20 S', 330, 170)]), 'slow_in', 'whip', emph=['huit', 'minutes']),
        seg("Autrement dit, cette lumière a passé bien plus de temps à sortir du Soleil… qu'à voyager dans l'espace.", V(SUN193, 1.0, speed=0.6), 'push', 'fade'),
        seg("Quand elle a quitté le cœur du Soleil, il n'y avait sur Terre ni villes, ni agriculture, ni écriture.", V(ISS, 2600.0, cx=0.5), 'drift', 'black', emph=['écriture'], music=0.6),
        seg("Le Soleil contient à lui seul plus de quatre-vingt-dix-neuf pour cent de la masse du système solaire.",
            V(SDO171, 0.0, speed=0.5, extra=[back(170, 520), txt('99,8 %', 330, 190, GOLD)]), 'in', 'zoom', emph=['quatre-vingt-dix-neuf']),
        seg("Et il continuera de briller pendant encore environ cinq milliards d'années.", V(SUN131, 1.0, speed=0.6), 'slow_in', 'fade', music=0.75),
        seg("La prochaine fois que tu sens le soleil sur ta peau, pense à ce voyage. Tu le savais ? Dis-le en commentaire.", V(SUN171, 5.0, speed=0.6), 'out', 'fade', music=0.3),
    ])

VIDEOS = [R11, R12, R13, R14, R15]
