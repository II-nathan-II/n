"""Contrôle qualité automatique des 10 MP4 : format, durée, intégrité, loudness, narration (Whisper), synchro des sous-titres, visuels."""
import os, sys, json, subprocess, re, glob
import numpy as np
import soundfile as sf
import cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import PROJECT, WORK, SR

def ffprobe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_streams', '-show_format', path],
                         capture_output=True, text=True).stdout
    return json.loads(out)

def decode_errors(path):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'null', '-'], capture_output=True, text=True)
    return r.stderr.strip()

def audio_of(path):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vn', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True)
    a = np.frombuffer(r.stdout, np.float32).reshape(-1, 2)
    return a

def true_peak_db(a):
    from scipy.signal import resample_poly
    up = resample_poly(a, 4, 1, axis=0)
    return 20 * np.log10(np.abs(up).max() + 1e-12)

def norm_words(s):
    s = s.lower().replace('’', "'")
    s = re.sub(r"[^a-zà-ÿœæç0-9' -]", ' ', s)
    return [w for w in re.split(r"[\s'-]+", s) if w]

def word_recall(ref, hyp):
    """Part des mots du script retrouvés (dans l'ordre) dans la transcription — LCS / longueur du script."""
    r, h = norm_words(ref), norm_words(hyp)
    n, m = len(r), len(h)
    dp = np.zeros((n + 1, m + 1), np.int32)
    for i in range(n):
        for j in range(m):
            dp[i + 1, j + 1] = dp[i, j] + 1 if r[i] == h[j] else max(dp[i, j + 1], dp[i + 1, j])
    return dp[n, m] / max(n, 1)

def caption_sync(tl, voice):
    """Pour chaque mot sous-titré : énergie de la voix pendant son intervalle (doit être parlé)."""
    hop = int(0.01 * SR)
    n = len(voice) // hop
    rms = np.sqrt((voice[:n * hop].reshape(n, hop) ** 2).mean(1))
    thr = np.percentile(rms[rms > 1e-4], 95) * 10 ** (-30 / 20)
    voiced, total, outside = 0, 0, 0
    for seg in tl['segments']:
        for w in seg['words']:
            total += 1
            a, b = int(w['s'] * 100), max(int(w['e'] * 100), int(w['s'] * 100) + 1)
            if rms[a:b].max() > thr:
                voiced += 1
            if w['s'] < seg['start'] - 0.01 or w['e'] > seg['speech_end'] + 0.05:
                outside += 1
    return voiced / max(total, 1), outside, total

def frames_check(path, dur, outimg, n=12):
    tiles, means, diffs = [], [], []
    prev = None
    for k in range(n):
        t = (k + 0.5) * dur / n
        r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.2f}', '-i', path, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True)
        img = np.frombuffer(r.stdout, np.uint8).reshape(1920, 1080, 3)
        means.append(float(img.mean()))
        if prev is not None:
            diffs.append(float(np.abs(img.astype(np.int16) - prev).mean()))
        prev = img.astype(np.int16)
        tiles.append(cv2.resize(img, (180, 320), interpolation=cv2.INTER_AREA))
    sheet = np.vstack([np.hstack(tiles[i:i + 6]) for i in range(0, n, 6)])
    cv2.imwrite(outimg, cv2.cvtColor(sheet, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 85])
    return means, diffs

def run(ids=None, asr=True):
    import build
    from tts import spoken_text
    import pyloudnorm as pyln
    vids = build.all_videos()
    ids = ids or sorted(vids)
    results = []
    qcdir = os.path.join(PROJECT, 'ANALYSE', 'controle_qualite')
    os.makedirs(qcdir, exist_ok=True)
    for vid in ids:
        v = vids[vid]
        path = os.path.join(PROJECT, v['niche'], f'{vid}.mp4')
        res = dict(id=vid, file=os.path.relpath(path, PROJECT), exists=os.path.exists(path))
        if not res['exists']:
            results.append(res); continue
        p = ffprobe(path)
        vs = [s for s in p['streams'] if s['codec_type'] == 'video'][0]
        au = [s for s in p['streams'] if s['codec_type'] == 'audio'][0]
        dur = float(p['format']['duration'])
        res.update(duration=round(dur, 2), width=vs['width'], height=vs['height'], vcodec=vs['codec_name'], profile=vs.get('profile'),
                   pix_fmt=vs['pix_fmt'], fps=vs['r_frame_rate'], acodec=au['codec_name'], sample_rate=int(au['sample_rate']),
                   channels=au['channels'], size_mb=round(int(p['format']['size']) / 1e6, 1), bitrate_kbps=int(int(p['format']['bit_rate']) / 1000))
        err = decode_errors(path)
        res['decode_errors'] = err[:300] if err else ''
        a = audio_of(path)
        meter = pyln.Meter(SR)
        res['lufs'] = round(meter.integrated_loudness(a), 1)
        res['true_peak_db'] = round(true_peak_db(a), 1)
        tl = json.load(open(os.path.join(WORK, vid, f'{vid}_timeline.json')))
        voice, _ = sf.read(os.path.join(WORK, vid, f'{vid}_voice.wav'), dtype='float32')
        vr, outside, total = caption_sync(tl, voice)
        res['caption_words'] = total; res['caption_words_voiced'] = round(vr, 3); res['caption_words_outside_segment'] = outside
        # musique vs voix : rapport de niveau (voix seule vs mix)
        speech = np.zeros(len(a), bool)
        for seg in tl['segments']:
            if seg['words']:
                speech[int(seg['start'] * SR):int(seg['speech_end'] * SR)] = True
        quiet = ~speech
        quiet[:int(0.5 * SR)] = False
        res['level_speech_db'] = round(20 * np.log10(np.sqrt((a[speech[:len(a)]] ** 2).mean()) + 1e-9), 1)
        res['level_gaps_db'] = round(20 * np.log10(np.sqrt((a[quiet[:len(a)]] ** 2).mean()) + 1e-9), 1) if quiet.any() else None
        means, diffs = frames_check(path, dur, os.path.join(qcdir, f'{vid}_planche.jpg'))
        res['frame_mean_min'] = round(min(means), 1); res['frame_change_mean'] = round(float(np.mean(diffs)), 1)
        if asr:
            from asr import transcribe
            tmp = os.path.join(WORK, f'{vid}_qc.wav')
            sf.write(tmp, a.mean(1), SR)
            hyp = transcribe(tmp)
            ref = ' '.join(spoken_text(s['text']) for s in v['segments'] if s.get('text'))
            res['asr_word_recall'] = round(word_recall(ref, hyp), 3)
            res['asr_excerpt'] = hyp[:220]
        checks = {
            'fichier présent': res['exists'],
            'durée 65–115 s': 65 <= dur <= 115,
            '1080×1920 (9:16)': res['width'] == 1080 and res['height'] == 1920,
            'H.264 / yuv420p': res['vcodec'] == 'h264' and res['pix_fmt'] == 'yuv420p',
            'AAC 48 kHz stéréo': res['acodec'] == 'aac' and res['sample_rate'] == 48000 and res['channels'] == 2,
            'décodage sans erreur': not res['decode_errors'],
            'loudness −15 à −13 LUFS': -15.5 <= res['lufs'] <= -12.5,
            'true peak ≤ −0,5 dBTP': res['true_peak_db'] <= -0.5,
            'sous-titres sur la voix (≥ 95 %)': res['caption_words_voiced'] >= 0.95 and outside == 0,
            'narration reconnue (Whisper ≥ 85 %)': res.get('asr_word_recall', 1) >= 0.85,
            'pas d\'écran noir / image figée': res['frame_mean_min'] > 3 and res['frame_change_mean'] > 2,
        }
        res['checks'] = checks
        res['ok'] = all(checks.values())
        print(vid, 'OK' if res['ok'] else 'PROBLÈME', {k: v for k, v in checks.items() if not v}, flush=True)
        results.append(res)
    json.dump(results, open(os.path.join(qcdir, 'qc_resultats.json'), 'w'), ensure_ascii=False, indent=1)
    return results

if __name__ == '__main__':
    ids = [a for a in sys.argv[1:] if not a.startswith('--')]
    run(ids or None, asr='--no-asr' not in sys.argv)
