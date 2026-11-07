"""Sous-titres dynamiques (ASS/libass) : mots groupés, mot actif surligné, pop-in, hook et étiquettes."""
import re
from common import W, H

def ass_time(t):
    t = max(0, t)
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f'{h}:{m:02d}:{s:05.2f}'

def bgr(hexrgb, alpha=0):
    r, g, b = int(hexrgb[0:2], 16), int(hexrgb[2:4], 16), int(hexrgb[4:6], 16)
    return f'&H{alpha:02X}{b:02X}{g:02X}{r:02X}'

THEMES = {
    'space': dict(font='Anton', size=148, upper=True, color='FFFFFF', active='FFD84A', emph='6FE3FF', outline=8, shadow=3,
                  hook_font='Anton', hook_size=150, hook_color='FFFFFF', hook_box='0B1630', label_box='FFD84A', label_color='0B1630', y=1330),
    'earth': dict(font='Anton', size=148, upper=True, color='FFFFFF', active='FFD84A', emph='FF8A3D', outline=8, shadow=3,
                  hook_font='Anton', hook_size=150, hook_color='FFFFFF', hook_box='3A1206', label_box='FF8A3D', label_color='1A0A04', y=1330),
    # style « réflexion » : un mot à la fois, police à empattements, au centre
    'reflexion': dict(font='DM Serif Display', size=176, upper=False, color='FFFFFF', active='FFFFFF', emph='F7C6A3', outline=0, shadow=0,
                      hook_font='DM Serif Display', hook_size=104, hook_color='FFFFFF', hook_box='000000', label_box='000000', label_color='F7C6A3',
                      y=1250, mode='word'),
    'psy': dict(font='Poppins ExtraBold', size=118, upper=False, color='FFFFFF', active='FFE135', emph='FF6FB5', outline=7, shadow=3,
                hook_font='Poppins Black', hook_size=128, hook_color='111111', hook_box='FFE135', label_box='FFFFFF', label_color='111111', y=1340),
}

def header(th):
    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{th['font']},{th['size']},{bgr(th['color'])},{bgr(th['active'])},{bgr('000000')},{bgr('000000', 0x70)},0,0,0,0,100,100,1,0,1,{th['outline']},{th['shadow']},5,60,60,0,1
Style: Calm,{th['font']},{int(th['size'] * 0.86)},{bgr('FFFFFF')},{bgr('FFFFFF')},{bgr('000000')},{bgr('000000', 0x80)},0,0,0,0,100,100,0,0,1,6,2,5,60,60,0,1
Style: Hook,{th['hook_font']},{th['hook_size']},{bgr(th['hook_color'])},{bgr(th['hook_color'])},{bgr(th['hook_box'])},{bgr('000000', 0x80)},0,0,0,0,100,100,0,0,3,18,0,5,70,70,0,1
Style: Word,{th['font']},{th['size']},{bgr(th['color'])},{bgr(th['color'])},{bgr('000000', 0x60)},{bgr('000000', 0x60)},0,0,0,0,100,100,1,0,1,{max(th['outline'], 0)},2,5,60,60,0,1
Style: Label,Poppins ExtraBold,94,{bgr(th['label_color'])},{bgr(th['label_color'])},{bgr(th['label_box'])},{bgr('000000', 0x90)},0,0,0,0,100,100,0,0,3,12,0,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def clean_word(w):
    return re.sub(r'[\s]', '', w)

def chunk_words(words, max_words=3, max_chars=17):
    """Groupe les mots en blocs courts, coupe après la ponctuation ; évite les mots orphelins."""
    chunks, cur = [], []
    for w in words:
        txt = w['w']
        if cur and (len(cur) >= max_words or len(' '.join(x['w'] for x in cur + [w])) > max_chars):
            chunks.append(cur); cur = []
        cur.append(w)
        if re.search(r'[.!?…:;,]["»]?$', txt):
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    # fusionne un mot seul avec le bloc précédent s'il reste de la place (et si le précédent ne finit pas une phrase)
    out = []
    for ch in chunks:
        if out and len(ch) == 1 and not re.search(r'[.!?…]["»]?$', out[-1][-1]['w']):
            merged = out[-1] + ch
            if len(merged) <= max_words + 1 and len(' '.join(x['w'] for x in merged)) <= max_chars + 4:
                out[-1] = merged; continue
        out.append(ch)
    return out

def norm(s):
    return re.sub(r'[^\wÀ-ÿ]', '', s.lower())

def esc(s):
    return s.replace('{', '(').replace('}', ')').replace('\\', '/')

def build_ass(video, timeline, path):
    th = dict(THEMES[video['theme']]); th.update(video.get('caption_theme', {}))
    out = [header(th)]
    y = th['y']
    segs = video['segments']
    for seg_spec, seg in zip(segs, timeline['segments']):
        words = seg['words']
        if not words:
            continue
        style = seg_spec.get('cap', 'normal')
        if style == 'none':
            continue
        cy = seg_spec.get('cap_y', y)
        emph = set(norm(e) for e in seg_spec.get('emph', []))
        if th.get('mode') == 'word':
            for wi, w in enumerate(words):
                s = w['s']
                e = words[wi + 1]['s'] if wi + 1 < len(words) and words[wi + 1]['s'] - w['e'] < 0.5 else min(w['e'] + 0.3, seg['end'])
                t = esc(w['w'].strip(',;:.!?…«»"'))
                if not t:
                    continue
                col = th['emph'] if norm(w['w']) in emph else th['color']
                out.append(f"Dialogue: 1,{ass_time(s)},{ass_time(e)},Word,,0,0,0,,{{\\pos({W // 2},{cy})\\c{bgr(col)}\\blur0.6\\fad(70,40)\\fscx94\\fscy94\\t(0,140,\\fscx100\\fscy100)}}{t}")
            continue
        chunks = chunk_words(words, 3 if style != 'calm' else 4, 17 if style != 'calm' else 21)
        for ci, ch in enumerate(chunks):
            c_start = ch[0]['s']
            c_end = ch[-1]['e']
            nxt = None
            if ci + 1 < len(chunks):
                nxt = chunks[ci + 1][0]['s']
            # prolonge jusqu'au bloc suivant si l'écart est petit
            if nxt is not None and nxt - c_end < 0.45:
                c_end = nxt
            else:
                c_end = min(c_end + 0.35, seg['end'])
            if style == 'calm':
                txt = ' '.join(esc(w['w']) for w in ch)
                fi = 120 if ci == 0 else 0
                fo = 150 if ci == len(chunks) - 1 else 0
                out.append(f"Dialogue: 0,{ass_time(c_start)},{ass_time(c_end)},Calm,,0,0,0,,{{\\pos({W // 2},{cy})\\fad({fi},{fo})}}{txt}")
                continue
            for wi, w in enumerate(ch):
                s = w['s'] if wi > 0 else c_start
                e = ch[wi + 1]['s'] if wi + 1 < len(ch) else c_end
                parts = []
                for wj, w2 in enumerate(ch):
                    t = esc(w2['w'].upper() if th['upper'] else w2['w'])
                    if wj == wi:
                        parts.append(f"{{\\c{bgr(th['active'])}\\fscx108\\fscy108}}{t}{{\\c{bgr(th['color'])}\\fscx100\\fscy100}}")
                    elif norm(w2['w']) in emph:
                        parts.append(f"{{\\c{bgr(th['emph'])}}}{t}{{\\c{bgr(th['color'])}}}")
                    else:
                        parts.append(t)
                anim = ''
                if wi == 0:
                    anim = '\\fscx72\\fscy72\\t(0,90,\\fscx106\\fscy106)\\t(90,160,\\fscx100\\fscy100)'
                out.append(f"Dialogue: 1,{ass_time(s)},{ass_time(e)},Cap,,0,0,0,,{{\\pos({W // 2},{cy}){anim}}}{' '.join(parts)}")
    # hook (texte d'accroche en haut, première phrase)
    hook = video.get('hook_text')
    if hook:
        first = timeline['segments'][0]
        end = max(first['end'], video.get('hook_min', 3.0))
        lines = hook.split('\\N')
        out.append(f"Dialogue: 2,{ass_time(0.0)},{ass_time(end)},Hook,,0,0,0,,{{\\pos({W // 2},{video.get('hook_y', 400)})\\fscx40\\fscy40\\t(0,140,\\fscx108\\fscy108)\\t(140,220,\\fscx100\\fscy100)\\fad(0,200)}}{hook}")
    # étiquettes
    for seg_spec, seg in zip(segs, timeline['segments']):
        lab = seg_spec.get('label')
        if lab:
            ly = seg_spec.get('label_y', 290)
            s, e = seg['start'], seg['end'] + seg_spec.get('label_extra', 0.0)
            out.append(f"Dialogue: 2,{ass_time(s + 0.05)},{ass_time(e)},Label,,0,0,0,,{{\\pos({W // 2},{ly})\\fad(150,150)\\fscx60\\fscy60\\t(0,160,\\fscx100\\fscy100)}}{lab}")
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(out) + '\n')
    return path
