"""NICHE_1 « Vertige Cosmique » — style « réflexion » (voir TikTok_Viral_Project/ANALYSE/STYLE_ESPACE_V3.md).

Animations 3D calculées par nos soins (layers_cine : planètes texturées avec les cartes NASA du domaine public,
étoiles, filaments, atome, galaxie), un mot à la fois en police à empattements, ton philosophique.
Faits vérifiés (sources dans docs.SOURCES).
"""
from common import W, H
from layers_base import Composite as C
import layers_cine as L
from videos_real import seg, V
from videos_space2 import SN

CINE = dict(grain=0.0, vignette=0.28)
NEURON = ((0.25, 0.95, 1.0), (0.3, 1.0, 0.65), (1.0, 0.65, 0.35))
BLOOD = ((1.0, 0.32, 0.28), (1.0, 0.55, 0.38), (1.0, 0.82, 0.55))
EARTH_N = 'earth_night_4k.jpg'
MID = (W / 2, H * 0.46)


def sc(*makers):
    """Scène = couches recréées à chaque appel."""
    return lambda: C([m() for m in makers])


REF01 = dict(
    id='reflexion_01', niche='NICHE_1', theme='reflexion', speed=1.0, voice_reverb=0.12, **CINE,
    title="L'infime et l'infini",
    hook_text="L'infime et l'infini",
    hook_y=330,
    music=dict(style='space', prog='minor_wonder', key=45, bpm=62, seed=2601, start=0.2),
    segments=[
        seg("Tu es fait d'environ sept milliards de milliards de milliards d'atomes.",
            sc(lambda: L.StarField(seed=3, bright=0.35), lambda: L.Filaments(seed=3, grow=[(0, 0.0), (5.5, 1.0)], center=MID, spin=0.1)),
            'slow_in', sfx=['boom'], music=0.45, emph=['atomes']),
        seg("Et pourtant, un atome… c'est presque du vide.",
            sc(lambda: L.Atom(center=MID, cloud=560)), 'slow_in', 'fade', emph=['vide']),
        seg("Si son noyau avait la taille d'une bille posée au centre d'un stade, ses électrons tourneraient quelque part… dans les tribunes.",
            sc(lambda: L.Atom(center=MID, cloud=1500, nucleus_scale=0.22, n_e=90000)), 'out', 'fade', emph=['bille', 'tribunes']),
        seg("Toi, moi, tout ce que tu touches… c'est surtout du vide.",
            sc(lambda: L.StarField(seed=5, bright=0.5, drift=(0, -6)), lambda: L.Filaments(seed=21, grow=[(0, 1.0)], center=MID, spin=0.08, bright=0.45)),
            'slow_in', 'black', emph=['vide']),
        seg("Maintenant, recule.",
            sc(lambda: L.StarField(seed=7, bright=0.7), lambda: L.Globe(night=EARTH_N, r=[(0, 2600), (2.2, 430)], c=MID, lon0=5, spin=3.0)),
            'static', 'fade', sfx=['whoosh'], emph=['recule'], music=0.6),
        seg("La Terre. Plus de huit milliards d'humains sur une petite boule de roche, qui tourne dans le noir.",
            sc(lambda: L.StarField(seed=7, bright=0.7), lambda: L.Rays(center=MID), lambda: L.Globe(night=EARTH_N, r=430, c=MID, lon0=12, spin=3.0)),
            'slow_in', 'cut', emph=['Terre', 'huit']),
        seg("Recule encore. Vue de six milliards de kilomètres, elle n'est plus qu'un point bleu pâle.",
            sc(lambda: L.StarField(seed=8, bright=0.8), lambda: L.Globe(night=EARTH_N, r=[(0, 430), (3.4, 1.5)], c=MID, lon0=30, spin=3.0),
               lambda: L.Halo(center=MID, size=2.2, ring=46, fade=[(0, 0.0), (3.2, 0.0), (3.8, 1.0)], t_ring=3.8)),
            'static', 'fade', emph=['point', 'bleu', 'pâle']),
        seg("Notre Soleil n'est qu'une étoile parmi cent à quatre cents milliards, rien que dans notre galaxie.",
            sc(lambda: L.StarField(seed=9, bright=0.45), lambda: L.Galaxy(center=MID, r=[(0, 260), (6, 520)], spin=0.06)),
            'slow_in', 'fade', emph=['Soleil', 'galaxie']),
        seg("Et notre galaxie n'est qu'une parmi des centaines de milliards d'autres.",
            sc(lambda: L.Web(fade=[(0, 0.0), (0.8, 1.0)])), 'out', 'fade', emph=['centaines']),
        seg("Il y aurait plus d'étoiles dans l'Univers que de grains de sable sur toutes les plages de la Terre.",
            sc(lambda: L.StarField(seed=12, n=9000, bright=0.9, speed=0.05), lambda: L.Galaxy(center=(W * 0.3, H * 0.3), r=160, tilt=50, seed=2, fade=[(0, 0.6)]),
               lambda: L.Galaxy(center=(W * 0.72, H * 0.68), r=110, tilt=70, seed=4, roll=40, fade=[(0, 0.5)])),
            'slow_in', 'fade', emph=['étoiles', 'sable']),
        seg("De quoi se sentir minuscule.",
            sc(lambda: L.StarField(seed=14, bright=0.6, drift=(0, 8))), 'static', 'black', music=0.35, emph=['minuscule']),
        seg("Mais regarde de plus près : le fer de ton sang, le calcium de tes os… ont été fabriqués au cœur d'étoiles, il y a des milliards d'années.",
            V(SN, 6.0, speed=0.6), 'slow_in', 'flash', sfx=['impact'], emph=['fer', 'calcium'], music=0.7),
        seg("Tu es, littéralement, de la poussière d'étoiles.",
            sc(lambda: L.StarField(seed=15, bright=0.35), lambda: L.Filaments(seed=8, palette=BLOOD, grow=[(0, 0.2), (4, 1.0)], center=MID, spin=0.1)),
            'slow_in', 'fade', emph=['poussière', 'étoiles']),
        seg("L'astronome Carl Sagan disait : nous sommes un moyen pour le cosmos de se connaître lui-même.",
            sc(lambda: L.StarField(seed=16, bright=0.4), lambda: L.Filaments(seed=33, roots=11, grow=[(0, 0.3), (5, 1.0)], center=MID, spin=0.07)),
            'slow_in', 'fade', emph=['cosmos', 'lui-même'], music=0.75),
        seg("Alors… infime, ou infini ? Dis-le-moi en commentaire.",
            sc(lambda: L.StarField(seed=7, bright=0.7), lambda: L.Rays(center=MID), lambda: L.Globe(night=EARTH_N, r=[(0, 300), (5, 380)], c=MID, lon0=40, spin=3.0)),
            'slow_in', 'fade', emph=['infime', 'infini'], music=0.4),
    ])

VIDEOS = [REF01]
