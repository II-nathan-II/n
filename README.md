# Studio TikTok automatisé — 10 vidéos virales en français

Ce dépôt contient **10 vidéos TikTok finalisées** (MP4 H.264/AAC, 1080×1920, plus d'une minute) et le pipeline Python qui les produit de A à Z : scripts, voix off, **montage de vraies séquences libres de droits (NASA)**, recadrage 9:16, transitions, sous-titres dynamiques, musique originale, export et contrôle qualité.

- **v2 (actuelle)** : montages d'images réelles — `pipeline/videos_real.py`, sources récupérées par `pipeline/footage.py` (NASA SVS, NASA Image and Video Library ; lecture partielle à distance des fichiers de plusieurs Go).
- **Niches 3 et 4 (prêtes à produire)** : « Villa Vitamine », télé-réalité de fruits en 10 épisodes, et « Cristal ASMR », 10 vidéos de 90 s. Elles sont écrites dans `pipeline/fruits_series.py` (personnages, dialogues, prompts) et montées par `pipeline/ai_assemble.py` à partir des plans générés par IA vidéo (Wan 3.0 via Higgsfield, crédits nécessaires).
- **v1** : version 100 % générée par code (illusions d'optique, espace procédural) — toujours disponible dans l'historique Git et via `TT_VERSION=v1`.

```
TikTok_Viral_Project/
├── NICHE_1/            # « Les secrets de l'Univers » : video_01.mp4 … video_05.mp4
├── NICHE_2/            # « Planète extrême »         : video_06.mp4 … video_10.mp4
├── NICHE_3_VILLA_VITAMINE/  # saison 1 écrite (bible, dialogues, prompts) — à générer
├── NICHE_4_CRISTAL_ASMR/    # série ASMR écrite (plans, prompts) — à générer
├── NICHE_3_ASMR_TEST/       # deux plans IA de test (fraise en verre, Kiki)
├── SCRIPTS/            # scripts complets minutés (+ sources des faits)
├── PUBLICATION/        # titres, descriptions, hashtags, accroches, couvertures, horaires (MD + CSV)
├── ANALYSE/            # analyse des tendances et des niches, droits, rapport de contrôle qualité
└── RECAPITULATIF.md    # caractéristiques techniques de chaque vidéo
pipeline/               # code de production
```

## Régénérer les vidéos

Prérequis : Python 3.11+, FFmpeg avec libx264 et libass.

```bash
pip install numpy scipy pillow opencv-python-headless soundfile onnxruntime kokoro-onnx numba pyloudnorm sherpa-onnx requests
```

Ressources (dans `/opt/assets`, modifiable via la variable `TT_ASSETS`) :
- `models/kokoro-v1.0.onnx` et `models/voices-v1.0.bin` — [kokoro-onnx, release model-files-v1.0](https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0)
- `models/sherpa-onnx-whisper-small/` — contrôle qualité uniquement ([sherpa-onnx asr-models](https://github.com/k2-fsa/sherpa-onnx/releases/tag/asr-models))
- `geo/ne_50m_land.geojson` — [Natural Earth](https://github.com/nvkelso/natural-earth-vector)
- `fonts/` — Anton, Poppins (ExtraBold, Black, SemiBold), Montserrat, Bebas Neue, Orbitron, Archivo Black ([google/fonts](https://github.com/google/fonts))

```bash
cd pipeline
python3 footage.py svs "black hole"     # chercher des séquences (svs | nasa | commons)
python3 build.py --jobs 3              # les 10 vidéos (télécharge les sources au besoin)
python3 build.py video_04 --preview    # aperçu rapide d'une vidéo
python3 qc.py                          # contrôle qualité (format, loudness, Whisper, synchro)
python3 docs.py                        # SCRIPTS/, PUBLICATION/, RECAPITULATIF.md
python3 fruits_docs.py                 # documents des niches 3 et 4
python3 ai_assemble.py episode_01      # montage d'un épisode à partir des plans IA ($TT_AI_CLIPS/episode_01/01.mp4…)
python3 ai_assemble.py asmr_01 --placeholder   # animatique (cartons à la place des plans manquants)
```

Chaque vidéo est décrite dans `pipeline/videos_real.py` : une liste de segments (texte de narration, extrait vidéo `V(source, point d'entrée, …)`, caméra, transition, effets sonores, intensité musicale). Réseau requis : `images-api.nasa.gov`, `images-assets.nasa.gov`, `svs.gsfc.nasa.gov`. Le balisage `{affiché|prononcé}` permet d'afficher « 7 000 km/h » tout en faisant dire « sept mille kilomètres par heure ».
