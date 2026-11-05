"""Assemblage : narration → plans → caméra/transitions → étalonnage → encodage H.264/AAC avec sous-titres."""
import os, sys, json, math, subprocess, time
import numpy as np
import cv2
import soundfile as sf
from common import *
import tts, audio, captions

cv2.setNumThreads(2)

# ----------------------------------------------------------------------------- caméra
CAMS = {
    'in': dict(z=(1.0, 1.14)), 'out': dict(z=(1.16, 1.0)), 'slow_in': dict(z=(1.0, 1.06)),
    'left': dict(z=(1.12, 1.12), dx=(50, -50)), 'right': dict(z=(1.12, 1.12), dx=(-50, 50)),
    'up': dict(z=(1.12, 1.12), dy=(70, -70)), 'down': dict(z=(1.12, 1.12), dy=(-70, 70)),
    'drift': dict(z=(1.05, 1.1), r=(-1.2, 1.2)), 'static': dict(z=(1.0, 1.0)), 'push': dict(z=(1.0, 1.25)),
    'tilt': dict(z=(1.1, 1.14), r=(2.0, -2.0)),
}
AUTO = ['in', 'left', 'out', 'drift', 'right', 'slow_in', 'up', 'in', 'down', 'tilt']

def cam_params(spec, i):
    if spec is None or spec == 'auto':
        spec = AUTO[i % len(AUTO)]
    if isinstance(spec, str):
        spec = CAMS[spec]
    d = dict(z=(1.0, 1.0), dx=(0, 0), dy=(0, 0), r=(0, 0), focus=(W / 2, 760))
    d.update(spec)
    return d

def cam_matrix(c, k, extra_z=1.0, shake=(0, 0)):
    k = ease_in_out(k)
    z = lerp(*c['z'], k) * extra_z
    dx = lerp(*c['dx'], k) + shake[0]; dy = lerp(*c['dy'], k) + shake[1]
    r = lerp(*c['r'], k)
    fx, fy = c['focus']
    M = cv2.getRotationMatrix2D((fx, fy), r, z)
    M[0, 2] += dx; M[1, 2] += dy
    return M

# ----------------------------------------------------------------------------- plans
class Ctx:
    """Donne aux scènes l'accès aux instants (marques) de la narration."""
    def __init__(self, video, tl, start):
        self.video, self.tl, self.start = video, tl, start
    def at(self, mark, field='start'):
        for spec, seg in zip(self.video['segments'], self.tl['segments']):
            if spec.get('mark') == mark:
                return seg[field]
        raise KeyError(mark)
    def local(self, mark, field='start'):
        return self.at(mark, field) - self.start

class Shot:
    def __init__(self, scene, start, cam, trans, idx):
        self.scene, self.start, self.cam, self.trans, self.idx = scene, start, cam, trans, idx
        self.end = None

def build_shots(video, tl, setup=True):
    shots = []
    for i, (spec, seg) in enumerate(zip(video['segments'], tl['segments'])):
        sc = spec.get('scene', 'same')
        if sc == 'same' and shots:
            continue
        start = 0.0 if not shots else max(0.0, seg['start'] - 0.06)
        import inspect
        if callable(sc):
            scene = sc(Ctx(video, tl, start)) if len(inspect.signature(sc).parameters) == 1 else sc()
        else:
            scene = sc
        shots.append(Shot(scene, start, cam_params(spec.get('cam'), len(shots)), spec.get('trans', 'cut'), len(shots)))
    for a, b in zip(shots, shots[1:]):
        a.end = b.start
    shots[-1].end = tl['duration']
    for s in shots:
        s.dur = s.end - s.start
        if setup:
            s.scene.setup(s.dur)
    return shots

TDUR = {'cut': 0.0, 'fade': 0.45, 'zoom': 0.32, 'whip': 0.28, 'flash': 0.36, 'black': 0.6, 'glitch': 0.3, 'slide': 0.32}

def blend(a, b, p, kind, rng):
    if kind == 'fade':
        return a * (1 - p) + b * p
    if kind == 'black':
        return a * max(0, 1 - 2 * p) if p < 0.5 else b * (2 * p - 1)
    if kind == 'flash':
        w = 1 - abs(2 * p - 1)
        base = a if p < 0.5 else b
        return base + w * 1.2
    if kind == 'zoom':
        e = ease_in_out(p)
        za = 1 + 0.45 * e; zb = 0.8 + 0.2 * e
        Ma = cv2.getRotationMatrix2D((W / 2, H / 2), 0, za); Mb = cv2.getRotationMatrix2D((W / 2, H / 2), 0, zb)
        A = cv2.warpAffine(a, Ma, (W, H), borderMode=cv2.BORDER_REFLECT)
        A2 = cv2.warpAffine(a, cv2.getRotationMatrix2D((W / 2, H / 2), 0, za * 1.04), (W, H), borderMode=cv2.BORDER_REFLECT)
        B = cv2.warpAffine(b, Mb, (W, H), borderMode=cv2.BORDER_REFLECT)
        A = (A + A2) / 2
        return A * (1 - e) + B * e
    if kind in ('whip', 'slide'):
        e = ease_in_out(p)
        off = int(W * e) if kind == 'whip' else int(H * e)
        out = np.empty_like(a)
        if kind == 'whip':
            out[:, :W - off] = a[:, off:]; out[:, W - off:] = b[:, :off]
            k = int(1 + 90 * (1 - abs(2 * p - 1)))
            if k > 2:
                out = cv2.blur(out, (k, 1))
        else:
            out[:H - off] = a[off:]; out[H - off:] = b[:off]
            k = int(1 + 70 * (1 - abs(2 * p - 1)))
            if k > 2:
                out = cv2.blur(out, (1, k))
        return out
    if kind == 'glitch':
        base = (a if p < 0.5 else b).copy()
        w = 1 - abs(2 * p - 1)
        sh = int(30 * w)
        if sh:
            base[..., 0] = np.roll(base[..., 0], sh, axis=1); base[..., 2] = np.roll(base[..., 2], -sh, axis=1)
            for _ in range(6):
                y = rng.integers(0, H - 80); hh = rng.integers(10, 80)
                base[y:y + hh] = np.roll(base[y:y + hh], int(rng.integers(-80, 80) * w), axis=1)
        return base
    return b

# ----------------------------------------------------------------------------- étalonnage
def make_lut(theme):
    x = np.arange(256, dtype=np.float32) / 255
    if theme == 'space':
        r = np.clip(x + 0.04 * np.sin(np.pi * x) * (x - 0.35), 0, 1)
        g = x
        b = np.clip(x + 0.05 * (1 - x) * (0.6 - x), 0, 1)
        s = lambda v: np.clip(v + 0.06 * np.sin(2 * np.pi * v) * -0.5 * 0 + (v - 0.5) * 0.06 * np.sin(np.pi * v), 0, 1)
        r, g, b = s(r), s(g), s(b)
    else:
        s = lambda v: np.clip(v + (v - 0.5) * 0.05 * np.sin(np.pi * v), 0, 1)
        r, g, b = s(x), s(x), s(np.clip(x * 1.01, 0, 1))
    return (np.stack([r, g, b], 1) * 255).astype(np.uint8).reshape(1, 256, 3)

def tonemap(x):
    return x * (1 + x / 4.0) / (1 + x)

# ----------------------------------------------------------------------------- rendu principal
def render_video(video, out_path, workdir, preview=False, max_seconds=None, force_frames=False):
    t_start = time.time()
    os.makedirs(workdir, exist_ok=True)
    vid = video['id']
    # 1. narration
    voice, tl = tts.synthesize(video, workdir)
    sf.write(os.path.join(workdir, f'{vid}_voice.wav'), voice, SR)
    json.dump(tl, open(os.path.join(workdir, f'{vid}_timeline.json'), 'w'), ensure_ascii=False, indent=1)
    dur = tl['duration']
    print(f'[{vid}] narration {dur:.1f}s', flush=True)
    # 2. sous-titres
    ass_path = os.path.join(workdir, f'{vid}.ass')
    captions.build_ass(video, tl, ass_path)
    # 3. audio : musique + sfx + mix
    markers = [(0.0, video['music'].get('start', 0.15))]
    sfx_events = []
    emph_times, shake_times = [], []
    for spec, seg in zip(video['segments'], tl['segments']):
        if 'music' in spec:
            markers.append((seg['start'], spec['music']))
        for k, s in enumerate(spec.get('sfx', [])):
            if isinstance(s, str):
                s = (s, 0.0)
            name, off = s[0], s[1]
            gain = s[2] if len(s) > 2 else {'boom': -9, 'impact': -10, 'whoosh': -17, 'whoosh_soft': -20, 'riser': -15, 'tick': -14,
                                             'pop': -16, 'shimmer': -16, 'glitch': -17, 'heartbeat': -10, 'ding': -14, 'reverse': -15, 'type': -18}[name]
            t0 = seg['start'] + off if off >= 0 else seg['start'] + off
            if name == 'riser':
                t0 = seg['start'] + off - 2.4
            sfx_events.append((max(0, t0), name, gain, 0, len(sfx_events)))
            if name in ('boom', 'impact'):
                shake_times.append(seg['start'] + off)
        emph = set(captions.norm(e) for e in spec.get('emph', []))
        for w in seg['words']:
            if captions.norm(w['w']) in emph:
                emph_times.append(w['s'])
    master = os.path.join(workdir, f'{vid}_master.mkv' if max_seconds is None else f'{vid}_master_preview.mkv')
    need_frames = force_frames or not os.path.exists(master) or max_seconds is not None
    shots = build_shots(video, tl, setup=need_frames)
    # whoosh automatique sur les transitions marquées
    for sh in shots[1:]:
        if sh.trans in ('whip', 'zoom', 'slide') and not any(abs(e[0] - sh.start) < 0.3 for e in sfx_events):
            sfx_events.append((max(0, sh.start - 0.22), 'whoosh_soft', -21, 0, 1000 + sh.idx))
        if sh.trans == 'glitch':
            sfx_events.append((max(0, sh.start - 0.05), 'glitch', -20, 0, 2000 + sh.idx))
    music = audio.compose(video['music'], dur, markers)
    mixed = audio.mix(voice, music, sfx_events, music_db=video['music'].get('db', -25.5))
    wav_path = os.path.join(workdir, f'{vid}_mix.wav')
    sf.write(wav_path, mixed, SR, subtype='PCM_16')
    print(f'[{vid}] audio ok ({time.time() - t_start:.0f}s)', flush=True)
    total = dur if max_seconds is None else min(dur, max_seconds)
    # 4. images → master sans sous-titres (quasi sans perte), réutilisable
    if need_frames:
        render_frames(video, shots, tl, master, total, emph_times, shake_times)
    # 5. encodage final : master + sous-titres + mix audio
    vf = f"ass={ass_path}:fontsdir={FONTS}"
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', master, '-i', wav_path, '-map', '0:v:0', '-map', '1:a:0', '-vf', vf,
           '-c:v', 'libx264', '-preset', 'veryfast' if preview else 'medium', '-crf', '26' if preview else '21',
           '-maxrate', '6M', '-bufsize', '12M', '-profile:v', 'high', '-level', '4.2', '-pix_fmt', 'yuv420p', '-g', '60',
           '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
           '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-movflags', '+faststart', '-t', f'{total:.3f}', out_path]
    subprocess.run(cmd, check=True)
    print(f'[{vid}] terminé en {time.time() - t_start:.0f}s → {out_path}', flush=True)
    return tl

def render_frames(video, shots, tl, master, total, emph_times, shake_times):
    vid = video['id']
    theme = video['theme']
    lut = make_lut(theme)
    vig = vignette(0.5 if theme == 'space' else 0.35)
    grain_amt = 0.016 if theme == 'space' else 0.009
    nframes = int(round(total * FPS))
    tmp = master + '.part.mkv'
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '11',
           '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', tmp]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    rng = np.random.default_rng(1)
    k = 0
    tr_last = time.time()
    for fi in range(nframes):
        t = fi / FPS
        while k + 1 < len(shots) and t >= shots[k + 1].start:
            k += 1
        sh = shots[k]
        img = render_shot(sh, t, emph_times, shake_times)
        td = TDUR.get(sh.trans, 0)
        if k > 0 and td > 0 and t - sh.start < td:
            prev = shots[k - 1]
            img_prev = render_shot(prev, t, emph_times, shake_times)
            img = blend(img_prev, img, (t - sh.start) / td, sh.trans, rng)
        clean = getattr(sh.scene, 'clean', False)
        if clean:
            out = to_u8(np.clip(img, 0, 1))
        else:
            img = tonemap(np.maximum(img, 0)) * vig + grain_frame(fi, grain_amt)
            out = cv2.LUT(to_u8(np.clip(img, 0, 1)), lut)
        proc.stdin.write(out.tobytes())
        if fi % 300 == 0 and fi:
            el = time.time() - tr_last
            print(f'[{vid}] frame {fi}/{nframes} ({300 / el:.1f} fps)', flush=True)
            tr_last = time.time()
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError('encodage master échoué')
    os.replace(tmp, master)

def render_shot(sh, t, emph_times, shake_times):
    lt = t - sh.start
    img = sh.scene.render(lt, sh.dur)
    clean = getattr(sh.scene, 'clean', False)
    extra_z, shake = 1.0, (0.0, 0.0)
    if not clean:
        # punch-in sur les coupes franches
        if sh.trans == 'cut' and sh.idx > 0:
            extra_z *= 1 + 0.07 * (1 - ease_out(lt / 0.28))
        for te in emph_times:
            d = t - te
            if -0.05 < d < 0.7:
                extra_z *= 1 + 0.045 * (ease_out((d + 0.05) / 0.12) if d < 0.07 else math.exp(-(d - 0.07) / 0.22))
        for tb in shake_times:
            d = t - tb
            if 0 <= d < 0.6:
                a = 16 * math.exp(-d / 0.16)
                shake = (shake[0] + a * math.sin(d * 87), shake[1] + a * math.cos(d * 71))
    k = lt / max(sh.dur, 1e-3)
    M = cam_matrix(sh.cam, k, extra_z, shake)
    if abs(M[0, 0] - 1) < 1e-4 and abs(M[0, 1]) < 1e-5 and abs(M[0, 2]) < 0.01 and abs(M[1, 2]) < 0.01:
        return img
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
