"""Montage « Le faux milliardaire » (scènes Grok de l'utilisateur) : recadrage vertical sur celui qui parle,
ouverture sur la chute, accroche, cartons de noms, sous-titres 2 lignes, musique, fin « À suivre ».
Usage : python3 build.py plans.json sortie.mp4 [couverture.jpg]"""
import sys, json, os, numpy as np, soundfile as sf
sys.path.insert(0, '/home/user/n/pipeline')
import ai_assemble as A, fruits_series as FS, audio
from common import SR, FONTS

spec = json.load(open(sys.argv[1]))
out = sys.argv[2]
cover = sys.argv[3] if len(sys.argv) > 3 else None
wd = os.path.dirname(os.path.abspath(out)) + '/work'
os.makedirs(wd, exist_ok=True)
scenes = spec['scenes']


def probe_wh(src):
    import subprocess
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', src],
                       capture_output=True, text=True)
    return [int(v) for v in r.stdout.strip().split(',')[:2]]


def cut(k, sl):
    """Un morceau de scène → 1080×1920 recadré (x fixe ou panoramique x0→x1), avec son."""
    src = scenes[str(sl['s'])]
    w, h = probe_wh(src)
    cw = int(round(h * 9 / 16)) // 2 * 2
    x0, x1 = sl.get('x', sl.get('x0', 0)), sl.get('x', sl.get('x1', 0))
    x0, x1 = min(max(0, x0), w - cw), min(max(0, x1), w - cw)
    d = sl['t1'] - sl['t0']
    xe = f"{x0}+({x1 - x0})*min(t/{d:.3f},1)" if x1 != x0 else str(x0)
    sub = f"{wd}/cut{k:02d}.mp4"
    A.run(['ffmpeg', '-v', 'error', '-y', '-ss', f"{sl['t0']:.3f}", '-t', f'{d:.3f}', '-i', src,
           '-vf', f"crop={cw}:{h}:'{xe}':0,scale=1080:1920:flags=lanczos,eq=saturation=1.07:contrast=1.03,fps=30,format=yuv420p",
           '-af', 'aresample=48000', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '12', '-c:a', 'aac', '-b:a', '256k', sub])
    return sub, d


segs, t = [], 0.0
for k, sl in enumerate(spec['slices']):
    sub, d = cut(k, sl)
    mp4, wav = f"{wd}/n{k:02d}.mp4", f"{wd}/n{k:02d}.wav"
    A.normalize(sub, mp4, wav, d, None, fit=False)
    segs.append(dict(t0=t, dur=d, mp4=mp4, wav=wav, sl=sl)); t += d

END = 2.6
A.run(['ffmpeg', '-v', 'error', '-y', '-sseof', '-0.1', '-i', segs[-1]['mp4'], '-frames:v', '1', '-update', '1', f"{wd}/end.png"])
A.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-t', f'{END:.3f}', '-i', f"{wd}/end.png", '-vf', 'boxblur=24:3,eq=brightness=-0.22,fps=30,format=yuv420p',
       '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', f"{wd}/end.mp4"])
total = t + END
open(f"{wd}/c.txt", "w").write(''.join(f"file '{s['mp4']}'\n" for s in segs) + f"file '{wd}/end.mp4'\n")
A.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f"{wd}/c.txt", '-c', 'copy', f"{wd}/master.mp4"])

n = int(round(total * SR)); native = np.zeros((n, 2), np.float32)
ass = A.ass_header()
for s in segs:
    a, _ = sf.read(s['wav'], dtype='float32', always_2d=True)
    k = int(round(s['t0'] * SR)); native[k:k + len(a)] += a[:max(0, n - k)]
    sl = s['sl']
    if sl.get('lines'):
        ass += A.duo_caps(dict(lines=[('x', l) for l in sl['lines']]), a, s['dur'], s['t0'])
    if sl.get('nom'):
        a0, b0 = s['t0'] + 0.15, s['t0'] + min(s['dur'], 3.0)
        ass += A.ev('Name', a0, b0, r'{\fad(120,150)\pos(70,420)}' + A.esc(sl['nom'].upper()))
        ass += A.ev('Role', a0 + 0.1, b0, r'{\fad(120,150)\pos(74,524)}' + A.esc(sl['role']))
    if sl.get('top'):
        ass += A.ev('Ep', s['t0'] + 0.05, s['t0'] + s['dur'] - 0.05, r'{\fad(120,120)}' + A.esc(sl['top']))
# accroche sur l'ouverture
hook_end = segs[0]['dur']
for k, l in enumerate(spec['accroche']):
    ass += A.ev('HookBox', 0.05 + 0.08 * k, hook_end, A.POP + r'{\pos(540,%d)}' % (430 + k * 150) + A.esc(l), layer=3)
# fin
ass += A.ev('End', t + 0.1, total, A.POP + r'{\pos(540,820)}' + A.esc(spec.get('fin_titre', 'À SUIVRE…')))
ass += A.ev('EndSub', t + 0.3, total, r'{\fad(150,0)\pos(540,1010)}' + A.esc(spec['question']))
ass += A.ev('Ep', t + 0.6, total, r'{\fad(150,0)\pos(540,1180)}' + A.esc(spec['cta']))
open(f"{wd}/t.ass", "w").write(ass)

voice = audio.set_loudness(native.mean(1), -16.0)
music = audio.compose(dict(FS.SERIES_MUSIC), total, [(0, 0.5), (total - 4, 0.85)])[:len(voice)]
if len(music) < len(voice):
    music = np.pad(music, ((0, len(voice) - len(music)), (0, 0)))
duck = audio.duck_curve(voice, depth_db=-9.0)
m = min(len(music), len(voice), len(duck))
voice, music = voice[:m], audio.set_loudness(music[:m], -29.0) * duck[:m, None]
mix = A.loud_limit(np.stack([voice, voice], 1) + music, -14.0)
sf.write(f"{wd}/mix.wav", mix.astype(np.float32), SR)
A.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f"{wd}/master.mp4", '-i', f"{wd}/mix.wav", '-map', '0:v:0', '-map', '1:a:0',
       '-vf', f"ass={wd}/t.ass:fontsdir={FONTS}", '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p',
       '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', '-t', f'{total:.3f}', out])
if cover:
    A.prepend_cover(cover, out, wd)
print(out, round(total, 1))
