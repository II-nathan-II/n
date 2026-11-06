"""Niche 3 et 4 : « Villa Vitamine » (télé-réalité de fruits, saison 1) et « Cristal ASMR ».

Source unique pour : les prompts de génération (Higgsfield / Wan 3.0, son natif), le montage
(`ai_assemble.py`) et les documents (`fruits_docs.py`). Personnages et univers originaux : on
reprend le genre « télé-réalité dans une villa du Sud », pas une émission ni des personnes réelles.
"""

MODEL = dict(model='wan3_0', resolution='720p', aspect_ratio='9:16', generate_audio=True)
CREDITS_PER_SECOND = {'480p': 1.0, '720p': 1.75, '1080p': 3.5}   # Wan 3.0, relevé le 6 novembre 2026
RETAKE = 1.3                                                    # ~30 % de plans à refaire

# ───────────────────────────── VILLA VITAMINE ─────────────────────────────

STYLE = ("Vertical 9:16 shot, bright colorful stylized 3D animation like a family animated feature film, "
         "sunny Mediterranean light, shallow depth of field, expressive cartoon faces, family-friendly reality-TV parody.")

SETTINGS = {
    'villa':   "a luxury white villa on the Mediterranean coast of southern France, turquoise pool, palm trees, cicadas, blue sky",
    'piscine': "the edge of a turquoise villa pool with sunbeds, palm trees and sparkling water",
    'conf':    "a reality-TV confessional corner: pastel pink armchair with pink and mint cushions, the villa pool softly blurred behind",
    'cuisine': "a bright open villa kitchen with fruit bowls, a blender and a sea view",
    'salon':   "a sunny villa living room with white sofas, plants and big windows on the sea",
    'jardin':  "the villa garden with olive trees, lavender and string lights",
    'nuit':    "the villa pool at night with lanterns, fairy lights and a starry sky",
    'soiree':  "an all-white night pool party at the villa with fairy lights, balloons and a DJ table",
    'portail': "the villa gate at night under a street lamp, gravel path",
    'tropical': "a new tropical island villa at sunset with huts on stilts and a lagoon",
}

CHARACTERS = {
    'kiki': dict(nom='Kiki', fruit='kiwi', role='le tombeur', color='8CD64B',
                 look="Kiki, a kiwi fruit character: fuzzy brown oval body, big brown eyes, small arms and legs, tiny sunglasses pushed on top of his head, thin gold chain, confident smirk",
                 voix="young man's voice, sunny southern French accent, cocky and charming",
                 replique="« Moi, jaloux ? Jamais. »"),
    'berenice': dict(nom='Bérénice', fruit='banane', role='la reine du drama', color='FFE135',
                 look="Bérénice, a banana character: bright yellow curved body, long eyelashes, glossy pink nails, small gold hoop earrings, diva attitude",
                 voix="young woman's voice, southern French accent, dramatic and sassy",
                 replique="« Je suis pas venue pour me faire des amis. »"),
    'cyril': dict(nom='Cyril', fruit='citron', role="l'acide", color='F4F14A',
                 look="Cyril, a lemon character: bright yellow round lemon body, thick frowning eyebrows, arms crossed, sour skeptical face",
                 voix="man's voice, dry and sarcastic, slightly nasal",
                 replique="« C'est pas pour être acide, mais… »"),
    'pepin': dict(nom='Pépin', fruit='pomme', role='le timide', color='B6F36A',
                 look="Pépin, a small green apple character: shiny green body with a leaf on top, round glasses, shy smile, blushes easily",
                 voix="soft shy young man's voice, a bit clumsy",
                 replique="« Ça va, ça va ! Je suis juste… tombé dans les pommes. »"),
    'margaux': dict(nom='Margaux', fruit='mangue', role='la nouvelle', color='FF9A3C',
                 look="Margaux, a mango character: orange-to-red gradient mango body, a wavy green leaf like a hair tuft, a hibiscus flower behind the ear, mysterious confident look",
                 voix="calm confident young woman's voice, slightly exotic accent",
                 replique="« Oui, je suis exotique. »"),
    'fanny': dict(nom='Fanny', fruit='fraise', role='la commère', color='FF4D6D',
                 look="Fanny, a strawberry character: red body with yellow seeds, green leafy hat, big gossip smile, always holding a pink phone",
                 voix="bubbly fast-talking young woman's voice, southern French accent",
                 replique="« Vous savez pas la nouvelle ? »"),
    'coco': dict(nom='Coco', fruit='noix de coco', role="l'ex", color='C9A27E',
                 look="Coco, a coconut character: hairy brown round shell body, dark sunglasses, white tank top, bodybuilder pose",
                 voix="deep slow man's voice, overconfident",
                 replique="« Dur à l'extérieur… dur à l'intérieur aussi. »"),
    'ananas': dict(nom='Monsieur Ananas', fruit='ananas', role='le présentateur', color='FFC93C',
                 look="Monsieur Ananas, a pineapple TV host character: golden pineapple body, tall green leafy crown, red bow tie, holding presenter cards",
                 voix="deep theatrical TV host voice",
                 replique="« Le verger a parlé. »"),
}


def S(kind, dur, where, who, action, lines=(), text=None, sfx=None, off=False):
    """Un plan généré. kind : etab (ambiance), scene, conf (confessionnal), host, react (réaction muette).
    off=True : les répliques sont dites en voix off (personnage hors champ)."""
    return dict(kind=kind, dur=dur, where=where, who=list(who), action=action, lines=list(lines), text=text, sfx=sfx, off=off)


EPISODES = [
    dict(id='episode_01', num=1, titre="Bienvenue à la Villa",
         accroche="Ils ne savent pas encore ce qui les attend…",
         suite="Épisode 2 : la nouvelle arrive",
         shots=[
             S('etab', 6, 'villa', [], "Slow aerial drone shot gliding over the villa and the pool, sparkling water, no characters"),
             S('host', 8, 'piscine', ['ananas'], "stands at the edge of the pool, opens his arms wide to the camera",
               [('ananas', "Bienvenue à la Villa Vitamine ! Six fruits, un été… et une seule règle : rester frais !")]),
             S('scene', 7, 'villa', ['kiki'], "arrives at the villa entrance rolling a suitcase, takes off his sunglasses and looks around amazed",
               [('kiki', "La villa, le soleil, la piscine… Franchement, j'ai la pêche !")]),
             S('conf', 8, 'conf', ['kiki'], "sits in the armchair, winks at the camera",
               [('kiki', "Moi c'est Kiki. Les filles disent que je suis tout doux à l'extérieur… et sucré à l'intérieur.")]),
             S('scene', 7, 'villa', ['berenice'], "walks down the villa stairs like a runway, sunglasses on, hand on hip",
               [('berenice', "Coucou la villa ! Votre reine est arrivée.")]),
             S('conf', 7, 'conf', ['berenice'], "sits with legs crossed, flips her imaginary hair",
               [('berenice', "Je suis pas venue pour me faire des amis. Je suis venue pour briller.")]),
             S('scene', 6, 'salon', ['cyril'], "walks in with arms crossed, looks at the decoration with disgust",
               [('cyril', "Encore une villa pleine de fruits trop mûrs…")]),
             S('conf', 8, 'conf', ['cyril'], "sits stiffly, raises one eyebrow",
               [('cyril', "C'est pas pour être acide, mais je donne trois jours à Kiki avant de se faire presser.")]),
             S('scene', 7, 'salon', ['pepin'], "trips over a suitcase and falls onto a big cushion, then gets up embarrassed",
               [('pepin', "Ça va, ça va ! Je suis juste… tombé dans les pommes.")], sfx='impact'),
             S('scene', 8, 'cuisine', ['fanny', 'kiki', 'berenice'], "Fanny runs into the kitchen waving her pink phone while Kiki and Bérénice turn around",
               [('fanny', "Vous savez pas la nouvelle ? Demain… une nouvelle arrive à la villa !")]),
             S('react', 5, 'cuisine', ['kiki', 'berenice'], "dramatic slow push-in: Kiki raises an eyebrow with a smile, Bérénice drops her glass of juice in shock", sfx='boom'),
             S('etab', 7, 'portail', [], "a mysterious suitcase with a mango sticker waits alone at the gate, a feminine silhouette in the shadows, suspense",
               [('ananas', "Et elle… elle va tout changer.")], sfx='riser', off=True),
         ]),
    dict(id='episode_02', num=2, titre="La nouvelle",
         accroche="Quand la nouvelle arrive, Kiki perd ses lunettes…",
         suite="Épisode 3 : clash à la piscine",
         shots=[
             S('etab', 5, 'villa', [], "Morning at the villa, sun rising over the pool, birds, no characters"),
             S('scene', 7, 'cuisine', ['fanny', 'pepin', 'cyril'], "Fanny bursts into the breakfast room in panic, Pépin spills his cereal",
               [('fanny', "Elle arrive ! Elle arrive ! Tout le monde à sa place !")]),
             S('scene', 8, 'piscine', ['margaux'], "walks along the pool in slow motion, wind in her leaf, everyone turns",
               [('margaux', "Bonjour tout le monde… Moi c'est Margaux. Et oui, je suis exotique.")]),
             S('react', 5, 'piscine', ['kiki'], "slow motion: Kiki's jaw drops and his sunglasses slide off his head into the pool", sfx='whoosh'),
             S('conf', 7, 'conf', ['kiki'], "fans himself with his hand, dreamy eyes",
               [('kiki', "Margaux… c'est pas un fruit, c'est un dessert.")]),
             S('conf', 8, 'conf', ['berenice'], "fake smile that slowly turns into a glare",
               [('berenice', "Elle est mignonne… pour une mangue. Mais ici, la reine, c'est moi.")]),
             S('scene', 8, 'piscine', ['cyril', 'pepin'], "lying on sunbeds side by side, Cyril with a cocktail, Pépin with sunscreen on his nose",
               [('cyril', "Tu vas voir, tout ça va finir en compote."), ('pepin', "Moi, j'aime bien la compote…")]),
             S('scene', 8, 'cuisine', ['kiki', 'margaux', 'pepin'], "Kiki shows off at the blender for Margaux, Pépin washes dishes in the background",
               [('kiki', "Je te prépare un smoothie ?"), ('margaux', "Seulement s'il est sans pépins.")]),
             S('conf', 6, 'conf', ['pepin'], "looks offended, pushes up his glasses",
               [('pepin', "Sans pépins ? Mais… j'ai rien fait, moi !")]),
             S('scene', 8, 'jardin', ['kiki', 'fanny', 'berenice'], "Kiki talks to Fanny by the hedge while Bérénice hides behind a big plant, listening",
               [('kiki', "Bérénice, elle est cool… mais Margaux, c'est autre chose.")]),
             S('react', 5, 'jardin', ['berenice'], "extreme close-up on Bérénice behind the leaves, she gasps, one eye twitches", [('berenice', "Autre chose ?!")], sfx='boom'),
             S('host', 7, 'nuit', ['ananas'], "leans toward the camera with a mysterious smile",
               [('ananas', "Demain, à la villa… ça va glisser. Et pas que sur les peaux de banane.")], sfx='riser'),
         ]),
    dict(id='episode_03', num=3, titre="Clash à la piscine",
         accroche="Bérénice contre Margaux : le transat de la discorde",
         suite="Épisode 4 : le jeu de la vérité",
         shots=[
             S('etab', 5, 'piscine', [], "Hot midday at the pool, heat haze, one empty pink sunbed in the spotlight, no characters"),
             S('scene', 9, 'piscine', ['berenice', 'margaux'], "Bérénice stands over Margaux who is lying on the pink sunbed",
               [('berenice', "Toi, la mangue, tu te calmes. Ici, c'est mon transat."), ('margaux', "Ton transat ? Il y a ton nom dessus ?")]),
             S('react', 5, 'piscine', ['kiki', 'pepin', 'fanny', 'cyril'], "the other fruits gasp together with hands on their mouths", sfx='boom'),
             S('conf', 7, 'conf', ['margaux'], "calm, adjusts the flower behind her ear",
               [('margaux', "Elle croit que je vais me laisser presser ? Je suis pas un jus de fruit, moi.")]),
             S('scene', 8, 'jardin', ['fanny', 'cyril'], "Fanny whispers in Cyril's ear behind an olive tree",
               [('fanny', "Il paraît que Margaux est déjà sortie avec un ananas…"), ('cyril', "Intéressant. Très intéressant.")]),
             S('conf', 7, 'conf', ['cyril'], "rubs his hands with a wicked smile",
               [('cyril', "Quand ça clashe, moi je suis comme un citron : je pique là où ça fait mal.")]),
             S('scene', 8, 'piscine', ['pepin', 'berenice', 'margaux'], "Pépin steps between the two girls, arms raised to calm them",
               [('pepin', "Les filles ! On peut couper la poire en deux ?"), ('berenice', "Il n'y a pas de poire ici !")]),
             S('scene', 6, 'piscine', ['pepin'], "Pépin steps back onto a banana peel, slips in slow motion and falls into the pool with a huge splash", sfx='impact'),
             S('react', 5, 'piscine', ['kiki', 'fanny', 'berenice'], "everyone bursts out laughing, Bérénice tries hard not to laugh"),
             S('conf', 7, 'conf', ['berenice'], "looks away innocently, whistles",
               [('berenice', "La peau de banane, c'était pas moi. Enfin… je crois.")]),
             S('scene', 7, 'piscine', ['kiki', 'pepin'], "Kiki wraps a towel around a soaked, shivering Pépin",
               [('kiki', "Respire, mon Pépin. Ça va aller.")]),
             S('host', 8, 'nuit', ['ananas'], "holds a stack of cards under a single spotlight",
               [('ananas', "Ce soir… c'est le jeu de la vérité. Et personne ne pourra mentir.")], sfx='riser'),
         ]),
    dict(id='episode_04', num=4, titre="Le jeu de la vérité",
         accroche="Kiki doit choisir : Bérénice ou Margaux ?",
         suite="Épisode 5 : le retour de l'ex",
         shots=[
             S('etab', 5, 'nuit', [], "Night, a circle of chairs around a fire pit by the pool, lanterns, suspense, no characters"),
             S('host', 8, 'nuit', ['ananas'], "stands in the middle of the circle, shuffling cards",
               [('ananas', "Je pose une question, vous répondez. Et la vérité… finit toujours par sortir du jus.")]),
             S('scene', 8, 'nuit', ['ananas', 'cyril'], "the host points a card at Cyril, who thinks hard",
               [('ananas', "Cyril, as-tu déjà dit du bien de quelqu'un ?"), ('cyril', "Une fois. Et je l'ai regretté.")]),
             S('scene', 8, 'nuit', ['ananas', 'pepin'], "the host turns to Pépin, who turns bright red",
               [('ananas', "Pépin, es-tu amoureux ?"), ('pepin', "Peut-être… de quelqu'un qui a des pépins, elle aussi…")]),
             S('react', 5, 'nuit', ['fanny'], "Fanny blushes and hides her face behind her pink phone"),
             S('conf', 7, 'conf', ['fanny'], "squeals, kicks her little legs",
               [('fanny', "Des pépins… comme moi ? Oh non. Oh si. Oh non !")]),
             S('scene', 9, 'nuit', ['ananas', 'kiki'], "close-up on Kiki sweating under the spotlight",
               [('ananas', "Kiki… Bérénice ou Margaux ?"), ('kiki', "Euh… très bonne question… Bérénice… euh… Margaux…")]),
             S('react', 5, 'nuit', ['berenice', 'margaux'], "Bérénice and Margaux slowly turn their heads toward Kiki, eyes narrowed", sfx='boom'),
             S('conf', 7, 'conf', ['kiki'], "shrugs with a nervous laugh",
               [('kiki', "Ma réponse ? Je suis mi-figue, mi-raisin. Voilà.")]),
             S('conf', 7, 'conf', ['berenice'], "furious, fanning herself",
               [('berenice', "Il hésite ? Il HÉSITE ? Moi, on m'hésite pas !")]),
             S('scene', 5, 'nuit', ['kiki', 'berenice', 'margaux', 'pepin', 'fanny', 'cyril'], "suddenly all the lights go out, darkness, the fruits scream, a phone flashlight sweeps around", sfx='impact'),
             S('etab', 7, 'nuit', ['coco'], "in the darkness, a big silhouette lit from below by a phone screen, only sunglasses visible",
               [('coco', "Salut Bérénice… Tu m'as manqué.")], sfx='riser'),
         ]),
    dict(id='episode_05', num=5, titre="Le retour de l'ex",
         accroche="L'ex de Bérénice débarque… et il n'est pas venu pour elle",
         suite="Épisode 6 : le complot",
         shots=[
             S('etab', 5, 'villa', [], "Morning at the villa, a big shadow appears on the pool water, no characters visible"),
             S('scene', 8, 'piscine', ['coco'], "flexes his arms by the pool, the sunbeds shake",
               [('coco', "Salut la villa. Moi c'est Coco. Dur à l'extérieur… dur à l'intérieur aussi.")]),
             S('react', 5, 'piscine', ['berenice'], "Bérénice spits out her juice in surprise", sfx='whoosh'),
             S('conf', 7, 'conf', ['berenice'], "rolls her eyes",
               [('berenice', "Coco, c'est mon ex. On s'est séparés parce qu'il était… impossible à ouvrir.")]),
             S('scene', 9, 'piscine', ['coco', 'kiki'], "Coco and Kiki face to face, Coco twice as big",
               [('coco', "Alors c'est toi, le petit poilu ?"), ('kiki', "Petit ? Je fais un mètre… de charisme.")]),
             S('conf', 7, 'conf', ['kiki'], "rolls his eyes with attitude, then sighs",
               [('kiki', "Moi, jaloux ? Jamais. … Bon. Un petit peu.")]),
             S('scene', 7, 'jardin', ['fanny'], "Fanny films herself with her pink phone like a live stream",
               [('fanny', "Info exclusive : l'ex de Bérénice est là, et il a des biceps de noix de coco !")]),
             S('conf', 6, 'conf', ['cyril'], "sips a lemonade, satisfied",
               [('cyril', "Une noix de coco chez des fruits tout tendres ? Ça va faire des dégâts.")]),
             S('scene', 8, 'nuit', ['coco', 'berenice'], "at the pool bar, Coco leans toward Bérénice",
               [('berenice', "Coco, si t'es revenu pour moi, c'est non."), ('coco', "Pour toi ? Non…")]),
             S('react', 4, 'nuit', ['berenice'], "Bérénice frozen, confused, a cricket chirps"),
             S('scene', 8, 'nuit', ['coco', 'margaux'], "Coco turns slowly and points at Margaux",
               [('coco', "Je suis revenu pour Margaux."), ('margaux', "Pardon ?!")], sfx='boom'),
             S('host', 7, 'nuit', ['ananas'], "shakes a cocktail shaker, smiling",
               [('ananas', "Une noix de coco, une mangue, un kiwi… Ça sent le cocktail explosif.")], sfx='riser'),
         ]),
    dict(id='episode_06', num=6, titre="Le complot",
         accroche="Cyril prépare un piège… et Pépin a tout vu",
         suite="Épisode 7 : la Soirée Blanche",
         shots=[
             S('etab', 5, 'jardin', [], "Night garden, crickets, two small shadows behind a hedge, no faces"),
             S('scene', 9, 'jardin', ['cyril', 'fanny'], "Cyril and Fanny plotting behind the hedge with a flashlight",
               [('cyril', "Si Kiki part, Bérénice pleure."), ('fanny', "Et une Bérénice qui pleure… ça fait des vues !")]),
             S('conf', 6, 'conf', ['fanny'], "innocent smile",
               [('fanny', "Je suis pas méchante. Je suis… journaliste.")]),
             S('scene', 8, 'salon', ['cyril'], "in the dark living room, Cyril types on a phone with a green kiwi case, evil grin lit by the screen",
               [('cyril', "« Margaux, rejoins-moi à minuit au jardin. Kiki. » Parfait.")]),
             S('scene', 5, 'salon', ['margaux'], "Margaux reads a message on her phone and smiles softly"),
             S('conf', 7, 'conf', ['margaux'], "dreamy",
               [('margaux', "Un rendez-vous à minuit ? Kiki est plus romantique que je pensais.")]),
             S('scene', 8, 'salon', ['pepin', 'cyril'], "Pépin turns on the light and catches Cyril holding the green phone",
               [('pepin', "Cyril ? C'est le téléphone de Kiki ?"), ('cyril', "Hein ? Non. C'est une calculatrice.")]),
             S('conf', 7, 'conf', ['pepin'], "unimpressed, arms crossed",
               [('pepin', "Une calculatrice… avec la photo de Kiki en fond d'écran. Il me prend pour une poire.")]),
             S('scene', 6, 'jardin', ['margaux'], "midnight, Margaux waits alone under the string lights, moonlight, wind"),
             S('scene', 8, 'jardin', ['berenice', 'margaux'], "Bérénice appears behind Margaux with a flashlight under her face",
               [('berenice', "Tiens, tiens… Tu attends quelqu'un, la mangue ?")], sfx='boom'),
             S('react', 4, 'jardin', ['margaux'], "Margaux jumps, shocked"),
             S('host', 7, 'nuit', ['ananas'], "in front of a giant white cake, smiling mysteriously",
               [('ananas', "Demain soir, c'est la Soirée Blanche. Et quelqu'un va finir… dans la piscine.")], sfx='riser'),
         ]),
    dict(id='episode_07', num=7, titre="La Soirée Blanche",
         accroche="Battle de danse, premier slow… et un gâteau dans la piscine",
         suite="Épisode 8 : l'enquête",
         shots=[
             S('etab', 5, 'soiree', [], "All-white party by the pool, fairy lights, balloons, music, wide shot"),
             S('scene', 8, 'soiree', ['coco', 'kiki'], "dance battle in a circle, Coco flexes, Kiki does a spin",
               [('coco', "Battle de danse, le poilu !"), ('kiki', "Attention, ça va secouer le cocotier !")]),
             S('react', 5, 'soiree', ['fanny', 'pepin', 'margaux', 'cyril'], "the crowd of fruits cheers and jumps"),
             S('scene', 9, 'soiree', ['pepin', 'fanny'], "Pépin shyly offers his hand to Fanny under the fairy lights",
               [('pepin', "Fanny… tu veux danser avec moi ?"), ('fanny', "Pépin… ça fait trois épisodes que j'attends ça.")]),
             S('conf', 7, 'conf', ['pepin'], "beaming with happiness",
               [('pepin', "J'ai pas glissé, j'ai rien cassé… C'est le plus beau jour de ma vie.")]),
             S('scene', 9, 'nuit', ['berenice', 'kiki'], "on the terrace, Bérénice confronts Kiki",
               [('berenice', "Le message de minuit, c'était toi ?"), ('kiki', "Quel message ? Je te jure sur ma pulpe !")]),
             S('conf', 7, 'conf', ['berenice'], "annoyed but smiling",
               [('berenice', "Il a l'air sincère… Et quand il est sincère, il est mignon. C'est énervant.")]),
             S('etab', 5, 'soiree', [], "a giant white three-tier cake on a table at the edge of the pool, close-up"),
             S('etab', 5, 'soiree', [], "a big shadowy figure pushes the cake into the pool, huge splash, face not visible", sfx='impact'),
             S('react', 5, 'soiree', ['berenice', 'margaux', 'fanny'], "everyone screams with hands on their heads", [('fanny', "Le gâteau !")]),
             S('conf', 6, 'conf', ['cyril'], "too innocent",
               [('cyril', "Moi j'ai rien vu. J'étais en train de… compter mes zestes.")]),
             S('host', 7, 'piscine', ['ananas'], "holds a dripping cake topper, staring into the camera",
               [('ananas', "Qui a fait ça ? Demain… on mène l'enquête.")], sfx='riser'),
         ]),
    dict(id='episode_08', num=8, titre="L'enquête",
         accroche="Qui a jeté le gâteau ? Fanny a tout filmé",
         suite="Épisode 9 : les nominations",
         shots=[
             S('etab', 5, 'piscine', [], "Morning, cake crumbs floating in the pool, a lonely cherry, no characters"),
             S('host', 8, 'salon', ['ananas'], "wearing a detective hat, holding a magnifying glass",
               [('ananas', "Personne ne quitte la villa tant que le coupable n'a pas parlé.")]),
             S('scene', 8, 'salon', ['berenice', 'cyril'], "everyone points at Cyril, who throws up his arms",
               [('berenice', "C'est forcément Cyril !"), ('cyril', "Moi ? Je suis acide, pas criminel !")]),
             S('conf', 7, 'conf', ['cyril'], "dramatic sigh",
               [('cyril', "Pour une fois que je suis innocent, personne ne me croit. L'histoire de ma vie.")]),
             S('scene', 7, 'salon', ['fanny'], "Fanny jumps on the sofa, holding up her pink phone",
               [('fanny', "Attendez ! J'ai tout filmé pendant la soirée !")]),
             S('react', 5, 'salon', ['kiki', 'berenice', 'margaux', 'pepin'], "everyone huddles around the phone screen, faces lit by it"),
             S('react', 5, 'salon', ['coco'], "slow zoom on Coco, who swallows hard and sweats", sfx='boom'),
             S('scene', 8, 'salon', ['coco'], "Coco raises his hands and confesses",
               [('coco', "Ok, ok… C'était moi. Je voulais gâcher la soirée de Kiki.")]),
             S('conf', 7, 'conf', ['kiki'], "furious but funny",
               [('kiki', "Il a jeté mon gâteau à la piscine. Lui, il va finir en lait de coco.")]),
             S('scene', 9, 'salon', ['margaux', 'berenice'], "Margaux turns to Bérénice",
               [('margaux', "Et le faux message, c'était Cyril. Pépin l'a vu."), ('berenice', "Donc… Kiki ne m'a pas trahie ?")]),
             S('react', 5, 'salon', ['berenice', 'kiki'], "Bérénice looks at Kiki and smiles softly, he smiles back, romantic music"),
             S('host', 7, 'nuit', ['ananas'], "under red lights, dead serious",
               [('ananas', "Ce soir… les nominations. Et c'est VOUS qui allez décider.")], sfx='riser'),
         ]),
    dict(id='episode_09', num=9, titre="Les nominations",
         accroche="Coco ou Cyril : c'est toi qui décides",
         suite="Épisode 10 : le verdict (selon vos votes)",
         vote="Coco ou Cyril ? Vote en commentaire !",
         shots=[
             S('etab', 5, 'nuit', [], "Night, dramatic red lights around the pool, smoke, tension, no characters"),
             S('host', 8, 'nuit', ['ananas'], "stands in front of all the fruits lined up",
               [('ananas', "Les fruits ont voté. Deux nominés ce soir… et un seul restera.")]),
             S('react', 5, 'nuit', ['kiki', 'berenice', 'margaux', 'pepin', 'fanny', 'cyril', 'coco'], "quick nervous close-ups of the fruits, heartbeat"),
             S('host', 6, 'nuit', ['ananas'], "opens an envelope", [('ananas', "Premier nominé… Coco.")], sfx='boom'),
             S('conf', 7, 'conf', ['coco'], "shrugs",
               [('coco', "Normal. J'ai jeté un gâteau dans une piscine. Même moi, je me nommerais.")]),
             S('host', 7, 'nuit', ['ananas'], "opens a second envelope, surprised",
               [('ananas', "Deuxième nominé… et c'est une surprise… Cyril.")], sfx='boom'),
             S('conf', 7, 'conf', ['cyril'], "bitter",
               [('cyril', "Évidemment. Quand t'es le citron de l'histoire, on te presse jusqu'au bout.")]),
             S('scene', 9, 'nuit', ['kiki', 'berenice'], "Kiki and Bérénice on a sunbed under the stars",
               [('kiki', "Quoi qu'il arrive, c'est toi."), ('berenice', "Mi-figue, mi-raisin ?"), ('kiki', "Non. Cent pour cent banane.")]),
             S('react', 4, 'nuit', ['fanny', 'pepin'], "Fanny and Pépin watching from afar, melting with emotion"),
             S('scene', 7, 'nuit', ['margaux'], "Margaux alone on the terrace looking at the sea",
               [('margaux', "Et moi, dans tout ça… je suis venue pour qui ?")]),
             S('host', 8, 'nuit', ['ananas'], "points at the camera",
               [('ananas', "À vous de jouer ! Coco ou Cyril ? Votez en commentaire !")], sfx='riser'),
         ]),
    dict(id='episode_10', num=10, titre="Le verdict",
         accroche="Le public a voté : qui quitte la villa ?",
         suite="Saison 2 : la Villa Tropicale",
         note="Deux versions du plan 4 et du plan 5 (selon le vote de l'épisode 9) : générer celle du nominé éliminé.",
         shots=[
             S('etab', 5, 'nuit', [], "Last night at the villa, suitcases by the door, golden lights"),
             S('host', 8, 'nuit', ['ananas'], "holds a golden envelope in front of the two nominees",
               [('ananas', "Vous avez voté par milliers. Celui qui quitte la Villa Vitamine… est…")]),
             S('react', 5, 'nuit', ['coco', 'cyril'], "drumroll, alternating close-ups of Coco and Cyril sweating", sfx='riser'),
             S('host', 5, 'nuit', ['ananas'], "reveals the card", [('ananas', "… Coco !")], sfx='boom'),
             S('scene', 8, 'portail', ['coco'], "Coco walks away with his suitcase, turns back one last time",
               [('coco', "Je reviendrai… encore plus dur.")]),
             S('scene', 8, 'piscine', ['kiki', 'berenice'], "Kiki and Bérénice hold hands at the pool at sunset",
               [('kiki', "Alors, on est un couple ?"), ('berenice', "On est un smoothie, Kiki. Un smoothie.")]),
             S('scene', 8, 'jardin', ['fanny', 'pepin'], "Fanny shows Pépin a photo of them on her phone",
               [('fanny', "Promis, je poste plus rien sans te demander."), ('pepin', "Tu peux poster… juste celle-là.")]),
             S('scene', 8, 'salon', ['margaux'], "Margaux packing her bag finds a mysterious letter with a tropical stamp and reads it",
               [('margaux', "« Margaux, ta vraie famille t'attend… à la Villa Tropicale. »")]),
             S('react', 4, 'salon', ['margaux'], "Margaux drops the letter, shocked", sfx='boom'),
             S('host', 8, 'piscine', ['ananas'], "bows to the camera in front of the villa",
               [('ananas', "La saison 1 est terminée… Mais à la Villa Tropicale, tout ne fait que commencer.")]),
             S('etab', 6, 'tropical', [], "teaser: new silhouettes of a dragon fruit and a passion fruit walking toward the camera at sunset", sfx='riser'),
         ],
         variante_cyril=[
             S('host', 5, 'nuit', ['ananas'], "reveals the card", [('ananas', "… Cyril !")], sfx='boom'),
             S('scene', 8, 'portail', ['cyril'], "Cyril walks away with his suitcase, turns back one last time",
               [('cyril', "Vous allez regretter mon acidité.")]),
         ]),
]

SERIES_MUSIC = dict(style='lofi', prog='lofi_c', key=53, bpm=96, seed=3101)

# ───────────────────────────── CRISTAL ASMR ─────────────────────────────

ASMR_BASE = ("Vertical ASMR macro video. {action} {subject}. {detail} Soft studio top light, dark background, shallow depth of field, "
             "ultra-detailed, slow satisfying motion. Sound: {sound}, no music, no voice.")

ACTIONS = [
    ("A sharp chef's knife slowly slices", "on a dark walnut cutting board"),
    ("A small silver spoon gently taps", "on a black marble surface"),
    ("A knife cuts in slow motion through", "on a dark slate board"),
    ("A sharp blade presses down until it cracks", "on a wooden board"),
]

MATERIALS = {
    'verre':   dict(nom='en verre', desc='made of perfectly translucent glass', detail='The glass is crystal clear with a colored tint; pieces glint and slide apart.', sound='crisp delicate glass crunching and tapping'),
    'cristal': dict(nom='en cristal', desc='carved from sparkling faceted crystal', detail='Light refracts into tiny rainbows; slices break cleanly.', sound='high-pitched crystal clinks and crisp cracks'),
    'glace':   dict(nom='en glace', desc='made of frozen clear ice with frost on the surface', detail='Ice crackles, cold mist rises, shards scatter.', sound='crunchy ice cracking and fizzing'),
    'ambre':   dict(nom='en ambre', desc='made of glossy golden amber like hard candy', detail='Thick caramel-like amber shatters into shiny shards.', sound='deep crunchy candy cracks'),
    'gelee':   dict(nom='en gelée', desc='made of wobbly transparent jelly', detail='The jelly wobbles and squishes slowly, glossy and bouncy.', sound='soft squishy jelly sounds and gentle wobbles'),
    'lave':    dict(nom='en lave', desc='made of glowing molten lava rock with orange cracks', detail='Glowing orange interior, sparks and embers.', sound='crackling embers, sizzle and rock cracking'),
    'or':      dict(nom='en or', desc='made of shiny solid gold', detail='Thin golden shavings curl off the blade, reflections everywhere.', sound='metallic scraping and soft golden clinks'),
    'savon':   dict(nom='en savon', desc='made of pastel soap', detail='Soft soap curls and cubes fall.', sound='soft soap carving and crumbling'),
    'chocolat': dict(nom='en chocolat', desc='made of glossy chocolate with a crunchy shell', detail='The shell snaps, revealing a smooth center.', sound='crisp chocolate snaps'),
    'diamant': dict(nom='en diamant', desc='made of flawless sparkling diamond', detail='Brilliant reflections; the blade struggles, then a clean cleave.', sound='sharp crystalline cracks and tiny tinkles'),
}

FRUITS = {
    'fraise': 'strawberry', 'framboise': 'raspberry', 'cerise': 'pair of cherries', 'mûre': 'blackberry', 'myrtille': 'handful of blueberries',
    'grenade': 'pomegranate', 'pastèque': 'watermelon slice', 'citron': 'lemon', 'orange': 'orange', 'pamplemousse': 'grapefruit',
    'citron vert': 'lime', 'mandarine': 'mandarin', 'kiwi': 'kiwi', 'pomme': 'apple', 'poire': 'pear', 'pêche': 'peach',
    'raisin': 'bunch of grapes', 'banane': 'banana', 'ananas': 'pineapple', 'mangue': 'mango', 'fruit du dragon': 'dragon fruit',
    'noix de coco': 'coconut', 'litchi': 'lychee', 'fruit de la passion': 'passion fruit', 'avocat': 'avocado', 'figue': 'fig',
    'abricot': 'apricot', 'prune': 'plum', 'melon': 'melon', 'carambole': 'star fruit', 'myrtille géante': 'giant blueberry',
}


def A(subject_fr, material):
    return (subject_fr, material)


ASMR = [
    dict(id='asmr_01', num=1, titre="Fruits rouges en verre", accroche="Le n°11 m'a donné des frissons",
         plans=[A(f, 'verre') for f in ['fraise', 'framboise', 'cerise', 'mûre', 'grenade', 'pastèque', 'myrtille', 'prune', 'figue',
                                         'raisin', 'fraise', 'cerise', 'framboise', 'grenade', 'pastèque', 'myrtille géante', 'mûre', 'fraise']]),
    dict(id='asmr_02', num=2, titre="Agrumes en cristal", accroche="Écoute le son du n°7",
         plans=[A(f, 'cristal') for f in ['citron', 'orange', 'pamplemousse', 'citron vert', 'mandarine', 'citron', 'orange', 'pamplemousse',
                                           'citron vert', 'mandarine', 'citron', 'orange', 'pamplemousse', 'citron vert', 'mandarine', 'orange', 'citron', 'pamplemousse']]),
    dict(id='asmr_03', num=3, titre="Fruits gelés qui craquent", accroche="Le craquement du n°14…",
         plans=[A(f, 'glace') for f in ['pastèque', 'kiwi', 'fraise', 'citron', 'raisin', 'pêche', 'mangue', 'framboise', 'ananas',
                                         'pomme', 'cerise', 'orange', 'myrtille', 'banane', 'poire', 'litchi', 'melon', 'grenade']]),
    dict(id='asmr_04', num=4, titre="Fruits en ambre", accroche="On dirait du caramel… écoute",
         plans=[A(f, 'ambre') for f in ['pomme', 'poire', 'pêche', 'abricot', 'figue', 'cerise', 'raisin', 'prune', 'mandarine',
                                         'fraise', 'kiwi', 'citron', 'mangue', 'ananas', 'litchi', 'grenade', 'orange', 'pomme']]),
    dict(id='asmr_05', num=5, titre="Fruits en gelée", accroche="Le plus doux de tous (n°9)",
         plans=[A(f, 'gelee') for f in ['fraise', 'pêche', 'mangue', 'kiwi', 'raisin', 'citron', 'pastèque', 'myrtille géante', 'litchi',
                                         'orange', 'cerise', 'ananas', 'framboise', 'melon', 'banane', 'poire', 'fruit du dragon', 'fraise']]),
    dict(id='asmr_06', num=6, titre="Fruits en lave", accroche="Ne regarde pas le n°13 avec le son à fond",
         plans=[A(f, 'lave') for f in ['pomme', 'grenade', 'orange', 'mangue', 'fraise', 'ananas', 'pêche', 'citron', 'cerise',
                                        'pastèque', 'noix de coco', 'figue', 'prune', 'raisin', 'kiwi', 'poire', 'abricot', 'melon']]),
    dict(id='asmr_07', num=7, titre="Fruits en or massif", accroche="Couper de l'or… le n°5 est fou",
         plans=[A(f, 'or') for f in ['pomme', 'poire', 'banane', 'ananas', 'fraise', 'cerise', 'citron', 'raisin', 'pêche',
                                      'mangue', 'kiwi', 'orange', 'figue', 'noix de coco', 'grenade', 'abricot', 'prune', 'pomme']]),
    dict(id='asmr_08', num=8, titre="Fruits exotiques en verre", accroche="Le fruit du dragon (n°3) est incroyable",
         plans=[A(f, 'verre') for f in ['mangue', 'ananas', 'fruit du dragon', 'fruit de la passion', 'litchi', 'carambole', 'noix de coco',
                                         'kiwi', 'banane', 'avocat', 'mangue', 'fruit du dragon', 'carambole', 'litchi', 'ananas', 'fruit de la passion', 'noix de coco', 'mangue']]),
    dict(id='asmr_09', num=9, titre="Du plus mou au plus dur", accroche="Jusqu'où le couteau peut aller ?",
         plans=[A('fraise', 'gelee'), A('pêche', 'gelee'), A('pomme', 'savon'), A('poire', 'savon'), A('cerise', 'chocolat'), A('orange', 'chocolat'),
                A('citron', 'glace'), A('kiwi', 'glace'), A('pomme', 'ambre'), A('figue', 'ambre'), A('fraise', 'verre'), A('pastèque', 'verre'),
                A('citron', 'cristal'), A('grenade', 'cristal'), A('pomme', 'or'), A('ananas', 'lave'), A('cerise', 'diamant'), A('fraise', 'diamant')]),
    dict(id='asmr_10', num=10, titre="Les fruits de la Villa en cristal", accroche="Tu reconnais qui ? (Villa Vitamine)",
         note="Crossover avec Villa Vitamine : figurines en cristal des personnages, tapotées à la cuillère (on ne coupe pas les personnages).",
         plans=[A(f, 'cristal') for f in ['kiwi', 'banane', 'citron', 'pomme', 'mangue', 'fraise', 'noix de coco', 'ananas', 'kiwi',
                                           'banane', 'citron', 'pomme', 'mangue', 'fraise', 'noix de coco', 'ananas', 'kiwi', 'banane']]),
]
ASMR_SHOT = 5   # secondes par plan → 18 plans = 90 s


# ───────────────────────────── PROMPTS ─────────────────────────────

def shot_prompt(shot):
    """Prompt Wan 3.0 d'un plan de Villa Vitamine (image + son natif, dialogue en français)."""
    parts = [STYLE, f"Setting: {SETTINGS[shot['where']]}."]
    for c in shot['who']:
        parts.append(CHARACTERS[c]['look'] + '.')
    parts.append(f"Action: {shot['action']}.")
    if shot['kind'] == 'conf':
        parts.append("Reality-TV confessional framing: the character faces the camera, medium close-up.")
    if shot['lines']:
        for who, txt in shot['lines']:
            c = CHARACTERS[who]
            if shot.get('off'):
                parts.append(f'{c["nom"]} is not visible; his voice is heard off-screen ({c["voix"]}) saying in French: "{txt}"')
            else:
                parts.append(f'{c["nom"]} says in French ({c["voix"]}): "{txt}"')
        parts.append(("French voice-over" if shot.get('off') else "Lip-synced French dialogue") + ", light villa ambience (cicadas, water), no background music.")
    else:
        parts.append("No dialogue. Ambient sound only (cicadas, water, wind), no music.")
    return ' '.join(parts)


def asmr_prompt(video, i):
    fr, mat = video['plans'][i]
    m = MATERIALS[mat]
    act, surface = ACTIONS[i % len(ACTIONS)]
    if video['id'] == 'asmr_10':
        act, surface = ACTIONS[1]
        subject = f"a small cute cartoon {FRUITS[fr]} character figurine {m['desc']}, {surface}"
    else:
        subject = f"a {FRUITS[fr]} {m['desc']}, {surface}"
    return ASMR_BASE.format(action=act, subject=subject, detail=m['detail'], sound=m['sound'])


def episode_shots(ep, eliminated='coco'):
    shots = list(ep['shots'])
    if ep['id'] == 'episode_10' and eliminated == 'cyril':
        shots[3:5] = ep['variante_cyril']
    return shots


def jobs():
    """Liste de toutes les générations à lancer : (vidéo, n° de plan, prompt, durée)."""
    out = []
    for ep in EPISODES:
        for i, sh in enumerate(episode_shots(ep)):
            out.append((ep['id'], i + 1, shot_prompt(sh), sh['dur']))
    for v in ASMR:
        for i in range(len(v['plans'])):
            out.append((v['id'], i + 1, asmr_prompt(v, i), ASMR_SHOT))
    return out


def budget(resolution='720p'):
    rate = CREDITS_PER_SECOND[resolution]
    ep_s = {ep['id']: sum(s['dur'] for s in episode_shots(ep)) for ep in EPISODES}
    as_s = {v['id']: len(v['plans']) * ASMR_SHOT for v in ASMR}
    return dict(episodes={k: (s, round(s * rate * RETAKE)) for k, s in ep_s.items()},
                asmr={k: (s, round(s * rate * RETAKE)) for k, s in as_s.items()},
                total=round((sum(ep_s.values()) + sum(as_s.values())) * rate * RETAKE))


if __name__ == '__main__':
    b = budget()
    for k, (s, c) in {**b['episodes'], **b['asmr']}.items():
        print(f'{k}: {s} s générées → ≈ {c} crédits')
    print('TOTAL ≈', b['total'], 'crédits (720p)  |  480p ≈', budget('480p')['total'])
    print(len(jobs()), 'plans à générer')
