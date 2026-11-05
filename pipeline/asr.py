"""Transcription Whisper (sherpa-onnx) utilisée pour le contrôle qualité de la narration."""
import sys, numpy as np, soundfile as sf, sherpa_onnx
D = '/opt/assets/models/sherpa-onnx-whisper-small'
_rec = None
def recognizer():
    global _rec
    if _rec is None:
        _rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=f'{D}/small-encoder.int8.onnx', decoder=f'{D}/small-decoder.int8.onnx', tokens=f'{D}/small-tokens.txt', language='fr', task='transcribe', num_threads=4)
    return _rec
def transcribe(wav, chunk=25.0):
    a, sr = sf.read(wav, dtype='float32')
    if a.ndim > 1: a = a.mean(1)
    if sr != 16000:
        from scipy.signal import resample_poly
        a = resample_poly(a, 16000, sr).astype(np.float32); sr = 16000
    out = []
    n = int(chunk * sr)
    for i in range(0, len(a), n):
        s = recognizer().create_stream(); s.accept_waveform(sr, a[i:i+n]); recognizer().decode_stream(s); out.append(s.result.text.strip())
    return ' '.join(out)
if __name__ == '__main__':
    for w in sys.argv[1:]: print(w.split('/')[-1], '->', transcribe(w))
