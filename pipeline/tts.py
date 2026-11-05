"""Narration : synthèse Kokoro (voix française ff_siwis), découpage par phrase, timing des mots.

Balisage du texte : {texte affiché|texte prononcé}  ex. {64|soixante-quatre}
"""
import re, json, os, functools, hashlib
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly, butter, sosfilt
from common import SR, ASSETS

MODEL = os.path.join(ASSETS, 'models', 'kokoro-v1.0.onnx')
VOICES = os.path.join(ASSETS, 'models', 'voices-v1.0.bin')

_k = None
def kokoro():
    global _k
    if _k is None:
        from kokoro_onnx import Kokoro
        _k = Kokoro(MODEL, VOICES)
    return _k

@functools.lru_cache(maxsize=4096)
def phoneme_count(word):
    w = re.sub(r"[^\wÀ-ÿ'’-]", '', word)
    if not w:
        return 0
    ph = kokoro().tokenizer.phonemize(w, 'fr-fr')
    return max(1, len(re.sub(r'[ˈˌː\s]', '', ph)))

UNIT_RE = re.compile(r'\{([^|}]*)\|([^}]*)\}|(\S+)')

def parse_units(text):
    """→ liste d'unités (caption, spoken)."""
    units = []
    for m in UNIT_RE.finditer(text):
        if m.group(3) is not None:
            tok = m.group(3)
            # gestion d'une ponctuation collée après un bloc {..|..}
            if units and re.fullmatch(r'[,.;:!?…»)]+', tok):
                c, s = units[-1]; units[-1] = (c + tok, s + tok); continue
            units.append((tok, tok))
        else:
            units.append((m.group(1), m.group(2)))
    return units

def spoken_text(text):
    return ' '.join(s for _, s in parse_units(text))

def caption_text(text):
    return ' '.join(c for c, _ in parse_units(text))

def _trim(a, sr, thr_db=-42, margin=0.03):
    env = np.abs(a)
    peak = env.max() + 1e-9
    thr = peak * 10 ** (thr_db / 20)
    idx = np.where(env > thr)[0]
    if len(idx) == 0:
        return a
    s = max(0, idx[0] - int(margin * sr)); e = min(len(a), idx[-1] + int(margin * sr * 2))
    return a[s:e]

def _silences(a, sr, min_len=0.085, thr_db=-34):
    hop = int(0.01 * sr)
    n = len(a) // hop
    if n == 0:
        return []
    fr = a[:n * hop].reshape(n, hop)
    rms = np.sqrt((fr ** 2).mean(1) + 1e-12)
    thr = rms.max() * 10 ** (thr_db / 20)
    sil = rms < thr
    runs, i = [], 0
    while i < n:
        if sil[i]:
            j = i
            while j < n and sil[j]:
                j += 1
            if (j - i) * 0.01 >= min_len and i > 0 and j < n:
                runs.append((i * 0.01, j * 0.01))
            i = j
        else:
            i += 1
    return runs

BREAK_RE = re.compile(r'[,;:…—–.!?]["»)]*$')

def word_timings(units, dur, silences):
    """Répartit les unités sur la durée parlée, en alignant les pauses internes sur la ponctuation."""
    weights = [phoneme_count(s) + 1.2 for _, s in units]
    total = sum(weights)
    cum = np.cumsum([0] + weights)
    breaks = [i for i, (c, _) in enumerate(units[:-1]) if BREAK_RE.search(c)]
    assigned = []  # (unit_index, sil_start, sil_end)
    used = set()
    for b in breaks:
        exp = cum[b + 1] / total * dur
        best, bd = None, 0.22 * dur + 0.15
        for k, (s0, s1) in enumerate(silences):
            if k in used:
                continue
            c = (s0 + s1) / 2
            if abs(c - exp) < bd and (not assigned or s0 >= assigned[-1][2]):
                best, bd = k, abs(c - exp)
        if best is not None:
            used.add(best); assigned.append((b, silences[best][0], silences[best][1]))
    # sous-portions
    out = [None] * len(units)
    spans, prev_i, prev_t = [], 0, 0.0
    for b, s0, s1 in assigned:
        spans.append((prev_i, b + 1, prev_t, s0)); prev_i, prev_t = b + 1, s1
    spans.append((prev_i, len(units), prev_t, dur))
    for i0, i1, t0, t1 in spans:
        wsum = sum(weights[i0:i1]) or 1
        t = t0
        for i in range(i0, i1):
            d = (t1 - t0) * weights[i] / wsum
            out[i] = (t, t + d); t += d
    return out

DEFAULT_PAUSE = {'.': 0.30, '!': 0.32, '?': 0.36, '…': 0.45, ',': 0.14, ':': 0.24, ';': 0.2}

def synthesize(video, workdir):
    """Synthétise tous les segments. Retourne (audio float32 48k mono, timeline dict)."""
    os.makedirs(workdir, exist_ok=True)
    cache = os.path.join(workdir, 'tts_cache')
    os.makedirs(cache, exist_ok=True)
    voice = video.get('voice', 'ff_siwis'); speed = video.get('speed', 1.1)
    pieces, segs, t = [], [], 0.0
    lead = video.get('lead_in', 0.15)
    pieces.append(np.zeros(int(lead * SR), np.float32)); t = lead
    for i, seg in enumerate(video['segments']):
        text = seg.get('text', '')
        if not text:
            hold = seg.get('hold', 1.0)
            pieces.append(np.zeros(int(hold * SR), np.float32))
            segs.append(dict(i=i, start=t, end=t + hold, speech_end=t, words=[]))
            t += hold
            continue
        units = parse_units(text)
        spk = ' '.join(s for _, s in units)
        sp = seg.get('speed', speed)
        key = re.sub(r'\W+', '_', f'{voice}_{sp}_{spk}')[:120] + '_' + hashlib.md5(spk.encode()).hexdigest()[:10] + '.wav'
        path = os.path.join(cache, key)
        if os.path.exists(path):
            a, sr = sf.read(path, dtype='float32')
        else:
            a, sr = kokoro().create(spk, voice=voice, speed=sp, lang='fr-fr')
            a = np.asarray(a, np.float32)
            sf.write(path, a, sr)
        a = _trim(a, sr)
        a = resample_poly(a, SR, sr).astype(np.float32)
        dur = len(a) / SR
        sil = _silences(a, SR)
        wt = word_timings(units, dur, sil)
        words = [dict(w=c, s=round(t + s0, 3), e=round(t + s1, 3)) for (c, _), (s0, s1) in zip(units, wt)]
        last = units[-1][0].rstrip('»")')[-1:]
        pause = seg.get('pause', DEFAULT_PAUSE.get(last, 0.22))
        pieces.append(a)
        pieces.append(np.zeros(int(pause * SR), np.float32))
        segs.append(dict(i=i, start=round(t, 3), speech_end=round(t + dur, 3), end=round(t + dur + pause, 3), words=words,
                         text=caption_text(text), spoken=spk))
        t += dur + pause
    tail = video.get('tail', 1.2)
    pieces.append(np.zeros(int(tail * SR), np.float32))
    audio = np.concatenate(pieces)
    audio = process_voice(audio, reverb=video.get('voice_reverb', 0.0))
    timeline = dict(duration=len(audio) / SR, segments=segs)
    return audio, timeline

def process_voice(a, reverb=0.0):
    sos = butter(2, 75, 'highpass', fs=SR, output='sos')
    a = sosfilt(sos, a).astype(np.float32)
    # légère compression (RMS glissant)
    win = int(0.03 * SR)
    env = np.sqrt(np.convolve(a * a, np.ones(win) / win, mode='same') + 1e-9)
    ref = np.percentile(env[env > 1e-3], 90) if np.any(env > 1e-3) else 1
    thr = ref * 0.5
    gain = np.where(env > thr, (thr / env) ** 0.35, 1.0)
    a = a * gain
    # légère présence (shelf aigu)
    sos2 = butter(1, 3500, 'highpass', fs=SR, output='sos')
    a = a + 0.18 * sosfilt(sos2, a)
    if reverb > 0:
        from audio import simple_reverb
        a = a + reverb * simple_reverb(a, decay=1.4, mono=True)
    a = a / (np.abs(a).max() + 1e-9) * 0.89
    return a.astype(np.float32)
