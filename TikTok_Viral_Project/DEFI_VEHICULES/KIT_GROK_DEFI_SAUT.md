# Kit Grok : « Quel véhicule saute le plus loin ? »

Nouveau format pour un autre compte, inspiré du défi de sauts de voitures, avec notre propre version :
- pas de marques, mais des **types de véhicules** (citadine, bus scolaire, F1, monster truck…) ;
- un **tremplin en bois**, une **rangée de conteneurs colorés** et un **mur de béton blanc** au bout.

**Le principe :** chaque véhicule prend de l'élan, saute, et on compte le nombre de conteneurs qu'il passe avant de
s'écraser. Une vidéo, c'est 10 véhicules et environ 1 minute.

## Comment faire

1. **Le décor, une seule fois.** Dans **ChatGPT**, colle le prompt « Décor » ci-dessous. Garde l'image : c'est elle qui
   rend tous les clips cohérents.
2. **Pour chaque véhicule :**
   - Dans **ChatGPT**, joins l'image du décor et colle le prompt « Image » du véhicule. Tu obtiens l'image de départ.
   - Dans **Grok**, importe cette image et colle le prompt « Animation » du véhicule.
   - Format **9:16**, clip le plus long possible (10 s), son activé.
3. **Envoie-moi les 10 clips ici**, numérotés de 1 à 10. Le numéro peut être dans le nom du fichier.

Si un saut ne ressemble pas à ce qui est demandé (il saute trop ou pas assez loin), ce n'est pas grave : je compte les
conteneurs sur ce qu'on voit vraiment, et le classement suit.

## Ce que j'ajoute au montage

- **En haut :** l'accroche « Quel véhicule saute le plus loin ? » au début, puis le tableau des scores, avec une vignette
  de chaque véhicule (tirée de tes clips). Le score s'inscrit sous la vignette après chaque saut.
- **Pendant chaque saut :**
  - le nom du véhicule en grand, dit par une voix (« Le bus scolaire ! ») ;
  - le gros compteur de conteneurs pendant le vol ;
  - un bruit d'impact à l'atterrissage.
- **Partout :** une musique énergique originale, sans droits d'auteur.
- **À la fin :** le classement (podium des 3 premiers) et la question « Ton pronostic ? » pour les commentaires.
- **La couverture.**

---

## Décor (ChatGPT, une seule fois)

Vertical 9:16 image, realistic driving simulation video game look, sunny day. A straight three-lane coastal highway
seen from behind and above, like a racing game chase camera. The sea is on the right, green wooded hills on the left,
metal guardrails on both sides. Further down the road, a large wooden launch ramp across the whole road. Right after
the ramp, a long row of about 40 colorful shipping containers (orange, blue, red, green, yellow, grey) lined up side by
side across the road, forming a long flat corridor of container roofs. At the far end, a big white concrete wall. No
vehicles, no text, no logos.

## Prompts « Image » (ChatGPT, joindre l'image du décor)

Début commun (déjà inclus) : *Use exactly the attached scene, same camera angle, same lighting. Vertical 9:16, realistic
driving simulation video game look, no text, no logos, no brand badges.*

1. **La citadine** : … Place a small yellow city hatchback car in the middle lane at the start of the road, seen from behind, heading toward the ramp.
2. **Le SUV** : … Place a big white SUV in the middle lane at the start of the road, seen from behind, heading toward the ramp.
3. **La voiture de police** : … Place a dark blue and white police sedan with red and blue roof lights in the middle lane, seen from behind, heading toward the ramp.
4. **Le bus scolaire** : … Place a long yellow school bus in the middle lane, seen from behind, heading toward the ramp.
5. **Le pick-up** : … Place a dark green pickup truck in the middle lane, seen from behind, heading toward the ramp.
6. **La sportive** : … Place a low red sports coupé in the middle lane, seen from behind, heading toward the ramp.
7. **Le camion de pompiers** : … Place a big red fire truck with a ladder on its roof in the middle lane, seen from behind, heading toward the ramp.
8. **Le monster truck** : … Place a purple monster truck with giant wheels in the middle lane, seen from behind, heading toward the ramp.
9. **L'hypercar** : … Place a very low orange hypercar with a rear wing in the middle lane, seen from behind, heading toward the ramp.
10. **La Formule 1** : … Place a green Formula 1 race car in the middle lane, seen from behind, heading toward the ramp.

## Prompts « Animation » (Grok, avec l'image du véhicule)

Début commun (déjà inclus) : *Realistic driving simulation game physics with soft-body crash deformation. The camera
follows the vehicle from behind and above, smooth chase camera, no cuts. Engine sound, wind, loud crash at the end.*

1. **La citadine** : … The yellow hatchback accelerates hard, hits the wooden ramp and flies over the row of containers, then lands on them about one third of the way along, bounces, loses a wheel and spins to a stop with smoke and debris.
2. **Le SUV** : … The white SUV accelerates, launches off the ramp, flies a short distance and slams down on the first containers, rolls over twice and stops upside down, glass shattering.
3. **La voiture de police** : … The police car, sirens flashing, races to the ramp at full speed, flies high over the containers, lands about halfway along, crumples its front and slides with sparks.
4. **Le bus scolaire** : … The heavy yellow school bus gains speed slowly, barely gets off the ramp, nose-dives onto the very first containers and crashes heavily, bending in the middle, dust everywhere.
5. **Le pick-up** : … The green pickup truck accelerates, jumps off the ramp, lands on the containers about a quarter of the way along, tumbles sideways and loses its tailgate.
6. **La sportive** : … The red sports coupé races at very high speed, flies far over the containers, lands about two thirds of the way along, its front crushes and it spins with smoke.
7. **Le camion de pompiers** : … The big red fire truck rumbles to the ramp, launches off clumsily, lands hard on the first few containers, the ladder breaks off and flies away.
8. **Le monster truck** : … The purple monster truck charges the ramp, bounces high off it with its giant wheels, flies over many containers and lands about halfway along, bouncing several times.
9. **L'hypercar** : … The orange hypercar launches at extreme speed, flies very far over the containers, lands near the end of the row and crashes into the white concrete wall, exploding into debris.
10. **La Formule 1** : … The green Formula 1 car launches at extreme speed, flies over almost all the containers and smashes into the white concrete wall at the end, its wheels and wings flying off.

## L'ordre de la vidéo

Je monte dans cet ordre pour garder du suspense, avec les plus rapides à la fin :
citadine, SUV, police, bus, pick-up, sportive, pompiers, monster truck, hypercar, F1.
