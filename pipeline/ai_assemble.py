"""Montage des vidéos IA (niche 3 « Villa Vitamine », niche 4 « Cristal ASMR ») à partir des plans générés.

Plans attendus : $TT_AI_CLIPS/<video_id>/<NN>.mp4 (NN = numéro du plan, 01…), produits par Wan 3.0
via Higgsfield ou par Veo 3.1 (Ace Data) avec le son natif (dialogues, ambiance, sons ASMR). Le manifeste
`ai_clips_manifest.json` garde l'identifiant et l'URL de chaque génération pour pouvoir les retélécharger.

    python3 ai_assemble.py episode_01                # monte l'épisode (plans manquants → erreur)
    python3 ai_assemble.py episode_01 --placeholder  # animatique : plans manquants remplacés par des cartons
    python3 ai_assemble.py episode_10 --eliminated cyril
    python3 ai_assemble.py --fetch                   # retélécharge les plans listés dans le manifeste
    python3 ai_assemble.py episode_01 --skip-missing # version courte sans les plans non générés
"""
import os, sys, json, subprocess, re, shutil
import numpy as np
import soundfile as sf
from common import W, H, FPS, SR, FONTS, WORK, PROJECT, ASSETS, text_sprite, to_u8
import fruits_series as FS
import fruits_histoires as FH
from captions import ass_time, bgr, chunk_words
import audio

CLIPS = os.environ.get('TT_AI_CLIPS', os.path.join(ASSETS, 'ai_clips'))
MANIFEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ai_clips_manifest.json')
OUT_DIRS = {'episode': os.path.join(PROJECT, 'NICHE_3_VILLA_VITAMINE'), 'asmr': os.path.join(PROJECT, 'NICHE_4_CRISTAL_ASMR')}
END_CARD = 3.5


def run(cmd):
    subprocess.run(cmd, check=True)


def probe_dur(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path], capture_output=True, text=True)
    return float(r.stdout.strip())


def fetch():
    """Télécharge les plans du manifeste qui manquent localement."""
    import requests
    man = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {}
    for vid, shots in man.items():
        for n, info in shots.items():
            dst = os.path.join(CLIPS, vid, f'{int(n):02d}.mp4')
            if os.path.exists(dst) or not info.get('url'):
                continue
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with requests.get(info['url'], stream=True, timeout=120) as r:
                r.raise_for_status()
                with open(dst + '.part', 'wb') as f:
                    for chunk in r.iter_content(1 << 20):
                        f.write(chunk)
            os.replace(dst + '.part', dst)
            print('téléchargé', dst, flush=True)


# ─────────────────────────── plans ───────────────────────────

def placeholder(path_mp4, path_wav, dur, title, lines, color):
    """Carton d'animatique pour un plan pas encore généré."""
    img = np.zeros((H, W, 3), np.float32)
    c = np.array([int(color[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255
    g = np.linspace(0.35, 0.12, H, dtype=np.float32)[:, None, None]
    img[:] = c * g
    from common import blit_rgba
    spr = text_sprite(title, 'poppins_xb', 54, (255, 255, 255), 0, (0, 0, 0), None, 8, int(W * 0.84), 0, 'center')
    blit_rgba(img, spr, W / 2, 520)
    spr = text_sprite('PLAN À GÉNÉRER', 'poppins_black', 64, (255, 225, 53), 0, (0, 0, 0), None, 8, None, 0, 'center')
    blit_rgba(img, spr, W / 2, 330)
    png = path_mp4 + '.png'
    import cv2
    cv2.imwrite(png, cv2.cvtColor(to_u8(np.clip(img, 0, 1)), cv2.COLOR_RGB2BGR))
    run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-t', f'{dur:.3f}', '-i', png, '-vf', f'fps={FPS},format=yuv420p',
         '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', path_mp4])
    sf.write(path_wav, np.zeros((int(dur * SR), 2), np.float32), SR)


def normalize(src, path_mp4, path_wav, dur, crop=None):
    """Plan généré → 1080×1920, 30 i/s, durée fixée ; son à part en WAV 48 kHz stéréo.
    crop : recadrage 9:16 d'une source horizontale, avec panoramique de x0 à x1 entre t0 et t1 (secondes),
    en excluant le bas de l'image (filigrane) par la hauteur h."""
    if crop:
        c = crop
        x = (f"st(0,clip((t-{c['t0']})/{c['t1'] - c['t0']},0,1));"
             f"{c['x0']}+({c['x1'] - c['x0']})*ld(0)*ld(0)*(3-2*ld(0))")
        vf = (f"crop={c['w']}:{c['h']}:'{x}':0,scale={W}:{H}:flags=lanczos,"
              f'unsharp=5:5:0.6:5:5:0,fps={FPS},format=yuv420p')
    else:
        vf = (f'scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},'
              f'unsharp=5:5:0.45:5:5:0,fps={FPS},format=yuv420p')
    run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-t', f'{dur:.3f}', '-an', '-vf', vf,
         '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', path_mp4])
    tmp = path_wav + '.tmp.wav'
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-t', f'{dur:.3f}', '-vn', '-ac', '2', '-ar', str(SR), tmp])
    n = int(round(dur * SR))
    if r.returncode == 0 and os.path.exists(tmp):
        a, _ = sf.read(tmp, dtype='float32', always_2d=True); os.remove(tmp)
    else:
        a = np.zeros((n, 2), np.float32)
    a = a[:n] if len(a) >= n else np.pad(a, ((0, n - len(a)), (0, 0)))
    f = int(0.015 * SR)
    a[:f] *= np.linspace(0, 1, f)[:, None]; a[-f:] *= np.linspace(1, 0, f)[:, None]
    sf.write(path_wav, a, SR)


def speech_window(a, dur):
    """Fenêtre où l'on parle dans un plan (énergie 300–3400 Hz) ; repli : tout le plan."""
    if a is None or np.abs(a).max() < 1e-4:
        return 0.3, max(0.6, dur - 0.3)
    from scipy.signal import butter, sosfilt
    mono = a.mean(1)
    sos = butter(4, [300, 3400], btype='band', fs=SR, output='sos')
    b = sosfilt(sos, mono)
    hop = int(0.02 * SR)
    e = np.sqrt(np.convolve(b ** 2, np.ones(hop) / hop, mode='same'))[::hop]
    thr = max(np.percentile(e, 20) * 3.0, np.percentile(e, 95) * 0.25)
    on = np.where(e > thr)[0]
    if len(on) < 5:
        return 0.3, max(0.6, dur - 0.3)
    return max(0.0, on[0] * 0.02 - 0.05), min(dur, on[-1] * 0.02 + 0.15)


# ─────────────────────────── habillage (ASS) ───────────────────────────

def ass_header():
    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Poppins ExtraBold,150,{bgr('FFFFFF')},{bgr('FFFFFF')},{bgr('000000')},{bgr('000000', 0x70)},0,0,0,0,100,100,0,0,1,8,3,5,60,60,0,1
Style: Show,Poppins Black,112,{bgr('FFE135')},{bgr('FFE135')},{bgr('FF3D8B')},{bgr('000000', 0x60)},0,0,0,0,100,100,2,0,1,8,3,8,40,40,140,1
Style: Ep,Poppins ExtraBold,64,{bgr('FFFFFF')},{bgr('FFFFFF')},{bgr('000000')},{bgr('000000', 0x60)},0,0,0,0,100,100,0,0,1,6,2,8,40,40,290,1
Style: Hook,Poppins ExtraBold,126,{bgr('FFFFFF')},{bgr('FFFFFF')},{bgr('000000')},{bgr('000000', 0x70)},0,0,0,0,100,100,0,0,1,9,3,5,70,70,0,1
Style: Name,Poppins Black,104,{bgr('111111')},{bgr('111111')},{bgr('FFFFFF')},{bgr('000000', 0xFF)},0,0,0,0,100,100,0,0,3,16,0,7,70,60,0,1
Style: Role,Poppins SemiBold,64,{bgr('FFFFFF')},{bgr('FFFFFF')},{bgr('111111')},{bgr('000000', 0xFF)},0,0,0,0,100,100,0,0,3,12,0,7,70,60,0,1
Style: Conf,Poppins Black,60,{bgr('FFFFFF')},{bgr('FFFFFF')},{bgr('FF3D8B')},{bgr('000000', 0xFF)},0,0,0,0,100,100,3,0,3,12,0,9,60,60,170,1
Style: HookBox,Poppins Black,100,{bgr('111111')},{bgr('111111')},{bgr('FFE135')},{bgr('000000', 0x60)},0,0,0,0,100,100,0,0,3,22,4,5,70,70,0,1
Style: HookSub,Poppins ExtraBold,60,{bgr('FFFFFF')},{bgr('FFFFFF')},{bgr('000000')},{bgr('000000', 0x70)},0,0,0,0,100,100,0,0,1,6,2,5,70,70,0,1
Style: Count,Poppins ExtraBold,150,{bgr('FFE135')},{bgr('FFE135')},{bgr('000000')},{bgr('000000', 0x70)},0,0,0,0,100,100,0,0,1,9,3,5,60,60,0,1
Style: End,Poppins Black,150,{bgr('FFFFFF')},{bgr('FFFFFF')},{bgr('000000')},{bgr('000000', 0x70)},0,0,0,0,100,100,0,0,1,9,3,5,70,70,0,1
Style: Recap,Poppins SemiBold,74,{bgr('FFFFFF')},{bgr('FFFFFF')},{bgr('000000', 0x50)},{bgr('000000', 0xFF)},0,0,0,0,100,100,0,0,3,16,0,5,90,90,0,1
Style: Chute,Poppins Black,56,{bgr('14320A')},{bgr('14320A')},{bgr('B6F36A')},{bgr('000000', 0xFF)},0,0,0,0,100,100,1,0,3,14,0,9,60,60,270,1
Style: Word,Poppins ExtraBold,88,{bgr('FFFFFF')},{bgr('FFFFFF')},{bgr('000000')},{bgr('000000', 0x60)},0,0,0,0,100,100,1,0,1,7,2,5,60,60,0,1
Style: Duo,Poppins ExtraBold,76,{bgr('FFFFFF')},{bgr('FFFFFF')},{bgr('000000')},{bgr('000000', 0x60)},0,0,0,0,100,100,1,0,1,7,2,5,60,60,0,1
Style: EndSub,Poppins ExtraBold,86,{bgr('FFE135')},{bgr('FFE135')},{bgr('000000')},{bgr('000000', 0x70)},0,0,0,0,100,100,0,0,1,7,2,5,70,70,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def ev(style, t0, t1, text, layer=0):
    return f"Dialogue: {layer},{ass_time(t0)},{ass_time(t1)},{style},,0,0,0,,{text}\n"


def esc(s):
    return s.replace('{', '(').replace('}', ')').replace('\\', '/')


POP = r'{\fad(70,0)\t(0,90,\fscx108\fscy108)\t(90,180,\fscx100\fscy100)}'


def captions_for_line(t0, t1, who, text, lo=-1e9, hi=1e9, shift=0.0):
    """Sous-titres d'une réplique, découpés en blocs courts, couleur du personnage.
    Temps locaux au plan ; seuls les blocs dans [lo, hi] sont gardés, décalés de `shift`."""
    words = [dict(w=w) for w in text.split()]
    chunks = chunk_words(words, max_words=3, max_chars=18)
    lens = np.array([max(3, len(' '.join(x['w'] for x in ch))) for ch in chunks], np.float64)
    bounds = t0 + np.concatenate([[0], np.cumsum(lens)]) / lens.sum() * (t1 - t0)
    col = FS.CHARACTERS[who]['color']
    out = ''
    for ch, a, b in zip(chunks, bounds[:-1], bounds[1:]):
        a, b = max(a, lo), min(b, hi)
        if b - a < 0.15:
            continue
        txt = esc(' '.join(x['w'] for x in ch))
        out += ev('Cap', a + shift, b + shift, POP + '{\\pos(%d,1360)\\c%s&}' % (W // 2, bgr(col)) + txt)
    return out


def voiced_clock(a, w0, w1):
    """Temps « parlé » cumulé entre w0 et w1 (trames de 20 ms au-dessus du seuil de voix) : sert à poser les mots
    sur les moments où le personnage parle vraiment, pas sur les silences."""
    hop = 0.02
    n = max(1, int((w1 - w0) / hop))
    if a is None or np.abs(a).max() < 1e-4:
        return np.arange(1, n + 1) * hop, hop
    from scipy.signal import butter, sosfilt
    mono = a.mean(1)
    b = sosfilt(butter(4, [300, 3400], btype='band', fs=SR, output='sos'), mono)
    seg = b[int(w0 * SR):int(w0 * SR) + n * int(hop * SR)]
    seg = np.pad(seg, (0, max(0, n * int(hop * SR) - len(seg))))
    e = np.sqrt((seg.reshape(n, -1) ** 2).mean(1))
    thr = max(np.percentile(e, 20) * 2.0, np.percentile(e, 90) * 0.18)
    v = (e > thr).astype(np.float64)
    v = np.maximum(v, 0.08)                      # une petite part du temps aux silences : rien ne reste figé
    return np.cumsum(v) * hop, hop


def word_times(sh, a, dur):
    """Mots des répliques d'un plan et leurs instants de début/fin, posés sur la voix (voiced_clock)."""
    w0, w1 = speech_window(a, dur)
    words, line_of = [], []
    for k, ln in enumerate(sh['lines']):
        for w in ln[1].split():
            w = re.sub(r'^[«"“(]+|[»"”)]+$', '', w)
            if not re.search(r'[\wÀ-ÿ]', w):          # « ? », « ! », « ?! » isolés (espace français) : collés au mot d'avant
                if words and line_of[-1] == k:
                    words[-1] += w
                continue
            words.append(w); line_of.append(k)
    word_times.line_of = line_of
    if not words:
        return [], np.array([])
    weights = np.array([max(2.0, len(re.sub(r'[^\wÀ-ÿ]', '', w)) + 1.0) for w in words])
    clock, hop = voiced_clock(a, w0, w1)
    targets = np.concatenate([[0], np.cumsum(weights)]) / weights.sum() * clock[-1]
    times = w0 + np.searchsorted(clock, targets) * hop
    times[-1] = max(times[-1], w1)
    return words, times


PETITS_MOTS = set("c'est est pas que qui quoi les des une un le la mon ton son ma ta sa mes tes ses je tu il elle on nous vous ils "
                  "et ou mais donc dans pour avec sur sous par de du au aux ce ça cette ces y en ne n'est j'ai t'es t'as moi toi lui "
                  "oui non bon bah euh alors tout très plus qu'elle qu'il qu'on c'était j'suis".split())


def key_score(w, j):
    """Mot à mettre en jaune : le plus long, hors petits mots ; à égalité, le plus tardif (souvent la chute)."""
    core = re.sub(r'[^\wÀ-ÿ\']', '', w.lower())
    return (0 if core in PETITS_MOTS else len(core)) + 0.1 * j


def duo_caps(sh, a, dur, t_base, lo=0.0, hi=None):
    """Sous-titres en blocs de 2–3 mots (majuscules blanches), le mot le plus marquant en jaune."""
    if not sh['lines']:
        return ''
    hi = dur if hi is None else hi
    words, times = word_times(sh, a, dur)
    if not words:
        return ''
    line_of = word_times.line_of
    chunks = []
    for k in sorted(set(line_of)):                  # pas de bloc à cheval sur deux répliques
        chunks += chunk_words([dict(w=w, i=i) for i, w in enumerate(words) if line_of[i] == k], max_words=3, max_chars=20)
    out = ''
    for ch in chunks:
        a0, b0 = times[ch[0]['i']], max(times[ch[-1]['i'] + 1], times[ch[0]['i']] + 0.25)
        a1, b1 = max(a0, lo), min(b0, hi)
        if b1 - a1 < 0.12:
            continue
        key = max(range(len(ch)), key=lambda j: key_score(ch[j]['w'], j))
        txt = ' '.join((r'{\c%s&}' % bgr('FFD21F') + esc(x['w'].upper()) + r'{\c&HFFFFFF&}') if j == key else esc(x['w'].upper())
                       for j, x in enumerate(ch))
        out += ev('Duo', a1 + t_base - lo, b1 + t_base - lo, r'{\pos(540,1430)\fscx112\fscy112\t(0,80,\fscx100\fscy100)}' + txt)
    return out


def word_caps(sh, a, dur, t_base, lo=0.0, hi=None):
    """Sous-titres façon « un mot à la fois » (majuscules blanches, contour noir), calés sur la voix du plan."""
    if not sh['lines']:
        return ''
    hi = dur if hi is None else hi
    w0, w1 = speech_window(a, dur)
    words = [w for ln in sh['lines'] for w in ln[1].split()]
    words = [re.sub(r'^[«"“(]+|[»"”).,!?…:;]+$', '', w) for w in words]
    words = [w for w in words if re.search(r'[\wÀ-ÿ]', w)]
    if not words:
        return ''
    weights = np.array([max(2.0, len(re.sub(r'[^\wÀ-ÿ]', '', w)) + 1.0) for w in words])
    clock, hop = voiced_clock(a, w0, w1)
    targets = np.concatenate([[0], np.cumsum(weights)]) / weights.sum() * clock[-1]
    times = w0 + np.searchsorted(clock, targets) * hop
    times[-1] = max(times[-1], w1)
    out = ''
    for w, a0, b0 in zip(words, times[:-1], times[1:]):
        b0 = max(b0, a0 + 0.14)
        a1, b1 = max(a0, lo), min(b0, hi)
        if b1 - a1 < 0.08:
            continue
        out += ev('Word', a1 + t_base - lo, b1 + t_base - lo, r'{\pos(540,1420)\fscx115\fscy115\t(0,70,\fscx100\fscy100)}' + esc(w.upper()))
    return out


def shot_caps(sh, a, dur, t_base, lo=0.0, hi=None, mode='bloc'):
    if mode == 'mot':
        return word_caps(sh, a, dur, t_base, lo, hi)
    if mode == 'duo':
        return duo_caps(sh, a, dur, t_base, lo, hi)
    """Sous-titres de toutes les répliques d'un plan, calés sur la fenêtre où l'on parle."""
    if not sh['lines']:
        return ''
    hi = dur if hi is None else hi
    w0, w1 = speech_window(a, dur)
    lens = np.array([len(x[1]) for x in sh['lines']], np.float64)
    cuts = w0 + np.concatenate([[0], np.cumsum(lens)]) / lens.sum() * (w1 - w0)
    return ''.join(captions_for_line(a0, b0, ln[0], ln[1], lo, hi, t_base - lo)
                   for ln, a0, b0 in zip(sh['lines'], cuts[:-1], cuts[1:]))


def hook_box(spec, t0, t1, y):
    """Accroche d'ouverture : texte court en bandeau jaune (+ sous-titre éventuel), apparition « pop »."""
    lines = spec.get('accroche_ecran') or [spec['accroche']]
    out = ''
    for k, l in enumerate(lines[:2]):
        out += ev('HookBox', t0 + 0.08 * k, t1, POP + r'{\pos(540,%d)}' % (y + k * 150) + esc(l), layer=3)
    if spec.get('accroche_sous'):
        out += ev('HookSub', t0 + 0.3, t1, r'{\fad(120,0)\pos(540,%d)}' % (y + len(lines[:2]) * 150 + 10) + esc(spec['accroche_sous']), layer=3)
    return out


def flash(t):
    """Flash blanc d'une image sur toute la hauteur (transition ouverture choc → générique)."""
    return ev('Cap', max(0, t - 0.02), t + 0.25,
              r'{\an7\pos(0,0)\bord0\shad0\c&HFFFFFF&\alpha&H30&\t(0,250,\alpha&HFF&)\p1}m 0 0 l %d 0 %d %d 0 %d{\p0}' % (W, W, H, H), layer=5)


def loud_limit(x, target, ceiling=-2.0):
    """Gain + limiteur, recalé pour que le niveau intégré final tombe sur la cible malgré la limitation."""
    aim = target
    for _ in range(4):
        y = audio.limiter(audio.set_loudness(x, aim), ceiling)
        L = audio.loudness(y)
        if not np.isfinite(L) or abs(L - target) < 0.3:
            break
        aim += min(6.0, target - L)
    return y


# ─────────────────────────── montage ───────────────────────────

def react_from(prev_mp4, path_mp4, path_wav, dur):
    """Plan de réaction fabriqué au montage : dernière image du plan précédent, zoom dramatique (aucune génération)."""
    png = path_mp4 + '.png'
    run(['ffmpeg', '-v', 'error', '-y', '-sseof', '-0.15', '-i', prev_mp4, '-frames:v', '1', '-update', '1', png])
    n = int(round(dur * FPS))
    run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-i', png, '-t', f'{dur:.3f}',
         '-vf', f"scale={W * 2}:{H * 2},zoompan=z='1+0.30*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2.4-(ih/zoom/2.4)':d={n}:s={W}x{H}:fps={FPS},"
                f"eq=contrast=1.08:saturation=1.1,vignette=PI/4,format=yuv420p",
         '-frames:v', str(n), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', path_mp4])
    sf.write(path_wav, np.zeros((int(round(dur * SR)), 2), np.float32), SR)


COVER_DUR = 0.4


def prepend_cover(img, out, wd):
    """Met la couverture en toute première image (0,4 s, léger zoom) : c'est la couverture par défaut de TikTok."""
    n = int(round(COVER_DUR * FPS))
    cmp4 = os.path.join(wd, 'cover.mp4')
    run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-i', img, '-f', 'lavfi', '-i', f'anullsrc=r=48000:cl=stereo',
         '-vf', f"scale={W * 2}:{H * 2},zoompan=z='1+0.02*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},format=yuv420p",
         '-frames:v', str(n), '-t', f'{COVER_DUR:.3f}', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', '-c:a', 'aac', '-b:a', '192k', cmp4])
    tmp = out + '.cov.mp4'
    run(['ffmpeg', '-v', 'error', '-y', '-i', cmp4, '-i', out, '-filter_complex', '[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]',
         '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-maxrate', '8M', '-bufsize', '16M',
         '-profile:v', 'high', '-level', '4.2', '-pix_fmt', 'yuv420p', '-g', '60',
         '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
         '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-movflags', '+faststart', tmp])
    os.replace(tmp, out)


def build(vid, use_placeholders=False, eliminated='coco', skip_missing=False):
    """skip_missing : version courte quand des plans n'ont pas pu être générés (crédits) — les plans manquants sont
    retirés, un plan de réaction manquant est fabriqué à partir du plan précédent, et les plans dialogués sont gardés
    presque entiers (les répliques générées durent souvent plus que la durée prévue)."""
    is_trailer = vid in ('bande_annonce', 'teaser')
    is_story = vid.startswith('histoire')
    is_ep = vid.startswith('episode') or is_trailer or is_story
    pool = FH.HISTOIRES if is_story else FS.EPISODES if is_ep else FS.ASMR
    spec = {'bande_annonce': FS.TRAILER, 'teaser': FS.TEASER}.get(vid) or next(v for v in pool if v['id'] == vid)
    if is_ep:
        shots = FS.episode_shots(spec, eliminated)
        items = [(s['dur'], s) for s in shots]
    else:
        items = [(spec.get('shot', FS.ASMR_SHOT), dict(kind='asmr', plan=p)) for p in spec['plans']]
    wd = os.path.join(WORK, 'ai', vid)
    os.makedirs(wd, exist_ok=True)

    segs, t, missing = [], 0.0, []
    for i, (dur, sh) in enumerate(items, 1):
        src = os.path.join(CLIPS, vid, f'{i:02d}.mp4')
        mp4, wav = os.path.join(wd, f'n{i:02d}.mp4'), os.path.join(wd, f'n{i:02d}.wav')
        if os.path.exists(src):
            pd = probe_dur(src)
            d = min(dur, pd)
            if skip_missing and is_ep and sh.get('kind') not in ('etab', 'react'):
                d = max(d, pd - 0.3)
            normalize(src, mp4, wav, d, sh.get('crop') if is_ep else None)
            real = True
        else:
            missing.append(i)
            if skip_missing and is_ep and sh.get('kind') == 'react' and segs:
                d = min(dur, 2.4)
                react_from(segs[-1]['mp4'], mp4, wav, d)
                segs.append(dict(i=i, t0=t, dur=d, shot=sh, mp4=mp4, wav=wav, real=False))
                t += d
                continue
            if skip_missing or not use_placeholders:
                continue
            d = dur
            if is_ep:
                who = ', '.join(FS.CHARACTERS[c]['nom'] for c in sh['who']) or 'ambiance'
                title = f"Plan {i} · {sh['kind']} · {who}\n\n{sh['action']}"
                color = FS.CHARACTERS[sh['who'][0]]['color'] if sh['who'] else '4AA8FF'
            else:
                fr, mat = sh['plan']
                title = f"Plan {i} · {fr} {FS.MATERIALS[mat]['nom']}"; color = '6FA8DC'
            placeholder(mp4, wav, d, title, [], color)
            real = False
        segs.append(dict(i=i, t0=t, dur=d, shot=sh, mp4=mp4, wav=wav, real=real))
        t += d
    if missing and not use_placeholders and not skip_missing:
        raise SystemExit(f'{vid} : plans manquants {missing} dans {os.path.join(CLIPS, vid)} (ou --placeholder)')

    # ouverture choc : 3 s d'un plan fort de l'épisode, placées avant le générique (aucune génération en plus)
    cold = None
    if is_ep and spec.get('cold'):
        k, off, d = spec['cold']
        src_seg = next((x for x in segs if x['i'] == k), None)
        if src_seg:
            d = min(d, max(0.5, src_seg['dur'] - off))
            cmp4, cwav = os.path.join(wd, 'cold.mp4'), os.path.join(wd, 'cold.wav')
            run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{off:.3f}', '-i', src_seg['mp4'], '-t', f'{d:.3f}', '-an',
                 '-vf', f'fps={FPS},format=yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', cmp4])
            a, _ = sf.read(src_seg['wav'], dtype='float32', always_2d=True)
            ca = a[int(off * SR):int((off + d) * SR)].copy()
            ca = np.pad(ca, ((0, max(0, int(round(d * SR)) - len(ca))), (0, 0)))
            f = int(0.03 * SR)
            ca[:f] *= np.linspace(0, 1, f)[:, None]; ca[-f:] *= np.linspace(1, 0, f)[:, None]
            sf.write(cwav, ca, SR)
            for x in segs:
                x['t0'] += d
            cold = dict(i=0, t0=0.0, dur=d, shot=dict(kind='cold', who=[], lines=[]), mp4=cmp4, wav=cwav,
                        real=src_seg['real'], src=src_seg, off=off)
            segs.insert(0, cold)
            t += d

    # carton de fin : dernière image floutée + texte
    last = segs[-1]
    endpng = os.path.join(wd, 'end.png'); endmp4 = os.path.join(wd, 'end.mp4')
    run(['ffmpeg', '-v', 'error', '-y', '-sseof', '-0.1', '-i', last['mp4'], '-frames:v', '1', '-update', '1', endpng])
    run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-t', f'{END_CARD:.3f}', '-i', endpng,
         '-vf', f'boxblur=30:3,eq=brightness=-0.22:saturation=0.9,fps={FPS},format=yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', endmp4])
    total = t + END_CARD

    lst = os.path.join(wd, 'concat.txt')
    with open(lst, 'w') as f:
        for s in segs:
            f.write(f"file '{s['mp4']}'\n")
        f.write(f"file '{endmp4}'\n")
    master = os.path.join(wd, 'master.mp4')
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', master])

    # son natif bout à bout
    n = int(round(total * SR)) + SR
    native = np.zeros((n, 2), np.float32)
    shot_audio = {}
    for s in segs:
        a, _ = sf.read(s['wav'], dtype='float32', always_2d=True)
        k = int(round(s['t0'] * SR))
        native[k:k + len(a)] += a[:max(0, n - k)]
        shot_audio[s['i']] = a if s['real'] else None
    native = native[:int(round(total * SR))]

    # habillage
    ass = ass_header()
    caps_mode = spec.get('sous_titres', 'bloc')
    if is_ep:
        ts = cold['dur'] if cold else 0.0
        if cold:
            src = cold['src']
            ass += ev('Ep', 0, cold['dur'], r'{\fad(100,0)}CE SOIR À LA VILLA…')
            ass += hook_box(spec, 0.1, cold['dur'], 560)
            ass += shot_caps(src['shot'], shot_audio.get(src['i']), src['dur'], 0.0, cold['off'], cold['off'] + cold['dur'], mode=caps_mode)
            ass += flash(cold['dur'])
        if is_story:
            ass += ev('Ep', ts, ts + 3.0, r'{\fad(0,250)}' + esc(f"LES HISTOIRES DE LA VILLA · {spec['titre'].upper()}"))
        else:
            ass += ev('Show', ts, ts + 3.2, r'{\fad(0,250)}VILLA VITAMINE')
            ass += ev('Ep', ts, ts + 3.2, r'{\fad(0,250)}' + esc(f"ÉPISODE {spec['num']}/10 · {spec['titre'].upper()}" if spec['num'] else 'BIENTÔT SUR CE COMPTE'))
        first = segs[1] if cold else segs[0]
        if spec.get('recap'):
            ass += ev('Recap', first['t0'] + 0.2, first['t0'] + first['dur'] - 0.1, r'{\fad(150,150)\pos(540,1250)}' + esc(spec['recap']))
        elif not cold and not first['shot']['lines']:
            ass += ev('Hook', 0.15, first['dur'] - 0.1, POP + r'{\pos(540,1180)}' + esc(spec['accroche']))
        chute = FS.falls_before(spec['id']) if spec['num'] and not is_story else 0
        for x in segs:
            if x['shot'].get('gag') == 'chute' and not is_story:
                chute += 1
                ass += ev('Chute', x['t0'] + x['dur'] * 0.45, x['t0'] + x['dur'] - 0.05, POP + f'CHUTES DE PÉPIN : {chute}')
        seen = set()
        for s in segs:
            sh = s['shot']
            if sh['kind'] == 'conf':
                ass += ev('Conf', s['t0'] + 0.1, s['t0'] + s['dur'] - 0.1, r'{\fad(120,120)}CONFESSION')
            for c in ([] if is_story else sh['who']):
                if c in seen or (sh['kind'] in ('react', 'etab') and not sh['lines']):
                    continue
                seen.add(c)
                ch = FS.CHARACTERS[c]
                a, b = s['t0'] + 0.15, s['t0'] + min(s['dur'], 3.2)
                y = 420 + 190 * (len([x for x in sh['who'] if x in seen]) - 1)
                ass += ev('Name', a, b, r'{\fad(120,150)\pos(70,%d)\3c%s&}' % (y, bgr(ch['color'])) + esc(ch['nom'].upper()))
                ass += ev('Role', a + 0.1, b, r'{\fad(120,150)\pos(70,%d)}' % (y + 120) + esc(f"{ch['role']} · {ch['fruit']}"))
            ass += shot_caps(sh, shot_audio.get(s['i']), s['dur'], s['t0'], mode=caps_mode)
        te = t
        ass += ev('End', te + 0.1, total, POP + r'{\pos(540,820)}' + ('FIN' if is_story else 'VILLA VITAMINE' if not spec['num'] else 'À SUIVRE…' if spec['num'] < 10 else 'FIN DE LA SAISON 1'))
        ass += ev('EndSub', te + 0.25, total, r'{\fad(150,0)\pos(540,1010)}' + esc(spec.get('fin') or spec['suite']))
        cta = spec.get('vote') or spec.get('question') or 'Abonne-toi pour la suite'
        ass += ev('EndSub', te + 0.45, total, r'{\fad(150,0)\pos(540,1160)\c&HFFFFFF&}' + esc(cta))
        ass += ev('Ep', te + 0.65, total, r'{\fad(150,0)\pos(540,1290)}Abonne-toi pour ne rien rater')
    else:
        ass += hook_box(spec, 0.1, 3.2, 360)
        ass += ev('Ep', 3.0, t, r'{\fad(200,0)}' + esc(f"CRISTAL ASMR · {spec['titre'].upper()}"))
        N = len(segs)
        for s in segs:
            fr, mat = s['shot']['plan']
            ass += ev('Count', s['t0'] + 0.05, s['t0'] + s['dur'], POP + r'{\pos(540,1500)}' + f"{s['i']} / {N}")
        ass += ev('End', t + 0.1, total, POP + r'{\pos(540,860)}TON PRÉFÉRÉ ?')
        ass += ev('EndSub', t + 0.25, total, r'{\fad(150,0)\pos(540,1040)}Mets le numéro en commentaire')
    ass_path = os.path.join(wd, f'{vid}.ass')
    open(ass_path, 'w').write(ass)

    # mixage
    if is_ep:
        voice = native.mean(1)
        voice = audio.set_loudness(voice, -16.0) if np.abs(voice).max() > 1e-4 else voice
        markers = [(0, 0.55), (max(1, t - 8), 0.8), (t, 0.9)]
        music = audio.compose(dict(FS.SERIES_MUSIC), total, markers)[:len(voice)]
        music = audio.set_loudness(music, -27.0) * audio.duck_curve(voice, depth_db=-8.0)[:, None]
        mix = np.stack([voice, voice], 1) + music
        if cold:
            audio.add_at(mix, audio.sfx('whoosh', 0), max(0, cold['dur'] - 0.3), 0, 10 ** (-10 / 20))
        for s in segs:
            if s['shot'].get('sfx'):
                audio.add_at(mix, audio.sfx(s['shot']['sfx'], s['i']), s['t0'], 0, 10 ** (-12 / 20))
        mix = loud_limit(mix, -14.0)
    else:
        mix = native
        if np.abs(mix).max() > 1e-4:
            mix = loud_limit(mix, -15.0)
    wav = os.path.join(wd, f'{vid}_mix.wav')
    sf.write(wav, mix.astype(np.float32), SR)

    out_dir = os.path.join(OUT_DIRS['episode'], 'histoires') if is_story else OUT_DIRS['episode' if is_ep else 'asmr']
    if use_placeholders and missing:
        out_dir = os.path.join(wd, 'animatique')
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f'{vid}.mp4')
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', master, '-i', wav, '-map', '0:v:0', '-map', '1:a:0',
         '-vf', f'ass={ass_path}:fontsdir={FONTS}', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-maxrate', '7M', '-bufsize', '14M',
         '-profile:v', 'high', '-level', '4.2', '-pix_fmt', 'yuv420p', '-g', '60',
         '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
         '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-movflags', '+faststart', '-t', f'{total:.3f}', out + '.part.mp4'])
    os.replace(out + '.part.mp4', out)
    cov = spec.get('couverture')
    if cov and os.path.exists(os.path.join(PROJECT, cov)):
        prepend_cover(os.path.join(PROJECT, cov), out, wd)
        total += COVER_DUR
    print(f'[{vid}] {total:.1f} s → {out}' + (f'  (cartons : plans {missing})' if missing else ''), flush=True)
    return out


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if '--fetch' in sys.argv:
        fetch()
    elim = 'cyril' if '--eliminated' in sys.argv and 'cyril' in sys.argv else 'coco'
    ids = args or (['bande_annonce'] + [e['id'] for e in FS.EPISODES] + [v['id'] for v in FS.ASMR] if '--all' in sys.argv else [])
    for vid in ids:
        if vid == 'cyril':
            continue
        build(vid, '--placeholder' in sys.argv, elim, '--skip-missing' in sys.argv)
