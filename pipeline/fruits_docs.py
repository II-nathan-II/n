"""Documents des niches 3 (Villa Vitamine) et 4 (Cristal ASMR) : bible, scripts, prompts, publication, budget."""
import os
from common import PROJECT
import fruits_series as FS

N3 = os.path.join(PROJECT, 'NICHE_3_VILLA_VITAMINE')
N4 = os.path.join(PROJECT, 'NICHE_4_CRISTAL_ASMR')
KIND = {'etab': 'Ambiance', 'scene': 'Scène', 'conf': 'Confession', 'host': 'Présentateur', 'react': 'Réaction'}

EP_PUB = {  # horaire, idée de couverture
    1: ("Lundi 19 h 00", "Kiki lunettes sur la tête devant la piscine ; texte « ÉPISODE 1 : ILS ARRIVENT »"),
    2: ("Mardi 19 h 00", "Les lunettes de Kiki qui tombent en voyant Margaux ; « LA NOUVELLE »"),
    3: ("Mercredi 19 h 00", "Bérénice et Margaux face à face au transat ; « CLASH »"),
    4: ("Jeudi 19 h 00", "Kiki en sueur sous le projecteur ; « BÉRÉNICE OU MARGAUX ? »"),
    5: ("Vendredi 19 h 00", "Silhouette de Coco à contre-jour ; « L'EX DÉBARQUE »"),
    6: ("Samedi 18 h 00", "Cyril éclairé par l'écran du téléphone ; « LE PIÈGE »"),
    7: ("Dimanche 18 h 00", "Le gâteau qui tombe dans la piscine ; « QUI A FAIT ÇA ? »"),
    8: ("Lundi 19 h 00", "Fanny brandit son téléphone ; « J'AI TOUT FILMÉ »"),
    9: ("Mardi 19 h 00", "Coco et Cyril sous lumière rouge ; « C'EST TOI QUI VOTES »"),
    10: ("Jeudi 19 h 00 (48 h de vote)", "Enveloppe dorée ; « LE VERDICT »"),
}


def fmt(t):
    return f'{int(t // 60):02d}:{t % 60:04.1f}'


def credits(sec, res='720p'):
    return round(sec * FS.CREDITS_PER_SECOND[res] * FS.RETAKE)


def villa():
    os.makedirs(N3, exist_ok=True)
    L = ["# Villa Vitamine — saison 1", "",
         "Mini-série de télé-réalité humoristique en 10 épisodes de 80 à 90 s, jouée par des fruits en animation 3D. "
         "L'univers et les personnages sont originaux : on reprend les codes du genre (villa du Sud, confessions, clashs, soirées, "
         "nominations), pas une émission ni des personnes réelles. Tout public.", "",
         "## Personnages", "", "| Personnage | Fruit | Rôle | Réplique culte | Voix (consigne IA) |", "|---|---|---|---|---|"]
    for c in FS.CHARACTERS.values():
        L.append(f"| **{c['nom']}** | {c['fruit']} | {c['role']} | {c['replique']} | {c['voix']} |")
    L += ["", "## Ce qui doit faire accrocher", "",
          "| Levier | Dans la série |", "|---|---|",
          "| **Ouverture choc (0–3 s)** | Chaque épisode commence par 3 s de son moment le plus fort (« CE SOIR À LA VILLA… » + accroche), puis le générique. Cet extrait est repris d'un plan de l'épisode : aucune génération en plus |",
          "| **« Précédemment… »** | Rappel en une phrase sur le premier plan : un spectateur qui tombe sur l'épisode 6 comprend tout de suite |",
          "| **Un mystère sur toute la saison** | Qui est Margaux pour Monsieur Ananas ? Les indices tombent épisode après épisode, révélation au final : les spectateurs font leurs théories en commentaire |",
          "| **Gag récurrent** | Pépin tombe dans chaque épisode ; le compteur « CHUTES DE PÉPIN » à l'écran devient un rendez-vous (7 chutes dans la saison) |",
          "| **Répliques cultes** | « Moi, jaloux ? Jamais. » · « C'est pas pour être acide, mais… » · « Vous savez pas la nouvelle ? » · « mi-figue, mi-raisin » · « On est un smoothie » |",
          "| **Une question à chaque fin** | « Team Bérénice ou Team Margaux ? », « Qui a mis la peau de banane ? »… sur le carton de fin et en commentaire épinglé |",
          "| **Le public décide** | Vote Coco ou Cyril à l'épisode 9 ; l'épisode 10 montre l'élimination choisie (deux versions prévues) |",
          "", "## Fil rouge", "",
          "1. **Arrivées (ép. 1)** : Kiki drague, Bérénice règne, Cyril pique, Pépin tombe, Fanny répand les nouvelles. La nuit, Monsieur Ananas donne en secret une clé à une inconnue : « Personne ne doit savoir… Bienvenue, ma chérie. »",
          "2. **Le triangle (ép. 2–4)** : Margaux arrive, Kiki est sous le charme, Bérénice voit rouge. Clash au transat, jeu de la vérité, Kiki « mi-figue, mi-raisin ».",
          "3. **Le retour de l'ex (ép. 5)** : Coco débarque… pour Margaux. Monsieur Ananas : « Pas dans ma villa. »",
          "4. **Complot et enquête (ép. 6–8)** : faux message de Cyril, gâteau dans la piscine (et Pépin avec). La vidéo de Fanny démasque Coco… et montre Margaux en train de faire un câlin à Monsieur Ananas.",
          "5. **Le public décide (ép. 9)** : Coco ou Cyril.",
          "6. **Final (ép. 10)** : élimination votée, révélation (« Monsieur Ananas, c'est mon père »), Kiki et Bérénice (« On est un smoothie »), Pépin et Fanny. Puis une lettre : « Ma fille, rejoins-moi à la Villa Tropicale. Maman. » Annonce de la saison 2.",
          "", "### Les indices du mystère de Margaux", "",
          "| Épisode | Indice |", "|---|---|",
          "| 1 | Monsieur Ananas accueille une inconnue en secret : « Bienvenue, ma chérie » |",
          "| 2 | Clin d'œil complice entre Monsieur Ananas et Margaux, que Fanny remarque |",
          "| 3 | Rumeur : « on a vu Margaux en cachette… avec un ananas ! » et appel secret de Margaux (« personne ne se doute de rien ») |",
          "| 4 | Cyril : « Qui t'appelle en cachette tous les soirs ? » Margaux se fige, Monsieur Ananas tire sur son nœud papillon, et la panne de courant tombe à pic |",
          "| 5 | Monsieur Ananas, jaloux comme un père : « Une noix de coco qui tourne autour de Margaux ? Pas dans ma villa. » |",
          "| 6 | Au téléphone : « Oui, papa… Non, personne ne sait. » |",
          "| 8 | Sur la vidéo de Fanny : Margaux fait un câlin à Monsieur Ananas, qui confisque le téléphone |",
          "| 9 | Cyril : « Bizarrement… la mangue n'est jamais nominée. » Margaux : « Demain, il faudra que je dise la vérité. » |",
          "| 10 | Révélation, puis lettre de la mère, qui lance la saison 2 |",
          ""]
    for ep in FS.EPISODES:
        shots = FS.episode_shots(ep)
        gen = sum(s['dur'] for s in shots)
        L += [f"## Épisode {ep['num']} — {ep['titre']}", "",
              f"**Ouverture choc (0–3 s) :** extrait du plan {ep['cold'][0]} — accroche à l'écran : « {ep['accroche']} »  ",
              *( [f"**Précédemment :** {ep['recap'].split(' : ', 1)[1]}  "] if ep.get('recap') else [] ),
              f"**Question finale :** {ep['question']}  ",
              f"**Durée :** {gen} s générées + 3 s d'ouverture + 3,5 s de carton de fin ≈ {gen + 6.5:.0f} s  ",
              f"**Fin :** À SUIVRE… {ep['suite']}" + (f" — **vote :** {ep['vote']}" if ep.get('vote') else ''), ""]
        if ep.get('note'):
            L += [f"> {ep['note']}", ""]
        L += ["| # | Temps | Type | Plan (consigne pour l'IA, en anglais) | Dialogue |", "|---|---|---|---|---|"]
        t = ep['cold'][2] if ep.get('cold') else 0   # temps dans la vidéo finale (après l'ouverture choc)
        for i, s in enumerate(shots, 1):
            who = ', '.join(FS.CHARACTERS[c]['nom'] for c in s['who'])
            if s.get('off'):
                who = (who + ', ' if who else '') + 'voix off de ' + ', '.join(FS.CHARACTERS[w]['nom'] for w, _ in s['lines'])
            dia = '<br>'.join(f"**{FS.CHARACTERS[w]['nom']}** : {txt}" for w, txt in s['lines']) or '—'
            sfx = f" *(son : {s['sfx']})*" if s.get('sfx') else ''
            if s.get('gag') == 'chute':
                sfx += ' **[chute de Pépin]**'
            L.append(f"| {i} | {fmt(t)} | {KIND[s['kind']]} | {who + ' — ' if who else ''}{s['action']}{sfx} | {dia} |")
            t += s['dur']
        if ep['id'] == 'episode_10':
            L += ["", "Variante si le public élimine Cyril (plans 4 et 5) :", ""]
            for s in ep['variante_cyril']:
                L.append(f"- {KIND[s['kind']]} — " + ' / '.join(f"**{FS.CHARACTERS[w]['nom']}** : {txt}" for w, txt in s['lines']))
        h, cov = EP_PUB[ep['num']]
        L += ["", "**Publication**", "",
              f"- Titre : {ep['accroche']} — Villa Vitamine ép. {ep['num']} 🍓",
              f"- Description : {ep['accroche']} Épisode {ep['num']}/10, la suite demain à 19 h. "
              + f"{ep['question']} 👇 (Contenu généré par IA)",
              f"- Hashtags : #villavitamine #telerealite #humour #fruits #serie",
              f"- Horaire : {h}", f"- Couverture : {cov}", ""]
    open(os.path.join(N3, 'SAISON_1.md'), 'w').write('\n'.join(L))

    P = ["# Villa Vitamine — prompts de génération", "",
         f"Modèle : **Wan 3.0** (Higgsfield), {FS.MODEL['resolution']}, 9:16, son natif activé (dialogues en français et ambiance). "
         "Un fichier par plan : `<épisode>/<NN>.mp4`. Pour garder les mêmes personnages d'un plan à l'autre, joindre la fiche "
         "du personnage (image de référence générée au début) en `image_references`.", "",
         "## Fiches personnages (images de référence)", ""]
    for k, c in FS.CHARACTERS.items():
        P += [f"- **{c['nom']}** — `Character reference sheet, front view, neutral pose, white background. {FS.STYLE} {c['look']}.`"]
    for ep in FS.EPISODES:
        P += ["", f"## Épisode {ep['num']} — {ep['titre']}", ""]
        for i, s in enumerate(FS.episode_shots(ep), 1):
            P += [f"**{ep['id']}/{i:02d}.mp4** — {s['dur']} s", "", "```", FS.shot_prompt(s), "```", ""]
    open(os.path.join(N3, 'PROMPTS_GENERATION.md'), 'w').write('\n'.join(P))


def asmr():
    os.makedirs(N4, exist_ok=True)
    L = ["# Cristal ASMR — série de 10 vidéos", "",
         f"Chaque vidéo enchaîne {len(FS.ASMR[0]['plans'])} plans de {FS.ASMR_SHOT} s, soit {len(FS.ASMR[0]['plans']) * FS.ASMR_SHOT} s, plus un carton de fin de 3,5 s. "
         "Ce sont des fruits en verre, cristal, glace, ambre, gelée, lave ou or, tranchés ou tapotés en macro. Le son est généré avec l'image : "
         "aucune voix ni musique protégée. Habillage : accroche (0–3 s), compteur « n / 18 », vote final (« Ton préféré ? Mets le numéro en commentaire »).", "",
         "| # | Titre | Accroche | Matières | Publication |", "|---|---|---|---|---|"]
    slots = ["Lundi 12 h 30", "Mardi 12 h 30", "Mercredi 12 h 30", "Jeudi 12 h 30", "Vendredi 12 h 30",
             "Samedi 11 h 00", "Dimanche 11 h 00", "Lundi 12 h 30", "Mardi 12 h 30", "Mercredi 12 h 30"]
    for v, slot in zip(FS.ASMR, slots):
        mats = sorted({FS.MATERIALS[m]['nom'] for _, m in v['plans']})
        L.append(f"| {v['num']} | {v['titre']} | {v['accroche']} | {', '.join(mats)} | {slot} |")
    for v in FS.ASMR:
        L += ["", f"## {v['num']}. {v['titre']}", ""]
        if v.get('note'):
            L += [f"> {v['note']}", ""]
        L.append(' · '.join(f"{i}. {fr} {FS.MATERIALS[m]['nom']}" for i, (fr, m) in enumerate(v['plans'], 1)))
        L += ["", f"- Titre : {v['titre']} 🔪✨ (ASMR)",
              f"- Description : {v['accroche']}… Lequel tu préfères ? Mets le numéro 👇 (Contenu généré par IA)",
              "- Hashtags : #asmr #satisfaisant #oddlysatisfying #fruits #cristalasmr",
              f"- Couverture : plan n°{1 + (v['num'] * 5) % 18} en gros plan, texte « {v['titre'].upper()} »"]
    open(os.path.join(N4, 'SERIE_ASMR.md'), 'w').write('\n'.join(L) + '\n')

    P = ["# Cristal ASMR — prompts de génération", "",
         f"Modèle : **Wan 3.0** (Higgsfield), {FS.MODEL['resolution']}, 9:16, {FS.ASMR_SHOT} s par plan, son natif activé. Un fichier par plan : `<vidéo>/<NN>.mp4`.", ""]
    for v in FS.ASMR:
        P += [f"## {v['num']}. {v['titre']}", ""]
        for i in range(len(v['plans'])):
            P += [f"**{v['id']}/{i + 1:02d}.mp4**", "", "```", FS.asmr_prompt(v, i), "```", ""]
    open(os.path.join(N4, 'PROMPTS_GENERATION.md'), 'w').write('\n'.join(P))


def budget_table():
    b, b4 = FS.budget('720p'), FS.budget('480p')
    ep = sum(c for _, c in b['episodes'].values()); asm = sum(c for _, c in b['asmr'].values())
    ep4 = sum(c for _, c in b4['episodes'].values()); asm4 = sum(c for _, c in b4['asmr'].values())
    one_ep = round(ep / len(b['episodes'])); one_as = round(asm / len(b['asmr']))
    return [
        "| Lot | 720p (recommandé) | 480p (plus économique, image moins nette) |", "|---|---|---|",
        f"| 1 épisode Villa Vitamine | ≈ {one_ep} crédits | ≈ {round(ep4 / 10)} crédits |",
        f"| 1 vidéo Cristal ASMR | ≈ {one_as} crédits | ≈ {round(asm4 / 10)} crédits |",
        f"| Saison 1 complète (10 épisodes) | ≈ {ep} crédits | ≈ {ep4} crédits |",
        f"| Série ASMR complète (10 vidéos) | ≈ {asm} crédits | ≈ {asm4} crédits |",
        f"| **Les 20 vidéos** | **≈ {b['total']} crédits** | **≈ {b4['total']} crédits** |",
        "", f"Base : Wan 3.0 à {FS.CREDITS_PER_SECOND['720p']} crédit/s en 720p et {FS.CREDITS_PER_SECOND['480p']} crédit/s en 480p "
        f"(tarifs relevés sur le compte le 6 novembre 2026), avec environ 30 % de plans à refaire. Il faut ajouter quelques crédits pour les 8 fiches personnages.",
    ]


if __name__ == '__main__':
    villa(); asmr()
    open(os.path.join(PROJECT, 'ANALYSE', 'budget_niches_3_4.md'), 'w').write('# Budget de génération — niches 3 et 4\n\n' + '\n'.join(budget_table()) + '\n')
    print('docs niches 3 et 4 écrits')
