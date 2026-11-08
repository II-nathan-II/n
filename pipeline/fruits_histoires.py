"""« Les histoires de la Villa » : format court publié entre les épisodes de Villa Vitamine (même compte).

Mini-drames indépendants de 60 à 75 s : une situation de la vie de tous les jours (beauté, héritage, rencard,
téléphone perdu…), de l'humour, un retournement à la fin. Les personnages de la série sont dans le nouveau style
(fruits à corps humain, tenues, décors détaillés : personnages/distribution_nouveau_style.jpg). Sous-titres en
blocs de 2–3 mots avec un mot en jaune. Histoires originales : on ne reprend ni les personnages ni les intrigues
d'autres créateurs.

Les plans suivent la même structure que les épisodes (fruits_series.S) ; une réplique peut être dite hors champ
avec un 3e élément 'off' : ('fanny', "Dis-lui qu'elle a des yeux magnifiques.", 'off').
"""
import fruits_series as FS
from fruits_series import S

STYLE_H = ("Vertical 9:16 shot, hyper-detailed stylized 3D animation like a feature film, cinematic lighting, "
           "humanoid fruit characters with human-proportioned bodies, expressive fruit heads and real clothes, "
           "rich detailed set, shallow depth of field.")

# Nouveau style des personnages de la série (tenues de distribution_nouveau_style.jpg)
LOOK_H = dict(
    kiki="Kiki, a humanoid kiwi man: kiwi head with a bright green face and fuzzy brown skin, yellow sunglasses on top of his head, gold chain, colorful tropical shirt over a white tank top, beige shorts",
    berenice="Bérénice, a humanoid banana woman: tall yellow banana head with a brown stem, white cat-eye sunglasses, pink lips, gold hoop earrings, yellow crop top and yellow high-waisted trousers",
    cyril="Cyril, a humanoid lemon man: bumpy yellow lemon head with a small leaf, thick dark frowning eyebrows, grey t-shirt and blue jeans",
    pepin="Pépin, a humanoid green apple young man: shiny green apple head with a stem and two leaves, round black glasses, blushing cheeks, green polo shirt and beige shorts, slightly shorter than the others",
    fanny="Fanny, a humanoid strawberry woman: red strawberry head with yellow seeds and a green leafy hat, big blue eyes, pink sundress, always holding a pink phone",
    margaux="Margaux, a humanoid mango woman: orange-to-red gradient mango head with a wavy green leaf tuft and a pink hibiscus flower, flowing orange summer dress",
    ananas="Monsieur Ananas, a humanoid pineapple man: golden pineapple head with a tall leafy crown, red bow tie, white tuxedo jacket and black trousers",
)

# Personnages qui n'apparaissent que dans les histoires
EXTRA = dict(
    papi_kiwi=dict(nom='Papi Kiwi', fruit='kiwi', role="le grand-père", color='9C8B6A',
                   look="Papi Kiwi, an elderly humanoid kiwi man: wrinkled kiwi head with greyish fuzzy skin, bushy white mustache and eyebrows, small round glasses, beige cardigan, wooden cane",
                   voix="warm old man's voice, gentle southern French accent"),
    kiki_petit=dict(nom='Petit Kiki', fruit='kiwi', role="Kiki enfant", color='8CD64B',
                    look="little Kiki as a small child: tiny humanoid kiwi boy with a bright green face and fuzzy brown skin, red t-shirt and dungarees",
                    voix="small child's voice"),
    pruneau=dict(nom='Maître Pruneau', fruit='pruneau', role="le notaire", color='5B3A6B',
                 look="Maître Pruneau, a humanoid prune notary: dark purple wrinkled prune head, tiny glasses on the tip of his nose, dark three-piece suit",
                 voix="slow solemn old man's voice"),
    lola=dict(nom='Lola', fruit='litchi', role="l'esthéticienne", color='F4A6C0',
              look="Lola, a humanoid lychee beautician: bumpy pink lychee head with a glossy white face, pink salon uniform, holding a jar of cream",
              voix="soft friendly young woman's voice"),
    raisin=dict(nom='Le serveur', fruit='raisin', role="le serveur", color='7A3E8E',
                look="a humanoid grape waiter: head made of a bunch of purple grapes, black waistcoat, white shirt and bow tie",
                voix="polite formal waiter's voice"),
)
for k, v in EXTRA.items():
    FS.CHARACTERS.setdefault(k, dict(v, replique=''))

SETTINGS_H = dict(
    sdb="a luxurious pink bathroom with a big round mirror ringed by makeup lights",
    institut="an elegant beauty salon with pink reclining chairs, mirrors and shelves of cream jars",
    notaire="a dusty notary office with wooden shelves, stacks of files and a green desk lamp",
    ferme="an old stone farmhouse with a small orchard in the Provence countryside",
    marche="a sunny Provençal village market with colorful fruit stalls and a crowd",
    resto="a romantic seaside restaurant terrace at sunset with candles and fairy lights",
    chambre="a cozy villa bedroom with pink pillows and fairy lights",
)
for k, v in SETTINGS_H.items():
    FS.SETTINGS.setdefault(k, v)


def shot_prompt(shot):
    """Prompt Veo d'un plan d'histoire (nouveau style, dialogue français, hors champ possible par réplique)."""
    parts = [STYLE_H, f"Setting: {FS.SETTINGS[shot['where']]}."]
    for c in shot['who']:
        parts.append((LOOK_H.get(c) or FS.CHARACTERS[c]['look']) + '.')
    parts.append(f"Action: {shot['action']}.")
    if shot['kind'] == 'conf':
        parts.append("Reality-TV confessional framing: the character sits in a pastel pink armchair and faces the camera, medium close-up.")
    for line in shot['lines']:
        who, txt = line[0], line[1]
        c = FS.CHARACTERS[who]
        if len(line) > 2 and line[2] == 'off' or shot.get('off'):
            parts.append(f'{c["nom"]} is not visible; her or his voice is heard off-screen ({c["voix"]}) saying in French: "{txt}"')
        else:
            parts.append(f'{c["nom"]} says in French ({c["voix"]}): "{txt}"')
    parts.append("Lip-synced French dialogue, natural ambience, no background music." if shot['lines']
                 else "No dialogue. Natural ambient sound only, no music.")
    return ' '.join(parts)


def L(who, txt, off=False):
    return (who, txt, 'off') if off else (who, txt)


HISTOIRES = [
    dict(id='histoire_01', num=1, titre="La première tache",
         accroche="Bérénice trouve sa première tache… et panique",
         accroche_ecran=["ELLE A TROUVÉ", "SA 1RE TACHE…"],
         couverture='NICHE_3_VILLA_VITAMINE/couvertures/histoire_01.jpg', sous_titres='duo',
         cold=(2, 0.0, 2.5),
         question="Toi, tu les préfères mûres ou pas mûres ? 🍌",
         suite="Tu veux une autre histoire de la Villa ?",
         shots=[
             S('scene', 7, 'sdb', ['berenice'], "morning, Bérénice hums happily in front of the mirror, then freezes: a tiny brown spot on her yellow cheek",
               [L('berenice', "Coucou ma beauté… Attends. C'est quoi ÇA ?!")]),
             S('react', 4, 'sdb', ['berenice'], "extreme close-up on the tiny brown spot on her cheek, then she screams in horror, dramatic zoom",
               [L('berenice', "NOOOOON !")], sfx='boom'),
             S('scene', 7, 'salon', ['berenice', 'fanny', 'kiki'], "Bérénice bursts into the living room pointing at her cheek, Fanny and Kiki on the sofa lean in to look",
               [L('berenice', "Urgence ! J'ai une tache ! Une TACHE !"), L('fanny', "Oh ma pauvre… ça commence toujours comme ça.")]),
             S('scene', 6, 'salon', ['kiki', 'berenice'], "Kiki leans back on the sofa with a charming smile while Bérénice glares at him",
               [L('kiki', "Franchement ? T'es encore plus belle un peu mûre.")]),
             S('conf', 6, 'conf', ['berenice'], "outraged, takes off her sunglasses",
               [L('berenice', "Mûre ?! J'ai vingt-deux ans ! Bon… vingt-deux jours. Mais quand même !")]),
             S('scene', 7, 'institut', ['berenice', 'lola'], "Bérénice lies in a beauty chair with cucumber slices on her eyes while Lola the lychee beautician spreads cream on her cheek",
               [L('lola', "Crème anti-taches, masque au concombre… et surtout, pas de soleil."), L('berenice', "Pas de soleil ? Dans une villa ?!")]),
             S('scene', 6, 'piscine', ['berenice', 'cyril'], "Bérénice hides under a huge parasol wrapped in towels with a giant hat while everyone else sunbathes; Cyril walks past and stares",
               [L('cyril', "Elle bronze pas. Elle se cache.")]),
             S('scene', 7, 'cuisine', ['berenice'], "at night, Bérénice sneaks into the dark kitchen in a bathrobe and sits inside the open fridge, lit by its cold light",
               [L('berenice', "Le frigo, ça ralentit tout. C'est scientifique.")]),
             S('react', 4, 'cuisine', ['pepin', 'berenice'], "Pépin in pyjamas opens the fridge for a midnight snack, sees Bérénice sitting inside, screams and falls backwards",
               [L('pepin', "AAAAAH !")], sfx='impact', gag='chute'),
             S('scene', 8, 'cuisine', ['kiki', 'berenice', 'fanny'], "morning, Kiki proudly presents a golden banana bread cake to Bérénice, Fanny smiles in the background",
               [L('berenice', "C'est quoi, ça ?"), L('kiki', "Du banana bread. Les meilleures bananes, c'est celles qui ont des taches.")]),
             S('react', 4, 'cuisine', ['berenice', 'fanny'], "Bérénice is touched, slowly smiles and takes off her sunglasses; Fanny films the moment with her pink phone",
               [L('fanny', "Je poste, je poste !")]),
             S('conf', 6, 'conf', ['berenice'], "smiles proudly, then points a finger at the camera",
               [L('berenice', "Une tache, c'est du caractère. Mais deux… on en reparle.")]),
         ]),
    dict(id='histoire_02', num=2, titre="L'héritage de Papi Kiwi",
         accroche="Papi Kiwi leur laisse un trésor… mais pas celui qu'ils croient",
         accroche_ecran=["PAPI A LAISSÉ", "UN TRÉSOR…"],
         couverture='NICHE_3_VILLA_VITAMINE/couvertures/histoire_02.jpg', sous_titres='duo',
         cold=(3, 0.0, 2.5),
         question="Toi, t'aurais planté les graines ou tout revendu ? 🌱",
         suite="Tu veux une autre histoire de la Villa ?",
         shots=[
             S('etab', 4, 'ferme', [], "rainy grey morning over the old farmhouse and its empty orchard, slow push-in, melancholic"),
             S('scene', 7, 'notaire', ['pruneau', 'kiki', 'cyril'], "Maître Pruneau opens a sealed envelope at his desk; Kiki and his cousin Cyril sit in front of him, leaning forward",
               [L('pruneau', "Votre grand-père, Papi Kiwi, vous laisse… son trésor.")]),
             S('react', 4, 'notaire', ['kiki', 'cyril'], "Kiki and Cyril turn to each other with huge greedy eyes, dramatic zoom",
               [L('cyril', "Un trésor ?!")], sfx='boom'),
             S('scene', 7, 'notaire', ['pruneau', 'kiki', 'cyril'], "Maître Pruneau slides a small old wooden box across the desk; Kiki and Cyril both grab it and pull",
               [L('cyril', "Donne ! C'est moi le préféré !"), L('kiki', "T'es venu deux fois en dix ans !")]),
             S('scene', 6, 'notaire', ['kiki', 'cyril'], "they open the box: inside, only a small cloth bag of seeds and a handwritten letter; Kiki holds up the seeds, disappointed",
               [L('kiki', "Des… graines ? C'est ça, le trésor ?")]),
             S('conf', 6, 'conf', ['cyril'], "arms crossed, deeply offended",
               [L('cyril', "Trente ans à lui rendre visite… enfin, deux fois. Et j'ai des graines.")]),
             S('scene', 8, 'ferme', ['papi_kiwi', 'kiki_petit'], "warm golden flashback: Papi Kiwi kneels in the sunny orchard and plants a seed with little Kiki, ruffling his head",
               [L('papi_kiwi', "Un jour, tout ça sera à toi, mon petit. Faut juste être patient.")]),
             S('scene', 7, 'ferme', ['kiki'], "present day in the rain, Kiki kneels alone in the old orchard and carefully plants the seeds, emotional",
               [L('kiki', "D'accord, Papi. Je vais être patient.")]),
             S('etab', 4, 'ferme', [], "time-lapse: seasons pass over the orchard, little seedlings grow into a lush orchard full of fuzzy brown fruit, sunshine"),
             S('scene', 8, 'marche', ['kiki', 'cyril'], "Kiki runs a busy market stall full of baskets of kiwis, customers lining up; Cyril arrives sheepishly, hands in his pockets",
               [L('cyril', "Euh… cousin… t'aurais pas un petit job pour moi ?"), L('kiki', "Bien sûr. Tu commences par… arroser.")]),
             S('react', 4, 'ferme', ['cyril'], "wide shot: Cyril stands in a gigantic orchard holding a tiny watering can and sighs", sfx='whoosh'),
             S('scene', 6, 'ferme', ['kiki'], "Kiki stands under the trees at sunset holding an old framed photo of Papi Kiwi, smiling with wet eyes",
               [L('kiki', "Merci, Papi. Le vrai trésor, c'était la patience… et les kiwis.")]),
         ]),
    dict(id='histoire_03', num=3, titre="Le rencard acide",
         accroche="Cyril est trop acide pour draguer… sauf que",
         accroche_ecran=["IL EST TROP ACIDE", "POUR DRAGUER ?"],
         couverture='NICHE_3_VILLA_VITAMINE/couvertures/histoire_03.jpg', sous_titres='duo',
         cold=(5, 0.0, 2.5),
         question="Ton pire rencard, c'était quoi ? 😅",
         suite="Tu veux la suite du rencard ?",
         shots=[
             S('scene', 7, 'salon', ['cyril', 'fanny'], "Cyril practices a compliment stiffly in front of a mirror; behind him Fanny facepalms",
               [L('cyril', "T'es… pas moche."), L('fanny', "Cyril. Non.")]),
             S('scene', 7, 'salon', ['fanny', 'cyril'], "Fanny puts a tiny earpiece in Cyril's ear with a conspiratorial smile",
               [L('fanny', "Ce soir, je te parle à l'oreille. Tu répètes TOUT ce que je dis."), L('cyril', "Tout ?")]),
             S('etab', 4, 'resto', [], "golden sunset over the sea, candles flickering on the restaurant terrace"),
             S('scene', 7, 'resto', ['margaux', 'cyril'], "Margaux sits elegantly at a candlelit table; Cyril sits down stiffly in front of her",
               [L('margaux', "Alors, Cyril… parle-moi de toi.")]),
             S('scene', 6, 'resto', ['cyril', 'margaux'], "Cyril listens to the voice in his earpiece, then speaks to Margaux with a blank face",
               [L('fanny', "Dis-lui qu'elle a des yeux magnifiques.", True), L('cyril', "Tu as des yeux… acceptables.")]),
             S('react', 4, 'resto', ['fanny'], "Fanny hides behind a big potted plant at the next table, phone in hand, and facepalms hard"),
             S('scene', 7, 'resto', ['cyril', 'raisin'], "the grape waiter arrives with a notepad; Cyril orders very seriously",
               [L('fanny', "Commande un dessert, un truc sucré !", True), L('cyril', "Deux citrons pressés. Sans sucre.")]),
             S('react', 4, 'resto', ['fanny'], "behind the plant, Fanny falls off her chair in despair", sfx='impact'),
             S('scene', 8, 'resto', ['margaux', 'cyril'], "the drinks arrive; Margaux sips the lemonade, her eyes light up and she smiles",
               [L('margaux', "Sans sucre ?… Enfin quelqu'un qui me comprend.")]),
             S('scene', 6, 'resto', ['cyril', 'margaux'], "Cyril, surprised, almost smiles for the first time; Margaux laughs softly",
               [L('cyril', "Toi aussi, tu trouves que le monde est trop sucré ?"), L('margaux', "Beaucoup trop.")]),
             S('react', 4, 'resto', ['fanny'], "Fanny pops her head out of the plant, mouth wide open in shock, and drops her phone", sfx='boom'),
             S('conf', 6, 'conf', ['cyril'], "arms crossed but with a tiny smile",
               [L('cyril', "C'est pas pour être acide… mais j'ai un deuxième rencard.")]),
         ]),
    dict(id='histoire_04', num=4, titre="24 h sans téléphone",
         accroche="Fanny perd son téléphone… et découvre tous les secrets de la villa",
         accroche_ecran=["ELLE A PERDU", "SON TÉLÉPHONE…"],
         couverture='NICHE_3_VILLA_VITAMINE/couvertures/histoire_04.jpg', sous_titres='duo',
         cold=(2, 0.5, 2.5),
         question="Toi, tu tiendrais 24 h sans ton téléphone ? 📵",
         suite="Tu veux une autre histoire de la Villa ?",
         shots=[
             S('scene', 6, 'chambre', ['fanny'], "Fanny wakes up and frantically pats the bed and pillows looking for something",
               [L('fanny', "Mon téléphone… Où est mon téléphone ?")]),
             S('scene', 7, 'salon', ['fanny', 'pepin'], "Fanny turns the living room upside down, cushions flying everywhere; Pépin watches from the doorway",
               [L('pepin', "T'as regardé sous le canapé ?"), L('fanny', "J'ai regardé sous la VILLA, Pépin !")]),
             S('conf', 6, 'conf', ['fanny'], "trembling, hugging a cushion",
               [L('fanny', "Sans téléphone, je sais rien. Je suis aveugle. Je suis… une fraise des bois.")]),
             S('scene', 7, 'cuisine', ['fanny', 'ananas'], "Fanny sits awkwardly next to Monsieur Ananas who is drinking his morning coffee",
               [L('fanny', "Alors… ça va, vous ?"), L('ananas', "Personne ne m'a jamais demandé ça.")]),
             S('scene', 8, 'cuisine', ['ananas', 'fanny'], "Monsieur Ananas looks into his coffee, emotional; Fanny listens, touched",
               [L('ananas', "Présenter une émission, c'est lourd. Parfois, je parle à mes cartes.")]),
             S('scene', 7, 'jardin', ['pepin', 'fanny'], "Pépin and Fanny sit on a garden bench under string lights",
               [L('pepin', "Je tombe tout le temps parce que je regarde les gens au lieu de regarder où je marche."), L('fanny', "C'est mignon, Pépin.")]),
             S('scene', 7, 'piscine', ['berenice', 'fanny'], "on sunbeds by the pool, Bérénice leans toward Fanny and whispers a secret behind her hand",
               [L('berenice', "Tu le dis à personne. Je dors avec une veilleuse."), L('fanny', "Promis.")]),
             S('conf', 6, 'conf', ['fanny'], "amazed, eyes shining",
               [L('fanny', "En une journée, j'ai appris plus de secrets qu'en un an de téléphone. Et je les ai gardés.")]),
             S('scene', 7, 'chambre', ['fanny'], "at night Fanny takes off her leafy hat before bed and her pink phone falls out of it onto the floor; she stares at it, speechless",
               [L('fanny', "…Il était dans mon chapeau.")], sfx='boom'),
             S('react', 4, 'chambre', ['fanny'], "close-up: the pink phone on the floor lights up and buzzes nonstop with endless notifications, Fanny's face lit by the screen"),
             S('scene', 6, 'chambre', ['fanny'], "Fanny picks up the phone, looks at it… then puts it in a drawer, closes it and smiles",
               [L('fanny', "Demain. Ce soir, j'ai mieux à faire : parler à quelqu'un.")]),
             S('react', 4, 'salon', ['kiki', 'pepin', 'berenice'], "Kiki, Pépin and Bérénice in pyjamas peek through the doorway, stunned",
               [L('kiki', "Elle est malade ?")]),
         ]),
]


def jobs():
    """(histoire, n° de plan, prompt Veo, durée) pour toutes les histoires."""
    return [(h['id'], i + 1, shot_prompt(sh), sh['dur']) for h in HISTOIRES for i, sh in enumerate(h['shots'])]


if __name__ == '__main__':
    for h in HISTOIRES:
        d = sum(s['dur'] for s in h['shots'])
        print(f"{h['id']}  {h['titre']:<26} {len(h['shots'])} plans  {d} s  ≈ {0.72 * len(h['shots']):.1f} crédits Ace Data")
