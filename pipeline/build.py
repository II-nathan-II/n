"""Point d'entrée : python3 build.py [video_01 ...] [--preview] [--seconds N] [--jobs N]"""
import os, sys, argparse, time, json
from concurrent.futures import ProcessPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import PROJECT, WORK

def all_videos():
    import videos_space, videos_psy
    return {v['id']: v for v in videos_space.VIDEOS + videos_psy.VIDEOS}

def run_one(vid, preview, seconds, force=False):
    import render
    v = all_videos()[vid]
    outdir = os.path.join(PROJECT, v['niche'])
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, f'{vid}.mp4') if not preview else os.path.join(WORK, f'{vid}_preview.mp4')
    wd = os.path.join(WORK, vid)
    t = time.time()
    render.render_video(v, out, wd, preview=preview, max_seconds=seconds, force_frames=force)
    return vid, out, time.time() - t

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('ids', nargs='*')
    ap.add_argument('--preview', action='store_true')
    ap.add_argument('--seconds', type=float, default=None)
    ap.add_argument('--jobs', type=int, default=1)
    ap.add_argument('--force-frames', action='store_true')
    a = ap.parse_args()
    ids = a.ids or sorted(all_videos())
    os.makedirs(WORK, exist_ok=True)
    if a.jobs <= 1:
        for vid in ids:
            print(run_one(vid, a.preview, a.seconds, a.force_frames), flush=True)
    else:
        with ProcessPoolExecutor(a.jobs) as ex:
            futs = [ex.submit(run_one, vid, a.preview, a.seconds, a.force_frames) for vid in ids]
            for f in as_completed(futs):
                try:
                    print(f.result(), flush=True)
                except Exception as e:
                    import traceback; traceback.print_exc()
