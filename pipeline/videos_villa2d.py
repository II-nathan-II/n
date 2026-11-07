"""« Villa Vitamine » — épisode 1 en dessin animé 2D (test, pas destiné à la publication pour l'instant).

Même histoire que la version IA prévue (fruits_series.EPISODES[0]) : on reprend les répliques du script,
mais tout est dessiné par nos soins (layers_villa) et chaque personnage a sa voix (mélange de timbres Kokoro).
"""
from common import W, H
from layers_base import Composite
import layers_villa as V
from videos_real import seg

VOICE = dict(ananas=('mix:ff_siwis=0.55,am_onyx=0.45', 0.92), kiki=('mix:ff_siwis=0.5,im_nicola=0.5', 1.04),
             berenice=('mix:ff_siwis=0.6,if_sara=0.4', 1.0), cyril=('mix:ff_siwis=0.4,bm_george=0.6', 0.97),
             pepin=('mix:ff_siwis=0.5,am_puck=0.5', 1.02), fanny=('ff_siwis', 1.15))
HEX = dict(kiki='8CD64B', berenice='FFE135', cyril='F4F14A', pepin='B6F36A', fanny='FF6D8A', ananas='FFC93C')
COL = dict(kiki=(0.55, 0.84, 0.29), berenice=(1.0, 0.88, 0.21), cyril=(0.96, 0.94, 0.29), pepin=(0.71, 0.95, 0.42),
           fanny=(1.0, 0.30, 0.43), ananas=(1.0, 0.79, 0.24))
GROUND = 1430


def line(who, text, scene, cam='static', trans='cut', mark=None, **kw):
    v, sp = VOICE[who]
    return seg(text, scene, cam, trans, voice=v, speed=sp, active=HEX[who], mark=mark or who, **kw)


def hold(scene, secs, cam='static', trans='cut', **kw):
    return seg('', scene, cam, trans, hold=secs, **kw)


def comp(*layers):
    return Composite(list(layers), clean=True)


def conf(who, mark, name, role, expr='smile', arms='down', wink=None):
    def make(ctx):
        return comp(V.Set('conf'), V.Fruit(who, (540, 1390), 620, expr, arms, talk=mark, ctx=ctx, wink=wink),
                    V.ConfFront(), V.NameTag(name, role, COL[who]), V.Bug())
    return make


SUITCASE = lambda: V.spr_suitcase(170, (1.0, 0.72, 0.25))


def sc_cold(ctx):
    return comp(V.Set('portail'),
                V.Fruit('ananas', (400, 1560), 470, 'sly', 'key', gaze=[(0, -1.0), (1.0, 1.0)], ctx=ctx),
                V.Fruit('margaux', (720, 1560), 470, legs=True, shadow=True),
                V.Prop(lambda: V.spr_suitcase(150, (0.35, 0.30, 0.45), sticker=(1.0, 0.55, 0.20)), (880, 1480)),
                V.Vignette(0.55))


def sc_logo(ctx):
    return comp(V.Set('villa'), V.Logo(780, 0.15, 'ÉPISODE 1 · BIENVENUE À LA VILLA'))


def sc_host(ctx):
    return comp(V.Set('piscine'), V.Fruit('ananas', (540, 1325), 560, 'smile', [(0, 'down'), (0.3, 'open')], talk='h1', ctx=ctx), V.Bug())


def sc_kiki_in(ctx):
    return comp(V.Set('villa'),
                V.Prop(SUITCASE, [(0, (-60, 1340)), (1.4, (640, 1340))]),
                V.Fruit('kiki', [(0, (-200, GROUND)), (1.4, (470, GROUND))], 470, 'smirk', talk='k1', ctx=ctx, gaze=[(0, 1.0), (1.6, 0.0)]),
                V.Bug())


def sc_berenice_in(ctx):
    return comp(V.Set('villa'),
                V.Fruit('berenice', [(0, (1260, GROUND)), (1.5, (560, GROUND))], 490, 'diva', 'hip', shades=True, talk='b1', ctx=ctx,
                        rot=[(0, 0), (0.4, 4), (0.8, -4), (1.2, 4), (1.5, 0)]),
                V.Bug())


def sc_cyril_in(ctx):
    return comp(V.Set('salon'),
                V.Fruit('cyril', [(0, (-200, 1500)), (1.3, (520, 1500))], 470, 'grumpy', 'cross', talk='c1', ctx=ctx, gaze=[(0, 1.0), (1.4, -0.6)]),
                V.Bug())


def sc_pepin(ctx):
    p = [(0, (-180, 1500)), (0.8, (420, 1500)), (1.05, (560, 1490)), (1.6, (560, 1490)), (2.0, (600, 1500))]
    return comp(V.Set('salon'),
                V.Prop(lambda: V.spr_suitcase(120, (0.55, 0.84, 0.29)), (500, 1450), rot=-90),
                V.Prop(lambda: V.spr_cushion(240, 90), (760, 1470)),
                V.Fruit('pepin', p, 440, [(0, 'smile'), (0.8, 'shock'), (1.9, 'shy')], talk='p1', ctx=ctx,
                        rot=[(0, 0), (0.8, 0), (1.05, -82), (1.6, -82), (2.0, 0)], shadow=True),
                V.Prop(lambda: V.spr_stars_dizzy(60), [(1.1, (720, 1300)), (2.0, (620, 990)), (3.0, (610, 990))], t0=1.1, t1=3.2),
                V.Pill('CHUTES DE PÉPIN : 1', (780, 330), 1.2, (0.71, 0.95, 0.42)),
                V.Bug())


def sc_kitchen(ctx):
    return comp(V.Set('cuisine'),
                V.Fruit('kiki', (260, 1660), 400, 'smile', gaze=[(0, -1.0), (0.6, 1.0)], phase=0.7),
                V.Fruit('berenice', (500, 1660), 420, 'smile', 'glass', gaze=[(0, -1.0), (0.7, 1.0)], phase=1.4),
                V.Fruit('fanny', [(0, (1300, 1680)), (0.7, (820, 1680))], 430, 'smile', 'phone', talk='f1', ctx=ctx, gaze=-1.0),
                V.Bug())


def sc_react(ctx):
    return comp(V.Set('cuisine'),
                V.Fruit('kiki', (300, 1720), 560, [(0, 'smile'), (0.3, 'sly')], gaze=0.5, bob=0),
                V.Fruit('berenice', (760, 1720), 580, [(0, 'smile'), (0.3, 'shock')], [(0, 'glass'), (0.55, 'down')], gaze=-0.3, bob=0),
                V.Prop(lambda: V.spr_ball(30, (1.0, 0.65, 0.20), None, False, True), [(0.55, (940, 1360)), (1.05, (930, 1700))], t0=0.55, t1=1.05),
                V.Splash((930, 1700), 1.05),
                V.Vignette(0.35))


def sc_portal(ctx):
    return comp(V.Set('portail'),
                V.Fruit('ananas', (400, 1560), 480, 'sly', 'key', talk='a2', ctx=ctx, gaze=[(0, -1.0), (0.8, 1.0), (1.6, -1.0), (2.4, 1.0)]),
                V.Fruit('margaux', (720, 1560), 480),
                V.Prop(lambda: V.spr_suitcase(150, (0.35, 0.30, 0.45), sticker=(1.0, 0.55, 0.20)), (880, 1480)),
                V.Vignette(0.55))


def sc_end(ctx):
    heads = [V.Fruit(w, (150 + k * 195, 1180), 230, 'smile', phase=k * 0.6) for k, w in enumerate(['kiki', 'berenice', 'cyril', 'pepin', 'fanny'])]
    return comp(V.Set('villa'), V.Vignette(0.7), V.Logo(430, 0.0), *heads,
                V.Pill('TON FRUIT PRÉFÉRÉ ?', (540, 800), 0.3, (1.0, 0.42, 0.62), 64, (255, 255, 255)),
                V.Pill('ÉPISODE 2 : LA NOUVELLE ARRIVE', (540, 1340), 0.9, (1.0, 0.83, 0.24), 44))


VV01 = dict(
    id='villa2d_episode_01', niche='NICHE_3_VILLA_VITAMINE', theme='villa', speed=1.0, voice_reverb=0.02, grain=0.0, vignette=0.0,
    title="Villa Vitamine — épisode 1 (dessin animé, test)",
    hook_text="6 FRUITS, 1 VILLA…\\NET UN SECRET DÈS LE 1ER SOIR", hook_y=360, hook_min=2.6,
    music=dict(style='lofi', prog='lofi_c', key=50, bpm=96, seed=6101, start=0.35, db=-28.5),
    segments=[
        hold(sc_cold, 2.6, 'slow_in', sfx=[('riser', 2.5)], music=0.35),
        hold(sc_logo, 2.6, 'static', 'flash', sfx=['boom', ('pop', 0.2), ('ding', 0.7)], music=0.85),
        line('ananas', "Bienvenue à la Villa Vitamine ! Six fruits, un été… et une seule règle : rester frais !", sc_host, 'slow_in', mark='h1', music=0.5),
        line('kiki', "La villa, le soleil, la piscine… Franchement, j'ai la pêche !", sc_kiki_in, 'static', 'whip', mark='k1'),
        line('kiki', "Moi c'est Kiki. Tout doux à l'extérieur… et très sucré à l'intérieur.",
             conf('kiki', 'k2', 'KIKI', 'le tombeur', 'smirk', wink=(2.2, 2.7)), 'slow_in', mark='k2'),
        line('berenice', "Coucou la villa ! Votre reine est arrivée.", sc_berenice_in, 'static', 'whip', mark='b1'),
        line('berenice', "Je suis pas venue pour me faire des amis. Je suis venue pour briller.",
             conf('berenice', 'b2', 'BÉRÉNICE', 'la reine du drama', 'diva', 'hip'), 'slow_in', mark='b2'),
        line('cyril', "Encore une villa pleine de fruits trop mûrs…", sc_cyril_in, 'static', 'whip', mark='c1'),
        line('cyril', "C'est pas pour être acide, mais je donne trois jours à Kiki avant de se faire presser.",
             conf('cyril', 'c2', 'CYRIL', "l'acide", 'grumpy', 'cross'), 'slow_in', mark='c2'),
        hold(sc_pepin, 1.55, 'static', 'whip', sfx=[('impact', 1.05)]),
        line('pepin', "Ça va, ça va ! Je suis juste… tombé dans les pommes.", 'same', mark='p1'),
        line('fanny', "Vous savez pas la nouvelle ? Demain… une nouvelle arrive à la villa !", sc_kitchen, 'static', 'whip', mark='f1', music=0.6),
        hold(sc_react, 2.4, 'in', 'cut', sfx=['boom', ('impact', 1.05)], music=0.9),
        line('ananas', "Personne ne doit savoir… Bienvenue, ma chérie.", sc_portal, 'slow_in', 'black', mark='a2', sfx=[('riser', 2.0)], music=0.35),
        hold(sc_end, 3.6, 'static', 'flash', sfx=['boom', ('pop', 0.3), ('pop', 0.9)], music=0.8),
    ])

VIDEOS = [VV01]
