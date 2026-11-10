"""Montage d'une histoire à partir des scènes générées (Grok…), version « rétention » :
ouverture choc (gros plans, impact, musique dramatique, sous-titres en grand), flash + « Quelques heures plus tôt… »,
puis l'histoire dans l'ordre, recadrée en vertical sur celui qui parle, sans temps morts.

Usage : python3 montage_scenes_v2.py plan.json sortie.mp4

Morceaux possibles dans plan["slices"] :
  {"s": 6, "t0": 4.0, "t1": 5.0, "x": 390, "lines": [...]}           plan de la scène 6, recadré à x (ou "x0"/"x1" : panoramique)
  options : "zoom": 0.08 (lente poussée avant), "big": true (sous-titres en grand), "nom"/"role" (carton de nom),
            "audio": {"s": 6, "t0": 6.4, "t1": 7.55, "delay": 0.1} (son pris dans une autre scène), "sfx": [["impact", 0.0, 0.9]]
  {"card": "QUELQUES HEURES|PLUS TÔT…", "s": 2, "t": 0.3, "x": 0, "dur": 0.9}   carton sur image floutée, entrée en flash blanc
"""
import sys, json, os, subprocess, numpy as np, soundfile as sf
sys.path.insert(0, '/home/user/n/pipeline')
import ai_assemble as A, fruits_series as FS, audio
from common import SR, FONTS

spec = json.load(open(sys.argv[1]))
out = sys.argv[2]
wd = os.path.dirname(os.path.abspath(out)) + '/work_v2'
os.makedirs(wd, exist_ok=True)
scenes = spec['scenes']
ENC = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '12']


def probe_wh(src):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', src],
                       capture_output=True, text=True)
    return [int(v) for v in r.stdout.strip().split(',')[:2]]


def vfilter(sl, src, d):
    w, h = probe_wh(src)
    cw = int(round(h * 9 / 16)) // 2 * 2
    x0, x1 = sl.get('x', sl.get('x0', 0)), sl.get('x', sl.get('x1', 0))
    x0, x1 = min(max(0, x0), w - cw), min(max(0, x1), w - cw)
    xe = f"{x0}+({x1 - x0})*min(t/{d:.3f},1)" if x1 != x0 else str(x0)
    vf = f"crop={cw}:{h}:'{xe}':0,scale=1080:1920:flags=lanczos"
    z = sl.get('zoom')
    if z:   # poussée avant lente : on agrandit progressivement puis on recadre au centre
        vf += (f",scale=w='trunc(1080*(1+{z}*min(t/{d:.3f},1))/2)*2':h='trunc(1920*(1+{z}*min(t/{d:.3f},1))/2)*2'"
               f":eval=frame:flags=bicubic,crop=1080:1920:(iw-1080)/2:(ih-1920)/2")
    return vf + ',eq=saturation=1.07:contrast=1.03,fps=30,format=yuv420p'


def cut(k, sl):
    sub = f"{wd}/cut{k:02d}.mp4"
    if 'card' in sl:
        d = sl['dur']
        src = scenes[str(sl['s'])]
        vf = vfilter(dict(x=sl.get('x', 0)), src, d) + ',boxblur=26:3,eq=brightness=-0.28'
        A.run(['ffmpeg', '-v', 'error', '-y', '-ss', f"{sl['t']:.3f}", '-i', src, '-frames:v', '1', '-vf', vf, f"{wd}/card{k}.png"])
        A.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-t', f'{d:.3f}', '-i', f"{wd}/card{k}.png", '-f', 'lavfi', '-t', f'{d:.3f}',
               '-i', 'anullsrc=r=48000:cl=stereo', '-vf', 'fps=30,format=yuv420p,fade=t=in:st=0:d=0.22:color=white',
               *ENC, '-c:a', 'aac', '-b:a', '256k', '-shortest', sub])
        return sub, d
    src = scenes[str(sl['s'])]
    d = sl['t1'] - sl['t0']
    vf = vfilter(sl, src, d)
    if 'audio' in sl:
        au = sl['audio']; asrc = scenes[str(au['s'])]; ad = au['t1'] - au['t0']; dl = int(au.get('delay', 0) * 1000)
        A.run(['ffmpeg', '-v', 'error', '-y', '-ss', f"{sl['t0']:.3f}", '-t', f'{d:.3f}', '-i', src,
               '-ss', f"{au['t0']:.3f}", '-t', f'{ad:.3f}', '-i', asrc,
               '-filter_complex', f"[0:v]{vf}[v];[1:a]aresample=48000,afade=t=out:st={max(0, ad - 0.04):.3f}:d=0.04,adelay={dl}|{dl},apad[a]",
               '-map', '[v]', '-map', '[a]', '-t', f'{d:.3f}', *ENC, '-c:a', 'aac', '-b:a', '256k', sub])
    else:
        A.run(['ffmpeg', '-v', 'error', '-y', '-ss', f"{sl['t0']:.3f}", '-t', f'{d:.3f}', '-i', src,
               '-vf', vf, '-af', 'aresample=48000', *ENC, '-c:a', 'aac', '-b:a', '256k', sub])
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
       *ENC, f"{wd}/end.mp4"])
total = t + END
open(f"{wd}/c.txt", "w").write(''.join(f"file '{s['mp4']}'\n" for s in segs) + f"file '{wd}/end.mp4'\n")
A.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f"{wd}/c.txt", '-c', 'copy', f"{wd}/master.mp4"])

# ----------------------------------------------------------------------------- texte
n = int(round(total * SR)); native = np.zeros((n, 2), np.float32)
ass = A.ass_header()
story_t0 = next((s['t0'] + s['dur'] for s in segs if 'card' in s['sl']), 0.0)
for s in segs:
    a, _ = sf.read(s['wav'], dtype='float32', always_2d=True)
    k = int(round(s['t0'] * SR)); native[k:k + len(a)] += a[:max(0, n - k)]
    sl = s['sl']
    if 'card' in sl:
        l1, l2 = (sl['card'].split('|') + [''])[:2]
        ass += A.ev('End', s['t0'] + 0.12, s['t0'] + s['dur'], A.POP + r'{\fs128\pos(540,860)}' + A.esc(l1), layer=3)
        ass += A.ev('End', s['t0'] + 0.2, s['t0'] + s['dur'], A.POP + r'{\fs128\pos(540,1010)}' + A.esc(l2), layer=3)
        continue
    if sl.get('lines'):
        caps = A.duo_caps(dict(lines=[('x', l) for l in sl['lines']]), a, s['dur'], s['t0'])
        if sl.get('big'):     # ouverture : sous-titres plus gros, au centre de l'écran, entrée plus marquée
            caps = caps.replace(r'\pos(540,1430)\fscx112\fscy112\t(0,80,\fscx100\fscy100)',
                                r'\pos(540,1300)\fscx215\fscy215\t(0,90,\fscx185\fscy185)')
        ass += caps
    if sl.get('nom'):
        a0, b0 = s['t0'] + 0.15, s['t0'] + min(s['dur'], 3.0)
        ass += A.ev('Name', a0, b0, r'{\fad(120,150)\pos(70,420)}' + A.esc(sl['nom'].upper()))
        ass += A.ev('Role', a0 + 0.1, b0, r'{\fad(120,150)\pos(74,524)}' + A.esc(sl['role']))
ass += A.ev('End', t + 0.1, total, A.POP + r'{\pos(540,820)}' + A.esc(spec.get('fin_titre', 'FIN')))
ass += A.ev('EndSub', t + 0.3, total, r'{\fad(150,0)\pos(540,1010)}' + A.esc(spec['question']))
ass += A.ev('Ep', t + 0.6, total, r'{\fad(150,0)\pos(540,1180)}' + A.esc(spec['cta']))
open(f"{wd}/t.ass", "w").write(ass)

# ----------------------------------------------------------------------------- son
voice = audio.set_loudness(native.mean(1), -16.0)
m = len(voice)
# musique : tension dramatique sur l'ouverture, puis la musique de l'histoire après « Quelques heures plus tôt »
drama = audio.compose(dict(style='space', prog='minor_dark', key=38, bpm=84, seed=911), story_t0 + 1.0, [(0, 1.0), (story_t0, 1.0)])
drama = drama[:int(story_t0 * SR)]
fo = min(len(drama), int(0.25 * SR)); drama[-fo:] *= np.linspace(1, 0, fo)[:, None]
story = audio.compose(dict(FS.SERIES_MUSIC), total - story_t0 + 1.0, [(0, 0.55), (total - story_t0 - 4, 0.85)])
music = np.zeros((m, 2), np.float32)
music[:len(drama)] += audio.set_loudness(drama, -22.0)[:m]
k0 = int(story_t0 * SR); L = min(len(story), m - k0)
music[k0:k0 + L] += audio.set_loudness(story, -29.0)[:L]
duck = audio.duck_curve(voice, depth_db=-9.0)[:m]
music *= duck[:, None]
# effets : impact à la première image, battement sous Léo, souffle sur le flash
fx = np.zeros((m, 2), np.float32)
for s in segs:
    for name, off, gain in s['sl'].get('sfx', []):
        e = audio.sfx(name, seed=int(s['t0'] * 10)) * gain
        k = int((s['t0'] + off) * SR); L = min(len(e), m - k)
        if L > 0:
            fx[k:k + L] += e[:L]
mix = A.loud_limit(np.stack([voice, voice], 1) + music + fx, -14.0)
sf.write(f"{wd}/mix.wav", mix.astype(np.float32), SR)

# ----------------------------------------------------------------------------- export TikTok
A.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f"{wd}/master.mp4", '-i', f"{wd}/mix.wav", '-map', '0:v:0', '-map', '1:a:0',
       '-vf', f"ass={wd}/t.ass:fontsdir={FONTS}", '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-maxrate', '8M', '-bufsize', '16M',
       '-profile:v', 'high', '-level', '4.2', '-pix_fmt', 'yuv420p', '-g', '60',
       '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
       '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-movflags', '+faststart', '-t', f'{total:.3f}', out])
print(out, round(total, 1))
