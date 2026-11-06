import time, sys, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
out = sys.argv[1]
text = "Il existe une planète où il pleut du verre. Et pas doucement : à plus de sept mille kilomètres par heure, de côté. Elle s'appelle HD 189733 b, et elle se trouve à soixante-quatre années-lumière de nous."
k = Kokoro('/opt/assets/models/kokoro-v1.0.onnx', '/opt/assets/models/voices-v1.0.bin')
for sp in (1.0, 1.1):
    t=time.time(); a, sr = k.create(text, voice='ff_siwis', speed=sp, lang='fr-fr'); dt=time.time()-t
    sf.write(f'{out}/kokoro_siwis_{sp}.wav', a, sr); print('kokoro', sp, len(a)/sr, 'sec audio in', round(dt,2))
import sherpa_onnx
for v in ['tom','siwis','upmc']:
    d=f'/opt/assets/models/vits-piper-fr_FR-{v}-medium'
    cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=f'{d}/fr_FR-{v}-medium.onnx', tokens=f'{d}/tokens.txt', data_dir=f'{d}/espeak-ng-data'), num_threads=4))
    tts = sherpa_onnx.OfflineTts(cfg)
    for sid in ([0] if v!='upmc' else [0,1]):
        t=time.time(); g = tts.generate(text, sid=sid, speed=1.0); dt=time.time()-t
        sf.write(f'{out}/piper_{v}_{sid}.wav', np.array(g.samples, dtype=np.float32), int(g.sample_rate)); print('piper', v, sid, len(g.samples)/g.sample_rate, 'in', round(dt,2))
