"""Montage des vidéos IA (niche 3 « Villa Vitamine », niche 4 « Cristal ASMR ») à partir des plans générés.

Plans attendus : $TT_AI_CLIPS/<video_id>/<NN>.mp4 (NN = numéro du plan, 01…), produits par Wan 3.0
via Higgsfield avec le son natif (dialogues, ambiance, sons ASMR). Le manifeste
`ai_clips_manifest.json` garde l'identifiant et l'URL de chaque génération pour pouvoir les retélécharger.

    python3 ai_assemble.py episode_01                # monte l'épisode (plans manquants → erreur)
    python3 ai_assemble.py episode_01 --placeholder  # animatique : plans manquants remplacés par des cartons
    python3 ai_assemble.py episode_10 --eliminated cyril
    python3 ai_assemble.py --fetch                   # retélécharge les plans listés dans le manifeste
"""
import os, sys, json, subprocess, re, shutil
import numpy as np
import soundfile as sf
from common import W, H, FPS, SR, FONTS, WORK, PROJECT, ASSETS, text_sprite, to_u8
import fruits_series as FS
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


def normalize(src, path_mp4, path_wav, dur):
    """Plan généré → 1080×1920, 30 i/s, durée fixée ; son à part en WAV 48 kHz stéréo."""
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
Style: Count,Poppins ExtraBold,150,{bgr('FFE135')},{bgr('FFE135')},{bgr('000000')},{bgr('000000', 0x70)},0,0,0,0,100,100,0,0,1,9,3,5,60,60,0,1
Style: End,Poppins Black,150,{bgr('FFFFFF')},{bgr('FFFFFF')},{bgr('000000')},{bgr('000000', 0x70)},0,0,0,0,100,100,0,0,1,9,3,5,70,70,0,1
Style: Recap,Poppins SemiBold,74,{bgr('FFFFFF')},{bgr('FFFFFF')},{bgr('000000', 0x50)},{bgr('000000', 0xFF)},0,0,0,0,100,100,0,0,3,16,0,5,90,90,0,1
Style: Chute,Poppins Black,56,{bgr('14320A')},{bgr('14320A')},{bgr('B6F36A')},{bgr('000000', 0xFF)},0,0,0,0,100,100,1,0,3,14,0,9,60,60,270,1
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


def shot_caps(sh, a, dur, t_base, lo=0.0, hi=None):
    """Sous-titres de toutes les répliques d'un plan, calés sur la fenêtre où l'on parle."""
    if not sh['lines']:
        return ''
    hi = dur if hi is None else hi
    w0, w1 = speech_window(a, dur)
    lens = np.array([len(x[1]) for x in sh['lines']], np.float64)
    cuts = w0 + np.concatenate([[0], np.cumsum(lens)]) / lens.sum() * (w1 - w0)
    return ''.join(captions_for_line(a0, b0, who, txt, lo, hi, t_base - lo)
                   for (who, txt), a0, b0 in zip(sh['lines'], cuts[:-1], cuts[1:]))


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

def build(vid, use_placeholders=False, eliminated='coco'):
    is_trailer = vid == 'bande_annonce'
    is_ep = vid.startswith('episode') or is_trailer
    spec = FS.TRAILER if is_trailer else next(v for v in (FS.EPISODES if is_ep else FS.ASMR) if v['id'] == vid)
    if is_ep:
        shots = FS.episode_shots(spec, eliminated)
        items = [(s['dur'], s) for s in shots]
    else:
        items = [(FS.ASMR_SHOT, dict(kind='asmr', plan=p)) for p in spec['plans']]
    wd = os.path.join(WORK, 'ai', vid)
    os.makedirs(wd, exist_ok=True)

    segs, t, missing = [], 0.0, []
    for i, (dur, sh) in enumerate(items, 1):
        src = os.path.join(CLIPS, vid, f'{i:02d}.mp4')
        mp4, wav = os.path.join(wd, f'n{i:02d}.mp4'), os.path.join(wd, f'n{i:02d}.wav')
        if os.path.exists(src):
            d = min(dur, probe_dur(src))
            normalize(src, mp4, wav, d)
            real = True
        else:
            missing.append(i)
            if not use_placeholders:
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
    if missing and not use_placeholders:
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
    if is_ep:
        ts = cold['dur'] if cold else 0.0
        if cold:
            src = cold['src']
            ass += ev('Ep', 0, cold['dur'], r'{\fad(100,0)}CE SOIR À LA VILLA…')
            ass += ev('Hook', 0.1, cold['dur'], POP + r'{\pos(540,640)}' + esc(spec['accroche']))
            ass += shot_caps(src['shot'], shot_audio.get(src['i']), src['dur'], 0.0, cold['off'], cold['off'] + cold['dur'])
            ass += flash(cold['dur'])
        ass += ev('Show', ts, ts + 3.2, r'{\fad(0,250)}VILLA VITAMINE')
        ass += ev('Ep', ts, ts + 3.2, r'{\fad(0,250)}' + esc(f"ÉPISODE {spec['num']}/10 · {spec['titre'].upper()}" if spec['num'] else 'BIENTÔT SUR CE COMPTE'))
        first = segs[1] if cold else segs[0]
        if spec.get('recap'):
            ass += ev('Recap', first['t0'] + 0.2, first['t0'] + first['dur'] - 0.1, r'{\fad(150,150)\pos(540,1250)}' + esc(spec['recap']))
        elif not cold and not first['shot']['lines']:
            ass += ev('Hook', 0.15, first['dur'] - 0.1, POP + r'{\pos(540,1180)}' + esc(spec['accroche']))
        chute = FS.falls_before(spec['id']) if spec['num'] else 0
        for x in segs:
            if x['shot'].get('gag') == 'chute':
                chute += 1
                ass += ev('Chute', x['t0'] + x['dur'] * 0.45, x['t0'] + x['dur'] - 0.05, POP + f'CHUTES DE PÉPIN : {chute}')
        seen = set()
        for s in segs:
            sh = s['shot']
            if sh['kind'] == 'conf':
                ass += ev('Conf', s['t0'] + 0.1, s['t0'] + s['dur'] - 0.1, r'{\fad(120,120)}CONFESSION')
            for c in sh['who']:
                if c in seen or (sh['kind'] in ('react', 'etab') and not sh['lines']):
                    continue
                seen.add(c)
                ch = FS.CHARACTERS[c]
                a, b = s['t0'] + 0.15, s['t0'] + min(s['dur'], 3.2)
                y = 420 + 190 * (len([x for x in sh['who'] if x in seen]) - 1)
                ass += ev('Name', a, b, r'{\fad(120,150)\pos(70,%d)\3c%s&}' % (y, bgr(ch['color'])) + esc(ch['nom'].upper()))
                ass += ev('Role', a + 0.1, b, r'{\fad(120,150)\pos(70,%d)}' % (y + 120) + esc(f"{ch['role']} · {ch['fruit']}"))
            ass += shot_caps(sh, shot_audio.get(s['i']), s['dur'], s['t0'])
        te = t
        ass += ev('End', te + 0.1, total, POP + r'{\pos(540,820)}' + ('VILLA VITAMINE' if not spec['num'] else 'À SUIVRE…' if spec['num'] < 10 else 'FIN DE LA SAISON 1'))
        ass += ev('EndSub', te + 0.25, total, r'{\fad(150,0)\pos(540,1010)}' + esc(spec.get('fin') or spec['suite']))
        cta = spec.get('vote') or spec.get('question') or 'Abonne-toi pour la suite'
        ass += ev('EndSub', te + 0.45, total, r'{\fad(150,0)\pos(540,1160)\c&HFFFFFF&}' + esc(cta))
        ass += ev('Ep', te + 0.65, total, r'{\fad(150,0)\pos(540,1290)}Abonne-toi pour ne rien rater')
    else:
        ass += ev('Hook', 0.1, 3.0, POP + r'{\pos(540,330)}' + esc(spec['accroche']))
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

    out_dir = OUT_DIRS['episode' if is_ep else 'asmr']
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
        build(vid, '--placeholder' in sys.argv, elim)
