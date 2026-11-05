"""NICHE 2 — « Ton cerveau te ment » : 5 expériences interactives (scripts + mise en scène)."""
from common import W, H
from layers_base import *
from layers_psy import *

def seg(text, scene='same', **kw):
    d = dict(text=text, scene=scene); d.update(kw); return d

C = Composite
def CC(layers):
    return Composite(layers, clean=True)

def lab_bg(seed=0):
    return GradientBG((16, 18, 40), (4, 5, 12), blobs=3, blob_colors=((60, 90, 255), (255, 80, 160), (40, 200, 190)), seed=seed)

def big(text, color=(255, 225, 53), size=120, y=760, **kw):
    return Text(text, W / 2, y, size, 'poppins_black', color, max_width=920, **kw)

# ============================================================================= VIDÉO 06 — image rémanente
V06 = dict(
    id='video_06', niche='NICHE_2', theme='psy', speed=1.0,
    title='Ton cerveau va recolorer ce drapeau',
    hook_text='TON CERVEAU VA\\NRECOLORER\\NCE DRAPEAU', hook_y=290,
    music=dict(style='lofi', prog='lofi_a', key=57, bpm=84, seed=61, start=0.25, db=-27),
    segments=[
        seg("Ce drapeau n'a pas les bonnes couleurs. Mais dans trente secondes, tu vas voir le vrai.",
            lambda c: CC([InvertedFlag(switch_at=c.local('now')), Countdown(c.local('fix'), c.local('now'), y=1140, size=70, color=(200, 200, 200))]),
            cam='static', sfx=['pop'], cap_y=1360, music=0.3, mark='start'),
        seg("Fais l'expérience avec moi.", cap='calm', cap_y=1360),
        seg("Fixe le petit point blanc, au centre du drapeau. Ne bouge surtout pas les yeux.", cap='calm', cap_y=1360, mark='fix'),
        seg("Évite de cligner des yeux. Concentre-toi uniquement sur le point.", cap='calm', cap_y=1360),
        seg("Pendant que tu regardes, des cellules au fond de ton œil travaillent sans relâche.", cap='calm', cap_y=1360),
        seg("On les appelle les cônes. Il en existe trois sortes, sensibles surtout au rouge, au vert et au bleu.", cap='calm', cap_y=1360),
        seg("Et en ce moment même, certaines d'entre elles sont en train de s'épuiser.", cap='calm', cap_y=1360),
        seg("Reste bien sur le point… encore quelques secondes.", cap='calm', cap_y=1360),
        seg("Trois… deux… un…", cap='calm', cap_y=1360, speed=0.9, sfx=[('tick', 0.0), ('tick', 0.75), ('tick', 1.5)]),
        seg("Maintenant !", mark='now', cap_y=1360, sfx=['ding'], music=-1),
        seg('', hold=5.5, cap='none'),
        seg("Tu l'as vu ? Un drapeau bleu, blanc, rouge… sur un écran complètement blanc.", cap_y=1360, music=0.35, emph=['bleu', 'blanc', 'rouge']),
        seg("Ce drapeau n'a jamais été affiché. C'est ton cerveau qui l'a peint.",
            lambda: C([lab_bg(1), FlagCompare()]), cam='slow_in', trans='fade', emph=['cerveau'], music=0.5),
        seg("C'est ce qu'on appelle une image rémanente.", lambda: C([lab_bg(2), big('IMAGE\nRÉMANENTE', size=130)]), cam='in', trans='zoom', sfx=['pop']),
        seg("Là où tu fixais du cyan, tes cônes du vert et du bleu se sont fatigués.",
            lambda: C([lab_bg(3), ConeCells(drain=(0.85, 0.85, 0.05))]), cam='slow_in', trans='whip', emph=['cyan', 'fatigués']),
        seg("Sur le blanc, ce sont donc les cônes du rouge qui ont parlé le plus fort. Résultat : du rouge.", emph=['rouge']),
        seg("Et là où il y avait de l'orange, c'est l'inverse : ton cerveau a vu du bleu.",
            lambda: C([lab_bg(4), ConeCells(drain=(0.05, 0.6, 0.9))]), cam='slow_in', trans='whip', emph=['orange', 'bleu']),
        seg("Ce mécanisme a été décrit à la fin du dix-neuvième siècle par le physiologiste allemand {Ewald Hering.|Évald Érinng.}",
            lambda: C([lab_bg(5), ArchiveCard('Ewald Hering', '1878', 'Physiologiste allemand — théorie des couleurs opposées', seed=6)]), cam='slow_in', trans='fade', sfx=['type'], music=0.6),
        seg("Pour lui, notre vision fonctionne par paires de couleurs opposées.", lambda: C([lab_bg(6), OpponentPairs()]), cam='static', trans='zoom'),
        seg("Rouge contre vert. Bleu contre jaune. Noir contre blanc.", emph=['rouge', 'vert', 'bleu', 'jaune', 'noir', 'blanc']),
        seg("Quand un côté se fatigue, c'est l'autre que tu vois.", emph=['fatigue']),
        seg("C'est d'ailleurs l'une des raisons souvent avancées pour expliquer pourquoi les chirurgiens portent du vert ou du bleu.",
            lambda: C([AfterimageDemo(switch=0.45)]), cam='slow_in', trans='whip', music=0.7),
        seg("Après des heures à fixer du rouge, un mur blanc se couvrirait de taches vertes. Sur du vert, elles se fondent.", emph=['vertes']),
        seg("Ça a marché sur toi ? Écris « bleu blanc rouge » en commentaire si tu l'as vu.",
            lambda: CC([InvertedFlag(invert=False, bg=(20, 22, 40))]), cam='static', trans='fade', music=0.35, cap_y=1360),
    ])

# ============================================================================= VIDÉO 07 — spirale
V07 = dict(
    id='video_07', niche='NICHE_2', theme='psy', speed=1.0,
    title='Fixe cette spirale 30 secondes',
    hook_text='FIXE LE CENTRE\\N30 SECONDES', hook_y=230,
    music=dict(style='lofi', prog='lofi_b', key=55, bpm=86, seed=71, start=0.25, db=-27),
    segments=[
        seg("Regarde cette spirale pendant trente secondes… et le monde autour de toi va se mettre à bouger.",
            lambda c: CC([Spiral(stop_at=c.local('now')), Countdown(c.local('fix'), c.local('now'), y=1350, size=60, color=(170, 170, 170))]),
            cam='static', sfx=['pop'], cap_y=1430, music=0.3),
        seg("Fixe le point rouge au centre. Ne quitte pas le point des yeux.", cap='calm', cap_y=1430, mark='fix'),
        seg("Ce que tu es en train de vivre porte un nom : l'effet consécutif de mouvement.", cap='calm', cap_y=1430),
        seg("Aristote l'avait déjà remarqué il y a plus de deux mille ans, en regardant une rivière.", cap='calm', cap_y=1430),
        seg("Mais c'est en {1834|dix-huit cent trente-quatre} qu'un certain Robert Addams l'a décrit précisément, devant une cascade écossaise : les chutes de Foyers.", cap='calm', cap_y=1430),
        seg("Après avoir fixé l'eau qui tombait, il a regardé les rochers à côté… et ils semblaient remonter.", cap='calm', cap_y=1430),
        seg("C'est pour ça qu'on l'appelle aussi : l'illusion de la cascade.", cap='calm', cap_y=1430),
        seg("Continue de fixer le centre. Encore un tout petit peu.", cap='calm', cap_y=1430),
        seg("Trois… deux… un…", cap='calm', cap_y=1430, speed=0.9, sfx=[('tick', 0.0), ('tick', 0.75), ('tick', 1.5)]),
        seg("Maintenant, regarde cette image.", lambda: CC([Mosaic()]), mark='now', cap_y=1430, sfx=['ding'], music=-1),
        seg('', hold=4.5, cap='none'),
        seg("Elle bouge, non ? Elle semble rétrécir, comme aspirée vers l'intérieur.", cap_y=1430, music=0.3, emph=['rétrécir']),
        seg("Tu peux aussi regarder ta main, ou le mur autour de toi.", cap_y=1430),
        seg("Pourtant, rien ne bouge. L'image est parfaitement immobile.", cap_y=1430, emph=['immobile']),
        seg("Dans ton cerveau, certains neurones sont spécialisés dans la détection du mouvement.",
            lambda: C([lab_bg(7), Neurons(seed=3)]), cam='slow_in', trans='zoom', label='AIRE V5 : LE MOUVEMENT', music=0.55),
        seg("Certains réagissent quand les choses s'éloignent du centre. D'autres, quand elles s'en rapprochent.",
            lambda: C([lab_bg(8), Neurons(seed=4, balance_bar=True, labels=('Expansion', 'Contraction'))]), cam='static', trans='fade'),
        seg("Normalement, les deux groupes s'équilibrent."),
        seg("Mais pendant trente secondes, tu as surmené ceux qui détectent l'expansion. Ils se sont fatigués.",
            lambda: C([lab_bg(8), Neurons(seed=4, balance_bar=True, labels=('Expansion', 'Contraction'), fatigue=0.85, fatigue_at=0.15)]), cam='slow_in', emph=['fatigués'], music=0.7),
        seg("Quand la spirale s'arrête, l'autre groupe l'emporte… et ton cerveau voit un mouvement qui n'existe pas.", emph=['existe']),
        seg("La preuve que tu ne vois pas le monde tel qu'il est. Tu vois ce que ton cerveau en déduit.",
            lambda: C([lab_bg(9), big('TU VOIS CE QUE\nTON CERVEAU\nEN DÉDUIT', size=100)]), cam='in', trans='whip', sfx=['pop']),
        seg("Pas d'inquiétude : l'effet disparaît au bout de quelques secondes.", lambda: CC([Mosaic(seed=6)]), cam='static', trans='fade', music=0.45),
        seg("Combien de temps ça a duré pour toi ? Dis-le en commentaire.", lambda: CC([Spiral(speed=1.2)]), cam='static', trans='fade', music=0.35, cap_y=1430),
    ])

# ============================================================================= VIDÉO 08 — Troxler + lilac chaser
V08 = dict(
    id='video_08', niche='NICHE_2', theme='psy', speed=1.0,
    title='Fixe la croix : les couleurs vont disparaître',
    hook_text='LES COULEURS\\NVONT DISPARAÎTRE', hook_y=240,
    music=dict(style='lofi', prog='lofi_c', key=53, bpm=82, seed=81, start=0.25, db=-27),
    segments=[
        seg("Fixe la croix au centre… et ces couleurs vont disparaître sous tes yeux.", lambda: CC([Troxler()]), cam='static', sfx=['pop'], cap_y=1430, music=0.3),
        seg("Ne bouge pas les yeux. Garde-les bien sur la petite croix noire.", cap='calm', cap_y=1430),
        seg("Autour, il y a des taches de couleur. Elles ne bougent pas. Elles ne changent pas.", cap='calm', cap_y=1430),
        seg("Et pourtant… petit à petit, elles commencent à s'effacer.", cap='calm', cap_y=1430),
        seg("Certaines virent au gris. D'autres se fondent complètement dans le fond.", cap='calm', cap_y=1430),
        seg('', hold=2.5, cap='none'),
        seg("Si tu bouges les yeux, même un tout petit peu, elles reviennent d'un coup.", cap='calm', cap_y=1430),
        seg("C'est l'effet {Troxler,|Troxleur,} décrit par le médecin suisse {Ignaz Troxler,|Ignaz Troxleur,} en {1804|dix-huit cent quatre}.",
            lambda: C([lab_bg(10), ArchiveCard('Ignaz Troxler', '1804', 'Médecin et philosophe suisse', seed=8)]), cam='slow_in', trans='fade', sfx=['type'], music=0.5),
        seg("Ton cerveau ignore ce qui ne change pas. Ce qui est flou, immobile et sur le côté finit par être effacé.",
            lambda: C([Troxler(fade=(0.8, 4.5))]), cam='slow_in', trans='zoom', emph=['ignore']),
        seg("C'est une économie d'énergie : inutile de traiter mille fois la même information.",
            lambda: C([lab_bg(11), Neurons(seed=5, fatigue=0.9, fatigue_at=0.1)]), cam='static', trans='fade'),
        seg("Maintenant, on passe au niveau supérieur.", lambda: C([lab_bg(12), big('NIVEAU 2', size=160)]), cam='in', trans='glitch', sfx=[('riser', 0.0)], music=0.75),
        seg("Fixe la croix au centre. Des points roses disparaissent l'un après l'autre.", lambda: CC([LilacChaser()]), trans='flash', cam='static', cap_y=1430, music=0.4),
        seg("Ne les suis pas des yeux. Reste sur la croix, et attends.", cap='calm', cap_y=1430),
        seg("Au bout de quelques secondes, quelque chose d'étrange va se produire.", cap='calm', cap_y=1430),
        seg("Un point vert apparaît… et se met à tourner.", cap='calm', cap_y=1430),
        seg("Et si tu tiens bon, les points roses finissent par s'effacer. Il ne reste qu'un point vert qui tourne dans le vide.", cap='calm', cap_y=1430),
        seg('', hold=4.0, cap='none'),
        seg("Sauf qu'il n'y a aucun point vert à l'écran. Il n'y en a jamais eu.", cap_y=1430, emph=['aucun'], music=0.55),
        seg("Cette illusion s'appelle le {lilac chaser|laïlac tchéïseur}. Elle a été créée par {Jeremy Hinton|Djérémi Hinntone} vers {2005|deux mille cinq}.",
            lambda: C([lab_bg(13), ArchiveCard('Jeremy Hinton', '2005', 'Créateur du « lilac chaser »', seed=9)]), cam='slow_in', trans='fade', sfx=['type']),
        seg("Le vert, c'est une image rémanente : la couleur opposée du rose, que tes yeux créent chaque fois qu'un point disparaît.",
            lambda: C([LilacChaser(simulate=True, step=0.25)]), cam='slow_in', trans='zoom', emph=['rémanente'], music=0.7),
        seg("Et les points roses s'effacent grâce à l'effet {Troxler,|Troxleur,} que tu viens de découvrir.",
            lambda: C([LilacChaser(simulate=True, step=0.25, fade_pinks=(0.5, 3.0))]), cam='static', emph=['Troxler']),
        seg("Deux bugs de ton cerveau… réunis dans une seule image.", lambda: C([lab_bg(14), big('2 BUGS\n1 IMAGE', size=150)]), cam='in', trans='whip', sfx=['pop']),
        seg("Tu as vu le point vert ? Écris « vert » en commentaire si ça a marché.", lambda: CC([LilacChaser()]), cam='static', trans='fade', music=0.35, cap_y=1430),
    ])

# ============================================================================= VIDÉO 09 — tache aveugle
V09 = dict(
    id='video_09', niche='NICHE_2', theme='psy', speed=1.0,
    title='Tu as un trou dans ta vision',
    hook_text='TU AS UN TROU\\NDANS TA VISION', hook_y=330,
    music=dict(style='lofi', prog='lofi_d', key=58, bpm=88, seed=91, start=0.25, db=-27),
    segments=[
        seg("Il y a un trou dans ta vision. En ce moment même. Et ton cerveau te le cache.", lambda: CC([BlindSpot()]), cam='static', sfx=['pop'], music=0.3, cap_y=1300),
        seg("Je vais te le prouver en quinze secondes.", cap_y=1300),
        seg("Ferme ton œil gauche. Avec ton œil droit, fixe la croix, à gauche de l'écran.", cap='calm', cap_y=1300, emph=['gauche']),
        seg("Maintenant, rapproche lentement ton téléphone de ton visage… jusqu'à quinze ou vingt centimètres.", cap='calm', cap_y=1300),
        seg("Continue de fixer la croix. Ne regarde surtout pas le point.", cap='calm', cap_y=1300),
        seg("À un moment précis… le point noir disparaît complètement.", cap='calm', cap_y=1300),
        seg('', hold=3.0, cap='none'),
        seg("Tu l'as perdu ? Recule un peu : il revient.", cap_y=1300),
        seg("Ce n'est pas un trucage. Tu viens de trouver ta tache aveugle.", cap_y=1300, emph=['tache', 'aveugle'], sfx=['ding'], music=0.5),
        seg("Au fond de ton œil, il y a un endroit où le nerf optique quitte la rétine pour rejoindre le cerveau.",
            lambda: C([lab_bg(15), EyeDiagram(t_hl=2.5)]), cam='slow_in', trans='zoom'),
        seg("À cet endroit précis, il n'y a aucune cellule capable de capter la lumière. Aucune.", emph=['aucune']),
        seg("Chacun de tes yeux a donc un trou dans son champ de vision.",
            lambda: C([lab_bg(16), EyeDiagram(t_hl=0.0)]), cam='in', trans='cut', emph=['trou']),
        seg("Alors pourquoi tu ne l'as jamais remarqué ?", lambda: C([lab_bg(17), big('POURQUOI ?', size=170)]), cam='in', trans='whip', sfx=['pop'], music=0.6),
        seg("D'abord, tes deux yeux se complètent. Mais surtout… ton cerveau invente ce qui manque.",
            lambda: C([lab_bg(18), Neurons(seed=6)]), cam='slow_in', trans='fade', emph=['invente']),
        seg("Regarde. Même expérience, mais cette fois, le point coupe une ligne.", lambda: CC([BlindSpot(line=True)]), cam='static', trans='flash', cap_y=1300, music=0.35),
        seg("Œil gauche fermé, fixe la croix, et rapproche-toi doucement.", cap='calm', cap_y=1300),
        seg("Le point disparaît… mais la ligne, elle, paraît continue.", cap='calm', cap_y=1300),
        seg('', hold=2.5, cap='none'),
        seg("Ton cerveau a bouché le trou avec ce qui lui semblait logique. Il a littéralement dessiné une partie de l'image.",
            lambda: C([lab_bg(19), big('TON CERVEAU\nA DESSINÉ\nLA LIGNE', size=110)]), cam='in', trans='zoom', emph=['dessiné'], music=0.65),
        seg("La tache aveugle a été découverte vers {1660|seize cent soixante} par le physicien français Edme Mariotte.",
            lambda: C([lab_bg(20), ArchiveCard('Edme Mariotte', '1660', 'Physicien français — découvre la tache aveugle', seed=10)]), cam='slow_in', trans='fade', sfx=['type']),
        seg("Il s'amusait même à faire disparaître la tête des courtisans… à la cour du roi d'Angleterre.", emph=['tête']),
        seg("Alors la prochaine fois que tu es sûr de ce que tu as vu… souviens-toi qu'une partie, ton cerveau l'a inventée.",
            lambda: C([lab_bg(21), big("UNE PARTIE\nDE CE QUE TU VOIS\nEST INVENTÉE", size=92)]), cam='slow_in', trans='whip', music=0.5),
        seg("À quelle distance le point a disparu pour toi ? Réponds en commentaire.", lambda: CC([BlindSpot()]), cam='static', trans='fade', music=0.35, cap_y=1300),
    ])

# ============================================================================= VIDÉO 10 — ombre sur l'échiquier
V10 = dict(
    id='video_10', niche='NICHE_2', theme='psy', speed=1.02,
    title='A et B sont de la même couleur',
    hook_text='A ET B SONT\\NIDENTIQUES', hook_y=230,
    music=dict(style='lofi', prog='lofi_e', key=56, bpm=90, seed=101, start=0.3, db=-26.5),
    segments=[
        seg("Les cases A et B sont exactement de la même couleur.", lambda: CC([Checker()]), cam='static', sfx=['pop'], music=0.35, emph=['même']),
        seg("Oui, je sais. Ça paraît impossible."),
        seg("La case A paraît foncée. La case B paraît claire. C'est évident, non ?", emph=['foncée', 'claire']),
        seg("Pourtant, à l'écran, ce sont exactement les mêmes pixels. Le même gris.", emph=['pixels']),
        seg("Regarde : je relie les deux cases avec une bande de ce même gris.", lambda: CC([Checker(mode='bars', t0=0.6)]), trans='cut', cam='static', sfx=[('reverse', 0.0)], music=0.5),
        seg("La bande ne change jamais de couleur, d'un bout à l'autre.", emph=['jamais']),
        seg("Et maintenant, j'efface tout le reste.", lambda: CC([Checker(mode='isolate', t0=0.7)]), trans='cut', cam='static', sfx=[('whoosh_soft', 0.6)]),
        seg("Voilà. Deux carrés identiques.", emph=['identiques'], sfx=['ding']),
        seg("Je remets l'échiquier… et ton cerveau recommence à te mentir.", lambda: CC([Checker(mode='isolate', t0=0.8, back=True)]), trans='cut', cam='static', emph=['mentir']),
        seg("Même en connaissant la vérité, impossible de les voir pareilles."),
        seg("Cette illusion reprend le principe d'une image célèbre publiée en {1995|mille neuf cent quatre-vingt-quinze} par {Edward Adelson,|Èdouard Adèlsonne,} chercheur au {MIT.|èm-i-té.}",
            lambda: C([lab_bg(22), ArchiveCard('Edward Adelson', '1995', "Chercheur au MIT — l'ombre sur l'échiquier", seed=11)]), cam='slow_in', trans='fade', sfx=['type'], music=0.55),
        seg("Ton cerveau ne mesure pas la lumière qui arrive dans tes yeux. Il essaie de deviner la vraie couleur des objets.",
            lambda: C([lab_bg(23), Neurons(seed=7)]), cam='slow_in', trans='zoom', emph=['deviner']),
        seg("Il repère l'ombre du cylindre et se dit : cette case est à l'ombre, donc en réalité, elle doit être plus claire.",
            lambda: CC([Checker()]), cam='static', trans='fade', emph=['ombre']),
        seg("Alors il corrige, automatiquement. C'est ce qu'on appelle la constance des couleurs.",
            lambda: C([lab_bg(24), big('CONSTANCE\nDES COULEURS', size=120)]), cam='in', trans='whip', sfx=['pop'], music=0.7),
        seg("Sans ce réflexe, une feuille blanche te paraîtrait grise dès qu'elle passe à l'ombre.", lambda: C([PaperShadow()]), cam='slow_in', trans='fade'),
        seg("C'est une compétence vitale… qui devient un piège dès qu'on la teste.", emph=['piège']),
        seg("C'est exactement ce qui s'est passé avec la fameuse robe de {2015|deux mille quinze} : bleue et noire, ou blanche et dorée ?",
            lambda: C([DressSwatches()]), cam='slow_in', trans='whip', music=0.6),
        seg("Selon l'éclairage que ton cerveau imaginait, il corrigeait les couleurs dans un sens… ou dans l'autre."),
        seg("Et toi, à l'époque, tu la voyais de quelle couleur ? Dis-le en commentaire.", lambda: C([DressSwatches()]), cam='in', trans='fade', music=0.35),
    ])

VIDEOS = [V06, V07, V08, V09, V10]
