import sys; sys.path.insert(0, '/home/user/n/pipeline'); sys.path.insert(0, '/home/user/n/pipeline/dev')
from sheet import sheet
from layers_base import *
from layers_space import *
sheet([('row', Composite([SpaceBG(39, 'deep', 0.4), GalaxyRow(n=12), Text('× 3 000', 760, 1060, 130, 'anton', (255, 216, 74), t0=1.5)]))], sys.argv[1], cols=1, t_frac=0.9, scale=0.35)
