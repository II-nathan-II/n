"""Recherche et téléchargement de séquences RÉELLES libres de droits (NASA, Wikimedia Commons), avec métadonnées de licence.

Usage :
  python3 footage.py nasa "hurricane from space station" [--images]
  python3 footage.py get nasa:<nasa_id>            # télécharge la meilleure version
  python3 footage.py commons "volcano eruption"     # recherche de vidéos Commons
  python3 footage.py get commons:<File:Nom.webm>
  python3 footage.py sheet <id>                      # planche de vignettes pour choisir les passages
"""
import os, sys, json, re, subprocess, hashlib, urllib.parse
import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ASSETS

LIB = os.path.join(ASSETS, 'footage')
# ffmpeg/ffprobe lisent les sources distantes via le proxy HTTPS de l'environnement
if os.environ.get('HTTPS_PROXY') and not os.environ.get('http_proxy'):
    os.environ['http_proxy'] = os.environ['HTTPS_PROXY']
os.makedirs(LIB, exist_ok=True)
UA = {'User-Agent': 'TikTokStudioPipeline/1.0 (https://github.com/II-nathan-II/n; educational video production) python-requests'}
S = requests.Session(); S.headers.update(UA)
import time as _time
_orig_get = S.get
def _get(url, **kw):
    for k in range(6):
        r = _orig_get(url, **kw)
        if r.status_code != 429:
            return r
        _time.sleep(5 * (k + 1))
    return r
S.get = _get

def safe(name):
    return re.sub(r'[^A-Za-z0-9_.-]+', '_', name)[:120]

def meta_path(key):
    return os.path.join(LIB, safe(key) + '.json')

# ----------------------------------------------------------------------------- NASA
def nasa_search(q, media='video', n=25, page=1):
    r = S.get('https://images-api.nasa.gov/search', params=dict(q=q, media_type=media, page=page), timeout=30)
    r.raise_for_status()
    out = []
    for it in r.json()['collection']['items'][:n]:
        d = it['data'][0]
        out.append(dict(id=d['nasa_id'], title=d.get('title', ''), center=d.get('center', ''), date=d.get('date_created', '')[:10],
                        desc=re.sub(r'\s+', ' ', d.get('description', ''))[:200], creator=d.get('secondary_creator', '') or d.get('photographer', '')))
    return out

def nasa_assets(nid):
    r = S.get(f'https://images-api.nasa.gov/asset/{urllib.parse.quote(nid)}', timeout=30)
    r.raise_for_status()
    return [i['href'] for i in r.json()['collection']['items']]

def nasa_meta(nid):
    r = S.get('https://images-api.nasa.gov/search', params=dict(nasa_id=nid), timeout=30)
    r.raise_for_status()
    items = r.json()['collection']['items']
    return items[0]['data'][0] if items else {}

def head_size(url):
    try:
        h = S.head(url, timeout=20, allow_redirects=True)
        return int(h.headers.get('Content-Length', 0))
    except Exception:
        return 0

def nasa_get(nid, max_mb=700):
    hrefs = [h.replace('http://', 'https://') for h in nasa_assets(nid)]
    vids = [h for h in hrefs if h.lower().endswith(('.mp4', '.mov', '.m4v'))]
    imgs = [h for h in hrefs if h.lower().endswith(('.jpg', '.jpeg', '.png', '.tif'))]
    pick = None
    if vids:
        order = ['~orig', '~large', '~medium', '~mobile', '~small', '~preview']
        vids.sort(key=lambda h: next((i for i, o in enumerate(order) if o in h), 9))
        for h in vids:
            sz = head_size(h)
            if 0 < sz <= max_mb * 1e6:
                pick = h; break
        pick = pick or vids[-1]
    elif imgs:
        order = ['~orig', '~large', '~medium', '~small', '~thumb']
        imgs.sort(key=lambda h: next((i for i, o in enumerate(order) if o in h), 9))
        imgs = [h for h in imgs if not h.lower().endswith('.tif')] or imgs
        for h in imgs:
            sz = head_size(h)
            if 0 < sz <= 80e6:
                pick = h; break
        pick = pick or imgs[0]
    if not pick:
        raise RuntimeError(f'aucun fichier pour {nid}')
    ext = os.path.splitext(urllib.parse.urlparse(pick).path)[1].lower()
    key = 'nasa_' + nid
    path = os.path.join(LIB, safe(key) + ext)
    if not os.path.exists(path):
        _download(pick, path)
    d = nasa_meta(nid)
    meta = dict(key=key, source='NASA Image and Video Library', id=nid, url=pick, page=f'https://images.nasa.gov/details/{urllib.parse.quote(nid)}',
                title=d.get('title', ''), center=d.get('center', ''), date=d.get('date_created', '')[:10],
                credit=d.get('secondary_creator') or d.get('photographer') or d.get('center') or 'NASA',
                license='Domaine public (média NASA — usage libre, sans logo NASA ni suggestion de soutien)', path=path)
    json.dump(meta, open(meta_path(key), 'w'), ensure_ascii=False, indent=1)
    return meta

def nasa_remote(nid):
    """Très gros fichiers NASA : pas de téléchargement, ffmpeg lit seulement les passages utiles (requêtes HTTP partielles)."""
    key = 'nasar_' + nid
    mp = meta_path(key)
    if os.path.exists(mp):
        return json.load(open(mp))
    hrefs = [h.replace('http://', 'https://').replace(' ', '%20') for h in nasa_assets(nid)]
    vids = [h for h in hrefs if h.lower().endswith('.mp4')]
    order = ['~orig', '~large', '~medium', '~small', '~mobile']
    vids.sort(key=lambda h: next((i for i, o in enumerate(order) if o in h), 9))
    d = nasa_meta(nid)
    meta = dict(key=key, source='NASA Image and Video Library', id=nid, url=vids[0], page=f'https://images.nasa.gov/details/{urllib.parse.quote(nid)}',
                title=d.get('title', ''), credit=d.get('secondary_creator') or d.get('center') or 'NASA',
                license='Domaine public (média NASA — image uniquement)', path=vids[0])
    json.dump(meta, open(mp, 'w'), ensure_ascii=False, indent=1)
    return meta

# ----------------------------------------------------------------------------- NASA Scientific Visualization Studio
def svs_search(q, n=20):
    r = S.get('https://svs.gsfc.nasa.gov/api/search/', params=dict(search=q, limit=n), timeout=30)
    r.raise_for_status()
    return [dict(id=x['id'], type=x.get('result_type', ''), date=(x.get('release_date') or '')[:10], title=x.get('title', '')) for x in r.json()['results']]

def svs_page(pid):
    r = S.get(f'https://svs.gsfc.nasa.gov/api/{pid}', timeout=30)
    r.raise_for_status()
    return r.json()

def svs_movies(pid):
    d = svs_page(pid)
    out = []
    for g in d.get('media_groups', []):
        for it in g.get('items', []):
            inst = it.get('instance') or it
            if isinstance(inst, dict) and inst.get('media_type') == 'Movie' and str(inst.get('filename', '')).lower().endswith(('.mp4', '.mov', '.webm')):
                out.append(dict(file=inst['filename'], w=inst.get('width'), h=inst.get('height'), url=inst['url'].replace('http://', 'https://'),
                                alt=re.sub(r'\s+', ' ', inst.get('alt_text') or '')[:160]))
    return d, out

def svs_credit(d):
    txt = d.get('description') or ''
    m = re.search(r'Credit:\s*(.+?)(?:Music:|Watch this|Complete transcript|$)', txt)
    return (m.group(1).strip() if m else "NASA's Goddard Space Flight Center Scientific Visualization Studio")[:200]

def svs_get(pid, filename):
    d, movies = svs_movies(pid)
    mv = next((m for m in movies if m['file'] == filename), None)
    if mv is None:
        raise RuntimeError(f'{filename} introuvable dans SVS {pid}')
    key = f'svs_{pid}_{filename}'
    path = os.path.join(LIB, safe(key))
    if not os.path.exists(path):
        _download(mv['url'], path)
    meta = dict(key=key, source='NASA Scientific Visualization Studio', id=f'{pid}/{filename}', url=mv['url'], page=f'https://svs.gsfc.nasa.gov/{pid}/',
                title=d.get('title', ''), credit=svs_credit(d), license='Domaine public (NASA — image uniquement, bande-son non utilisée)', path=path)
    json.dump(meta, open(meta_path(key), 'w'), ensure_ascii=False, indent=1)
    return meta

# ----------------------------------------------------------------------------- Wikimedia Commons
OK_LICENSES = re.compile(r'^(public domain|pd|cc0|cc by(?!-nc)(?!-nd)[- ]?\d|cc-by-\d|cc by \d)', re.I)

def commons_search(q, n=25, video=True):
    sr = f'{q} filetype:video' if video else f'{q} filetype:bitmap'
    r = S.get('https://commons.wikimedia.org/w/api.php', params=dict(action='query', format='json', generator='search', gsrsearch=sr, gsrnamespace=6,
              gsrlimit=n, prop='imageinfo', iiprop='url|size|extmetadata|mediatype', iiextmetadatafilter='LicenseShortName|Artist|Credit|ImageDescription'), timeout=30)
    r.raise_for_status()
    out = []
    for p in (r.json().get('query', {}).get('pages', {}) or {}).values():
        ii = p.get('imageinfo', [{}])[0]
        em = ii.get('extmetadata', {})
        lic = em.get('LicenseShortName', {}).get('value', '')
        out.append(dict(id=p['title'], lic=lic, ok=bool(OK_LICENSES.match(lic.strip())) and 'SA' not in lic.upper(),
                        w=ii.get('width'), h=ii.get('height'), dur=ii.get('duration'), size_mb=round(ii.get('size', 0) / 1e6, 1),
                        artist=re.sub('<[^>]+>', '', em.get('Artist', {}).get('value', ''))[:80]))
    return out

def commons_get(title):
    r = S.get('https://commons.wikimedia.org/w/api.php', params=dict(action='query', format='json', titles=title, prop='imageinfo',
              iiprop='url|size|extmetadata', iiextmetadatafilter='LicenseShortName|Artist|Credit|LicenseUrl'), timeout=30)
    r.raise_for_status()
    p = next(iter(r.json()['query']['pages'].values()))
    ii = p['imageinfo'][0]; em = ii.get('extmetadata', {})
    lic = em.get('LicenseShortName', {}).get('value', '')
    if not (OK_LICENSES.match(lic.strip()) and 'SA' not in lic.upper()):
        raise RuntimeError(f'licence refusée pour usage commercial simple : {lic}')
    url = ii['url']
    ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
    key = 'commons_' + title.replace('File:', '')
    path = os.path.join(LIB, safe(key) + ext)
    if not os.path.exists(path):
        _download(url, path)
    meta = dict(key=key, source='Wikimedia Commons', id=title, url=url, page=ii.get('descriptionurl', ''),
                title=title.replace('File:', ''), credit=re.sub('<[^>]+>', '', em.get('Artist', {}).get('value', '')).strip(),
                license=lic, license_url=em.get('LicenseUrl', {}).get('value', ''), path=path)
    json.dump(meta, open(meta_path(key), 'w'), ensure_ascii=False, indent=1)
    return meta

def _download(url, path):
    tmp = path + '.part'
    with S.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(tmp, 'wb') as fh:
            for chunk in r.iter_content(1 << 20):
                fh.write(chunk)
    os.replace(tmp, path)

# ----------------------------------------------------------------------------- outils
def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_streams', '-show_format', path], capture_output=True, text=True).stdout
    d = json.loads(out)
    v = next((s for s in d.get('streams', []) if s['codec_type'] == 'video'), {})
    return dict(w=v.get('width'), h=v.get('height'), dur=float(d.get('format', {}).get('duration', 0) or 0), fps=v.get('r_frame_rate'))

def sheet(path, out, n=16, cols=8):
    import numpy as np, cv2
    info = probe(path)
    dur = info['dur']
    tiles = []
    if dur <= 0.5:  # image fixe
        img = cv2.imread(path)
        tiles = [cv2.resize(img, (320, int(320 * img.shape[0] / img.shape[1])))]
        cv2.imwrite(out, tiles[0]); return info
    for k in range(n):
        t = (k + 0.5) * dur / n
        r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.2f}', '-i', path, '-frames:v', '1', '-vf', 'scale=320:-2', '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True)
        img = cv2.imdecode(np.frombuffer(r.stdout, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            continue
        cv2.putText(img, f'{t:.1f}s', (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        tiles.append(img)
    h = max(t.shape[0] for t in tiles)
    tiles = [cv2.copyMakeBorder(t, 0, h - t.shape[0], 0, 0, cv2.BORDER_CONSTANT) for t in tiles]
    while len(tiles) % cols:
        tiles.append(tiles[0] * 0)
    cv2.imwrite(out, np.vstack([np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]), [cv2.IMWRITE_JPEG_QUALITY, 80])
    return info

def resolve(ref):
    """'nasa:<id>' ou 'commons:File:...' → métadonnées (télécharge si besoin)."""
    src, _, ident = ref.partition(':')
    if src == 'nasar':
        return nasa_remote(ident)
    if src == 'svs':
        pid, _, fn = ident.partition('/')
        key = f'svs_{pid}_{fn}'
        mp = meta_path(key)
        if os.path.exists(mp) and os.path.exists(json.load(open(mp))['path']):
            return json.load(open(mp))
        return svs_get(int(pid), fn)
    key = ('nasa_' + ident) if src == 'nasa' else ('commons_' + ident.replace('File:', ''))
    mp = meta_path(key)
    if os.path.exists(mp):
        m = json.load(open(mp))
        if os.path.exists(m['path']):
            return m
    return nasa_get(ident) if src == 'nasa' else commons_get(ident)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'nasa':
        media = 'image' if '--images' in sys.argv else 'video'
        for r in nasa_search(sys.argv[2], media):
            print(f"{r['id']} | {r['date']} | {r['center']} | {r['title'][:70]}")
    elif cmd == 'svs':
        for r in svs_search(sys.argv[2]):
            print(f"{r['id']} | {r['date']} | {r['type'][:16]:16} | {r['title'][:80]}")
    elif cmd == 'svsfiles':
        d, mv = svs_movies(int(sys.argv[2]))
        print(d.get('title')); print('CREDIT:', svs_credit(d))
        for m in mv:
            print(f"  {m['file']} | {m['w']}x{m['h']} | {m['alt'][:90]}")
    elif cmd == 'commons':
        for r in commons_search(sys.argv[2], video='--images' not in sys.argv):
            print(f"{'OK ' if r['ok'] else 'NO '}{r['lic'][:14]:14} | {r['w']}x{r['h']} | {r['dur']}s | {r['size_mb']}MB | {r['id'][:80]}")
    elif cmd == 'get':
        m = resolve(sys.argv[2]); print(json.dumps(m, ensure_ascii=False)); print(probe(m['path']))
    elif cmd == 'sheet':
        m = resolve(sys.argv[2]); print(sheet(m['path'], sys.argv[3]))
