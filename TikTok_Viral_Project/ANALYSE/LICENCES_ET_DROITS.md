# Droits des ressources utilisées (v2 — images réelles)

| Ressource | Origine | Licence / statut | Usage commercial |
|---|---|---|---|
| Séquences vidéo et photos | NASA Scientific Visualization Studio, NASA Image and Video Library (dont vidéos ISS de la NASA/JSC et données NOAA/GOES diffusées par la NASA) | **Domaine public** (médias NASA non soumis au droit d'auteur aux États-Unis) | ✅ — sans logo NASA ni suggestion de soutien ; mentionner « Images : NASA » |
| Bandes-son des vidéos NASA | — | Non utilisées (certaines contiennent de la musique sous licence) | — |
| Plans écartés | Interviews, présentateurs, logos, génériques, photos d'amateurs ou d'universités intégrées aux vidéos NASA | Droits tiers possibles → **non utilisés** | — |
| Scripts (10) | Rédigés pour ce projet | Originaux | ✅ |
| Habillage (sous-titres, compteurs, textes, effet de pluie) | Généré par `pipeline/` | Original | ✅ |
| Voix off | Synthèse locale **Kokoro-82M** (voix `ff_siwis`) | Apache 2.0 | ✅ (label « IA » conseillé) |
| Musiques (10) et effets sonores | Compositions procédurales (`pipeline/audio.py`) | Originales | ✅ |
| Polices | Anton, Poppins, Montserrat (Google Fonts) | SIL OFL 1.1 | ✅ |
| Outils | FFmpeg, Python (NumPy, SciPy, OpenCV, Pillow, Numba, ONNX Runtime) | Libres | ✅ |
| Contrôle qualité | Whisper small (sherpa-onnx), uniquement pour vérifier la narration | MIT | — |

Le détail des séquences utilisées (titre, crédit, page source) figure à la fin de chaque fichier de `SCRIPTS/`.

Wikimedia Commons avait été envisagé, avec des fichiers en domaine public ou CC BY : il a refusé les connexions depuis cet environnement (429), aucun fichier Commons n'est donc utilisé.

Références : [NASA Images and Media Usage Guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/).
