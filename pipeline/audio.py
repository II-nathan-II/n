"""Audio original : musique procédurale (aucun sample externe), effets sonores synthétisés, mixage et loudness."""
import numpy as np
from numba import njit
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.ndimage import minimum_filter1d
from common import SR

NOTE_A4 = 440.0
def midi_hz(m):
    return NOTE_A4 * 2 ** ((m - 69) / 12)


# ----------------------------------------------------------------------------- filtres
@njit(cache=True)
def onepole_lp_var(x, cutoff, sr):
    y = np.empty_like(x)
    z = 0.0
    for i in range(len(x)):
        a = 1.0 - np.exp(-2.0 * np.pi * cutoff[i] / sr)
        z += a * (x[i] - z)
        y[i] = z
    return y

@njit(cache=True)
def svf_bp_var(x, fc, q, sr):
    """Filtre passe-bande à état variable (Chamberlin), fréquence variable."""
    y = np.empty_like(x)
    low = 0.0; band = 0.0
    for i in range(len(x)):
        f = 2.0 * np.sin(np.pi * min(fc[i], sr / 6.0) / sr)
        high = x[i] - low - q * band
        band += f * high
        low += f * band
        y[i] = band
    return y

def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, 'lowpass', fs=SR, output='sos'), x, axis=0)

def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, 'highpass', fs=SR, output='sos'), x, axis=0)

def env_adsr(n, a, d, s, r, sustain_len):
    """Enveloppe ADSR en échantillons."""
    A, D, R = int(a * SR), int(d * SR), int(r * SR)
    S = max(0, int(sustain_len * SR) - A - D)
    e = np.concatenate([np.linspace(0, 1, max(A, 1)), np.linspace(1, s, max(D, 1)), np.full(S, s),
                        np.linspace(s, 0, max(R, 1))])
    if len(e) < n:
        e = np.pad(e, (0, n - len(e)))
    return e[:n].astype(np.float32)

_ir_cache = {}
def reverb_ir(decay=2.5, seed=3, stereo=True, damp=6000):
    key = (decay, seed, stereo, damp)
    if key not in _ir_cache:
        rng = np.random.default_rng(seed)
        n = int(decay * SR)
        t = np.arange(n) / SR
        chans = []
        for c in range(2 if stereo else 1):
            noise = rng.normal(0, 1, n)
            noise = lp(noise, damp, 1)
            ir = noise * np.exp(-6.9 * t / decay)
            ir[:int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
            chans.append(ir / np.sqrt((ir ** 2).sum()))
        _ir_cache[key] = np.stack(chans, 1).astype(np.float32)
    return _ir_cache[key]

def simple_reverb(x, decay=2.5, mono=False):
    ir = reverb_ir(decay, stereo=not mono)
    if mono:
        return fftconvolve(x, ir[:, 0])[:len(x)].astype(np.float32)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    return np.stack([fftconvolve(x[:, c], ir[:, c])[:len(x)] for c in range(2)], 1).astype(np.float32)


# ----------------------------------------------------------------------------- instruments
def add_at(buf, sig, t0, pan=0.0, gain=1.0):
    i0 = int(t0 * SR)
    if i0 < 0:
        sig = sig[-i0:]; i0 = 0
    if i0 >= len(buf):
        return
    n = min(len(sig), len(buf) - i0)
    if n <= 0:
        return
    l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
    if sig.ndim == 1:
        buf[i0:i0 + n, 0] += sig[:n] * gain * l * 1.414
        buf[i0:i0 + n, 1] += sig[:n] * gain * r * 1.414
    else:
        buf[i0:i0 + n] += sig[:n] * gain

def pad_note(freq, dur, rng, harmonics=10, bright=0.6, attack=1.2, release=1.8, detune=0.08):
    n = int((dur + release) * SR)
    t = np.arange(n) / SR
    out = np.zeros((n, 2), np.float32)
    for v, (dc, pan) in enumerate([(-detune, -0.6), (0.0, 0.0), (detune, 0.6)]):
        f = freq * 2 ** (dc / 12)
        ph = rng.uniform(0, 2 * np.pi)
        s = np.zeros(n, np.float32)
        for h in range(1, harmonics + 1):
            if f * h > 9000:
                break
            s += (np.sin(2 * np.pi * f * h * t + ph * h) / h ** (1.0 + (1 - bright))).astype(np.float32)
        l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
        out[:, 0] += s * l; out[:, 1] += s * r
    e = env_adsr(n, attack, 0.5, 0.85, release, dur)
    return out * e[:, None] * 0.12

def ep_note(freq, dur=1.6, vel=1.0, index=2.2, decay=1.4):
    """Piano électrique FM (type Rhodes)."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    I = index * np.exp(-t * 5) + 0.3
    s = np.sin(2 * np.pi * freq * t + I * np.sin(2 * np.pi * freq * t))
    s += 0.25 * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-t * 3)
    e = np.exp(-t / decay) * np.minimum(1, t / 0.004)
    return (s * e * vel * 0.25).astype(np.float32)

def pluck_note(freq, dur=1.2, vel=1.0, bright=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for h in range(1, 7):
        s += np.sin(2 * np.pi * freq * h * t) * (bright ** (h - 1)) * np.exp(-t * (2.5 + h * 1.5))
    e = np.minimum(1, t / 0.003)
    return (s * e * vel * 0.22).astype(np.float32)

def bell_note(freq, dur=3.0, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * freq * t + 1.5 * np.exp(-t * 1.5) * np.sin(2 * np.pi * freq * 3.5 * t))
    return (s * np.exp(-t / 1.1) * np.minimum(1, t / 0.002) * vel * 0.18).astype(np.float32)

def bass_note(freq, dur, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * freq * 2 * t)
    s = np.tanh(s * 1.4)
    e = env_adsr(n, 0.01, 0.2, 0.7, min(0.25, dur * 0.4), dur * 0.8)
    return (s * e * vel * 0.3).astype(np.float32)

def kick(vel=1.0):
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 45 + 95 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 7.5)
    s[:200] += np.random.default_rng(1).normal(0, 0.3, 200) * np.linspace(1, 0, 200)
    return (np.tanh(s * 1.5) * vel * 0.55).astype(np.float32)

def hat(vel=1.0, open_=False, seed=0):
    n = int((0.25 if open_ else 0.06) * SR)
    rng = np.random.default_rng(seed)
    s = hp(rng.normal(0, 1, n), 7000)
    t = np.arange(n) / SR
    s *= np.exp(-t * (14 if open_ else 60))
    return (s * vel * 0.12).astype(np.float32)

def snap(vel=1.0, seed=0):
    n = int(0.25 * SR)
    rng = np.random.default_rng(seed)
    t = np.arange(n) / SR
    s = sosfilt(butter(2, [900, 4500], 'bandpass', fs=SR, output='sos'), rng.normal(0, 1, n))
    s *= np.exp(-t * 22)
    return (s * vel * 0.35).astype(np.float32)


# ----------------------------------------------------------------------------- composition
PROGRESSIONS = {
    # accords en demi-tons relatifs à la tonique (tonalité mineure ou majeure)
    'minor_epic': [[0, 3, 7, 10], [8, 12, 15, 19], [3, 7, 10, 14], [10, 14, 17, 21]],    # i  VI  III  VII
    'minor_float': [[0, 3, 7, 14], [5, 8, 12, 15], [8, 12, 15, 19], [7, 10, 14, 17]],     # i  iv  VI  v
    'minor_dark': [[0, 3, 7, 10], [10, 14, 17, 20], [8, 12, 15, 19], [10, 14, 17, 21]],   # i VII VI VII
    'minor_wonder': [[0, 3, 7, 14], [8, 12, 15, 22], [5, 8, 12, 19], [7, 11, 14, 17]],    # i VI iv V
    'minor_drift': [[0, 7, 12, 15], [3, 10, 15, 19], [8, 15, 20, 24], [5, 12, 17, 20]],
    'lofi_a': [[2, 5, 9, 12], [7, 11, 14, 17], [0, 4, 7, 11], [9, 12, 16, 19]],           # ii7 V7 Imaj7 vi7
    'lofi_b': [[5, 9, 12, 16], [4, 7, 11, 14], [2, 5, 9, 12], [0, 4, 7, 11]],             # IVmaj7 iii7 ii7 Imaj7
    'lofi_c': [[0, 4, 7, 11], [9, 12, 16, 19], [5, 9, 12, 16], [7, 11, 14, 17]],          # Imaj7 vi7 IVmaj7 V7
    'lofi_d': [[9, 12, 16, 19], [5, 9, 12, 16], [0, 4, 7, 11], [7, 11, 14, 18]],
    'lofi_e': [[2, 5, 9, 12], [4, 7, 11, 14], [5, 9, 12, 16], [7, 11, 14, 17]],
}

def intensity_curve(markers, n):
    """markers : [(t, val)] ; val<0 = silence musical. → (gain_curve, intensity_curve)"""
    ts = np.array([m[0] for m in markers], np.float32)
    vs = np.array([m[1] for m in markers], np.float32)
    tt = np.arange(n) / SR
    # paliers lissés
    idx = np.clip(np.searchsorted(ts, tt, side='right') - 1, 0, len(vs) - 1)
    raw = vs[idx]
    mute = (raw < 0).astype(np.float32)
    inten = np.clip(raw, 0, 1)
    k = int(0.6 * SR)
    ker = np.ones(k, np.float32) / k
    inten = np.convolve(inten, ker, mode='same')
    km = int(0.25 * SR)
    mutes = np.convolve(mute, np.ones(km, np.float32) / km, mode='same')
    return (1 - mutes).astype(np.float32), inten.astype(np.float32)

def compose(cfg, duration, markers):
    """cfg : style, key (midi tonique), bpm, prog, seed. Retourne stéréo float32."""
    rng = np.random.default_rng(cfg.get('seed', 1))
    style = cfg['style']
    bpm = cfg['bpm']; beat = 60.0 / bpm; bar = beat * 4
    root = cfg['key']
    prog = PROGRESSIONS[cfg['prog']]
    n = int(duration * SR) + SR
    layers = {k: np.zeros((n, 2), np.float32) for k in ('pad', 'arp', 'bass', 'drums', 'tex')}
    bars_per_chord = cfg.get('bars_per_chord', 1 if style == 'lofi' else 2)
    chord_len = bar * bars_per_chord
    nchords = int(np.ceil(duration / chord_len)) + 1
    arp_pattern = cfg.get('arp', [0, 2, 1, 3, 2, 1, 3, 2])
    for ci in range(nchords):
        t0 = ci * chord_len
        ch = prog[ci % len(prog)]
        # pad
        for j, iv in enumerate(ch):
            f = midi_hz(root + iv + (0 if style != 'lofi' else 0))
            if style == 'lofi':
                pass
            else:
                add_at(layers['pad'], pad_note(f, chord_len, rng, bright=cfg.get('bright', 0.5),
                                               attack=min(1.6, chord_len * 0.4)), t0, 0, 1.0)
        # basse
        bf = midi_hz(root + ch[0] - 24 + (12 if ch[0] < 0 else 0))
        if style == 'lofi':
            add_at(layers['bass'], bass_note(bf, beat * 1.8), t0, 0, 1.0)
            add_at(layers['bass'], bass_note(bf, beat * 1.2, 0.8), t0 + beat * 2.5, 0, 1.0)
            # accords EP
            for k in range(2):
                for j, iv in enumerate(ch):
                    add_at(layers['pad'], ep_note(midi_hz(root + iv), dur=beat * 3.5, vel=0.9 - 0.1 * j),
                           t0 + k * beat * 2 + j * 0.012 + (beat * 0.5 if k else 0), pan=-0.3 + 0.2 * j, gain=1.0)
        else:
            add_at(layers['bass'], bass_note(bf, chord_len * 0.95, 0.8), t0, 0, 1.0)
            # drone grave
            add_at(layers['tex'], pad_note(midi_hz(root + ch[0] - 24), chord_len, rng, harmonics=3, attack=1.5, release=2.5) * 1.4, t0)
        # arpège
        step = beat / 2 if style != 'lofi' else beat / 2
        nsteps = int(chord_len / step)
        for s in range(nsteps):
            iv = ch[arp_pattern[s % len(arp_pattern)] % len(ch)] + 12 * (1 if (s // len(arp_pattern)) % 2 else 0)
            f = midi_hz(root + iv + 12)
            if style == 'lofi':
                if rng.random() < 0.55:
                    add_at(layers['arp'], pluck_note(f * 2, 0.9, 0.5 + 0.3 * rng.random(), 0.35), t0 + s * step + rng.normal(0, 0.008), pan=rng.uniform(-0.5, 0.5))
            else:
                add_at(layers['arp'], pluck_note(f, 1.4, 0.6 + 0.25 * rng.random(), cfg.get('pluck_bright', 0.45)), t0 + s * step, pan=0.5 * np.sin(s * 0.7))
        # cloches occasionnelles (espace)
        if style != 'lofi' and ci % 2 == 1:
            add_at(layers['tex'], bell_note(midi_hz(root + ch[-1] + 24), 3.5, 0.5), t0 + beat, pan=rng.uniform(-0.7, 0.7))
    # batterie / pulsation
    nbeats = int(duration / beat) + 2
    for b in range(nbeats):
        tb = b * beat
        if style == 'lofi':
            swing = beat * 0.08
            if b % 4 in (0,) or (b % 4 == 2 and rng.random() < 0.35):
                add_at(layers['drums'], kick(0.9), tb)
            if b % 4 == 2 or (b % 8 == 7 and rng.random() < 0.3):
                add_at(layers['drums'], snap(0.7, b), tb)
            add_at(layers['drums'], hat(0.55, seed=b), tb, pan=0.2)
            add_at(layers['drums'], hat(0.35, seed=b + 999), tb + beat / 2 + swing, pan=0.2)
        else:
            # pulsation type battement de cœur
            if b % 4 == 0:
                add_at(layers['drums'], kick(0.7), tb)
                add_at(layers['drums'], kick(0.45), tb + beat * 0.42)
            if b % 2 == 1:
                add_at(layers['drums'], hat(0.25, seed=b), tb + beat / 2, pan=0.4)
    # texture de souffle (vent cosmique)
    if style != 'lofi':
        noise = rng.normal(0, 1, n).astype(np.float32)
        tt = np.arange(n) / SR
        fc = (700 + 500 * np.sin(2 * np.pi * tt / 11.0)).astype(np.float32)
        w = svf_bp_var(noise, fc, 0.25, SR) * 0.04
        layers['tex'][:, 0] += w; layers['tex'][:, 1] += np.roll(w, 2400)
    # filtrage / effets par couche
    layers['pad'] = lp(layers['pad'], 5200 if style != 'lofi' else 3800)
    if style == 'lofi':
        layers['pad'] = layers['pad'] * (1 + 0.004 * np.sin(2 * np.pi * 0.7 * np.arange(n) / SR))[:, None]
    gain_mute, inten = intensity_curve(markers, n)
    def g(lo, hi):
        return np.clip((inten - lo) / (hi - lo), 0, 1)[:, None]
    mix = (layers['pad'] * (0.55 + 0.45 * g(0, 0.4)) +
           layers['tex'] * (0.9 - 0.3 * g(0.5, 1.0)) +
           layers['arp'] * g(0.25, 0.55) * 0.9 +
           layers['bass'] * (0.25 + 0.75 * g(0.3, 0.6)) +
           layers['drums'] * g(0.55, 0.8) * (1.0 if style == 'lofi' else 0.8))
    wet = simple_reverb(mix, decay=3.2 if style != 'lofi' else 1.6)
    mix = mix * 0.75 + wet * (0.55 if style != 'lofi' else 0.3)
    if style == 'lofi':
        # pompage léger + saturation douce
        mix = np.tanh(mix * 1.2) / 1.2
    mix = mix * gain_mute[:, None]
    mix = mix[:int(duration * SR)]
    fo = int(2.5 * SR)
    mix[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
    fi = int(0.8 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)[:, None]
    return mix.astype(np.float32)


# ----------------------------------------------------------------------------- effets sonores
def sfx(name, seed=0):
    rng = np.random.default_rng(seed)
    if name == 'whoosh':
        d = 0.55; n = int(d * SR); t = np.arange(n) / SR
        x = rng.normal(0, 1, n).astype(np.float32)
        fc = (300 + 4200 * np.sin(np.pi * t / d) ** 2).astype(np.float32)
        y = svf_bp_var(x, fc, 0.6, SR)
        e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
        y = y * e
        st = np.stack([y * (1 - t / d * 0.6), y * (0.4 + t / d * 0.6)], 1)
        return (st / (np.abs(st).max() + 1e-9) * 0.5).astype(np.float32)
    if name == 'whoosh_soft':
        s = sfx('whoosh', seed); return s * 0.5
    if name == 'boom':
        d = 2.2; n = int(d * SR); t = np.arange(n) / SR
        f = 32 + 40 * np.exp(-t * 6)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
        nz = lp(rng.normal(0, 1, n), 400) * np.exp(-t * 9) * 1.5
        y = np.tanh((s + nz) * 1.6)
        st = np.stack([y, y], 1) + simple_reverb(y.astype(np.float32), 2.5) * 0.35
        return (st / np.abs(st).max() * 0.85).astype(np.float32)
    if name == 'impact':
        d = 1.2; n = int(d * SR); t = np.arange(n) / SR
        s = np.sin(2 * np.pi * np.cumsum(50 + 80 * np.exp(-t * 20)) / SR) * np.exp(-t * 5)
        nz = sosfilt(butter(2, [200, 3000], 'bandpass', fs=SR, output='sos'), rng.normal(0, 1, n)) * np.exp(-t * 25)
        y = np.tanh((s + nz * 0.8) * 1.5)
        st = np.stack([y, y], 1) + simple_reverb(y.astype(np.float32), 1.5) * 0.3
        return (st / np.abs(st).max() * 0.7).astype(np.float32)
    if name == 'riser':
        d = 2.4; n = int(d * SR); t = np.arange(n) / SR
        x = rng.normal(0, 1, n).astype(np.float32)
        fc = (400 * 2 ** (t / d * 4)).astype(np.float32)
        y = svf_bp_var(x, fc, 0.5, SR)
        tone = np.sin(2 * np.pi * np.cumsum(180 * 2 ** (t / d * 2.5)) / SR) * 0.35
        e = (t / d) ** 2.2
        y = (y + tone) * e
        st = np.stack([y, np.roll(y, 300)], 1) + simple_reverb(y.astype(np.float32), 1.2) * 0.25
        return (st / np.abs(st).max() * 0.5).astype(np.float32)
    if name == 'tick':
        n = int(0.05 * SR); t = np.arange(n) / SR
        y = np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 180) + sosfilt(butter(2, 3000, 'highpass', fs=SR, output='sos'), rng.normal(0, 1, n)) * np.exp(-t * 300) * 0.5
        return (np.stack([y, y], 1) * 0.5).astype(np.float32)
    if name == 'pop':
        n = int(0.09 * SR); t = np.arange(n) / SR
        y = np.sin(2 * np.pi * np.cumsum(500 + 700 * t / 0.09) / SR) * np.exp(-t * 45)
        return (np.stack([y, y], 1) * 0.35).astype(np.float32)
    if name == 'shimmer':
        d = 2.5; n = int(d * SR); t = np.arange(n) / SR
        y = np.zeros(n)
        for k in range(9):
            f = rng.choice([1760, 2093, 2349, 2637, 3136, 3520]) * rng.uniform(0.995, 1.005)
            t0 = rng.uniform(0, 0.6)
            y += np.sin(2 * np.pi * f * t) * np.exp(-np.maximum(t - t0, 0) * 2.2) * (t > t0) * 0.15
        st = np.stack([y, np.roll(y, 500)], 1) + simple_reverb(y.astype(np.float32), 2.5) * 0.6
        return (st / np.abs(st).max() * 0.35).astype(np.float32)
    if name == 'glitch':
        d = 0.35; n = int(d * SR)
        y = np.zeros(n)
        pos = 0
        while pos < n:
            L = int(rng.uniform(0.01, 0.05) * SR)
            f = rng.uniform(100, 2000)
            seg = np.sign(np.sin(2 * np.pi * f * np.arange(L) / SR)) * rng.uniform(0.2, 0.6)
            if rng.random() < 0.4:
                seg = rng.normal(0, 0.4, L)
            y[pos:pos + L] = seg[:max(0, min(L, n - pos))]
            pos += L + int(rng.uniform(0, 0.02) * SR)
        return (np.stack([y, np.roll(y, 120)], 1) * 0.3).astype(np.float32)
    if name == 'heartbeat':
        n = int(0.9 * SR); y = np.zeros(n)
        for t0, v in ((0, 1.0), (0.28, 0.7)):
            k = kick(v); i0 = int(t0 * SR); y[i0:i0 + len(k)] += lp(k, 150)[:n - i0]
        return (np.stack([y, y], 1) * 0.9).astype(np.float32)
    if name == 'ding':
        y = bell_note(1318.5, 2.5, 1.0) + bell_note(1975.5, 2.5, 0.4)
        st = np.stack([y, y], 1) + simple_reverb(y, 2.0) * 0.4
        return (st / np.abs(st).max() * 0.4).astype(np.float32)
    if name == 'reverse':
        d = 1.0; n = int(d * SR); t = np.arange(n) / SR
        y = hp(rng.normal(0, 1, n), 2500) * (t / d) ** 3
        return (np.stack([y, np.roll(y, 200)], 1) / np.abs(y).max() * 0.35).astype(np.float32)
    if name == 'type':
        n = int(0.03 * SR); t = np.arange(n) / SR
        y = hp(rng.normal(0, 1, n), 1500) * np.exp(-t * 250)
        return (np.stack([y, y], 1) * 0.3).astype(np.float32)
    raise ValueError(name)


# ----------------------------------------------------------------------------- mixage
def loudness(x):
    import pyloudnorm as pyln
    m = pyln.Meter(SR)
    return m.integrated_loudness(x if x.ndim == 2 else np.stack([x, x], 1))

def set_loudness(x, target):
    L = loudness(x)
    if not np.isfinite(L):
        return x
    return x * 10 ** ((target - L) / 20)

def limiter(x, ceiling_db=-1.0, look=0.005, release=0.08):
    c = 10 ** (ceiling_db / 20)
    peak = np.abs(x).max(1)
    g = np.minimum(1.0, c / (peak + 1e-9))
    k = int(look * SR)
    g = minimum_filter1d(g, size=2 * k + 1)
    a = np.exp(-1.0 / (release * SR))
    g2 = _smooth_release(g.astype(np.float64), a)
    return (x * g2[:, None]).astype(np.float32)

@njit(cache=True)
def _smooth_release(g, a):
    out = np.empty_like(g)
    z = 1.0
    for i in range(len(g)):
        if g[i] < z:
            z = g[i]
        else:
            z = a * z + (1 - a) * g[i]
        out[i] = z
    return out

def duck_curve(voice, depth_db=-7.0, attack=0.04, release=0.45):
    win = int(0.03 * SR)
    env = np.sqrt(np.convolve(voice ** 2, np.ones(win) / win, mode='same'))
    thr = 0.02
    act = np.clip(env / thr, 0, 1)
    out = np.empty_like(act)
    z = 0.0
    aa = np.exp(-1 / (attack * SR)); ar = np.exp(-1 / (release * SR))
    out = _follow(act.astype(np.float64), aa, ar)
    return (10 ** (depth_db * out / 20)).astype(np.float32)

@njit(cache=True)
def _follow(x, aa, ar):
    y = np.empty_like(x)
    z = 0.0
    for i in range(len(x)):
        c = aa if x[i] > z else ar
        z = c * z + (1 - c) * x[i]
        y[i] = z
    return y

def mix(voice, music, sfx_events, music_db=-26.0, voice_db=-16.0, final_db=-14.0):
    n = len(voice)
    music = music[:n] if len(music) >= n else np.pad(music, ((0, n - len(music)), (0, 0)))
    v = set_loudness(voice, voice_db)
    m = set_loudness(music, music_db) * duck_curve(v)[:, None]
    out = np.stack([v, v], 1) + m
    for (t0, name, gain_db, pan, seed) in sfx_events:
        s = sfx(name, seed)
        add_at(out, s, t0, 0, 10 ** (gain_db / 20))
    out = set_loudness(out, final_db)
    out = limiter(out, -2.0)
    return out.astype(np.float32)
