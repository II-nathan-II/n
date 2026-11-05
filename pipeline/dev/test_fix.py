import sys; sys.path.insert(0, '/home/user/n/pipeline'); sys.path.insert(0, '/home/user/n/pipeline/dev')
from sheet import sheet
from layers_base import *
from layers_space import *
from layers_psy import *
S = [('grid', Composite([SpaceBG(26, 'deep', 0.4), SpacetimeGrid(depth=2.6, waves=1.0)])),
     ('grid_deep', Composite([SpaceBG(61, 'deep', 0.3), SpacetimeGrid(depth=5.0)])),
     ('checker', Composite([Checker()], clean=True)),
     ('checker_bars', Composite([Checker(mode='bars', t0=0.0)], clean=True)),
     ('thermo', Composite([VenusSurface(seed=12), Fn(lambda f, t, d: f.__imul__(0.45)), Thermometer()])),
     ('bars', Composite([SpaceBG(72, 'deep', 0.3), Bars([('1 tour sur elle-même', 243, (255, 190, 90)), ('1 tour du Soleil', 225, (110, 180, 255))], 243, y0=720)])),
     ('co2', Composite([GradientBG(), Molecule([('C', (0, 0, 0)), ('O', (-0.75, 0, 0)), ('O', (0.75, 0, 0))], label='CO2', scale=220, wobble=True)])),
     ('star_grow', Composite([SpaceBG(3, 'purple', 0.8, zoom=(1.0, 1.7), drift=(0, 0)), Star(40, size1=330, color=(255, 190, 120), corona=1.2)])),
]
sheet(S, sys.argv[1], cols=4, t_frac=0.9)
