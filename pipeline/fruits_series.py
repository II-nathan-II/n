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


def S(kind, dur, where, who, action, lines=(), text=None, sfx=None, off=False, gag=None, crop=None):
    """Un plan généré. kind : etab (ambiance), scene, conf (confessionnal), host, react (réaction muette).
    off=True : les répliques sont dites en voix off (personnage hors champ). gag='chute' : chute de Pépin (compteur)."""
    return dict(kind=kind, dur=dur, where=where, who=list(who), action=action, lines=list(lines), text=text, sfx=sfx, off=off, gag=gag, crop=crop)


# Structure de chaque épisode (pensée pour la rétention TikTok) :
#   cold   : ouverture choc de 3 s = extrait d'un plan fort de l'épisode (plan, début, durée), sans génération en plus ;
#   recap  : « Précédemment… » affiché sur le premier plan, pour qu'un nouveau spectateur prenne la série en cours ;
#   fil rouge : le secret de Margaux (sa relation avec Monsieur Ananas), semé d'indices jusqu'à la révélation finale ;
#   gag récurrent : Pépin tombe à chaque épisode (compteur « Chutes de Pépin » à l'écran) ;
#   question : appel au commentaire sur le carton de fin (« Team Bérénice ou Team Margaux ? »).
EPISODES = [
    dict(id='episode_01', num=1, titre="Bienvenue à la Villa",
         accroche="6 fruits, 1 villa… et un secret dès le premier soir",
         accroche_ecran=["LE PRÉSENTATEUR", "TRICHE DÉJÀ…"],
         couverture='NICHE_3_VILLA_VITAMINE/couvertures/episode_01.jpg', sous_titres='mot',
         cold=(12, 0.0, 3.0),
         question="Ton fruit préféré pour l'instant ?",
         suite="Épisode 2 : la nouvelle arrive",
         shots=[
             S('etab', 4, 'villa', [], "Slow aerial drone shot gliding over the villa and the pool, sparkling water, no characters"),
             S('host', 8, 'piscine', ['ananas'], "stands at the edge of the pool, opens his arms wide to the camera",
               [('ananas', "Bienvenue à la Villa Vitamine ! Six fruits, un été… et une seule règle : rester frais !")]),
             S('scene', 6, 'villa', ['kiki'], "arrives at the villa entrance rolling a suitcase, takes off his sunglasses and looks around amazed",
               [('kiki', "La villa, le soleil, la piscine… Franchement, j'ai la pêche !")]),
             S('conf', 7, 'conf', ['kiki'], "sits in the armchair, winks at the camera",
               [('kiki', "Moi c'est Kiki. Tout doux à l'extérieur… et très sucré à l'intérieur.")]),
             S('scene', 6, 'villa', ['berenice'], "walks down the villa stairs like a runway, sunglasses on, hand on hip",
               [('berenice', "Coucou la villa ! Votre reine est arrivée.")]),
             S('conf', 7, 'conf', ['berenice'], "sits with legs crossed, flips her imaginary hair",
               [('berenice', "Je suis pas venue pour me faire des amis. Je suis venue pour briller.")]),
             S('scene', 6, 'salon', ['cyril'], "walks in with arms crossed, looks at the decoration with disgust",
               [('cyril', "Encore une villa pleine de fruits trop mûrs…")]),
             S('conf', 7, 'conf', ['cyril'], "sits stiffly, raises one eyebrow",
               [('cyril', "C'est pas pour être acide, mais je donne trois jours à Kiki avant de se faire presser.")]),
             S('scene', 6, 'salon', ['pepin'], "trips over a suitcase and falls face first onto a big cushion, then gets up embarrassed",
               [('pepin', "Ça va, ça va ! Je suis juste… tombé dans les pommes.")], sfx='impact', gag='chute'),
             S('scene', 7, 'cuisine', ['fanny', 'kiki', 'berenice'], "Fanny runs into the kitchen waving her pink phone while Kiki and Bérénice turn around",
               [('fanny', "Vous savez pas la nouvelle ? Demain… une nouvelle arrive à la villa !")]),
             S('react', 4, 'cuisine', ['kiki', 'berenice'], "dramatic slow push-in: Kiki raises an eyebrow with a smile, Bérénice drops her glass of juice in shock", sfx='boom'),
             S('scene', 8, 'portail', ['ananas'], "at night, Monsieur Ananas secretly hands a golden key to a feminine silhouette standing next to a suitcase with a mango sticker, he looks around to make sure nobody is watching, suspense",
               [('ananas', "Personne ne doit savoir… Bienvenue, ma chérie.")], sfx='riser'),
         ]),
    dict(id='episode_02', num=2, titre="La nouvelle",
         recap="Précédemment : une inconnue est arrivée en secret… et Monsieur Ananas la connaît.",
         accroche="Quand la nouvelle arrive, Kiki perd ses lunettes (et la tête)",
         accroche_ecran=["LA NOUVELLE ARRIVE…", "ET KIKI PERD LA TÊTE"],
         couverture='NICHE_3_VILLA_VITAMINE/couvertures/episode_02.jpg', sous_titres='duo',
         cold=(4, 0.5, 2.5),
         question="Team Bérénice ou Team Margaux ?",
         suite="Épisode 3 : clash à la piscine",
         shots=[
             S('etab', 4, 'villa', [], "Morning at the villa, sun rising over the pool, birds, no characters"),
             S('scene', 6, 'cuisine', ['fanny', 'pepin'], "Fanny bursts into the breakfast room in panic, Pépin spills his cereal",
               [('fanny', "Elle arrive ! Elle arrive ! Tout le monde à sa place !")]),
             S('scene', 7, 'piscine', ['margaux'], "walks along the pool in slow motion, wind in her leaf, everyone turns",
               [('margaux', "Bonjour tout le monde… Moi c'est Margaux. Et oui, je suis exotique.")]),
             S('react', 4, 'piscine', ['kiki'], "slow motion: Kiki's jaw drops and his sunglasses slide off his head into the pool", sfx='whoosh'),
             S('conf', 6, 'conf', ['kiki'], "fans himself with his hand, dreamy eyes",
               [('kiki', "Margaux… c'est pas un fruit, c'est un dessert.")]),
             S('conf', 7, 'conf', ['berenice'], "fake smile that slowly turns into a glare",
               [('berenice', "Elle est mignonne… pour une mangue. Mais ici, la reine, c'est moi.")]),
             S('scene', 6, 'piscine', ['ananas', 'margaux'], "Monsieur Ananas walks past Margaux by the pool and discreetly winks at her; she winks back with a tiny smile"),
             S('conf', 6, 'conf', ['fanny'], "leans toward the camera, suspicious",
               [('fanny', "Vous avez vu ? Monsieur Ananas lui a fait un clin d'œil. Bizarre… très bizarre.")]),
             S('scene', 8, 'cuisine', ['kiki', 'margaux', 'pepin'], "Kiki shows off at the blender for Margaux, Pépin washes dishes in the background",
               [('kiki', "Je te prépare un smoothie ?"), ('margaux', "Seulement s'il est sans pépins.")]),
             S('conf', 6, 'conf', ['pepin'], "looks offended, leans back too far and falls off the armchair",
               [('pepin', "Sans pépins ? Mais j'ai rien fait, moi !")], sfx='impact', gag='chute'),
             S('scene', 7, 'jardin', ['kiki', 'fanny', 'berenice'], "Kiki talks to Fanny by the hedge while Bérénice hides behind a big plant, listening",
               [('kiki', "Bérénice, elle est cool… mais Margaux, c'est autre chose.")]),
             S('react', 4, 'jardin', ['berenice'], "extreme close-up on Bérénice behind the leaves, she gasps, one eye twitches", [('berenice', "Autre chose ?!")], sfx='boom'),
             S('host', 6, 'nuit', ['ananas'], "leans toward the camera with a mysterious smile",
               [('ananas', "Demain… ça va glisser. Et pas que sur les peaux de banane.")], sfx='riser'),
         ]),
    dict(id='episode_03', num=3, titre="Clash à la piscine",
         recap="Précédemment : Kiki a craqué pour Margaux… et Bérénice a tout entendu.",
         accroche="Elle a pris SON transat. Grosse erreur.",
         cold=(7, 0.5, 3.0),
         question="Qui a mis la peau de banane ?",
         suite="Épisode 4 : le jeu de la vérité",
         shots=[
             S('etab', 4, 'piscine', [], "Hot midday at the pool, heat haze, one empty pink sunbed in the spotlight, no characters"),
             S('scene', 9, 'piscine', ['berenice', 'margaux'], "Bérénice stands over Margaux who is lying on the pink sunbed",
               [('berenice', "Toi, la mangue, tu te calmes. Ici, c'est mon transat."), ('margaux', "Ton transat ? Il y a ton nom dessus ?")]),
             S('react', 4, 'piscine', ['kiki', 'pepin', 'fanny', 'cyril'], "the other fruits gasp together with hands on their mouths", sfx='boom'),
             S('conf', 6, 'conf', ['margaux'], "calm, adjusts the flower behind her ear",
               [('margaux', "Elle croit que je vais me laisser presser ? Je suis pas un jus de fruit, moi.")]),
             S('scene', 8, 'jardin', ['fanny', 'cyril'], "Fanny whispers in Cyril's ear behind an olive tree",
               [('fanny', "Il paraît qu'on a vu Margaux en cachette… avec un ananas !"), ('cyril', "Un ananas ? Intéressant. Très intéressant.")]),
             S('scene', 8, 'piscine', ['pepin', 'berenice', 'margaux'], "Pépin steps between the two girls, arms raised to calm them",
               [('pepin', "Les filles ! On peut couper la poire en deux ?"), ('berenice', "Il n'y a pas de poire ici !")]),
             S('scene', 6, 'piscine', ['pepin'], "Pépin steps back onto a banana peel, slips in slow motion and falls into the pool with a huge splash", sfx='impact', gag='chute'),
             S('react', 4, 'piscine', ['kiki', 'fanny', 'berenice'], "everyone bursts out laughing, Bérénice tries hard not to laugh"),
             S('conf', 6, 'conf', ['berenice'], "looks away innocently, whistles",
               [('berenice', "La peau de banane, c'était pas moi. Enfin… je crois.")]),
             S('scene', 7, 'jardin', ['margaux'], "at the far end of the garden, Margaux whispers on her phone, looking around nervously",
               [('margaux', "Non… personne ne se doute de rien. Promis.")]),
             S('conf', 6, 'conf', ['cyril'], "narrows his eyes, rubs his hands",
               [('cyril', "Des appels en cachette ? C'est pas pour être acide, mais… je vais trouver.")]),
             S('host', 7, 'nuit', ['ananas'], "holds a stack of cards under a single spotlight",
               [('ananas', "Ce soir… c'est le jeu de la vérité. Et personne ne pourra mentir.")], sfx='riser'),
         ]),
    dict(id='episode_04', num=4, titre="Le jeu de la vérité",
         recap="Précédemment : clash au transat… et Margaux passe des appels en cachette.",
         accroche="Bérénice ou Margaux ? Kiki doit répondre.",
         cold=(5, 1.0, 3.0),
         question="À ton avis, qui appelle Margaux ?",
         suite="Épisode 5 : le retour de l'ex",
         shots=[
             S('etab', 4, 'nuit', [], "Night, a circle of chairs around a fire pit by the pool, lanterns, suspense, no characters"),
             S('host', 7, 'nuit', ['ananas'], "stands in the middle of the circle, shuffling cards",
               [('ananas', "Je pose une question, vous répondez. Et la vérité finit toujours par sortir du jus.")]),
             S('scene', 8, 'nuit', ['ananas', 'pepin'], "the host turns to Pépin, who turns bright red",
               [('ananas', "Pépin, es-tu amoureux ?"), ('pepin', "Peut-être… de quelqu'un qui a des pépins, elle aussi…")]),
             S('react', 4, 'nuit', ['fanny'], "Fanny blushes and hides her face behind her pink phone"),
             S('scene', 9, 'nuit', ['ananas', 'kiki'], "close-up on Kiki sweating under the spotlight",
               [('ananas', "Kiki… Bérénice ou Margaux ?"), ('kiki', "Euh… Bérénice… euh… Margaux…")]),
             S('react', 4, 'nuit', ['berenice', 'margaux'], "Bérénice and Margaux slowly turn their heads toward Kiki, eyes narrowed", sfx='boom'),
             S('conf', 6, 'conf', ['kiki'], "shrugs with a nervous laugh",
               [('kiki', "Ma réponse ? Je suis mi-figue, mi-raisin. Voilà.")]),
             S('conf', 6, 'conf', ['berenice'], "furious, fanning herself",
               [('berenice', "Il hésite ? Il HÉSITE ? Moi, on m'hésite pas !")]),
             S('scene', 8, 'nuit', ['cyril', 'margaux'], "Cyril snatches a card from the host and reads it to Margaux with a wicked smile",
               [('cyril', "Margaux… qui t'appelle en cachette tous les soirs ?")]),
             S('react', 4, 'nuit', ['margaux', 'ananas'], "Margaux freezes; behind her, Monsieur Ananas nervously pulls on his bow tie"),
             S('scene', 4, 'nuit', ['kiki', 'berenice', 'margaux', 'pepin', 'fanny', 'cyril'], "suddenly all the lights go out, darkness, the fruits scream, a phone flashlight sweeps around", sfx='impact'),
             S('etab', 7, 'nuit', ['coco'], "in the darkness, a big silhouette lit from below by a phone screen, only sunglasses visible",
               [('coco', "Salut Bérénice… Tu m'as manqué.")], sfx='riser'),
         ]),
    dict(id='episode_05', num=5, titre="Le retour de l'ex",
         recap="Précédemment : en pleine panne de courant, une voix a surgi dans le noir…",
         accroche="L'ex de Bérénice est là… mais pas pour elle",
         cold=(10, 0.0, 3.0),
         question="Team Kiki ou Team Coco ?",
         suite="Épisode 6 : le complot",
         shots=[
             S('etab', 4, 'villa', [], "Morning at the villa, a big shadow appears on the pool water, no characters visible"),
             S('scene', 8, 'piscine', ['coco', 'pepin'], "Coco flexes his arms by the pool, the sunbeds shake and Pépin falls off his sunbed",
               [('coco', "Salut la villa. Moi c'est Coco. Dur à l'extérieur… dur à l'intérieur aussi.")], sfx='impact', gag='chute'),
             S('react', 4, 'piscine', ['berenice'], "Bérénice spits out her juice in surprise", sfx='whoosh'),
             S('conf', 7, 'conf', ['berenice'], "rolls her eyes",
               [('berenice', "Coco, c'est mon ex. On s'est séparés parce qu'il était… impossible à ouvrir.")]),
             S('scene', 9, 'piscine', ['coco', 'kiki'], "Coco and Kiki face to face, Coco twice as big",
               [('coco', "Alors c'est toi, le petit poilu ?"), ('kiki', "Petit ? Je fais un mètre… de charisme.")]),
             S('conf', 7, 'conf', ['kiki'], "rolls his eyes with attitude, then sighs",
               [('kiki', "Moi, jaloux ? Jamais. … Bon. Un petit peu.")]),
             S('scene', 7, 'jardin', ['fanny'], "Fanny films herself with her pink phone like a live stream",
               [('fanny', "Vous savez pas la nouvelle ? L'ex de Bérénice est là, et il a des biceps de noix de coco !")]),
             S('scene', 8, 'nuit', ['coco', 'berenice'], "at the pool bar, Coco leans toward Bérénice",
               [('berenice', "Coco, si t'es revenu pour moi, c'est non."), ('coco', "Pour toi ? Non…")]),
             S('react', 4, 'nuit', ['berenice'], "Bérénice frozen, confused, a cricket chirps"),
             S('scene', 8, 'nuit', ['coco', 'margaux'], "Coco turns slowly and points at Margaux",
               [('coco', "Je suis revenu pour Margaux."), ('margaux', "Pardon ?!")], sfx='boom'),
             S('host', 7, 'nuit', ['ananas'], "watches Coco from afar, squeezing a cocktail shaker so hard it bends",
               [('ananas', "Une noix de coco qui tourne autour de Margaux ? Pas dans ma villa.")], sfx='riser'),
         ]),
    dict(id='episode_06', num=6, titre="Le complot",
         recap="Précédemment : Coco est revenu… pour Margaux. Et Monsieur Ananas n'a pas aimé.",
         accroche="Un faux message à minuit… et tout bascule",
         cold=(9, 0.0, 3.0),
         question="Cyril est-il allé trop loin ?",
         suite="Épisode 7 : la Soirée Blanche",
         shots=[
             S('etab', 4, 'jardin', [], "Night garden, crickets, two small shadows behind a hedge, no faces"),
             S('scene', 9, 'jardin', ['cyril', 'fanny'], "Cyril and Fanny plotting behind the hedge with a flashlight",
               [('cyril', "Si Kiki part, Bérénice pleure."), ('fanny', "Et une Bérénice qui pleure… ça fait des vues !")]),
             S('scene', 8, 'salon', ['cyril'], "in the dark living room, Cyril types on a phone with a green kiwi case, evil grin lit by the screen",
               [('cyril', "« Margaux, rejoins-moi à minuit au jardin. Kiki. » Parfait.")]),
             S('conf', 6, 'conf', ['margaux'], "dreamy",
               [('margaux', "Un rendez-vous à minuit ? Kiki est plus romantique que je pensais.")]),
             S('scene', 8, 'salon', ['pepin', 'cyril'], "Pépin turns on the light and catches Cyril holding the green phone",
               [('pepin', "Cyril ? C'est le téléphone de Kiki ?"), ('cyril', "Hein ? Non. C'est une calculatrice.")]),
             S('conf', 7, 'conf', ['pepin'], "unimpressed, arms crossed",
               [('pepin', "Une calculatrice… avec la photo de Kiki en fond d'écran. Il me prend pour une poire.")]),
             S('scene', 8, 'nuit', ['margaux'], "alone on the dark terrace, Margaux whispers into her phone, checking that nobody hears",
               [('margaux', "Oui, papa… Non, personne ne sait. Je te le promets.")]),
             S('scene', 5, 'jardin', ['margaux'], "midnight, Margaux waits alone under the string lights, moonlight, wind"),
             S('scene', 7, 'jardin', ['berenice', 'margaux'], "Bérénice appears behind Margaux with a flashlight under her face",
               [('berenice', "Tiens, tiens… Tu attends quelqu'un, la mangue ?")], sfx='boom'),
             S('react', 4, 'jardin', ['margaux'], "Margaux jumps, shocked"),
             S('host', 7, 'nuit', ['ananas'], "in front of a giant white cake, smiling mysteriously",
               [('ananas', "Demain soir, c'est la Soirée Blanche. Et quelqu'un va finir… dans la piscine.")], sfx='riser'),
         ]),
    dict(id='episode_07', num=7, titre="La Soirée Blanche",
         recap="Précédemment : le faux message de Cyril… et Bérénice a surpris Margaux à minuit.",
         accroche="Battle de danse, premier slow… et un gâteau dans la piscine",
         cold=(9, 1.0, 3.0),
         question="Qui a jeté le gâteau ? Ton suspect en commentaire",
         suite="Épisode 8 : l'enquête",
         shots=[
             S('etab', 4, 'soiree', [], "All-white party by the pool, fairy lights, balloons, music, wide shot"),
             S('scene', 8, 'soiree', ['coco', 'kiki'], "dance battle in a circle, Coco flexes, Kiki does a spin",
               [('coco', "Battle de danse, le poilu !"), ('kiki', "Attention, ça va secouer le cocotier !")]),
             S('react', 4, 'soiree', ['fanny', 'pepin', 'margaux', 'cyril'], "the crowd of fruits cheers and jumps"),
             S('scene', 9, 'soiree', ['pepin', 'fanny'], "Pépin shyly offers his hand to Fanny under the fairy lights",
               [('pepin', "Fanny… tu veux danser avec moi ?"), ('fanny', "Pépin… ça fait trois épisodes que j'attends ça.")]),
             S('conf', 6, 'conf', ['pepin'], "beaming with happiness",
               [('pepin', "J'ai pas glissé, j'ai rien cassé… C'est le plus beau jour de ma vie.")]),
             S('scene', 9, 'nuit', ['berenice', 'kiki'], "on the terrace, Bérénice confronts Kiki",
               [('berenice', "Le message de minuit, c'était toi ?"), ('kiki', "Quel message ? Je te jure sur ma pulpe !")]),
             S('conf', 6, 'conf', ['berenice'], "annoyed but smiling",
               [('berenice', "Il a l'air sincère… Et quand il est sincère, il est mignon. C'est énervant.")]),
             S('etab', 4, 'soiree', [], "a giant white three-tier cake on a table at the edge of the pool, close-up"),
             S('etab', 6, 'soiree', ['pepin'], "a big shadowy figure pushes the cake into the pool, huge splash, the wave knocks Pépin into the water too, the figure's face is not visible", sfx='impact', gag='chute'),
             S('react', 4, 'soiree', ['berenice', 'margaux', 'fanny'], "everyone screams with hands on their heads", [('fanny', "Le gâteau ! … Et Pépin !")]),
             S('conf', 6, 'conf', ['cyril'], "too innocent",
               [('cyril', "Moi j'ai rien vu. J'étais en train de… compter mes zestes.")]),
             S('host', 6, 'piscine', ['ananas'], "holds a dripping cake topper, staring into the camera",
               [('ananas', "Qui a fait ça ? Demain… on mène l'enquête.")], sfx='riser'),
         ]),
    dict(id='episode_08', num=8, titre="L'enquête",
         recap="Précédemment : un gâteau a fini dans la piscine… et Pépin aussi.",
         accroche="Fanny a tout filmé. Même ce qu'il ne fallait pas.",
         cold=(7, 0.0, 3.0),
         question="Pourquoi Margaux fait un câlin à Monsieur Ananas ?",
         suite="Épisode 9 : les nominations",
         shots=[
             S('etab', 4, 'piscine', [], "Morning, cake crumbs floating in the pool, a lonely cherry, no characters"),
             S('host', 7, 'salon', ['ananas'], "wearing a detective hat, holding a magnifying glass",
               [('ananas', "Personne ne quitte la villa tant que le coupable n'a pas parlé.")]),
             S('scene', 8, 'salon', ['berenice', 'cyril'], "everyone points at Cyril, who throws up his arms",
               [('berenice', "C'est forcément Cyril !"), ('cyril', "Moi ? Je suis acide, pas criminel !")]),
             S('scene', 6, 'salon', ['fanny'], "Fanny jumps on the sofa, holding up her pink phone",
               [('fanny', "Attendez ! J'ai tout filmé pendant la soirée !")]),
             S('react', 4, 'salon', ['kiki', 'berenice', 'margaux', 'pepin'], "everyone huddles around the phone screen, faces lit by it"),
             S('react', 4, 'salon', ['coco'], "slow zoom on Coco, who swallows hard and sweats", sfx='boom'),
             S('scene', 8, 'salon', ['coco'], "Coco raises his hands and confesses",
               [('coco', "Ok, ok… C'était moi. Je voulais gâcher la soirée de Kiki.")]),
             S('conf', 6, 'conf', ['kiki'], "furious but funny",
               [('kiki', "Il a jeté mon gâteau à la piscine. Lui, il va finir en lait de coco.")]),
             S('scene', 8, 'salon', ['margaux', 'berenice'], "Margaux turns to Bérénice",
               [('margaux', "Et le faux message, c'était Cyril. Pépin l'a vu."), ('berenice', "Donc… Kiki ne m'a pas trahie ?")]),
             S('react', 4, 'salon', ['berenice', 'kiki'], "Bérénice looks at Kiki and smiles softly, he smiles back, romantic music"),
             S('scene', 7, 'salon', ['fanny'], "Fanny zooms into her phone video, eyes wide",
               [('fanny', "Attendez… zoomez… Pourquoi Margaux fait un câlin à Monsieur Ananas ?!")], sfx='boom'),
             S('host', 5, 'salon', ['ananas'], "snatches the phone from Fanny, sweating, forced smile",
               [('ananas', "Ce soir… les nominations !")], sfx='riser'),
         ]),
    dict(id='episode_09', num=9, titre="Les nominations",
         recap="Précédemment : Coco a avoué… et Margaux a fait un câlin à Monsieur Ananas.",
         accroche="Coco ou Cyril : c'est toi qui décides",
         cold=(6, 0.0, 3.0),
         question="Coco ou Cyril ? Vote en commentaire !",
         vote="Coco ou Cyril ? Vote en commentaire !",
         suite="Épisode 10 : le verdict (selon vos votes)",
         shots=[
             S('etab', 4, 'nuit', [], "Night, dramatic red lights around the pool, smoke, tension, no characters"),
             S('host', 8, 'nuit', ['ananas'], "stands in front of all the fruits lined up",
               [('ananas', "Les fruits ont voté. Deux nominés ce soir… et un seul restera.")]),
             S('react', 4, 'nuit', ['kiki', 'berenice', 'margaux', 'pepin', 'fanny', 'cyril', 'coco'], "quick nervous close-ups of the fruits, heartbeat"),
             S('host', 5, 'nuit', ['ananas'], "opens an envelope", [('ananas', "Premier nominé… Coco.")], sfx='boom'),
             S('conf', 6, 'conf', ['coco'], "shrugs",
               [('coco', "Normal. J'ai jeté un gâteau dans une piscine. Même moi, je me nommerais.")]),
             S('host', 6, 'nuit', ['ananas'], "opens a second envelope", [('ananas', "Deuxième nominé… Cyril.")], sfx='boom'),
             S('conf', 8, 'conf', ['cyril'], "bitter, then suspicious",
               [('cyril', "Évidemment. Et bizarrement… la mangue, elle, n'est jamais nominée.")]),
             S('scene', 9, 'nuit', ['kiki', 'berenice'], "Kiki and Bérénice on a sunbed under the stars",
               [('kiki', "Quoi qu'il arrive, c'est toi."), ('berenice', "Mi-figue, mi-raisin ?"), ('kiki', "Non. Cent pour cent banane.")]),
             S('react', 4, 'nuit', ['fanny', 'pepin'], "Fanny and Pépin watch from a bench, melting with emotion; Pépin leans in to hug Fanny and falls off the bench", sfx='impact', gag='chute'),
             S('scene', 7, 'nuit', ['margaux'], "Margaux alone on the terrace looking at the sea",
               [('margaux', "Demain, il faudra que je dise la vérité. À tout le monde.")]),
             S('host', 8, 'nuit', ['ananas'], "points at the camera",
               [('ananas', "À vous de jouer ! Coco ou Cyril ? Votez en commentaire !")], sfx='riser'),
         ]),
    dict(id='episode_10', num=10, titre="Le verdict",
         recap="Précédemment : Coco et Cyril sont nominés… et vous avez voté.",
         accroche="Le verdict… et le secret de Margaux",
         cold=(2, 3.5, 3.0),
         question="Tu veux une saison 2 ?",
         suite="Saison 2 : la Villa Tropicale",
         note="Deux versions des plans 4 et 5 (selon le vote de l'épisode 9) : générer celle du nominé éliminé.",
         shots=[
             S('etab', 4, 'nuit', [], "Last night at the villa, suitcases by the door, golden lights"),
             S('host', 8, 'nuit', ['ananas'], "holds a golden envelope in front of the two nominees",
               [('ananas', "Vous avez voté par milliers. Celui qui quitte la Villa Vitamine… est…")]),
             S('react', 4, 'nuit', ['coco', 'cyril'], "drumroll, alternating close-ups of Coco and Cyril sweating", sfx='riser'),
             S('host', 4, 'nuit', ['ananas'], "reveals the card", [('ananas', "… Coco !")], sfx='boom'),
             S('scene', 7, 'portail', ['coco'], "Coco walks away with his suitcase, turns back one last time",
               [('coco', "Je reviendrai… encore plus dur.")]),
             S('scene', 8, 'piscine', ['margaux', 'kiki', 'berenice', 'pepin', 'fanny', 'cyril'], "Margaux stands in front of everyone at the pool, takes a deep breath",
               [('margaux', "Il faut que je vous dise un truc… Monsieur Ananas, c'est mon père.")]),
             S('react', 4, 'piscine', ['kiki', 'berenice', 'pepin', 'fanny', 'cyril'], "all the fruits shout in shock at the same time", [('fanny', "QUOI ?!")], sfx='boom'),
             S('host', 7, 'piscine', ['ananas', 'margaux'], "Monsieur Ananas hugs Margaux proudly, a tear in his eye",
               [('ananas', "Le verger a parlé… et ma fille aussi.")]),
             S('scene', 8, 'piscine', ['kiki', 'berenice'], "Kiki and Bérénice hold hands at the pool at sunset",
               [('kiki', "Alors, on est un couple ?"), ('berenice', "On est un smoothie, Kiki. Un smoothie.")]),
             S('scene', 7, 'jardin', ['fanny', 'pepin'], "Fanny shows Pépin a photo of them on her phone; he steps back happily and falls into the lavender",
               [('fanny', "Promis, je poste plus rien sans te demander."), ('pepin', "Tu peux poster… juste celle-là.")], sfx='impact', gag='chute'),
             S('scene', 7, 'salon', ['margaux'], "Margaux finds a letter with a tropical stamp in her suitcase and reads it, shocked",
               [('margaux', "« Ma fille, rejoins-moi à la Villa Tropicale. Maman. »")], sfx='boom'),
             S('etab', 6, 'tropical', [], "teaser: the silhouette of a papaya queen and new fruit silhouettes (dragon fruit, passion fruit) walking toward the camera at sunset", sfx='riser'),
         ],
         variante_cyril=[
             S('host', 4, 'nuit', ['ananas'], "reveals the card", [('ananas', "… Cyril !")], sfx='boom'),
             S('scene', 7, 'portail', ['cyril'], "Cyril walks away with his suitcase, turns back one last time",
               [('cyril', "Vous allez regretter mon acidité.")]),
         ]),
]

# Bande-annonce (5 plans de 5 s) : pensée pour les crédits gratuits du site Kling, afin de tester l'audience
# avant de produire la saison. Plans repris de la saison (mêmes répliques), raccourcis à 5 s.
TRAILER = dict(id='bande_annonce', num=0, titre="Bande-annonce",
               accroche="La télé-réalité la plus juteuse de l'été",
               fin="ÉPISODE 1 · DEMAIN 19 H",
               question="Ton fruit préféré ?",
               shots=[
                   S('etab', 5, 'villa', [], "Slow aerial drone shot gliding over the villa and the pool, sparkling water, no characters"),
                   S('conf', 5, 'conf', ['berenice'], "sits with legs crossed, flips her imaginary hair, diva attitude",
                     [('berenice', "Je suis pas venue pour me faire des amis.")]),
                   S('scene', 5, 'salon', ['pepin'], "trips over a suitcase and falls face first onto a big cushion, then looks up embarrassed",
                     [('pepin', "Je suis juste… tombé dans les pommes.")], sfx='impact', gag='chute'),
                   S('react', 5, 'piscine', ['kiki'], "slow motion: Kiki's jaw drops and his sunglasses slide off his head into the pool as a mysterious mango character walks by", sfx='whoosh'),
                   S('scene', 5, 'portail', ['ananas'], "at night, Monsieur Ananas secretly hands a golden key to a feminine silhouette next to a suitcase with a mango sticker, suspense",
                     [('ananas', "Personne ne doit savoir… Bienvenue, ma chérie.")], sfx='riser'),
               ])

# Teaser (12 s) monté avec les plans déjà générés : Monsieur Ananas (Kling 3.0, site Kling, 16:9 recadré en
# 9:16 avec un panoramique vers l'inconnue) et Kiki (Wan 3.0 via Higgsfield). Plans dans NICHE_3_VILLA_VITAMINE/plans/teaser/.
TEASER = dict(id='teaser', num=0, titre="Teaser",
              accroche="Qui est cette inconnue ?",
              fin="ÉPISODE 1 · BIENTÔT",
              question="Qui est cette inconnue ? Tes théories en commentaire",
              shots=[
                  S('scene', 5, 'portail', ['ananas'], "at night, Monsieur Ananas secretly hands a golden key to a feminine silhouette next to a suitcase with a mango sticker",
                    [('ananas', "Personne ne doit savoir… Bienvenue, ma chérie.")], sfx='riser',
                    crop=dict(w=568, h=1010, x0=376, x1=1250, t0=2.2, t1=4.2)),
                  S('conf', 3, 'conf', ['kiki'], "rolls his eyes", [('kiki', "Moi, jaloux ? Jamais.")]),
              ])

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
    'cristal': dict(nom='en cristal', desc='carved from sparkling faceted crystal tinted in its natural colour', detail='Light refracts into tiny rainbows; slices break cleanly.', sound='high-pitched crystal clinks and crisp cracks'),
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
    'orange sanguine': 'blood orange', 'kumquat': 'pair of kumquats', 'yuzu': 'yuzu',
    'clémentine': 'clementine', 'cédrat': "Buddha's hand citron", 'bergamote': 'bergamot',
}


def A(subject_fr, material):
    return (subject_fr, material)


ASMR = [
    # version produite le 7 novembre (Veo 3.1 fast, plans de 8 s coupés à 7 s) : 12 plans
    dict(id='asmr_01', num=1, titre="Fruits rouges en verre", accroche="Le n°11 m'a donné des frissons", shot=7.0,
         accroche_ecran=["ATTENDS LE N°11…"], accroche_sous="(mets le son)",
         plans=[A(f, 'verre') for f in ['fraise', 'framboise', 'cerise', 'mûre', 'grenade', 'pastèque', 'myrtille', 'prune', 'figue',
                                         'raisin', 'myrtille géante', 'pastèque']]),
    dict(id='asmr_02', num=2, titre="Agrumes en cristal", accroche="Écoute le son du n°7", shot=7.0,
         accroche_ecran=["ÉCOUTE LE N°7…"], accroche_sous="(mets le son)",
         # 12 agrumes différents (comme le n°1) ; le n°7 (orange sanguine coupée au ralenti) est le plus spectaculaire.
         plans=[A(f, 'cristal') for f in ['citron', 'orange', 'citron vert', 'pamplemousse', 'mandarine', 'kumquat',
                                           'orange sanguine', 'yuzu', 'clémentine', 'cédrat', 'bergamote', 'pamplemousse']]),
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

# Nouveau style (à partir de l'épisode 2) : personnages-fruits à corps humain, tenues d'été, lumière de coucher de soleil
STYLE_NEW = ("Vertical 9:16 shot, hyper-detailed stylized 3D animation like a feature film, vibrant saturated colors, "
             "warm golden-hour tropical light, humanoid fruit characters with human-proportioned bodies, expressive fruit heads "
             "and stylish summer outfits, reality-TV parody, shallow depth of field.")
LOOK_NEW = dict(
    kiki="Kiki, a humanoid kiwi man: kiwi head with a bright green face and fuzzy brown skin, yellow sunglasses on top of his head, gold chain, colorful tropical shirt over a white tank top, beige shorts",
    berenice="Bérénice, a humanoid banana woman: tall yellow banana head with a brown stem, white cat-eye sunglasses, pink lips, gold hoop earrings, yellow crop top and yellow high-waisted trousers",
    cyril="Cyril, a humanoid lemon man: bumpy yellow lemon head with a small leaf, thick dark frowning eyebrows, grey t-shirt and blue jeans",
    pepin="Pépin, a humanoid green apple young man: shiny green apple head with a stem and two leaves, round black glasses, blushing cheeks, green polo shirt and beige shorts, slightly shorter than the others",
    fanny="Fanny, a humanoid strawberry woman: red strawberry head with yellow seeds and a green leafy hat, big blue eyes, pink sundress, always holding a pink phone",
    margaux="Margaux, a humanoid mango woman: orange-to-red gradient mango head with a wavy green leaf tuft and a pink hibiscus flower, flowing orange summer dress",
    ananas="Monsieur Ananas, a humanoid pineapple man: golden pineapple head with a tall leafy crown, red bow tie, white tuxedo jacket and black trousers, holding presenter cards",
    coco="Coco, a humanoid coconut man: hairy brown coconut head, dark sunglasses, white tank top on a bodybuilder body, gold chain",
)


def shot_prompt(shot, new_style=None):
    """new_style=None : nouveau style pour tous les épisodes sauf le 1 (déjà généré dans l'ancien style)."""
    if new_style is None:
        new_style = shot.get('_ep', 2) != 1
    if new_style:
        parts = [STYLE_NEW, f"Setting: {SETTINGS[shot['where']]}."]
        for c in shot['who']:
            parts.append((LOOK_NEW.get(c) or CHARACTERS[c]['look']) + '.')
        parts.append(f"Action: {shot['action']}.")
        if shot['kind'] == 'conf':
            parts.append("Reality-TV confessional framing: the character sits in a pastel pink armchair and faces the camera, medium close-up.")
        for line in shot['lines']:
            c = CHARACTERS[line[0]]
            if shot.get('off') or (len(line) > 2 and line[2] == 'off'):
                parts.append(f'{c["nom"]} is not visible; the voice is heard off-screen ({c["voix"]}) saying in French: "{line[1]}"')
            else:
                parts.append(f'{c["nom"]} says in French ({c["voix"]}): "{line[1]}"')
        parts.append("Lip-synced French dialogue, light villa ambience, no background music." if shot['lines']
                     else "No dialogue. Ambient sound only, no music.")
        return ' '.join(parts)
    return _shot_prompt_v1(shot)


def _shot_prompt_v1(shot):
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
        name = FRUITS[fr]
        art = 'an' if name[0].lower() in 'aeiou' else 'a'
        extra = ', revealing a deep ruby-red crystal inside' if fr == 'orange sanguine' else ''
        subject = f"{art} {name} {m['desc']}{extra}, {surface}"
    return ASMR_BASE.format(action=act, subject=subject, detail=m['detail'], sound=m['sound'])


def falls_before(ep_id):
    """Nombre de chutes de Pépin dans les épisodes précédents (compteur cumulé à l'écran)."""
    n = 0
    for ep in EPISODES:
        if ep['id'] == ep_id:
            return n
        n += sum(1 for s in episode_shots(ep) if s.get('gag') == 'chute')
    return n


def episode_shots(ep, eliminated='coco'):
    shots = [dict(sh, _ep=ep.get('num', 2)) for sh in ep['shots']]
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
