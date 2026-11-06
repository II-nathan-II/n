# Studio TikTok automatisé — 10 vidéos virales en français

Ce dépôt contient **10 vidéos TikTok finalisées** (MP4 H.264/AAC, 1080×1920, 82 à 97 s) et le pipeline Python qui les a produites de A à Z : scripts, voix off, visuels générés, montage, sous-titres dynamiques, musique originale, export et contrôle qualité.

```
TikTok_Viral_Project/
├── NICHE_1/            # « Les secrets de l'Univers » : video_01.mp4 … video_05.mp4
├── NICHE_2/            # « Ton cerveau te ment »     : video_06.mp4 … video_10.mp4
├── SCRIPTS/            # scripts complets minutés (+ sources des faits)
├── PUBLICATION/        # titres, descriptions, hashtags, accroches, couvertures, horaires (MD + CSV)
├── ANALYSE/            # analyse des tendances et des niches, droits, rapport de contrôle qualité
└── RECAPITULATIF.md    # caractéristiques techniques de chaque vidéo
pipeline/               # code de production
```

## Régénérer les vidéos

Prérequis : Python 3.11+, FFmpeg avec libx264 et libass.

```bash
pip install numpy scipy pillow opencv-python-headless soundfile onnxruntime kokoro-onnx numba pyloudnorm sherpa-onnx
```

Ressources (dans `/opt/assets`, modifiable via la variable `TT_ASSETS`) :
- `models/kokoro-v1.0.onnx` et `models/voices-v1.0.bin` — [kokoro-onnx, release model-files-v1.0](https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0)
- `models/sherpa-onnx-whisper-small/` — contrôle qualité uniquement ([sherpa-onnx asr-models](https://github.com/k2-fsa/sherpa-onnx/releases/tag/asr-models))
- `geo/ne_50m_land.geojson` — [Natural Earth](https://github.com/nvkelso/natural-earth-vector)
- `fonts/` — Anton, Poppins (ExtraBold, Black, SemiBold), Montserrat, Bebas Neue, Orbitron, Archivo Black ([google/fonts](https://github.com/google/fonts))

```bash
cd pipeline
python3 build.py --jobs 3              # les 10 vidéos
python3 build.py video_04 --preview    # aperçu rapide d'une vidéo
python3 qc.py                          # contrôle qualité (format, loudness, Whisper, synchro)
python3 docs.py                        # SCRIPTS/, PUBLICATION/, RECAPITULATIF.md
```

Chaque vidéo est décrite dans `pipeline/videos_space.py` et `pipeline/videos_psy.py` : une liste de segments (texte de narration, scène, caméra, transition, effets sonores, intensité musicale). Le balisage `{affiché|prononcé}` permet d'afficher « 7 000 km/h » tout en faisant dire « sept mille kilomètres par heure ».
