import sys; sys.path.insert(0, '/home/user/n/pipeline'); sys.path.insert(0, '/home/user/n/pipeline/dev')
from sheet import sheet
from layers_base import *
from layers_space import *
S = [('blackhole', Composite([SpaceBG(4, 'purple', 0.6), BlackHole()])),
     ('bh_close', Composite([SpaceBG(4, 'deep', 0.6), BlackHole(rs=180, incl=0.12)])),
     ('galaxy', Composite([SpaceBG(5, 'deep'), Galaxy(size=1000, incl=1.0)])),
     ('rain', Composite([CloudLayers('cobalt'), GlassRain()])),
     ('vent', Composite([Vent(), Particles(80, (180,200,220), (1,3), (5,-15), 0.4)])),
     ('web', Composite([Solid((1,1,4)), CosmicWeb(highlight_void=0.8)])),]
sheet(S, sys.argv[1], cols=3, scale=0.3)
